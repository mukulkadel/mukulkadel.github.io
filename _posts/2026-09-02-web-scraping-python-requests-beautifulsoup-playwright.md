---
layout: post
title: "Web Scraping with Python: Requests, BeautifulSoup, and Playwright"
date: "2026-09-02 00:00:00 +0530"
slug: web-scraping-python-requests-beautifulsoup-playwright
description: "A practical tutorial on web scraping in Python, covering static HTML parsing with Requests and BeautifulSoup and JavaScript-rendered pages with Playwright."
categories: ["Programming", "Tutorials"]
tags: ["web scraping", "python", "beautifulsoup", "playwright", "requests", "automation", "html", "data extraction", "tutorial"]
---

Not every website has an API, and even when one exists, it doesn't always expose the data you actually need. Web scraping fills that gap, but "web scraping" covers two genuinely different problems depending on the site: static HTML you can parse directly, and JavaScript-rendered pages where the data doesn't exist in the HTML until a browser runs the page's scripts. This post covers both, and how to tell which one you're dealing with before you pick a tool.

## Step 1: Figure Out Which Kind of Site You're Scraping

Before writing any code, check whether the data you want is actually present in the raw HTML response, or only appears after JavaScript runs.

```bash
$ curl -s https://example.com/products | grep -o "product-price" | head -1
```

If that returns nothing but the price is visible in a browser, the content is being rendered client-side — you'll need a real browser engine (Playwright), not a plain HTTP request. If it does show up, `requests` plus `BeautifulSoup` is simpler, faster, and lighter.

## Static HTML: `requests` + `BeautifulSoup`

For pages where the data is present in the initial HTML response, `requests` fetches it and `BeautifulSoup` parses it.

```bash
$ pip install requests beautifulsoup4
```

```python
import requests
from bs4 import BeautifulSoup

response = requests.get("https://example.com/products")
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

for product in soup.select(".product-card"):
    name = product.select_one(".product-name").get_text(strip=True)
    price = product.select_one(".product-price").get_text(strip=True)
    print(f"{name}: {price}")
```

```
$ python scrape_products.py
Wireless Mouse: $24.99
Mechanical Keyboard: $89.99
USB-C Hub: $34.50
```

`select()` uses CSS selectors, which is usually the fastest way to target elements if you already know CSS — `.product-card` matches every element with that class, and `select_one()` grabs the first match within each card. `raise_for_status()` matters more than it looks: without it, a 404 or 500 response silently returns an empty or error-page body, and you'd parse garbage instead of getting a clear exception.

### Handling Pagination

Most real scraping targets span multiple pages, which means the scraper needs a loop, not a single request.

```python
import requests
from bs4 import BeautifulSoup
import time

all_products = []
page = 1

while True:
    response = requests.get(f"https://example.com/products?page={page}")
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select(".product-card")

    if not cards:
        break

    for card in cards:
        all_products.append(card.select_one(".product-name").get_text(strip=True))

    page += 1
    time.sleep(1)  # be a polite scraper

print(f"Collected {len(all_products)} products across {page - 1} pages")
```

```
$ python scrape_paginated.py
Collected 143 products across 8 pages
```

The `time.sleep(1)` between requests isn't decorative — hammering a site with requests as fast as your network allows is how scrapers get IP-banned, and it's inconsiderate to the site's infrastructure regardless. Checking `if not cards: break` is the natural termination condition — an empty page means you've gone past the last real page.

## JavaScript-Rendered Pages: Playwright

When data is injected into the page by JavaScript after load — a common pattern for single-page apps built with React, Vue, or similar — `requests` only ever sees the empty shell HTML, because it never executes any script. Playwright drives a real browser engine, so it sees the page exactly as a human visitor would, including anything rendered after the fact.

```bash
$ pip install playwright
$ playwright install chromium
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com/dashboard")

    # Wait for the JS-rendered content to actually appear
    page.wait_for_selector(".stat-card")

    cards = page.query_selector_all(".stat-card")
    for card in cards:
        label = card.query_selector(".stat-label").inner_text()
        value = card.query_selector(".stat-value").inner_text()
        print(f"{label}: {value}")

    browser.close()
```

```
$ python scrape_dashboard.py
Active Users: 12,483
Revenue Today: $8,204
Signups: 312
```

`wait_for_selector()` is the critical line — without it, Playwright might query the DOM before the JavaScript has finished fetching and rendering the data, and `query_selector_all` would just return nothing. This is the single most common bug in browser-based scraping: treating a rendered-in-JS page as if it were available the instant `goto()` returns, when it actually needs a moment (or an explicit wait condition) to finish populating.

### Waiting for Network Activity Instead of a Specific Selector

Sometimes you don't know the exact selector to wait for, but you know the data comes from an API call the page makes after load. Playwright lets you wait on network idle instead:

```python
page.goto("https://example.com/dashboard", wait_until="networkidle")
```

`networkidle` waits until there have been no new network requests for a short window, which is a reasonable proxy for "the page has finished loading its data" when you don't have a specific element to key off of.

## Respecting `robots.txt` and Rate Limits

Before scraping any site, check its `robots.txt` for disallowed paths, and read its terms of service — scraping is a gray area legally and ethically depending on what you're doing with the data, and many sites explicitly prohibit it for certain paths.

```bash
$ curl -s https://example.com/robots.txt
```

```
User-agent: *
Disallow: /admin/
Disallow: /api/internal/
Crawl-delay: 2
```

`Crawl-delay: 2` is a direct request from the site operator for at least 2 seconds between your requests — respecting it (via `time.sleep()`) is both good etiquette and reduces the odds of getting blocked outright.

## Choosing Between the Two Approaches

| | `requests` + `BeautifulSoup` | Playwright |
|---|---|---|
| Speed | Fast — no browser overhead | Slower — launches a real browser |
| Handles JavaScript | No | Yes |
| Resource usage | Low | Higher (memory, CPU) |
| Best for | Static sites, server-rendered HTML, APIs | SPAs, infinite scroll, login-gated content |

The practical rule: always try `requests` first, since it's an order of magnitude faster and lighter — only reach for Playwright once you've confirmed (via the `curl` check from step 1) that the data genuinely isn't present without JavaScript execution.

## Conclusion

Web scraping in Python splits cleanly into two problems with two different tools: `requests` + `BeautifulSoup` for content that's already in the raw HTML, and Playwright for content that only exists after JavaScript runs. Checking which situation you're in before writing code saves the overhead of reaching for a full browser engine when a simple HTTP request would have worked. Whichever tool you use, rate-limit your requests, respect `robots.txt`, and treat the target site's infrastructure the way you'd want your own scraped — politely and without unnecessary load.
