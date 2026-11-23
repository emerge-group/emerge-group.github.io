#!/usr/bin/env python3
"""Fetch publications for the EMERGE PIs from NVA (Nasjonalt vitenarkiv) and print papers.bib.

NVA replaces CRISTIN as the Norwegian research registry. Its search API can return BibTeX
directly; this script asks for Level 1/2 (peer-reviewed) results for each PI, merges them
(shared papers appear once), tidies a few fields for the al-folio bib layout, and writes
_bibliography/papers.bib. bioRxiv preprints (any level) go to _bibliography/preprints.bib.

Usage: python3 bin/fetch_publications.py
"""
import difflib
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SEARCH_API = "https://api.nva.unit.no/search/resources"
PERSON_URI = "https://api.nva.unit.no/cristin/person/{}"
LANDING_PAGE = "https://nva.sikt.no/registration/{}"

# EMERGE lab PIs with their CRISTIN/NVA person IDs
PIS = [
    {"name": "Simen Rød Sandve", "id": "317809"},
    {"name": "Torgeir Rhoden Hvidsten", "id": "40149"},
    {"name": "Siri Fjellheim", "id": "317404"},
]

# Ask NVA itself for Level 1/2 results instead of re-deriving the level client-side:
# book chapters carry their level on the parent anthology, so NVA's own filter is the
# only reliable way to match what nva.sikt.no shows.
LEVELS = "LevelOne,LevelTwo"
# The level system started in 2004, so older papers are "Unassigned" in NVA. For those,
# keep academic articles/reviews/chapters published before 2004.
UNASSIGNED = "Unassigned"
PRE_LEVEL_YEAR = 2004
PRE_LEVEL_TYPES = {"AcademicArticle", "AcademicLiteratureReview", "AcademicChapter"}
PAGE_SIZE = 100

# bioRxiv preprints: NVA registers them as AcademicArticle with journal "BioRxiv";
# also match bioRxiv DOIs (10.1101/YYYY.MM.DD... and the newer 10.64898/... prefix).
BIORXIV_DOI = re.compile(r"10\.1101/\d{4}\.\d{2}\.\d{2}\.|10\.64898/", re.I)

BIORXIV_API = "https://api.biorxiv.org/details/biorxiv/{}"

# Preprints to always hide (bioRxiv DOI), e.g. ones published under a very different title
# that neither the bioRxiv link nor the title match catches. Add a comment saying why.
SKIP_PREPRINTS = {
    "10.1101/2024.07.05.602039",  # snowy owl centromeres -> Genome Biology 2026 (10.1186/s13059-026-04175-y)
}

# A preprint counts as published when a paper in the peer-reviewed list has the same first
# author, is from the same year or later, and has a near-identical title (SEQ_MATCH) or shares
# most of the title's key words (WORD_MATCH). Tuned on the PIs' preprints in Nov 2026.
SEQ_MATCH = 0.75
WORD_MATCH = 0.55
STOPWORDS = set("a an the of in and to for from by with on at is are as its into via using reveals reveal".split())

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_bibliography")

# BibTeX fields kept in the output (everything else NVA sends is dropped)
KEEP_FIELDS = [
    "author", "title", "journal", "booktitle", "publisher", "school", "year", "month",
    "volume", "number", "pages", "doi", "html", "isbn", "issn", "abstract",
]

HEADERS = {
    "User-Agent": "emerge-group-website (+https://emerge-group.github.io)",
    "Accept": "text/x-bibtex; charset=utf-8",
}

try:
    import certifi

    _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_ctx = ssl.create_default_context()


def fetch_bibtex_page(person_id, levels, frm):
    query = {"contributor": PERSON_URI.format(person_id), "size": PAGE_SIZE, "from": frm}
    if levels:
        query["scientificValue"] = levels
    params = urllib.parse.urlencode(query)
    req = urllib.request.Request(f"{SEARCH_API}?{params}", headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60, context=_ssl_ctx) as r:
                return r.read().decode("utf-8")
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def split_entries(text):
    """Split a BibTeX string into top-level entries by tracking brace depth."""
    entries, i, n = [], 0, len(text)
    while True:
        start = text.find("@", i)
        if start == -1:
            return entries
        brace = text.find("{", start)
        if brace == -1:
            return entries
        depth, j = 0, brace
        while j < n:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        entries.append(text[start:j + 1])
        i = j + 1


def parse_entry(raw):
    """Return (type, key, {field: value}) for one BibTeX entry with braced values."""
    m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", raw)
    if not m:
        return None
    etype, key = m.group(1).lower(), m.group(2)
    body = raw[m.end():-1]
    fields, i, n = {}, 0, len(body)
    while i < n:
        fm = re.compile(r"\s*,?\s*([A-Za-z_][\w-]*)\s*=\s*").match(body, i)
        if not fm:
            break
        name = fm.group(1).lower()
        i = fm.end()
        if i < n and body[i] == "{":
            depth, j = 0, i
            while j < n:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            fields[name] = body[i + 1:j].strip()
            i = j + 1
        else:  # bare value (numbers)
            vm = re.compile(r"([^,\n]*)").match(body, i)
            fields[name] = vm.group(1).strip().strip('"')
            i = vm.end()
    return etype, key, fields


def ascii_word(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z]", "", s)


def readable_key(fields, used):
    """AuthorYearWord, e.g. Baudement2026Developmental (suffix a, b, ... if taken)."""
    first_author = fields.get("author", "Unknown").split(" and ")[0].strip()
    if "," in first_author:
        last = first_author.split(",")[0]
    else:
        last = first_author.split()[-1] if first_author.split() else "Unknown"
    words = [ascii_word(w) for w in fields.get("title", "").split()]
    first_word = next((w for w in words if w), "untitled")
    base = f"{ascii_word(last) or 'Unknown'}{fields.get('year', '0000')}{first_word}"
    key, k = base, 0
    while key in used:
        key = base + "abcdefghijklmnopqrstuvwxyz"[k]
        k += 1
    used.add(key)
    return key


def tidy(fields, nva_id):
    doi = fields.get("doi", "")
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I).strip()
    if doi:
        fields["doi"] = doi
    else:
        fields.pop("doi", None)
        fields["html"] = LANDING_PAGE.format(nva_id)  # shown as an "HTML" button
    return {k: fields[k] for k in KEEP_FIELDS if fields.get(k)}


MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def sort_key(item):
    _, _, f = item
    year = int(f["year"]) if str(f.get("year", "")).isdigit() else 0
    return (-year, -MONTHS.get(str(f.get("month", "")).lower()[:3], 0), f.get("title", "").lower())


def fetch_all(person_id, levels):
    entries, frm = [], 0
    while True:
        page = split_entries(fetch_bibtex_page(person_id, levels, frm))
        entries += [p for p in (parse_entry(raw) for raw in page) if p]
        if len(page) < PAGE_SIZE:
            return entries
        frm += PAGE_SIZE
        time.sleep(0.3)


def is_pre_level_academic(fields):
    year = int(fields["year"]) if str(fields.get("year", "")).isdigit() else 9999
    nva_type = fields.get("note", "").replace("nva type:", "").strip()
    return year < PRE_LEVEL_YEAR and nva_type in PRE_LEVEL_TYPES


def is_biorxiv(fields):
    return "biorxiv" in fields.get("journal", "").lower() or bool(BIORXIV_DOI.search(fields.get("doi", "")))


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def ascii_lower(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def title_words(t):
    return re.findall(r"[a-z0-9]+", ascii_lower(t))


def key_words(t):
    return {w for w in title_words(t) if w not in STOPWORDS and len(w) > 2}


def first_author_surname(fields):
    a = fields.get("author", "").split(" and ")[0].strip()
    name = a.split(",")[0] if "," in a else (a.split()[-1] if a.split() else "")
    return ascii_lower(name)


def year_of(fields):
    y = str(fields.get("year", ""))
    return int(y) if y.isdigit() else 0


def similar_published(pre, papers):
    """Return the published paper that looks like this preprint's journal version, if any."""
    author, year = first_author_surname(pre), year_of(pre)
    pre_words, pre_title = key_words(pre.get("title", "")), " ".join(title_words(pre.get("title", "")))
    for f in papers:
        if norm_title(f.get("title", "")) == norm_title(pre.get("title", "")):
            return f
        if first_author_surname(f) != author or year_of(f) < year:
            continue
        seq = difflib.SequenceMatcher(None, pre_title, " ".join(title_words(f.get("title", "")))).ratio()
        words = key_words(f.get("title", ""))
        overlap = len(pre_words & words) / max(1, min(len(pre_words), len(words)))
        if seq >= SEQ_MATCH or overlap >= WORD_MATCH:
            return f
    return None


def biorxiv_published_doi(doi):
    """Journal DOI that bioRxiv links this preprint to, or None (also on any lookup error)."""
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi or "", flags=re.I)
    if not doi:
        return None
    req = urllib.request.Request(BIORXIV_API.format(doi), headers={"User-Agent": HEADERS["User-Agent"]})
    try:
        with urllib.request.urlopen(req, timeout=30, context=_ssl_ctx) as r:
            versions = json.loads(r.read().decode("utf-8")).get("collection") or []
    except Exception as e:
        print(f"  bioRxiv lookup failed for {doi}: {e}", file=sys.stderr)
        return None
    published = (versions[-1].get("published") or "") if versions else ""
    return published.lower() if published and published.upper() != "NA" else None


def drop_published_preprints(preprints, papers):
    paper_fields = [f for _, _, f in papers.values()]
    paper_dois = {re.sub(r"^https?://(dx\.)?doi\.org/", "", f.get("doi", ""), flags=re.I).lower()
                  for f in paper_fields}
    kept = {}
    for nva_id, entry in preprints.items():
        f = entry[2]
        label = f.get("title", "")[:70]
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", f.get("doi", ""), flags=re.I).lower()
        if doi in SKIP_PREPRINTS:
            print(f"  skipped (SKIP_PREPRINTS): {label}", file=sys.stderr)
            continue
        pub = biorxiv_published_doi(f.get("doi"))
        if pub and pub in paper_dois:
            print(f"  published (bioRxiv link {pub}): {label}", file=sys.stderr)
            continue
        match = similar_published(f, paper_fields)
        if match:
            print(f"  published (similar title: {match.get('title', '')[:50]}): {label}", file=sys.stderr)
            continue
        if pub:
            print(f"  bioRxiv says published as {pub}, not in the list yet; keeping: {label}", file=sys.stderr)
        kept[nva_id] = entry
        time.sleep(0.2)
    return kept


def render(entries):
    used, out = set(), []
    for etype, nva_id, fields in sorted(entries, key=sort_key):
        clean = tidy(dict(fields), nva_id)
        key = readable_key(clean, used)
        width = max(len(k) for k in clean)
        lines = [f"@{etype}{{{key},"]
        lines += [f"  {k:<{width}} = {{{v}}}," for k, v in clean.items()]
        lines.append("}")
        out.append("\n".join(lines))
    return "\n\n".join(out)


def write(name, header, body):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n" + body + "\n")
    return path


def main():
    papers, preprints = {}, {}
    for pi in PIS:
        print(f"Fetching {pi['name']} ...", file=sys.stderr)
        leveled = fetch_all(pi["id"], LEVELS)
        older = [e for e in fetch_all(pi["id"], UNASSIGNED) if is_pre_level_academic(e[2])]
        everything = fetch_all(pi["id"], None)
        pre = [e for e in everything if is_biorxiv(e[2])]
        for etype, nva_id, fields in leveled + older:
            if not is_biorxiv(fields):
                papers.setdefault(nva_id, (etype, nva_id, fields))
        for etype, nva_id, fields in pre:
            fields["journal"] = "bioRxiv"
            preprints.setdefault(nva_id, ("article", nva_id, fields))
        print(f"  {len(leveled)} Level 1/2 + {len(older)} pre-{PRE_LEVEL_YEAR} articles, "
              f"{len(pre)} bioRxiv preprints", file=sys.stderr)

    if not papers:
        sys.exit("No publications returned from NVA; refusing to write an empty bibliography.")

    # drop preprints whose journal version is already in the peer-reviewed list
    print("Checking preprints for published versions ...", file=sys.stderr)
    preprints = drop_published_preprints(preprints, papers)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pis = "% PIs: Sandve (317809), Hvidsten (40149), Fjellheim (317404)\n"
    write("papers.bib",
          f"% Auto-generated from NVA (nva.sikt.no) on {today}; Level 1/2 results + pre-{PRE_LEVEL_YEAR} academic articles\n" + pis,
          render(papers.values()))
    write("preprints.bib",
          f"% Auto-generated from NVA (nva.sikt.no) on {today}; bioRxiv preprints whose journal version is not in papers.bib\n" + pis,
          render(preprints.values()))
    print(f"\nWrote {len(papers)} publications and {len(preprints)} preprints.", file=sys.stderr)


if __name__ == "__main__":
    main()
