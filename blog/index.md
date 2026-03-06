---
layout: default
title: Blog
permalink: /blog/
---

# Blog

Welcome to my blog where I write about technology, development, and various other topics.

<ul class="post-list">
{% for post in site.posts %}
  <li class="post-list-item">
    <h3 class="post-list-title">
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </h3>
    <div class="post-list-meta">
      <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
      {% if post.author %}
      <span class="post-author">by {{ post.author }}</span>
      {% endif %}
    </div>
    <p class="post-list-excerpt">{{ post.excerpt | strip_html }}</p>
    {% if post.categories %}
    <div class="post-categories">
      {% for category in post.categories %}
      <a href="{{ '/categories/#' | append: category | relative_url }}" class="category-tag">{{ category }}</a>
      {% endfor %}
    </div>
    {% endif %}
  </li>
{% endfor %}
</ul>
