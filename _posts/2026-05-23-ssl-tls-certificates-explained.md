---
layout: post
title: "SSL/TLS Certificates Explained: How HTTPS Actually Works"
date: "2026-05-23 00:00:00 +0530"
slug: ssl-tls-certificates-explained
description: "Understand how TLS certificates work, what the handshake does, how certificate authorities establish trust, and how to get and configure free HTTPS with Let's Encrypt."
categories: ["wiki"]
tags: ["ssl", "tls", "https", "certificates", "security", "networking", "encryption", "web server", "nginx", "let's encrypt", "certbot"]
---

Every time you see a padlock in your browser or visit a site over HTTPS, a complex handshake is happening behind the scenes. Most developers know that TLS provides encryption, but the details — how browsers decide to trust a certificate, what's actually inside the certificate file, and what all those OpenSSL error messages mean — stay murky. Understanding TLS properly makes you a better debugger and helps you make informed decisions about certificate types and configurations.

## SSL vs TLS: What's the Difference?

SSL (Secure Sockets Layer) is the predecessor to TLS (Transport Layer Security). SSL 2.0 and 3.0 are both deprecated and broken. TLS 1.0 and 1.1 are also deprecated. You should be running **TLS 1.2 at minimum**, with TLS 1.3 as the goal.

In practice, everyone still says "SSL certificate" — the term has stuck even though the protocol is TLS. When someone says "install an SSL cert," they mean a certificate used with TLS.

## How the TLS Handshake Works

Before any encrypted HTTP data is sent, the client and server negotiate a TLS session:

```
Client                                Server
  |                                     |
  |---- ClientHello ------------------>|  (TLS version, cipher suites, random)
  |<--- ServerHello -------------------| (chosen cipher, server random)
  |<--- Certificate -------------------| (server's public certificate)
  |<--- ServerHelloDone ---------------|
  |                                     |
  | (client verifies certificate)       |
  |                                     |
  |---- ClientKeyExchange ------------>| (pre-master secret, encrypted with server's public key)
  |---- ChangeCipherSpec ------------->|
  |---- Finished ---------------------->|
  |<--- ChangeCipherSpec --------------|
  |<--- Finished ----------------------|
  |                                     |
  |==== Encrypted HTTP traffic ========|
```

TLS 1.3 streamlines this significantly — it reduces the handshake to 1 round trip (vs 2 for TLS 1.2) and removes weak cipher suites from the negotiation entirely.

## What's Inside a Certificate

A TLS certificate is an X.509 document containing:

- The **subject** (the domain or entity the cert is for)
- The **public key** (used to establish the session key)
- The **issuer** (the Certificate Authority that signed it)
- **Validity dates** (not before / not after)
- **Subject Alternative Names (SANs)** — the list of domains the cert covers
- A **digital signature** from the issuing CA

You can inspect a certificate with OpenSSL:

```bash
$ openssl x509 -in /etc/ssl/certs/example.pem -text -noout

Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 04:bb:...
        Issuer: C=US, O=Let's Encrypt, CN=R3
        Validity
            Not Before: May 20 00:00:00 2026 GMT
            Not After : Aug 18 23:59:59 2026 GMT
        Subject: CN=example.com
        Subject Alternative Names:
            DNS:example.com
            DNS:www.example.com
```

## Certificate Authorities and the Trust Chain

Your browser trusts a certificate because it was signed by a Certificate Authority (CA) that your OS or browser already trusts. This is the **chain of trust**:

```
Root CA (built into your OS/browser)
  └── Intermediate CA (signed by Root CA)
        └── Your Certificate (signed by Intermediate CA)
```

Browsers ship with a list of ~150 trusted Root CAs. If your cert was signed by any of them (directly or via an intermediate), the browser trusts it. Self-signed certificates fail because they're not signed by any trusted CA — the chain leads nowhere.

You can view the chain with:

```bash
$ openssl s_client -connect example.com:443 -showcerts
```

## Certificate Types

| Type | Validation | Use case |
|---|---|---|
| **DV** (Domain Validated) | CA proves you control the domain | Most websites, APIs |
| **OV** (Organization Validated) | CA verifies organization identity | Corporate sites |
| **EV** (Extended Validation) | Rigorous org vetting | Banks, large enterprises |

For most applications, DV certificates are correct — they provide the same encryption as OV/EV. The visual distinction in browsers (EV certs used to show a green bar) has been removed by Chrome and Firefox. Use DV.

## Wildcard and Multi-Domain Certificates

A **wildcard** cert covers one level of subdomain:

- `*.example.com` covers `api.example.com`, `www.example.com`, `app.example.com`
- It does NOT cover `sub.api.example.com`

A **SAN cert** (multi-domain) lists specific hostnames explicitly and can cover completely different domains in one certificate.

## Getting a Free Certificate with Let's Encrypt

Let's Encrypt is a free, automated CA. The recommended client is `certbot`:

```bash
# Install certbot (Ubuntu)
$ sudo apt install certbot python3-certbot-nginx

# Get and install a cert (Nginx auto-config)
$ sudo certbot --nginx -d example.com -d www.example.com

# Follow the prompts. When done, certbot edits your nginx config automatically.

# Verify auto-renewal (Let's Encrypt certs expire in 90 days)
$ sudo certbot renew --dry-run
```

For a standalone server (no web server running yet):

```bash
$ sudo certbot certonly --standalone -d example.com
```

Certs are stored in `/etc/letsencrypt/live/example.com/`.

## Nginx Configuration with TLS

```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com www.example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # TLS version and cipher configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

Use `ssl_prefer_server_ciphers off` with TLS 1.3 — the client's cipher preference is fine.

## Checking Certificate Expiry

```bash
# Check a live site's cert expiry
$ echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -dates
notBefore=May 20 00:00:00 2026 GMT
notAfter=Aug 18 23:59:59 2026 GMT

# Days until expiry
$ echo | openssl s_client -connect example.com:443 2>/dev/null \
  | openssl x509 -noout -enddate \
  | sed 's/notAfter=//' \
  | xargs -I{} date -d "{}" +%s \
  | xargs -I{} sh -c 'echo $(( ($1 - $(date +%s)) / 86400 )) days remaining' _ {}
87 days remaining
```

## Common TLS Errors

| Error | Cause |
|---|---|
| `SSL_ERROR_RX_RECORD_TOO_LONG` | Server is serving plain HTTP on a TLS port |
| `CERTIFICATE_VERIFY_FAILED` | Self-signed cert or missing intermediate cert |
| `ERR_CERT_DATE_INVALID` | Certificate has expired or system clock is wrong |
| `ERR_SSL_VERSION_OR_CIPHER_MISMATCH` | Server only supports deprecated protocols |
| `ERR_CERT_COMMON_NAME_INVALID` | Hostname doesn't match any SAN on the cert |

When debugging, always start with `openssl s_client -connect host:443` — it shows the full chain and negotiated protocol.

## Conclusion

TLS is what makes HTTP trustworthy: it authenticates the server (so you know you're talking to the real example.com) and encrypts the session (so nobody in the middle can read or modify it). The trust model chains from your browser's built-in CA list through intermediate CAs to your certificate. For most applications, a free Let's Encrypt DV certificate with TLS 1.2/1.3 and a proper Nginx configuration covers everything you need. Rotate certs before expiry — certbot's auto-renewal handles this automatically if you let it.
