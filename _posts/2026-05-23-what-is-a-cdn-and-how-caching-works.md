---
layout: post
title: "What is a CDN and How Does Caching Work?"
date: "2026-05-23 00:00:00 +0530"
slug: what-is-a-cdn-and-how-caching-works
description: "Understand how CDNs cache and serve content at the edge, how Cache-Control headers drive caching behavior, and how to use curl to inspect what your CDN is actually doing."
categories: ["wiki"]
tags: ["cdn", "caching", "web performance", "cloudflare", "networking", "edge", "static assets", "devops", "latency", "cache-control", "http headers"]
---

A CDN isn't magic — it's a network of geographically distributed servers that cache your content close to your users. When a user in Mumbai requests your site hosted in Virginia, the response travels 14,000 km each way. Put a CDN edge node in Singapore, and that same request travels 400 km. Understanding how CDNs actually cache and invalidate content lets you use them far more effectively than just "put Cloudflare in front of it and call it done."

## What a CDN Actually Does

A CDN provider (Cloudflare, AWS CloudFront, Fastly, Akamai) operates hundreds of **Points of Presence (PoPs)** around the world — data centers with servers that sit between your users and your origin server.

```
User (Mumbai)
     ↓
CDN Edge Node (Singapore) ← cache hit? serve from here
     ↓ (cache miss only)
Origin Server (Virginia)
```

On a cache hit, the response comes from the edge node. On a cache miss, the edge fetches from origin, caches the response, and then delivers it. Future requests for the same resource from nearby users get the cached copy.

## How Caching Works: Cache-Control Headers

The CDN respects `Cache-Control` headers from your origin to decide what to cache and for how long.

```bash
$ curl -sI https://example.com/style.css | grep -i cache
Cache-Control: public, max-age=31536000, immutable
```

Key directives:

| Directive | Meaning |
|---|---|
| `public` | Response can be cached by the CDN (and browser) |
| `private` | Only the browser can cache it, not CDN |
| `no-cache` | Revalidate with the origin before serving cached copy |
| `no-store` | Never cache this response anywhere |
| `max-age=N` | Cache for N seconds |
| `s-maxage=N` | CDN-specific max-age (overrides `max-age` for CDNs) |
| `immutable` | Browser hint: this file never changes (don't revalidate) |
| `must-revalidate` | Must go back to origin once expired |

### Static Assets

CSS, JS, images, and fonts that have content hashes in their filenames can be cached forever:

```
/assets/app.a3f8c2d.js → Cache-Control: public, max-age=31536000, immutable
```

When the file changes, the filename changes. Old URLs serve old content from cache; new URLs fetch fresh content. This is **cache-busting by filename**.

### Dynamic Responses

API responses, HTML pages, and anything user-specific should generally not be CDN-cached:

```
Cache-Control: private, no-cache
```

Or for HTML that changes but is the same for all anonymous users:

```
Cache-Control: public, s-maxage=300, max-age=0
```

This tells the CDN to cache for 5 minutes but tells the browser not to cache locally.

## CDN vs Browser Cache

Two separate caches are involved:

```
Request flow:
Browser cache → CDN edge cache → Origin

Response flow (with headers):
Cache-Control: public, s-maxage=3600, max-age=300
                        ↑                 ↑
                   CDN caches 1hr     Browser caches 5min
```

`s-maxage` is for shared caches (CDNs, proxies). `max-age` is for the browser. You can set them independently.

## ETags and Conditional Requests

ETags provide a fingerprint for a response. Even when a cached response is "stale," the browser or CDN can validate it with the origin:

```bash
# First request — origin returns ETag
$ curl -sI https://example.com/data.json
ETag: "a3f8c2d45..."
Cache-Control: public, max-age=60

# 60 seconds later — revalidation request
$ curl -sI https://example.com/data.json -H 'If-None-Match: "a3f8c2d45..."'
HTTP/2 304 Not Modified   # Content unchanged, no body sent
```

A `304 Not Modified` response is tiny — no body, just headers. This saves bandwidth while still verifying freshness.

## Cache Invalidation

The hardest problem in CDN caching is invalidating content you didn't know you needed to invalidate.

**Cloudflare** — Purge by URL or prefix via API:

```bash
$ curl -X POST "https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/purge_cache" \
    -H "Authorization: Bearer {API_TOKEN}" \
    -H "Content-Type: application/json" \
    --data '{"files":["https://example.com/page.html"]}'
```

**AWS CloudFront** — Create an invalidation:

```bash
$ aws cloudfront create-invalidation \
    --distribution-id EDFDVBD6EXAMPLE \
    --paths "/page.html" "/assets/*"
```

**The golden rule**: don't rely on invalidation for your static assets. Use content-hashed filenames instead — they never need to be invalidated because changed content always has a new URL.

## What to Cache (and What Not To)

| Content type | Cache? | Typical max-age |
|---|---|---|
| Hashed CSS/JS bundles | Yes | 1 year |
| Images (with hash) | Yes | 1 year |
| Fonts | Yes | 1 year |
| HTML pages | Sometimes | 0–5 minutes |
| API responses (public) | Sometimes | 30–300 seconds |
| API responses (user-specific) | No | `private, no-cache` |
| Auth endpoints | No | `private, no-store` |

## Checking Cache Behavior with curl

```bash
# Check what CDN is serving and whether it's a cache hit
$ curl -sI https://example.com/style.css
HTTP/2 200
cf-cache-status: HIT        # Cloudflare — served from cache
age: 3421                   # seconds since it was cached
cache-control: public, max-age=31536000

# CloudFront headers
$ curl -sI https://example.com/image.png
x-cache: Hit from cloudfront
x-amz-cf-pop: SIN52-P2      # Singapore PoP
```

Common CDN cache status values:

| Status | Meaning |
|---|---|
| `HIT` | Served from edge cache |
| `MISS` | Fetched from origin, now cached |
| `BYPASS` | Not cached (origin sent `no-store` or similar) |
| `EXPIRED` | Was cached, now stale — revalidating |
| `DYNAMIC` | Explicitly excluded from caching |

## Conclusion

A CDN's value comes entirely from its caching behavior, and that behavior is controlled by the `Cache-Control` headers your origin sends. Static assets with content hashes should be cached aggressively with `max-age=31536000, immutable` — no invalidation needed. Dynamic content and HTML pages need shorter TTLs and possibly `s-maxage` to separate CDN and browser caching. Use `curl -sI` to verify what your CDN is actually doing rather than what you think you configured.
