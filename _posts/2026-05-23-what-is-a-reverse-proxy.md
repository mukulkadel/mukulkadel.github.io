---
layout: post
title: "What is a Reverse Proxy? (And When to Use One)"
date: "2026-05-23 00:00:00 +0530"
slug: what-is-a-reverse-proxy
description: "Learn what a reverse proxy is, how it differs from a forward proxy, and how to configure one with Nginx — covering SSL termination, load balancing, and header forwarding."
categories: ["wiki"]
tags: ["reverse proxy", "nginx", "haproxy", "networking", "web server", "load balancing", "devops", "proxy", "architecture", "ssl termination"]
---

A reverse proxy sits in front of your servers and intercepts incoming requests before they reach your application. It's one of the most common patterns in production infrastructure, and once you understand it, a lot of modern web architecture — CDNs, API gateways, load balancers — suddenly makes sense. The "reverse" in the name distinguishes it from a forward proxy, and that distinction tells you most of what you need to know.

## Forward Proxy vs Reverse Proxy

A **forward proxy** acts on behalf of clients. The client knows it's using a proxy; the server doesn't. Corporate networks use forward proxies to filter outbound traffic. VPNs work similarly.

A **reverse proxy** acts on behalf of servers. The client doesn't know about the backend servers; it only sees the proxy. The server doesn't know the real client IP unless the proxy passes it along in a header.

```
Forward proxy:
Client → [Proxy] → Internet

Reverse proxy:
Internet → [Proxy] → Server(s)
```

## What a Reverse Proxy Does

A reverse proxy can do any or all of the following:

- **SSL termination** — Handle TLS encryption/decryption so your backend servers receive plain HTTP. Centralizes certificate management.
- **Load balancing** — Distribute requests across multiple backend servers.
- **Caching** — Store responses and serve them without hitting the backend.
- **Compression** — Gzip or Brotli compress responses before sending to clients.
- **Authentication** — Enforce auth at the proxy layer before requests reach your app.
- **Rate limiting** — Throttle clients who make too many requests.
- **Request routing** — Route to different backends based on path, hostname, or headers.
- **Static file serving** — Serve `/assets/` directly from disk without hitting the app server.

## Reverse Proxy with Nginx

Nginx is the most common reverse proxy for web applications. The core directive is `proxy_pass`:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

All requests to `example.com` are forwarded to the Node.js (or Python, Go, etc.) app running on port 3000. The app only ever sees connections from localhost.

### Passing the Real Client IP

By default, your application sees the proxy's IP, not the client's. Fix this with the `X-Forwarded-For` header:

```nginx
location / {
    proxy_pass http://localhost:3000;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Your application reads the real IP from `X-Real-IP` or `X-Forwarded-For`. The `X-Forwarded-Proto` header tells your app whether the client used HTTP or HTTPS (important for generating correct redirect URLs).

### SSL Termination

The proxy handles TLS; the backend gets plain HTTP:

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Routing to Multiple Backends

Route different paths to different services:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    # API service
    location /api/ {
        proxy_pass http://localhost:4000/;
    }

    # Static files served directly
    location /assets/ {
        root /var/www/example.com;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend app
    location / {
        proxy_pass http://localhost:3000;
    }
}
```

Note the trailing slash on `proxy_pass http://localhost:4000/;` — this strips the `/api/` prefix before forwarding. Without the trailing slash, the `/api/` prefix is included in the upstream request.

### Load Balancing

Define an upstream group to load balance across multiple servers:

```nginx
upstream app_servers {
    server 10.0.0.1:3000;
    server 10.0.0.2:3000;
    server 10.0.0.3:3000;
}

server {
    listen 443 ssl;
    server_name example.com;

    location / {
        proxy_pass http://app_servers;
    }
}
```

Nginx uses round-robin by default. You can add `least_conn;` inside the `upstream` block for connection-based distribution.

### WebSocket Support

WebSockets require extra headers for the protocol upgrade:

```nginx
location /ws/ {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade    $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## When to Use a Reverse Proxy

**Always**, if you're running a production application. The benefits are substantial:

- Your app servers are never directly exposed to the internet.
- SSL can be configured once at the proxy layer instead of in every app.
- Horizontal scaling becomes simple — add servers to the upstream pool.
- You get request logging, rate limiting, and caching without touching application code.

The only case where you might skip it is a simple static site served directly from S3 or similar object storage — those are already behind their own infrastructure.

## Conclusion

A reverse proxy is one of the most important architectural decisions you make, and choosing one (almost always Nginx or HAProxy) is simpler than it sounds. Start with a basic `proxy_pass` configuration, add SSL termination, and always set `X-Forwarded-For` and `X-Forwarded-Proto` so your application has access to the real client context. As your traffic grows, adding load balancing is a two-line change to the upstream block — not a re-architecture.
