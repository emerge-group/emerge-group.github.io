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


EMERGE is a cross-faculty research group at NMBU uniting three research groups with complementary expertise in genome regulation, bioinformatics, and evolutionary biology. 

- **Sandve lab**: Genome evolution ([*read more here*](https://srsandve.org/))
- **Hvidsten lab**: Computational and statistical methods ([*read more here*](https://trhvidsten.com/))
- **Fjellheim lab**: Plant genetics and evolution ([*read more here*](https://fjellheimresearchgroup.blog/))

Together, EMERGE addresses fundamental questions about how genomes and traits evolves — from the molecular mechanisms to the ecological and evolutionary forces that drive adaptation across species.

Browse our [publications](/publications/), meet the [team](/profiles/), or explore our [projects](/projects/).

---

{% assign latest = site.posts.first %}
{% if latest %}
<div style="background: #f9f9f9; border-left: 4px solid #ccc; padding: 1rem 1.2rem; border-radius: 4px; margin-top: 1rem;">
  <div style="font-size: 0.8rem; color: #000; margin-bottom: 0.3rem;">Latest news — {{ latest.date | date: "%B %d, %Y" }}</div>
  <div style="font-weight: 600; margin-bottom: 0.5rem; color: #000;"><a href="{{ latest.url }}" style="color: #000;">{{ latest.title }}</a></div>
  <div style="font-size: 0.9rem; color: #000;">{{ latest.content | strip_html | truncatewords: 40 }}</div>
  <div style="margin-top: 0.6rem; font-size: 0.85rem;"><a href="/blog/" style="color: #000;">All news →</a></div>
</div>
{% endif %}
