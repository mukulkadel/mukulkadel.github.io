---
layout: post
title: "OWASP Top 10 Explained with Code Examples"
date: "2026-05-26 00:00:00 +0530"
slug: owasp-top-10-explained
description: "A developer-friendly walkthrough of the OWASP Top 10 web vulnerabilities — what they are, how attackers exploit them, and how to prevent each one."
categories: ["wiki", "Programming"]
tags: ["owasp", "security", "web security", "vulnerabilities", "xss", "sql injection", "csrf", "backend", "best practices"]
---

The OWASP Top 10 is the closest thing the web security world has to a shared curriculum. Published by the Open Worldwide Application Security Project, it lists the ten most critical web application security risks — risks that appear in real breaches, not just theoretical attacks. If you're building web applications and haven't internalized these, you have blind spots.

## A01: Broken Access Control

The most common flaw in modern applications. Broken access control means a user can act on resources they shouldn't be able to access — reading another user's data, elevating to admin, accessing URLs they shouldn't.

**Vulnerable code:**

```python
@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, current_user: User):
    invoice = db.get(Invoice, invoice_id)
    return invoice  # no check that invoice belongs to current_user
```

An attacker can iterate `invoice_id` and read anyone's invoices.

**Fix: always check ownership.**

```python
@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, current_user: User):
    invoice = db.get(Invoice, invoice_id)
    if not invoice or invoice.user_id != current_user.id:
        raise HTTPException(status_code=403)
    return invoice
```

Never trust the client to send only IDs they own. Validate on the server, every time.

## A02: Cryptographic Failures

Sensitive data exposed in transit or at rest because of weak or missing encryption. This includes: transmitting data over HTTP instead of HTTPS, storing passwords in plaintext or with MD5, weak cipher choices.

**Never store plaintext passwords:**

```python
# Wrong
user.password = request.password

# Wrong — MD5 is not suitable for passwords
import hashlib
user.password = hashlib.md5(request.password.encode()).hexdigest()

# Right — bcrypt/argon2 with work factor
from passlib.hash import argon2
user.password_hash = argon2.hash(request.password)

# Verify
is_valid = argon2.verify(request.password, user.password_hash)
```

Also: always use HTTPS (`Strict-Transport-Security` header), never log sensitive fields, and use AES-256-GCM for data-at-rest encryption.

## A03: Injection

Injection attacks send untrusted data to an interpreter — SQL, shell, LDAP — tricking it into executing unintended commands. SQL injection is the most famous example.

**Vulnerable:**

```python
# User controls `name` — attacker sends: "'; DROP TABLE users;--"
query = f"SELECT * FROM users WHERE name = '{name}'"
db.execute(query)
```

**Fixed — parameterized queries:**

```python
# The database driver handles escaping — injection is impossible
query = "SELECT * FROM users WHERE name = %s"
db.execute(query, (name,))
```

The same principle applies to shell commands:

```python
import subprocess

# Vulnerable to shell injection
subprocess.run(f"convert {filename} output.png", shell=True)

# Safe — never passes through shell
subprocess.run(["convert", filename, "output.png"])
```

## A04: Insecure Design

Security flaws baked into the architecture, not just the implementation. Examples: no rate limiting on login endpoints, password reset flows that leak whether an email exists, business logic that can be abused at scale.

Insecure design can't be patched away — it requires architectural changes. The fix is threat modeling during design: ask "what could an attacker do with this feature?" before building it.

```python
# Insecure design: reveals whether email is registered
@app.post("/forgot-password")
def forgot_password(email: str):
    user = db.find_user_by_email(email)
    if not user:
        return {"error": "Email not found"}  # leaks info
    send_reset_email(user)

# Better: same response regardless
@app.post("/forgot-password")
def forgot_password(email: str):
    user = db.find_user_by_email(email)
    if user:
        send_reset_email(user)
    return {"message": "If this email exists, a reset link has been sent"}
```

## A05: Security Misconfiguration

Default credentials left in place, verbose error messages leaking stack traces, unnecessary services exposed, debug mode enabled in production. This is the most avoidable category.

```python
# Don't expose stack traces in production
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if settings.DEBUG:
        raise exc  # full traceback for development
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}  # nothing for production
    )
```

Other essentials:
- Change all default passwords on deployment
- Disable directory listing on web servers
- Remove unused endpoints, features, and sample files
- Set security headers (CSP, X-Frame-Options, etc.)

## A06: Vulnerable and Outdated Components

Using libraries, frameworks, or OS packages with known CVEs. The `log4shell` vulnerability (CVE-2021-44228) is the canonical example — it affected thousands of Java applications through a transitive logging dependency.

```bash
# Python — check for vulnerabilities
$ pip-audit
Found 2 known vulnerabilities in 1 package
Name    Version ID                  Fix Versions
------- ------- ------------------- ------------
Pillow  9.0.0   PYSEC-2022-10998    9.0.1

# Node.js
$ npm audit
# JavaScript
$ yarn audit
```

Integrate these into your CI pipeline so vulnerabilities block deployment.

## A07: Identification and Authentication Failures

Weak authentication: missing brute-force protection, insecure session tokens, broken password reset flows, missing MFA.

**Brute-force protection:**

```python
from fastapi_limiter.depends import RateLimiter

@app.post("/login", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login(credentials: LoginCredentials):
    user = authenticate(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_session(user)
```

Five attempts per minute before rate limiting kicks in. Also: use constant-time comparison for password checks to prevent timing attacks.

```python
import hmac

def verify_password(plaintext: str, hashed: str) -> bool:
    # hmac.compare_digest is constant-time — prevents timing attacks
    return hmac.compare_digest(
        hash_password(plaintext).encode(),
        hashed.encode()
    )
```

## A08: Software and Data Integrity Failures

Assuming code and data from external sources are trustworthy. Examples: CI/CD pipelines that run arbitrary scripts from PRs, deserializing untrusted pickle/YAML data, auto-updating packages without integrity verification.

```python
# Dangerous — pickle can execute arbitrary code
import pickle
data = pickle.loads(user_supplied_bytes)

# Safe — JSON cannot execute code
import json
data = json.loads(user_supplied_bytes)
```

Also: verify package integrity with lockfiles (`package-lock.json`, `poetry.lock`), pin dependency versions in production, and sign your CI/CD artifacts.

## A09: Security Logging and Monitoring Failures

You can't detect a breach you're not logging. Missing audit logs, no alerting on suspicious patterns, logs that don't capture enough context to reconstruct an incident.

```python
import logging
import structlog

log = structlog.get_logger()

@app.post("/login")
async def login(credentials: LoginCredentials, request: Request):
    user = authenticate(credentials.email, credentials.password)

    if not user:
        log.warning(
            "login_failed",
            email=credentials.email,
            ip=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(status_code=401)

    log.info("login_success", user_id=user.id, ip=request.client.host)
    return create_session(user)
```

Ship logs to a centralized system (Datadog, Splunk, CloudWatch) and set up alerts for: >10 failed logins/minute per IP, logins from new countries, bulk data exports.

## A10: Server-Side Request Forgery (SSRF)

The application fetches a URL provided by the user — and an attacker uses that to reach internal services that shouldn't be accessible from the internet.

```python
# Vulnerable — attacker sends: http://169.254.169.254/latest/meta-data/
@app.get("/fetch")
def fetch_url(url: str):
    response = requests.get(url)
    return response.text
```

An attacker on AWS can use this to hit the instance metadata service and steal IAM credentials.

**Fix: validate and allowlist the URL:**

```python
from urllib.parse import urlparse

ALLOWED_HOSTS = {"api.trusted-partner.com", "cdn.example.com"}

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if parsed.hostname not in ALLOWED_HOSTS:
        return False
    return True

@app.get("/fetch")
def fetch_url(url: str):
    if not is_safe_url(url):
        raise HTTPException(status_code=400, detail="URL not allowed")
    return requests.get(url).text
```

## Conclusion

The OWASP Top 10 isn't an advanced hacking guide — these are the basics, and attackers exploit them routinely. Broken access control, injection, and cryptographic failures account for the majority of real-world breaches. Build security in from the design phase (A04), keep your dependencies updated (A06), log enough to detect and reconstruct incidents (A09), and validate every input and output that crosses a trust boundary.
