---
layout: page
permalink: /publications/
title: publications
description: Peer-reviewed publications and bioRxiv preprints from the EMERGE labs, updated monthly from NVA (nva.sikt.no).
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

{% capture preprint_list %}{% bibliography --file preprints %}{% endcapture %}
{% if preprint_list contains '<li' %}

## preprints

<div class="publications">

{{ preprint_list }}

</div>

{% endif %}

## peer-reviewed publications

<div class="publications">

{% bibliography %}

</div>
