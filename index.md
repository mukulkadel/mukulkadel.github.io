---
layout: default
title: Home
---

# Welcome to My Portfolio

Hello! I'm Mukul Kadel, a passionate developer and creator. This is my personal space where I share my thoughts, projects, and experiences.

## Featured Blog Posts

{% assign featured_posts = site.posts | first: 3 %}
<ul class="post-list">
{% for post in featured_posts %}
  <li class="post-list-item">
    <h3 class="post-list-title">
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </h3>
    <div class="post-list-meta">
      <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
    </div>
    <p class="post-list-excerpt">{{ post.excerpt | strip_html }}</p>
  </li>
{% endfor %}
</ul>

[View all blog posts →](/blog/)

## About Me

I'm a software developer with a passion for creating elegant solutions to complex problems. Welcome to my corner of the internet!

---

**Latest Updates:** Check back soon for migrated content from my WordPress site!
