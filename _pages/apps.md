---
layout: page
title: Apps & Tools
permalink: /apps/
description: Web tools and mini-apps I've built.
---

<div class="apps-grid">
  <a class="app-card" href="{{ '/apps/image-to-base64/' | relative_url }}">
    <div class="app-card-icon">🖼️</div>
    <h2 class="app-card-title">Image to Base64</h2>
    <p class="app-card-desc">Convert images to Base64 encoded strings instantly in your browser. No uploads, fully private.</p>
  </a>
  <a class="app-card" href="{{ '/apps/base64-to-image/' | relative_url }}">
    <div class="app-card-icon">🔄</div>
    <h2 class="app-card-title">Base64 to Image</h2>
    <p class="app-card-desc">Convert Base64 encoded strings back into viewable, downloadable images. No uploads, fully private.</p>
  </a>
  <a class="app-card" href="{{ '/apps/timer/' | relative_url }}">
    <div class="app-card-icon">⏱️</div>
    <h2 class="app-card-title">Timer &amp; Stopwatch</h2>
    <p class="app-card-desc">A simple countdown timer and stopwatch. Link directly to a preset, e.g. #5minutes.</p>
  </a>
  <a class="app-card" href="{{ '/apps/uuid-generator/' | relative_url }}">
    <div class="app-card-icon">🆔</div>
    <h2 class="app-card-title">UUID Generator</h2>
    <p class="app-card-desc">Generate one or many random UUID v4 values instantly in your browser.</p>
  </a>
</div>

<hr style="margin:3rem 0;">

<h2>Adding a React App</h2>

<p>To serve a React app from this site:</p>

<ol>
<li>Build your React app with <code>npm run build</code> (Create React App / Vite)</li>
<li>Copy the build output into <code>apps/your-app-name/</code></li>
<li>Add a card in <code>_pages/apps.md</code> linking to <code>/apps/your-app-name/</code></li>
<li>Commit and push — GitHub Actions will deploy it automatically</li>
</ol>

The built React app is served as static files, so it works perfectly with GitHub Pages.
