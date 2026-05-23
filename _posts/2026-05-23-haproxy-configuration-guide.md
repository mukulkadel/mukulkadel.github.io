---
layout: post
title: "HAProxy Configuration Guide with Cheat Sheet"
date: "2026-05-23 00:00:00 +0530"
slug: haproxy-configuration-guide
description: "A practical HAProxy configuration guide covering global settings, frontends, backends, load balancing algorithms, health checks, ACLs, and SSL termination."
categories: ["wiki", "Programming"]
tags: ["haproxy", "load balancing", "reverse proxy", "devops", "networking", "linux", "configuration", "cheatsheet", "high availability", "ssl"]
---

HAProxy is the workhorse of modern web infrastructure — a fast, reliable load balancer and proxy that powers millions of production deployments. Unlike Nginx or Traefik, HAProxy is purpose-built for load balancing, giving it surgical control over how traffic flows across your backend pool. If you're running more than one application server, HAProxy is almost certainly the right tool for the job.

## Installing HAProxy

```bash
# Ubuntu / Debian
$ sudo apt update && sudo apt install haproxy

# RHEL / CentOS / Amazon Linux
$ sudo yum install haproxy

# Verify the version
$ haproxy -v
HAProxy version 2.8.3 2023/08/11
```

The main config file lives at `/etc/haproxy/haproxy.cfg`.

## Config Structure

Every HAProxy config is made up of four sections:

```
global      # Process-level settings (daemon mode, logging, ulimits)
defaults    # Default values applied to all frontends and backends
frontend    # Listens for incoming connections
backend     # Defines the pool of servers to forward to
```

A minimal working config looks like this:

```
global
    log /dev/log local0
    maxconn 50000
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5s
    timeout client  30s
    timeout server  30s

frontend web
    bind *:80
    default_backend app_servers

backend app_servers
    balance roundrobin
    server app1 10.0.0.1:8080 check
    server app2 10.0.0.2:8080 check
    server app3 10.0.0.3:8080 check
```

## Frontend Configuration

The frontend is where HAProxy receives connections. You can bind to multiple ports, apply ACLs, and route to different backends.

```
frontend web
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/myapp.pem

    # Redirect HTTP to HTTPS
    redirect scheme https if !{ ssl_fc }

    # Route by hostname
    acl is_api hdr(host) -i api.example.com
    use_backend api_servers if is_api
    default_backend web_servers
```

## Backend Configuration

The backend defines the server pool and how HAProxy distributes traffic.

```
backend web_servers
    balance leastconn
    option httpchk GET /health
    http-check expect status 200
    server web1 10.0.0.1:8080 check inter 10s rise 2 fall 3
    server web2 10.0.0.2:8080 check inter 10s rise 2 fall 3
    server web3 10.0.0.3:8080 check inter 10s rise 2 fall 3 weight 2
```

`check` enables health checking. `inter` sets the check interval. `rise` and `fall` set how many successful/failed checks change the server's state.

## Load Balancing Algorithms

| Algorithm | Description |
|---|---|
| `roundrobin` | Distributes requests evenly in rotation |
| `leastconn` | Sends to the server with fewest active connections |
| `source` | Hashes client IP — same client always hits same server |
| `uri` | Hashes the request URI — same URL always hits same server |
| `random` | Random server selection |

`leastconn` is usually best for long-lived connections (databases, WebSockets). `roundrobin` is fine for stateless HTTP.

## Health Checks

HAProxy can check backend health at the TCP or HTTP level:

```
backend api_servers
    option httpchk GET /ping HTTP/1.1\r\nHost:\ api.example.com
    http-check expect status 200
    server api1 10.0.0.10:3000 check
    server api2 10.0.0.11:3000 check
```

For TCP-level checks (databases, non-HTTP services):

```
backend db_servers
    option tcp-check
    server db1 10.0.0.20:5432 check
```

## ACLs and Routing

ACLs let you route, block, or rewrite traffic based on headers, paths, IPs, and more:

```
frontend web
    bind *:80

    # Define ACLs
    acl is_api path_beg /api/
    acl is_static path_end .jpg .png .css .js
    acl internal_ip src 10.0.0.0/8

    # Block everything except internal IPs on the admin path
    acl is_admin path_beg /admin
    http-request deny if is_admin !internal_ip

    # Route based on ACLs
    use_backend static_servers if is_static
    use_backend api_servers    if is_api
    default_backend web_servers
```

## SSL Termination

HAProxy terminates SSL at the frontend. Combine your certificate and private key into a single `.pem` file:

```bash
$ cat server.crt server.key > /etc/ssl/certs/myapp.pem
```

Then configure the frontend:

```
frontend web_ssl
    bind *:443 ssl crt /etc/ssl/certs/myapp.pem
    bind *:80
    redirect scheme https if !{ ssl_fc }

    # Add standard security headers
    http-response set-header Strict-Transport-Security "max-age=63072000"
    http-response set-header X-Frame-Options SAMEORIGIN

    default_backend app_servers
```

Pass the real client IP to your backends:

```
backend app_servers
    option forwardfor
    http-request set-header X-Forwarded-Proto https
    server app1 10.0.0.1:8080 check
```

## Stats Page

HAProxy has a built-in stats dashboard. Enable it by adding a dedicated frontend:

```
frontend stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats auth admin:yourpassword
    stats hide-version
```

Visit `http://your-server:8404/stats` to see real-time connection counts, server states, and request rates.

## Validating and Reloading Config

```bash
# Validate config without restarting
$ haproxy -c -f /etc/haproxy/haproxy.cfg
Configuration file is valid

# Reload gracefully (keeps active connections alive)
$ sudo systemctl reload haproxy

# Full restart (drops active connections)
$ sudo systemctl restart haproxy
```

## Quick Cheat Sheet

```
# Frontend directives
bind *:80                           # Listen on port 80
bind *:443 ssl crt /path/to.pem    # Listen with SSL
default_backend name                # Send to this backend by default
use_backend name if acl_name        # Conditional routing

# Backend directives
balance roundrobin                  # Load balancing algorithm
server name ip:port check           # Add a server with health check
option httpchk GET /health          # HTTP health check endpoint
timeout server 30s                  # Server response timeout

# ACL operators
hdr(host) -i example.com           # Match Host header (case insensitive)
path_beg /api                       # Path starts with
path_end .jpg                       # Path ends with
src 10.0.0.0/8                     # Source IP range
```

## Conclusion

HAProxy's configuration is verbose compared to Nginx, but that verbosity is its strength — every behavior is explicit and tunable. Start with the four-section structure (global, defaults, frontend, backend), pick a load balancing algorithm that matches your workload, enable health checks, and use ACLs for any routing logic beyond simple default routing. The stats page alone is worth the setup time for production visibility.
