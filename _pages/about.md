---
layout: about
title: about
permalink: /
subtitle: Genome regulation and evolution research group

profile:
  align: right
  image:
  image_circular: false

selected_papers: false
social: true # includes social icons at the bottom of the page

announcements:
  enabled: false

latest_posts:
  enabled: false
---

<div style="text-align: center; margin: 0 auto 2rem auto;">
  <picture>
    <source srcset="/assets/img/reggae-480.webp" type="image/webp">
    <img src="/assets/img/reggae.tiff" style="width: 324px;" alt="EMERGE group">
  </picture>
</div>

Welcome to the G**e**no**me** **r**e**g**ulation and **e**volution (EMERGE) research group. 


EMERGE is a cross-faculty research group at NMBU uniting three research groups with complementary expertise in genome regulation, bioinformatics, and evolutionary biology. 

- **The Sandve lab** studies how genomes evolve with a focus on how large scale genome reorganization (polyploidy, transposable elements, genome scrambling) shape genome regulation including 3D organization. 

- **The Hvidsten lab** develops computational and statistical methods to model gene regulatory networks and understand how network-level properties give rise to novel gene regulation and traits. 

- **The Fjellheim lab** investigates how temperate grasses (Pooideae) evolved adaptations to cold climates over 65 million years, combining transcriptomics, genomics, and phylogenetics to trace the molecular basis of traits like frost tolerance and evolutionary biology to trace the molecular basis of traits like frost tolerance and flowering time. 

Together, EMERGE addresses fundamental questions about how genomes and traits evolves — from the molecular mechanisms to the ecological and evolutionary forces that drive adaptation across species.

Browse our [publications](/publications/), meet the [team](/profiles/), or explore our [projects](/projects/).

---

{% assign latest = site.posts.first %}
{% if latest %}
<div style="background: #f9f9f9; border-left: 4px solid #ccc; padding: 1rem 1.2rem; border-radius: 4px; margin-top: 1rem;">
  <div style="font-size: 0.8rem; color: #888; margin-bottom: 0.3rem;">Latest news — {{ latest.date | date: "%B %d, %Y" }}</div>
  <div style="font-weight: 600; margin-bottom: 0.5rem;"><a href="{{ latest.url }}">{{ latest.title }}</a></div>
  <div style="font-size: 0.9rem;">{{ latest.content | strip_html | truncatewords: 40 }}</div>
  <div style="margin-top: 0.6rem; font-size: 0.85rem;"><a href="/blog/">All news →</a></div>
</div>
{% endif %}
