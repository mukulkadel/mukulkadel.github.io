---
layout: page
title: Tags
permalink: /tags/
description: Browse all posts by tag.
excerpt_separator: "<!--more-->"
---

{% assign tags_sorted = site.tags | sort %}
{% if tags_sorted.size > 0 %}
<div class="category-grid" style="margin-bottom:3rem;">
  {% for tag in tags_sorted %}
  <a class="category-card" href="#{{ tag[0] | slugify }}" id="{{ tag[0] | slugify }}-link">
    <span class="category-card-name">{{ tag[0] }}</span>
    <span class="category-card-count">{{ tag[1].size }}</span>
  </a>
  {% endfor %}
</div>

{% for tag in tags_sorted %}
<section id="{{ tag[0] | slugify }}" style="margin-bottom:2.5rem;">
  <h2 style="border-bottom:1px solid var(--border);padding-bottom:0.4rem;">{{ tag[0] }}</h2>
  <ul class="post-list" style="margin-top:1rem;">
    {% for post in tag[1] %}
      {% include post-card.html post=post %}
    {% endfor %}
  </ul>
</section>
{% endfor %}
{% endif %}
