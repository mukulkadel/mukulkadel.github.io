---
layout: post
title: "Understanding HTTP/2 and HTTP/3: What Changed and Why"
date: "2026-05-23 00:00:00 +0530"
slug: http2-http3-explained
description: "A clear explanation of how HTTP/2 and HTTP/3 improve on HTTP/1.1 through multiplexing, header compression, QUIC, and 0-RTT connection setup."
categories: ["wiki"]
tags: ["http2", "http3", "networking", "web performance", "quic", "protocol", "web development", "browser", "tls", "multiplexing"]
---

HTTP has been the backbone of the web since 1991, but the version that carried most internet traffic for decades — HTTP/1.1 — was designed in 1997 and shows it. HTTP/2 and HTTP/3 are radical redesigns that tackle performance bottlenecks baked into that original spec. If you're optimizing a web application, you need to understand what each version actually changed and why it matters.

## What's Wrong with HTTP/1.1

HTTP/1.1 has three fundamental problems at scale:

**Head-of-line blocking** — Each request must wait for the previous response to finish before the next request can be sent on the same connection. Browsers work around this by opening 6–8 parallel connections per domain, but this has its own overhead.

**Uncompressed headers** — Every HTTP/1.1 request sends the same headers repeatedly (User-Agent, Accept-Encoding, Cookie, etc.), often adding hundreds of bytes to each request.

**No prioritization** — The protocol has no concept of "this resource is more important than that one." A 10 MB image blocks a 1 KB CSS file.

## HTTP/2: Three Core Improvements

HTTP/2 (ratified in 2015) keeps the same semantics — methods, status codes, headers — but completely redesigns the wire format.

### Multiplexing

HTTP/2 introduces *streams*. Multiple requests and responses can be in flight simultaneously over a single TCP connection, interleaved at the frame level:

```
Connection (single TCP)
├── Stream 1: GET /index.html → 200 OK (HTML)
├── Stream 3: GET /style.css  → 200 OK (CSS)
├── Stream 5: GET /app.js     → 200 OK (JS)
└── Stream 7: GET /logo.png   → 200 OK (image)
```

All four happen in parallel over one connection. No more per-domain connection limits.

### HPACK Header Compression

HTTP/2 compresses headers using HPACK, a dictionary-based compression scheme. The first request sends full headers; subsequent requests only send what changed. Headers that appear on every request (like `User-Agent`) are sent once and then referenced by index.

Typical header reduction: **80–90%** smaller header overhead after the first request.

### Stream Prioritization

Clients can tell the server which streams matter most. A browser can prioritize the render-blocking CSS file over the analytics image. Servers aren't required to honor priorities, but most do.

### Enabling HTTP/2 in Nginx

HTTP/2 requires TLS (all major browsers enforce this). In Nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/ssl/certs/example.pem;
    ssl_certificate_key /etc/ssl/private/example.key;

    location / {
        proxy_pass http://backend;
    }
}
```

That's it — just add `http2` to the `listen` directive.

### HTTP/2's Remaining Weakness

HTTP/2 multiplexes at the application layer, but it still sits on top of TCP. TCP is stream-oriented — it guarantees ordered delivery. If one packet is lost, TCP holds all subsequent packets in the buffer until the lost one is retransmitted. A single packet loss blocks all HTTP/2 streams simultaneously. This is called **TCP head-of-line blocking**, and HTTP/2 doesn't solve it.

## HTTP/3: QUIC Changes Everything

HTTP/3 (standardized in 2022) replaces TCP with **QUIC**, a UDP-based transport protocol originally developed by Google.

### Why UDP?

UDP is connectionless and has no ordering guarantees — which sounds bad. But QUIC builds its own reliability, ordering, and congestion control on top of UDP, stream by stream. A lost UDP packet only blocks the stream it belongs to, not every other stream.

```
HTTP/1.1: 1 request per connection (or 6+ connections)
HTTP/2:   N requests per TCP connection (TCP HoL blocking)
HTTP/3:   N requests per QUIC connection (no HoL blocking)
```

### 0-RTT Connection Setup

TLS 1.3 (used by HTTP/2) requires 1 round trip to establish a new connection. QUIC with HTTP/3 supports **0-RTT resumption** — if the client has previously connected to the server, it can send data immediately on the first packet, skipping the handshake entirely.

```
HTTP/1.1 + TLS 1.2:  3 round trips before first byte of data
HTTP/2 + TLS 1.3:    1 round trip (1-RTT)
HTTP/3 + QUIC:       0 round trips on reconnection (0-RTT)
```

### Connection Migration

QUIC connections are identified by a connection ID, not by IP and port. When a mobile user switches from Wi-Fi to cellular, the IP address changes — killing a TCP connection. QUIC survives this transparently. The connection migrates without dropping.

### Checking Which Protocol Your Site Uses

```bash
# Check HTTP version with curl
$ curl -sI --http2 https://example.com | grep -i "HTTP/"
HTTP/2 200

$ curl -sI --http3 https://example.com | grep -i "HTTP/"
HTTP/3 200

# Check with a browser: DevTools → Network → Protocol column
# h2 = HTTP/2, h3 = HTTP/3
```

Or use the `nghttp` tool:

```bash
$ nghttp -v https://example.com 2>&1 | grep "The negotiated protocol"
The negotiated protocol: h2
```

### Enabling HTTP/3 in Nginx

Nginx supports HTTP/3 from version 1.25.0+ (experimental, via the `http3` directive):

```nginx
server {
    listen 443 ssl;
    listen 443 quic reuseport;  # QUIC for HTTP/3
    http2 on;

    ssl_certificate     /etc/ssl/certs/example.pem;
    ssl_certificate_key /etc/ssl/private/example.key;

    # Tell browsers HTTP/3 is available
    add_header Alt-Svc 'h3=":443"; ma=86400';
}
```

Cloudflare, Fastly, and most modern CDNs already serve HTTP/3 automatically.

## Protocol Comparison

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Transport | TCP | TCP | QUIC (UDP) |
| Multiplexing | No | Yes | Yes |
| Head-of-line blocking | Yes (app) | Yes (TCP) | No |
| Header compression | No | HPACK | QPACK |
| 0-RTT | No | No | Yes |
| Connection migration | No | No | Yes |
| TLS required | No | In practice yes | Yes (built in) |
| Browser adoption | 100% | ~98% | ~85% |

## Conclusion

HTTP/2 was a major improvement over HTTP/1.1 for most web workloads — multiplexing alone eliminates the need for most HTTP performance hacks like domain sharding and CSS sprites. HTTP/3 takes it further by fixing the TCP head-of-line problem that HTTP/2 couldn't address, and its connection migration support makes a real difference on mobile networks. For most teams, the right move is to ensure HTTP/2 is enabled today (it likely is if you're behind a CDN or modern Nginx) and to let HTTP/3 roll out via CDN rather than configuring it yourself.
