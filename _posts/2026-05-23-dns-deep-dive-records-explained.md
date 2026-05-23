---
layout: post
title: "DNS Deep Dive: A Records, CNAME, MX, TTL Explained"
date: "2026-05-23 00:00:00 +0530"
slug: dns-deep-dive-records-explained
description: "A complete guide to how DNS resolution works, the most important record types, TTL and caching, and how to debug DNS issues with dig and nslookup."
categories: ["wiki"]
tags: ["dns", "networking", "a record", "cname", "mx", "ttl", "domain", "web", "devops", "sysadmin", "dig", "nslookup"]
---

DNS is the phonebook of the internet — a distributed, hierarchical system that translates human-readable domain names into IP addresses. When something goes wrong with DNS, everything breaks: websites won't load, emails won't send, and services silently fail in confusing ways. Understanding DNS properly — not just "add an A record pointing to your server IP" — is one of those foundational pieces of knowledge that pays off every time you deploy something.

## How DNS Resolution Works

When you type `example.com` into a browser, here's what actually happens:

```
Browser
  ↓
Local DNS cache (checked first)
  ↓
Recursive resolver (usually your ISP or 8.8.8.8)
  ↓
Root nameserver (.) — knows where .com nameservers are
  ↓
TLD nameserver (.com) — knows where example.com nameservers are
  ↓
Authoritative nameserver (ns1.example.com) — returns the actual record
  ↑
Answer propagates back up and is cached at each layer
```

The whole process typically takes 20–120 ms for a cold lookup. Subsequent lookups are answered from cache in under 1 ms.

## DNS Record Types

### A Record

Maps a hostname to an IPv4 address. The most fundamental record.

```
example.com.    300    IN    A    93.184.216.34
www.example.com. 300   IN    A    93.184.216.34
```

You can have multiple A records for the same hostname — DNS returns all of them, and the client picks one (usually the first, sometimes randomly). This is the simplest form of load balancing, though it has no health checking.

### AAAA Record

Maps a hostname to an IPv6 address. Same concept as A, but for IPv6.

```
example.com.    300    IN    AAAA    2606:2800:220:1:248:1893:25c8:1946
```

### CNAME Record

An alias — maps one hostname to another. The target must be an A (or AAAA) record, not an IP address.

```
www.example.com.    3600    IN    CNAME    example.com.
blog.example.com.   3600    IN    CNAME    mysite.netlify.app.
```

**The CNAME constraint**: you cannot put a CNAME on the root domain (`example.com`) because the root needs SOA and NS records, which can't coexist with a CNAME. Use an A record for the root and CNAME for subdomains. Some DNS providers offer "CNAME flattening" or "ALIAS" records to work around this.

**CNAME chain length**: avoid chaining CNAMEs (`a` → `b` → `c`). Each hop costs a DNS lookup and adds latency.

### MX Record

Specifies mail servers for a domain, with a priority value (lower = higher priority):

```
example.com.    3600    IN    MX    10    mail1.example.com.
example.com.    3600    IN    MX    20    mail2.example.com.
```

When email is sent to `user@example.com`, the sender's mail server looks up the MX records and tries them in priority order.

### TXT Record

Arbitrary text. Used for domain verification, SPF, DKIM, and DMARC:

```
; SPF — which servers are allowed to send email for this domain
example.com.    TXT    "v=spf1 include:_spf.google.com ~all"

; Domain ownership verification (Google Search Console, etc.)
example.com.    TXT    "google-site-verification=abc123..."

; DKIM public key (for email signing)
mail._domainkey.example.com.    TXT    "v=DKIM1; k=rsa; p=MIGfMA0..."
```

### NS Record

Nameserver — delegates authority for a zone to specific nameservers:

```
example.com.    NS    ns1.cloudflare.com.
example.com.    NS    ns2.cloudflare.com.
```

NS records are set at your domain registrar and point to whoever hosts your DNS zone.

### SOA Record

Start of Authority — metadata about the DNS zone itself (primary nameserver, admin email, serial number, refresh intervals). You rarely set this manually; your DNS provider manages it.

### PTR Record

Reverse DNS — maps an IP address back to a hostname. Used by mail servers to verify that sending servers are legitimate.

```
34.216.184.93.in-addr.arpa.    PTR    example.com.
```

## TTL: Time to Live

TTL is how long (in seconds) resolvers and clients should cache a DNS record before asking again.

```
example.com.    300    IN    A    93.184.216.34
              ↑
           TTL = 300 seconds = 5 minutes
```

**Implications**:

- **Low TTL (60–300s)**: DNS changes propagate quickly. Good before a migration, but generates more DNS traffic.
- **High TTL (3600–86400s)**: Changes are slow to propagate (up to 24 hours), but faster for end users.

**Best practice**: lower the TTL to 300 before a planned IP change, wait for the old TTL to expire, make the change, then raise the TTL back after confirming everything works.

## Debugging DNS with `dig`

`dig` is your primary DNS debugging tool:

```bash
# Basic A record lookup
$ dig example.com

;; ANSWER SECTION:
example.com.    300    IN    A    93.184.216.34

# Lookup a specific record type
$ dig example.com MX
$ dig example.com TXT
$ dig example.com NS

# Use a specific resolver (bypass your local cache)
$ dig @8.8.8.8 example.com

# Check the full resolution chain (+trace)
$ dig +trace example.com

# Short output
$ dig +short example.com
93.184.216.34

# Reverse DNS lookup
$ dig -x 93.184.216.34
```

## Debugging with `nslookup`

`nslookup` is available on Windows and macOS by default:

```bash
$ nslookup example.com
Server:    192.168.1.1
Address:   192.168.1.1#53

Non-authoritative answer:
Name:    example.com
Address: 93.184.216.34

# Query a specific record type
$ nslookup -type=MX example.com

# Query a specific server
$ nslookup example.com 8.8.8.8
```

## Common DNS Pitfalls

**"My DNS change isn't propagating"** — DNS propagation isn't magic. What's actually happening is that resolvers around the world are holding cached copies of the old record until their TTL expires. Check the old TTL before making changes.

**CNAME on the root domain** — This breaks things. Use an A record for `example.com` and a CNAME for `www.example.com`.

**Missing the trailing dot** — In zone files, hostnames are written with a trailing dot (`example.com.`) to indicate they're absolute. Without it, many DNS tools append the zone name, turning `mail` into `mail.example.com.`. `dig` adds trailing dots in output; most DNS UIs handle it for you.

**Forgetting SPF/DKIM/DMARC** — Email without these records gets flagged as spam or rejected outright. Set them up when you configure MX records.

## Conclusion

DNS is deceptively simple on the surface — point a domain at an IP, done — but the details matter when things go wrong or when you're setting up email, CDNs, or multi-region infrastructure. The record types you'll use most are A, CNAME, MX, and TXT. Keep TTLs low before planned changes, use `dig` to inspect what resolvers actually see (not what your DNS panel shows), and remember that "DNS propagation" is just cache TTL expiry — not something that happens on its own schedule.
