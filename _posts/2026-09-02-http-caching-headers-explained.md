---
layout: post
title: "How HTTP Caching Headers Work: Cache-Control, ETag, and Vary"
date: "2026-09-02 00:00:00 +0530"
slug: http-caching-headers-explained
description: "A practical guide to HTTP caching headers, covering Cache-Control directives, ETag validation, the Vary header, and how browsers and CDNs actually use them."
categories: ["wiki", "Programming"]
tags: ["http caching", "cache-control", "etag", "vary", "http headers", "web performance", "browser", "cdn", "nginx", "backend"]
---

Every HTTP response carries a set of headers that answer a question most developers never think to ask explicitly: can this response be reused for a future request, and if so, for how long, and does it need to be revalidated first? Get these headers wrong and you either serve stale content indefinitely or force every request to hit your origin server when a cached copy would've been perfectly fine. This post covers how `Cache-Control`, `ETag`, and `Vary` actually work together, and the specific mistakes that quietly break caching in production.

## Two Kinds of Caching: Fresh vs Stale

HTTP caching splits into two distinct questions, and conflating them is the source of most confusion:

1. **Is this cached response still fresh, or has it expired?** — governed by `Cache-Control`'s time-based directives.
2. **If it's expired, has the content actually changed, or can I just extend its freshness?** — governed by validators like `ETag` and `Last-Modified`.

A response can be fresh (use it immediately, no network round trip at all) or stale-but-validatable (worth checking with the server, but a full re-download might not be necessary). Understanding which state a cached response is in determines what actually happens on the next request.

## Cache-Control: The Primary Directive

`Cache-Control` is a response header (and sometimes a request header) that controls caching behavior directly:

```bash
$ curl -sI https://example.com/static/app.js | grep -i cache-control
Cache-Control: public, max-age=31536000, immutable
```

The most common directives:

- **`public`** — this response can be cached by any cache along the way (browser, CDN, shared proxy), not just the requesting browser.
- **`private`** — only the end user's own browser cache may store this; intermediate shared caches (CDNs, corporate proxies) must not, since the response is specific to that user (commonly used for personalized or authenticated responses).
- **`max-age=N`** — the response is fresh for `N` seconds from when it was generated. During this window, a cache can serve it directly with zero network requests to the origin.
- **`no-cache`** — despite the name, this does **not** mean "don't cache." It means "cache it, but revalidate with the server before using it every time." This is a genuinely confusing name that trips up a lot of people.
- **`no-store`** — this actually means "don't cache at all." The response must be fetched fresh every single time. Used for sensitive data (banking transactions, auth tokens) that should never persist in any cache.
- **`immutable`** — tells the browser this response will never change for as long as it's fresh, skipping even the conditional revalidation request a browser sometimes makes on reload — a meaningful optimization for versioned static assets.

```bash
# Sensitive data — never cache
Cache-Control: no-store

# Cache, but always check with the server first
Cache-Control: no-cache

# Cache for one hour, private to this browser only
Cache-Control: private, max-age=3600

# Cache forever, this exact URL will never point to different content
Cache-Control: public, max-age=31536000, immutable
```

## The `no-cache` / `no-store` Confusion in Practice

This is worth calling out explicitly because it's one of the most common mistakes: a developer wanting "always fetch fresh data" often reaches for `no-cache`, when what they actually mean is `no-store`.

```
no-cache  -> cache it, but revalidate on every use (may still avoid a full re-download)
no-store  -> never cache it, period, full request every time
```

Using `no-cache` when you meant `no-store` isn't catastrophic (revalidation still hits the network on every request), but it does mean the response is sitting in a cache somewhere it maybe shouldn't be — worth getting right specifically for anything sensitive, where "sitting in a cache" is itself a problem regardless of whether it gets served without revalidation.

## Validators: ETag and Last-Modified

Once a cached response goes stale (its `max-age` window has passed), the cache doesn't necessarily need to re-download the full response — it can ask the server "has this actually changed?" via a conditional request, using a **validator** the server provided on the original response.

**ETag** is an opaque identifier (often a hash of the content) representing a specific version of a resource:

```bash
$ curl -sI https://example.com/api/products/42
HTTP/1.1 200 OK
Cache-Control: max-age=0, must-revalidate
ETag: "a1b2c3d4e5f6"
```

On the next request, the cache sends this ETag back in an `If-None-Match` header:

```bash
$ curl -sI -H 'If-None-Match: "a1b2c3d4e5f6"' https://example.com/api/products/42
HTTP/1.1 304 Not Modified
```

A `304 Not Modified` response has **no body at all** — it just confirms the cached copy is still valid, letting the cache reset its freshness timer without re-transferring any content. This is the mechanism that makes `no-cache` cheap in practice: revalidation is a small header-only round trip, not a full re-download, as long as the content genuinely hasn't changed.

`Last-Modified`/`If-Modified-Since` is an older, coarser validator using a timestamp instead of a content hash — it works the same way conceptually but has lower precision (a resource that changes twice within the same second, for instance, can't be distinguished by timestamp alone the way an ETag can).

## Vary: Caching the Same URL Differently by Request

A single URL can legitimately need multiple different cached responses — the classic case is a response that differs based on the client's `Accept-Encoding` (compressed vs uncompressed) or `Accept-Language`. The `Vary` header tells caches which request headers factor into deciding whether a cached response is actually reusable for a new request.

```bash
$ curl -sI https://example.com/api/data -H 'Accept-Encoding: gzip'
HTTP/1.1 200 OK
Content-Encoding: gzip
Vary: Accept-Encoding
Cache-Control: public, max-age=3600
```

This tells a cache: don't serve this gzip-encoded response to a client that didn't request `gzip` in its own `Accept-Encoding` — cache it as a **separate entry**, keyed by the combination of URL and the varying header's value, rather than one shared entry per URL.

```
Cache key without Vary:  GET /api/data
Cache key with Vary:     GET /api/data + Accept-Encoding: gzip
                         GET /api/data + Accept-Encoding: identity
```

**Getting `Vary` wrong is a genuinely common production bug.** Forgetting `Vary: Accept-Encoding` on a compressible response can cause a cache to serve a gzip-compressed response to a client that can't decompress it (or vice versa), resulting in garbled content for some fraction of users depending on which variant happened to get cached first. Overusing `Vary` on a header with many possible values (`Vary: User-Agent`, which has effectively unlimited distinct values across real clients) has the opposite problem — it fragments the cache into so many nearly-unique entries that the cache hit rate collapses toward zero, since almost no two requests share the exact same header value.

## How CDNs and Browsers Actually Combine These

A request in practice usually passes through multiple cache layers, each making its own freshness decision:

```mermaid
graph LR
    Browser[Browser Cache] --> CDN[CDN Edge Cache] --> Origin[Origin Server]
```

The browser cache checks its own copy's freshness first; if stale or absent, the request goes to the CDN edge, which checks its own cached copy (which might still be fresh even if the browser's copy expired, since CDN and browser cache durations don't have to match); only if the CDN also lacks a fresh copy does the request finally reach the origin server. This is why `Cache-Control: public` matters specifically — it's what allows the CDN layer to cache the response at all, versus `private`, which restricts caching to the end user's own browser and forces every CDN-layer request through to the origin.

```bash
$ curl -sI https://example.com/static/logo.png | grep -iE 'cache-control|age|x-cache'
Cache-Control: public, max-age=86400
Age: 3421
X-Cache: HIT
```

The `Age` header (how many seconds this response has been sitting in a cache since the origin generated it) and `X-Cache: HIT`/`MISS` (a common but non-standard convention many CDNs add) are useful debugging signals — `Age` close to `max-age` means the cached copy is about to expire, and a string of `MISS` responses for a URL that should be cacheable is usually the first clue that a caching header is misconfigured somewhere in the chain.

## Conclusion

HTTP caching headers answer two separable questions — how long is this fresh, and once it's stale, has it actually changed — and getting them right means picking the correct `Cache-Control` directive for the sensitivity and mutability of the content, pairing it with an `ETag` so revalidation is cheap rather than a full re-download, and using `Vary` precisely enough to serve the right variant without fragmenting the cache into uselessness. The mistakes that actually bite in production aren't exotic — they're `no-cache` used where `no-store` was meant, a missing `Vary: Accept-Encoding` serving garbled compressed content to the wrong client, and `Cache-Control: private` silently preventing a CDN from ever caching a response that was meant to be shared.
