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
  <a class="app-card" href="{{ '/apps/password-generator/' | relative_url }}">
    <div class="app-card-icon">🔑</div>
    <h2 class="app-card-title">Password Generator</h2>
    <p class="app-card-desc">Generate strong random passwords or passphrases with a live strength meter.</p>
  </a>
  <a class="app-card" href="{{ '/apps/hash-generator/' | relative_url }}">
    <div class="app-card-icon">🔒</div>
    <h2 class="app-card-title">Hash Generator</h2>
    <p class="app-card-desc">Generate SHA-1, SHA-256, SHA-384, and SHA-512 hashes of any text.</p>
  </a>
  <a class="app-card" href="{{ '/apps/timestamp-converter/' | relative_url }}">
    <div class="app-card-icon">🕓</div>
    <h2 class="app-card-title">Unix Timestamp Converter</h2>
    <p class="app-card-desc">Convert Unix timestamps to human-readable dates and back.</p>
  </a>
  <a class="app-card" href="{{ '/apps/url-encoder-decoder/' | relative_url }}">
    <div class="app-card-icon">🔗</div>
    <h2 class="app-card-title">URL Encoder / Decoder</h2>
    <p class="app-card-desc">Encode or decode URL components instantly in your browser.</p>
  </a>
  <a class="app-card" href="{{ '/apps/case-converter/' | relative_url }}">
    <div class="app-card-icon">🔤</div>
    <h2 class="app-card-title">Case Converter</h2>
    <p class="app-card-desc">Convert text between camelCase, snake_case, kebab-case, and more.</p>
  </a>
  <a class="app-card" href="{{ '/apps/color-converter/' | relative_url }}">
    <div class="app-card-icon">🎨</div>
    <h2 class="app-card-title">Color Converter</h2>
    <p class="app-card-desc">Convert colors between HEX, RGB, and HSL with a live picker.</p>
  </a>
  <a class="app-card" href="{{ '/apps/word-counter/' | relative_url }}">
    <div class="app-card-icon">📝</div>
    <h2 class="app-card-title">Word &amp; Character Counter</h2>
    <p class="app-card-desc">Count words, characters, sentences, and estimate reading time.</p>
  </a>
  <a class="app-card" href="{{ '/apps/text-cleaner/' | relative_url }}">
    <div class="app-card-icon">🧹</div>
    <h2 class="app-card-title">Text Cleaner</h2>
    <p class="app-card-desc">Trim whitespace and collapse blank lines in messy pasted text.</p>
  </a>
  <a class="app-card" href="{{ '/apps/lorem-ipsum-generator/' | relative_url }}">
    <div class="app-card-icon">📄</div>
    <h2 class="app-card-title">Lorem Ipsum &amp; Dummy Data</h2>
    <p class="app-card-desc">Generate placeholder text or fake names, emails, and UUIDs.</p>
  </a>
  <a class="app-card" href="{{ '/apps/json-formatter/' | relative_url }}">
    <div class="app-card-icon">🗂️</div>
    <h2 class="app-card-title">JSON Formatter &amp; Validator</h2>
    <p class="app-card-desc">Format, validate, minify, and explore JSON in a collapsible tree.</p>
  </a>
  <a class="app-card" href="{{ '/apps/json-yaml-csv-converter/' | relative_url }}">
    <div class="app-card-icon">🔁</div>
    <h2 class="app-card-title">JSON, YAML &amp; CSV Converter</h2>
    <p class="app-card-desc">Convert data between JSON, YAML, and CSV formats.</p>
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
