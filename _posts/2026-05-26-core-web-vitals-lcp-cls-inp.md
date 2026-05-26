---
layout: post
title: "Understanding Core Web Vitals: LCP, CLS, INP for Developers"
date: "2026-05-26 00:00:00 +0530"
slug: core-web-vitals-lcp-cls-inp
description: "A developer's guide to Core Web Vitals — what LCP, CLS, and INP measure, how to diagnose poor scores, and the code-level fixes that actually move the needle."
categories: ["wiki", "Programming"]
tags: ["core web vitals", "lcp", "cls", "inp", "web performance", "seo", "frontend", "google", "page speed", "lighthouse"]
---

Core Web Vitals are Google's way of measuring whether a page feels good to use — not whether it loads fast in a vacuum, but whether it loads fast in a way users experience. They directly influence search ranking and they correlate with real business metrics: bounce rate, conversion, retention. Understanding them at the code level means you can actually fix them instead of staring at a Lighthouse score hoping it improves.

## The Three Metrics

| Metric | Measures | Good | Needs Improvement | Poor |
|--------|----------|------|-------------------|------|
| **LCP** | Loading performance | ≤ 2.5s | 2.5s – 4.0s | > 4.0s |
| **CLS** | Visual stability | ≤ 0.1 | 0.1 – 0.25 | > 0.25 |
| **INP** | Interactivity | ≤ 200ms | 200ms – 500ms | > 500ms |

These are measured at the 75th percentile of real user sessions — meaning 75% of your users should get a "Good" experience.

## Largest Contentful Paint (LCP)

LCP measures when the largest visible element in the viewport finishes rendering. That element is usually a hero image, a large heading, or a video poster.

### What hurts LCP

1. **Slow server response (TTFB)** — if the HTML arrives late, everything else is delayed
2. **Render-blocking resources** — CSS and synchronous `<script>` tags block the browser from rendering
3. **Unoptimized images** — large uncompressed images, missing `width`/`height`, no lazy loading coordination
4. **No preloading of the LCP resource** — browser discovers hero image too late

### Fixing LCP

**Preload the LCP image:**

```html
<!-- Tell the browser about this image before it parses the HTML that contains it -->
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">
```

**Use modern image formats and explicit dimensions:**

```html
<!-- Never omit width and height — they prevent layout shifts too -->
<img
    src="/hero.webp"
    width="1200"
    height="630"
    fetchpriority="high"
    loading="eager"
    decoding="async"
    alt="Hero image"
>
```

**Defer non-critical JavaScript:**

```html
<!-- Synchronous — blocks rendering -->
<script src="/analytics.js"></script>

<!-- Async — doesn't block, executes when ready -->
<script src="/analytics.js" async></script>

<!-- Defer — doesn't block, executes after HTML is parsed -->
<script src="/app.js" defer></script>
```

**Inline critical CSS, defer the rest:**

```html
<head>
    <!-- Inline only the CSS needed for above-the-fold content -->
    <style>
        .hero { background: #000; color: #fff; padding: 64px 0; }
    </style>

    <!-- Load the rest without blocking -->
    <link rel="preload" href="/main.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
</head>
```

**Check TTFB with a server-timing header:**

```bash
$ curl -I https://yoursite.com | grep server-timing
server-timing: db;dur=12, render;dur=4, total;dur=38
```

If TTFB is > 600ms, your backend or hosting is the bottleneck, not the frontend.

## Cumulative Layout Shift (CLS)

CLS measures how much visible content shifts unexpectedly during the page lifecycle. A banner loading in and pushing the article down, a font swap that moves text, an ad that appears and shifts content below it — all of these contribute to CLS.

The score is calculated as: **impact fraction × distance fraction**, summed over all unexpected shifts. An element that covers 50% of the viewport shifting by 25% of viewport height contributes 0.125.

### What causes layout shifts

1. **Images without explicit dimensions** — browser doesn't know height until image loads
2. **Late-loading fonts (FOUT/FOIT)** — font swap shifts text
3. **Dynamically injected content** — ads, cookie banners, modals that push content
4. **Animations that change layout properties** — `height`, `width`, `top`, `left`

### Fixing CLS

**Always set image dimensions:**

```html
<!-- Browser reserves the right amount of space before the image loads -->
<img src="/photo.jpg" width="800" height="400" alt="...">

<!-- For responsive images, use aspect-ratio in CSS -->
```

```css
.hero-image {
    width: 100%;
    aspect-ratio: 16 / 9;  /* reserves space before image loads */
}
```

**Preload fonts and use `font-display: optional`:**

```html
<link rel="preload" href="/fonts/Inter-Regular.woff2" as="font" type="font/woff2" crossorigin>
```

```css
@font-face {
    font-family: 'Inter';
    src: url('/fonts/Inter-Regular.woff2') format('woff2');
    font-display: optional;  /* if font isn't ready on first render, use fallback */
}
```

**Reserve space for ads and dynamic content:**

```css
/* Reserve space for ad slot — even if ad hasn't loaded yet */
.ad-slot {
    min-height: 250px;
    width: 300px;
}
```

**Use CSS transforms for animations, not layout properties:**

```css
/* Causes layout shift — forces browser to recalculate layout */
.slide-in { animation: slideIn 0.3s; }
@keyframes slideIn { from { top: -50px; } to { top: 0; } }

/* No layout shift — transform doesn't affect layout */
.slide-in { animation: slideIn 0.3s; }
@keyframes slideIn { from { transform: translateY(-50px); } to { transform: translateY(0); } }
```

## Interaction to Next Paint (INP)

INP replaced FID (First Input Delay) in March 2024. It measures the latency of all user interactions — clicks, taps, keyboard input — and reports the worst one (at the 98th percentile). An interaction is "done" when the browser has painted the visual response.

INP > 200ms means the page feels sluggish. Common culprits:

1. **Long JavaScript tasks blocking the main thread** — the browser can't paint until JS yields
2. **Heavy event handlers** — an `onClick` that does too much work synchronously
3. **Forced synchronous layout (layout thrashing)** — reading then writing DOM properties in a loop

### Fixing INP

**Break up long tasks with `setTimeout` or `scheduler.yield()`:**

```javascript
// Long task — blocks the main thread for 300ms
function processAllItems(items) {
    items.forEach(item => expensiveOperation(item));
}

// Chunked — yields to browser between batches
async function processAllItemsAsync(items) {
    const CHUNK_SIZE = 50;

    for (let i = 0; i < items.length; i += CHUNK_SIZE) {
        const chunk = items.slice(i, i + CHUNK_SIZE);
        chunk.forEach(item => expensiveOperation(item));

        // Yield to let the browser paint and handle input
        await new Promise(resolve => setTimeout(resolve, 0));
    }
}
```

**Move heavy work off the main thread with Web Workers:**

```javascript
// main.js
const worker = new Worker('/worker.js');

button.addEventListener('click', () => {
    worker.postMessage({ data: largeDataset });
    worker.onmessage = (e) => renderResult(e.data);
});
```

```javascript
// worker.js
self.onmessage = (e) => {
    const result = heavyComputation(e.data.data);
    self.postMessage(result);
};
```

**Avoid layout thrashing:**

```javascript
// Bad — read/write/read/write causes multiple layout recalculations
elements.forEach(el => {
    const height = el.offsetHeight;    // forces layout
    el.style.height = height + 10 + 'px';  // invalidates layout
});

// Good — batch reads, then batch writes
const heights = elements.map(el => el.offsetHeight);  // one layout
elements.forEach((el, i) => el.style.height = heights[i] + 10 + 'px');  // writes
```

## Measuring Core Web Vitals

**Lighthouse (lab data):** Run in Chrome DevTools (Lighthouse tab) or via CLI:

```bash
$ npx lighthouse https://yoursite.com --output=html --view
```

**Web Vitals JS library (real user data):**

```javascript
import { getLCP, getCLS, getINP } from 'web-vitals';

getLCP(({ value, rating }) => {
    console.log(`LCP: ${value}ms — ${rating}`);
    sendToAnalytics('lcp', value);
});

getCLS(({ value, rating }) => sendToAnalytics('cls', value));
getINP(({ value, rating }) => sendToAnalytics('inp', value));
```

**Chrome DevTools Performance panel:** record a trace, look for long tasks (red triangles), layout recalculations, and paint events.

**Google Search Console → Core Web Vitals report:** shows your real-user field data by page group, with pass/fail status.

## Conclusion

LCP is mostly a resource loading problem — preload the hero image, cut render-blocking resources, and improve TTFB. CLS is mostly a "reserve space for dynamic content" problem — always set image dimensions and avoid injecting content that shifts existing elements. INP is a main thread contention problem — break up long tasks, offload to Web Workers, and avoid forced synchronous layouts. All three are measurable with real-user data via the `web-vitals` library, which is how you know when a fix actually worked.
