---
layout: default
title: Home
---

# Mukul Kadel

Welcome to my personal blog and technical portfolio. Here you'll find articles about software development, technology, and my thoughts on various topics.

## Latest Articles

{% assign posts = site.posts | where_exp: "item", "item.path contains '_posts'" | sort: "date" | reverse %}
<ul class="post-list">
{% for post in posts | limit: 10 %}
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

[View all articles →](/blog/)

---

**Tech Stack:** Jekyll • GitHub Pages • Markdown  
**Social:** [GitHub](https://github.com/mukulkadel) • [Twitter](https://twitter.com/mukul_kadel) • [LinkedIn](https://linkedin.com/in/mukulkadel)
