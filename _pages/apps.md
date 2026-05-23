---
layout: page
title: Apps & Tools
permalink: /apps/
description: Web tools and mini-apps I've built.
---

<div class="apps-grid">
  <a class="app-card" href="{{ '/tools/image-to-base64/' | relative_url }}">
    <div class="app-card-icon">🖼️</div>
    <h2 class="app-card-title">Image to Base64</h2>
    <p class="app-card-desc">Convert images to Base64 encoded strings instantly in your browser. No uploads, fully private.</p>
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
