---
layout: default
title: Blog
permalink: /blog/
---

# Blog

All articles organized by date. Most recent first.

{% assign posts = site.posts | where_exp: "item", "item.path contains '_posts'" | sort: "date" | reverse %}
<ul class="post-list">
{% for post in posts %}
  <li class="post-list-item">
    <h3 class="post-list-title">
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </h3>
    <div class="post-list-meta">
      <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
    </div>
    {% if post.excerpt %}
    <p class="post-list-excerpt">{{ post.excerpt | strip_html | truncate: 150 }}</p>
    {% endif %}
  </li>
{% endfor %}
</ul>
