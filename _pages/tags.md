---
layout: page
title: Tags
permalink: /tags/
description: Browse all posts by tag.
---

<div class="browse-toolbar" role="group" aria-label="Filter by tag">
  <button class="browse-all-btn active" type="button" aria-pressed="true">
    All <span class="chip-count">{{ site.posts | size }}</span>
  </button>
  {% assign tags_sorted = site.tags | sort %}
  {% for tag in tags_sorted %}
  <button class="browse-chip" type="button" data-filter="{{ tag[0] | slugify }}" aria-pressed="false">
    {{ tag[0] }} <span class="chip-count">{{ tag[1].size }}</span>
  </button>
  {% endfor %}
</div>

<p class="browse-count"></p>

<ul class="post-list">
  {% for post in site.posts %}
    {% include post-card.html post=post %}
  {% endfor %}
</ul>

<p class="browse-empty">No posts with this tag.</p>
