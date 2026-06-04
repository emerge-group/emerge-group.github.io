---
layout: page
permalink: /blog/
title: news
description: News and updates from the EMERGE research group
nav: true
nav_order: 1
---

{% for post in site.posts %}
<div style="margin-bottom: 3rem;">
  <h2 style="margin-bottom: 0.2rem;">{{ post.title }}</h2>
  <p style="color: #888; font-size: 0.9rem; margin-bottom: 1rem;">{{ post.date | date: "%B %d, %Y" }}</p>
  <div>{{ post.content }}</div>
</div>
{% unless forloop.last %}<hr>{% endunless %}
{% endfor %}

{% if site.posts.size == 0 %}
<p>No news yet — check back soon.</p>
{% endif %}
