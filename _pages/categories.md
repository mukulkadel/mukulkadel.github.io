---
layout: page
title: Categories
permalink: /categories/
description: Browse posts by category or tag.
excerpt_separator: "<!--more-->"
---

{% assign categories_sorted = site.categories | sort %}
{% if categories_sorted.size > 0 %}
<div class="category-grid" style="margin-bottom:3rem;">
  {% for category in categories_sorted %}
  <a class="category-card" href="#{{ category[0] | slugify }}" id="{{ category[0] | slugify }}-link">
    <span class="category-card-name">{{ category[0] }}</span>
    <span class="category-card-count">{{ category[1].size }}</span>
  </a>
  {% endfor %}
</div>

{% for category in categories_sorted %}
<section id="{{ category[0] | slugify }}" style="margin-bottom:2.5rem;">
  <h2 style="border-bottom:1px solid var(--border);padding-bottom:0.4rem;">{{ category[0] }}</h2>
  <ul class="post-list" style="margin-top:1rem;">
    {% for post in category[1] %}
      {% include post-card.html post=post %}
    {% endfor %}
  </ul>
</section>
{% endfor %}
{% endif %}
