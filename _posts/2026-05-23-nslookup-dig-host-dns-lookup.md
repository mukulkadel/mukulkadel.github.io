---
layout: post
title: "nslookup, dig, and host — DNS Lookup Tools Explained"
date: "2026-05-23 00:00:00 +0530"
slug: nslookup-dig-host-dns-lookup
description: "Learn how to use nslookup, dig, and host to query DNS records, debug resolution issues, and inspect A, CNAME, MX, TXT, and NS records from the terminal."
categories: ["wiki", "unix"]
tags: ["nslookup", "dig", "host", "dns", "networking", "linux", "macos", "command line", "sysadmin", "debugging"]
---

When a domain isn't resolving the way you expect, or you need to verify that a DNS change has propagated, three tools cover the full range of what you need: `nslookup`, `dig`, and `host`. They all query DNS, but each has a different interface and level of detail. `dig` is the most powerful; `host` is the quickest for simple lookups; `nslookup` is the most widely available, including on Windows.

## Installing the Tools

On Debian/Ubuntu:

```bash
$ sudo apt install dnsutils      # provides dig and host
$ sudo apt install bind9-host    # alternative for host
```

On macOS, all three come pre-installed with the system tools.

## nslookup

`nslookup` is the simplest of the three and works on Linux, macOS, and Windows. It queries the system's configured DNS resolver by default.

### Basic A Record Lookup

```bash
$ nslookup example.com
Server:         192.168.1.1
Address:        192.168.1.1#53

Non-authoritative answer:
Name:   example.com
Address: 93.184.216.34
```

The "Non-authoritative answer" line means the response came from a caching resolver, not the authoritative nameserver for the domain — which is normal for most queries.

### Query a Specific DNS Server

Pass the server as the second argument:

```bash
$ nslookup example.com 8.8.8.8
Server:         8.8.8.8
Address:        8.8.8.8#53

Non-authoritative answer:
Name:   example.com
Address: 93.184.216.34
```

This queries Google's public DNS directly — useful when you suspect your local resolver has stale cache.

### Query Specific Record Types

```bash
$ nslookup -type=MX gmail.com
Server:         192.168.1.1
Address:        192.168.1.1#53

Non-authoritative answer:
gmail.com       mail exchanger = 10 alt1.gmail-smtp-in.l.google.com.
gmail.com       mail exchanger = 20 alt2.gmail-smtp-in.l.google.com.
gmail.com       mail exchanger = 5 gmail-smtp-in.l.google.com.
```

```bash
$ nslookup -type=TXT github.com
```

```bash
$ nslookup -type=NS example.com   # nameserver records
$ nslookup -type=AAAA example.com # IPv6 address
$ nslookup -type=CNAME www.github.com
```

### Reverse DNS Lookup (PTR)

Look up the hostname associated with an IP address:

```bash
$ nslookup 93.184.216.34
34.216.184.93.in-addr.arpa     name = 93.184.216.34.static.arin.net.
```

### Interactive Mode

Run `nslookup` without arguments to enter an interactive prompt:

```bash
$ nslookup
> set type=MX
> gmail.com
gmail.com       mail exchanger = 5 gmail-smtp-in.l.google.com.
> exit
```

## dig — The Power Tool

`dig` (Domain Information Groper) gives you the full DNS response including the question section, answer section, authority, and additional records — exactly what was returned, with timing. It's the go-to for debugging.

### Basic Lookup

```bash
$ dig example.com

; <<>> DiG 9.18.18 <<>> example.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; QUESTION SECTION:
;example.com.                   IN      A

;; ANSWER SECTION:
example.com.            3600    IN      A       93.184.216.34

;; Query time: 23 msec
;; SERVER: 192.168.1.1#53(192.168.1.1)
;; WHEN: Fri May 23 10:00:00 IST 2026
;; MSG SIZE  rcvd: 56
```

Key parts to read:
- **status: NOERROR** — successful response. `NXDOMAIN` means the domain doesn't exist.
- **ANSWER SECTION** — the actual records returned
- **3600** — the TTL in seconds (how long this can be cached)
- **Query time** — how long the lookup took

### Short Output with `+short`

When you just want the IP:

```bash
$ dig +short example.com
93.184.216.34
```

### Query Specific Record Types

```bash
$ dig MX gmail.com +short
5 gmail-smtp-in.l.google.com.
10 alt1.gmail-smtp-in.l.google.com.
20 alt2.gmail-smtp-in.l.google.com.
30 alt3.gmail-smtp-in.l.google.com.
40 alt4.gmail-smtp-in.l.google.com.
```

```bash
$ dig TXT github.com +short
"v=spf1 ip4:192.30.252.0/22 include:_netblocks.github.com ~all"
"MS=ms44452932"
```

```bash
$ dig NS example.com +short
a.iana-servers.net.
b.iana-servers.net.
```

```bash
$ dig CNAME www.github.com +short
github.com.
```

### Query a Specific DNS Server

```bash
$ dig @8.8.8.8 example.com
$ dig @1.1.1.1 example.com +short    # Cloudflare's resolver
```

Compare the response from your local resolver vs. an authoritative server to debug propagation issues.

### Reverse Lookup

```bash
$ dig -x 93.184.216.34 +short
93.184.216.34.static.arin.net.
```

### Check DNS Propagation — Query Authoritative Servers

First find the authoritative nameservers, then query them directly:

```bash
$ dig NS example.com +short
a.iana-servers.net.
b.iana-servers.net.

$ dig @a.iana-servers.net example.com +short
93.184.216.34
```

If the authoritative server returns the new value but your local resolver returns the old one, the record is updated but your resolver's cache hasn't expired yet (check the TTL).

### Trace the Full Resolution Path

`+trace` follows delegation from the root nameservers all the way down — very useful for diagnosing delegation issues:

```bash
$ dig +trace example.com
```

This queries the root servers (`.`), then the TLD servers (`.com`), then the authoritative servers — showing you every hop.

### Show Only the Answer Section

```bash
$ dig example.com +noall +answer
example.com.            3600    IN      A       93.184.216.34
```

### Query All Record Types (ANY)

```bash
$ dig example.com ANY
```

Note: many DNS providers now return an empty or minimal response to `ANY` queries to prevent DNS amplification attacks.

## host — Quick and Clean

`host` gives a clean, human-readable output with less noise than `dig`. It's great for quick checks.

### Basic Lookup

```bash
$ host example.com
example.com has address 93.184.216.34
example.com has IPv6 address 2606:2800:220:1:248:1893:25c8:1946
```

### Specific Record Types

```bash
$ host -t MX gmail.com
gmail.com mail is handled by 5 gmail-smtp-in.l.google.com.
gmail.com mail is handled by 10 alt1.gmail-smtp-in.l.google.com.

$ host -t TXT github.com
$ host -t NS example.com
$ host -t CNAME www.github.com
```

### Reverse Lookup

```bash
$ host 93.184.216.34
34.216.184.93.in-addr.arpa domain name pointer 93.184.216.34.static.arin.net.
```

### Query a Specific Server

```bash
$ host example.com 8.8.8.8
Using domain server:
Name: 8.8.8.8
Address: 8.8.8.8#53
Aliases:

example.com has address 93.184.216.34
```

### Verbose Mode

```bash
$ host -v example.com
```

Shows the full DNS message similar to `dig`.

## Practical Debugging Scenarios

### Verify a DNS record after updating it

```bash
$ dig @8.8.8.8 mysite.com +short
93.184.1.100

$ dig @1.1.1.1 mysite.com +short
93.184.1.100
```

If both return the new value, the record has propagated to major public resolvers.

### Check the TTL remaining on a cached record

```bash
$ dig example.com +noall +answer
example.com.            287     IN      A       93.184.216.34
```

The `287` means 287 seconds before this cache entry expires. If propagation feels slow, check whether the old TTL was very high.

### Verify an SPF record for email deliverability

```bash
$ dig TXT yourdomain.com +short | grep spf
"v=spf1 include:mailgun.org ~all"
```

### Check if a subdomain is a CNAME or A record

```bash
$ dig api.example.com +short
api.example.com is an alias for lb.example.com.
lb.example.com has address 203.0.113.10
```

### Confirm DKIM is published

```bash
$ dig TXT default._domainkey.yourdomain.com +short
"v=DKIM1; k=rsa; p=MIGfMA0GCS..."
```

## Quick Reference: Which Tool to Use

| Task | Best tool |
|---|---|
| Quick IP lookup | `host domain.com` or `dig +short domain.com` |
| Full DNS response with timing | `dig domain.com` |
| Trace full resolution path | `dig +trace domain.com` |
| Query from Windows | `nslookup` |
| Reverse IP lookup | `dig -x IP +short` or `host IP` |
| Check specific record type | `dig TYPE domain.com +short` |
| Debug propagation | `dig @8.8.8.8 domain.com` vs `dig @authoritative-ns domain.com` |

## Conclusion

For day-to-day DNS debugging, `dig +short` and `host` cover most needs — they're fast and readable. When you need to understand exactly what was returned (TTL, authority section, query timing), `dig` without `+short` is the right call. The `+trace` flag is invaluable when a domain isn't resolving at all and you need to see where the delegation chain breaks. Keep `nslookup` in mind for Windows environments where `dig` isn't available by default.
