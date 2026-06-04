#!/usr/bin/env python3
"""Fetch publications for EMERGE lab PIs from CRISTIN API and write papers.bib."""

import json
import re
import ssl
import sys
import urllib.request
from datetime import datetime

# macOS Python ships without system CA certs; create a permissive context for the CRISTIN API
_ssl_ctx = ssl.create_default_context()
try:
    import certifi
    _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE

CRISTIN_API = "https://api.cristin.no/v2"

# EMERGE lab PIs with their CRISTIN person IDs
PIS = [
    {"name": "Simen Rød Sandve",    "cristin_id": "317809"},
    {"name": "Torgeir Rhoden Hvidsten", "cristin_id": "40149"},
    {"name": "Siri Fjellheim",      "cristin_id": "317404"},
]

SUPPORTED_CATEGORIES = {"ARTICLE", "CHAPTER", "REPORT", "REVIEW", "SHORT_COMMUNICATION"}


def get(url):
    with urllib.request.urlopen(url, timeout=15, context=_ssl_ctx) as r:
        return json.loads(r.read().decode())


def fetch_all_results(cristin_id):
    results, page = [], 1
    while True:
        url = f"{CRISTIN_API}/results?contributor={cristin_id}&fields=all&per_page=50&page={page}"
        batch = get(url)
        if not batch:
            break
        results.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    return results


def fetch_contributors(cristin_result_id):
    try:
        url = f"{CRISTIN_API}/results/{cristin_result_id}/contributors?per_page=100"
        return get(url)
    except Exception:
        return []


def make_bibtex_key(result):
    first_author = ""
    preview = result.get("contributors", {}).get("preview", [])
    if preview:
        first_author = preview[0].get("surname", "Unknown")
    year = result.get("year_published", "0000")
    title = result.get("title", {}).get("en") or next(iter(result.get("title", {}).values()), "")
    first_word = re.sub(r"[^a-zA-Z]", "", title.split()[0]) if title.split() else "unknown"
    return f"{first_author}{year}{first_word}"


def format_author(contributor):
    first = contributor.get("first_name", "")
    last = contributor.get("surname", "")
    if first and last:
        return f"{last}, {first}"
    return last or first


def result_to_bibtex(result, contributors):
    category = result.get("category", {}).get("code", "ARTICLE")
    bib_type = "article" if category in {"ARTICLE", "REVIEW", "SHORT_COMMUNICATION"} else \
               "incollection" if category == "CHAPTER" else "techreport"

    key = make_bibtex_key(result)
    title = result.get("title", {}).get("en") or next(iter(result.get("title", {}).values()), "No title")
    year = result.get("year_published", "")

    author_list = [format_author(c) for c in contributors] if contributors else \
                  [format_author(c) for c in result.get("contributors", {}).get("preview", [])]
    author_str = " and ".join(author_list) if author_list else "Unknown"

    journal = result.get("journal", {}).get("name") or \
              result.get("channel", {}).get("title") or \
              result.get("series", {}).get("name") or ""

    doi = next((l["url"].replace("https://doi.org/", "") for l in result.get("links", [])
                if l.get("url_type") == "DOI"), "")

    volume = result.get("volume", "")
    issue = result.get("issue", "")
    pages = result.get("pages", {})
    pages_str = ""
    if isinstance(pages, dict) and pages.get("from"):
        pages_str = f"{pages['from']}--{pages['to']}" if pages.get("to") else pages["from"]

    lines = [f"@{bib_type}{{{key},"]
    lines.append(f"  author    = {{{author_str}}},")
    lines.append(f"  title     = {{{title}}},")
    lines.append(f"  year      = {{{year}}},")
    if journal:
        field = "journal" if bib_type == "article" else "booktitle"
        lines.append(f"  {field:<9} = {{{journal}}},")
    if volume:
        lines.append(f"  volume    = {{{volume}}},")
    if issue:
        lines.append(f"  number    = {{{issue}}},")
    if pages_str:
        lines.append(f"  pages     = {{{pages_str}}},")
    if doi:
        lines.append(f"  doi       = {{{doi}}},")
    lines.append("}")
    return "\n".join(lines)


def main():
    seen_ids = set()
    entries = []

    for pi in PIS:
        print(f"Fetching publications for {pi['name']} ...", file=sys.stderr)
        results = fetch_all_results(pi["cristin_id"])
        print(f"  {len(results)} results found", file=sys.stderr)

        for result in results:
            rid = result.get("cristin_result_id")
            if rid in seen_ids:
                continue
            seen_ids.add(rid)

            category = result.get("category", {}).get("code", "")
            if category not in SUPPORTED_CATEGORIES:
                continue

            contributor_count = result.get("contributors", {}).get("count", 0)
            if contributor_count > 6:
                contributors = fetch_contributors(rid)
            else:
                contributors = result.get("contributors", {}).get("preview", [])

            entries.append(result_to_bibtex(result, contributors))

    header = f"% Auto-generated from CRISTIN API on {datetime.utcnow().strftime('%Y-%m-%d')}\n" \
             f"% PIs: Sandve (317809), Hvidsten (40149), Fjellheim (317404)\n\n"

    output = header + "\n\n".join(entries) + "\n"
    print(output)
    print(f"\nTotal: {len(entries)} unique publications written.", file=sys.stderr)


if __name__ == "__main__":
    main()
