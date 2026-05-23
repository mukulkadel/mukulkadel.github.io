---
layout: page
title: Categories
permalink: /categories/
description: Browse all posts by category.
---

<div class="browse-toolbar" role="group" aria-label="Filter by category">
  <button class="browse-all-btn active" type="button" aria-pressed="true">
    All <span class="chip-count">{{ site.posts | size }}</span>
  </button>
  {% assign categories_sorted = site.categories | sort %}
  {% for category in categories_sorted %}
  <button class="browse-chip" type="button" data-filter="{{ category[0] | slugify }}" aria-pressed="false">
    {{ category[0] }} <span class="chip-count">{{ category[1].size }}</span>
  </button>
  {% endfor %}
</div>

<p class="browse-count"></p>

<ul class="post-list">
  {% for post in site.posts %}
    {% include post-card.html post=post %}
  {% endfor %}
</ul>

<p class="browse-empty">No posts in this category.</p>
