---
layout: post
title: "OAuth 2.0 and JWT Explained: How Auth Actually Works"
date: "2026-05-25 00:00:00 +0530"
slug: oauth2-jwt-explained
description: "A practical guide to OAuth 2.0 flows and JWT tokens — how they work together, when to use each grant type, and how to implement secure token validation in your API."
categories: ["wiki", "Programming"]
tags: ["oauth2", "jwt", "authentication", "authorization", "security", "tokens", "backend", "api", "refresh tokens"]
---

Authentication is one of those areas where developers frequently build something that looks right until it's attacked. OAuth 2.0 and JWT are two distinct things that are often conflated — OAuth 2.0 is an **authorization framework** (how you delegate access), while JWT is a **token format** (how you encode claims). Understanding the difference, and how they compose, is essential before wiring either into a production API.

## What OAuth 2.0 Actually Does

OAuth 2.0 isn't an authentication protocol — it's an authorization delegation protocol. It answers the question: how can a user let a third-party app access their data without giving it their password?

The core actors:
- **Resource Owner**: the user
- **Client**: the application requesting access (a mobile app, a CLI tool)
- **Authorization Server**: the service that issues tokens (Google, Auth0, your own auth server)
- **Resource Server**: the API holding the protected data

OAuth 2.0 defines several **grant types** for different scenarios.

## The Authorization Code Flow (for Web and Mobile Apps)

This is the most secure and most common flow. It's what happens when you click "Sign in with Google."

```
User         Client App        Auth Server       Resource Server
 |                |                 |                   |
 |--clicks login->|                 |                   |
 |                |---redirect----->|                   |
 |<------login page----------------|                   |
 |---credentials->|                |                   |
 |                |<---auth code---|                   |
 |                |                |                   |
 |                |--code + secret->|                  |
 |                |<-access + refresh token------------|
 |                |                 |                   |
 |                |---access token------------------->|
 |                |<--protected resource---------------|
```

The auth code is short-lived and single-use. It's exchanged server-to-server (your backend to the auth server), so tokens never pass through the user's browser. The **PKCE** extension (`code_verifier`/`code_challenge`) adapts this flow safely to mobile and single-page apps where a client secret can't be stored securely.

## Client Credentials Flow (for Machine-to-Machine)

When there's no user involved — a background job, a microservice calling another microservice — use client credentials:

```bash
$ curl -X POST https://auth.example.com/token \
  -d "grant_type=client_credentials" \
  -d "client_id=my-service" \
  -d "client_secret=s3cr3t" \
  -d "scope=read:orders"
```

```json
{
  "access_token": "eyJhbG...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read:orders"
}
```

No user is in the loop. The client authenticates with its own credentials and gets a token scoped to what that service is allowed to do.

## What is a JWT?

A JWT (JSON Web Token) is a compact, self-contained token format. It consists of three Base64URL-encoded parts separated by dots:

```
header.payload.signature
```

The header specifies the signing algorithm:

```json
{ "alg": "RS256", "typ": "JWT" }
```

The payload contains claims — facts about the user or session:

```json
{
  "sub": "user123",
  "email": "alice@example.com",
  "roles": ["admin"],
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "iat": 1748131200,
  "exp": 1748134800
}
```

The signature is computed over the header and payload using the auth server's private key (RS256) or a shared secret (HS256).

To verify a JWT on the resource server:

```python
import jwt

# Fetch the public key from the auth server's JWKS endpoint
public_key = fetch_jwks("https://auth.example.com/.well-known/jwks.json")

try:
    claims = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="https://api.example.com",
    )
except jwt.ExpiredSignatureError:
    raise HTTPException(401, "Token expired")
except jwt.InvalidTokenError:
    raise HTTPException(401, "Invalid token")
```

Verification checks:
1. Signature is valid — the token wasn't tampered with
2. `exp` is in the future — not expired
3. `iss` matches the expected issuer
4. `aud` matches this resource server's identifier

The key insight: the resource server **never calls the auth server** to validate a JWT. It validates the signature locally using the public key. This makes JWT validation fast and stateless, with no round-trip to the auth server on every request.

## Access Tokens and Refresh Tokens

**Access tokens** are short-lived (15 minutes to 1 hour) and sent with every API request in the `Authorization` header:

```
Authorization: Bearer eyJhbG...
```

**Refresh tokens** are long-lived (days to weeks), stored securely by the client, and used to get a new access token when the current one expires — without prompting the user to log in again:

```bash
$ curl -X POST https://auth.example.com/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..." \
  -d "client_id=my-app"
```

Why the split? Short-lived access tokens limit the damage if one is intercepted — it expires quickly. Refresh tokens stay server-side or in httpOnly cookies and are revocable.

## Token Revocation

JWTs are stateless — there's no server-side session to invalidate. If you need to revoke a token immediately (after logout or a password change), your options are:

**Short expiry**: keep access tokens to 15 minutes. A stolen token self-destructs quickly.

**Token blocklist**: maintain a Redis set of revoked token IDs (`jti` claim). Check it on every request. Adds one Redis lookup per API call.

**Refresh token rotation**: on every refresh, issue a new refresh token and invalidate the old one. If the old token is used again, treat it as a sign of theft and revoke the entire token family.

## Common Mistakes

**Putting sensitive data in the JWT payload.** The payload is Base64-encoded, not encrypted. Anyone with the token can decode and read the claims. Never put passwords, SSNs, or PII in a JWT payload. Use JWE (JSON Web Encryption) if you must encrypt claims.

**Using HS256 with a short or guessable secret.** HS256 uses a shared secret — every service that verifies tokens needs that secret, increasing exposure. Prefer RS256: the auth server holds the private key; services only need the public key.

**Ignoring the `aud` claim.** Without audience validation, a token from your staging environment can be replayed against production. Always set and validate `aud`.

**Storing access tokens in `localStorage`.** JavaScript-accessible storage is vulnerable to XSS. Store short-lived access tokens in memory and refresh tokens in httpOnly cookies.

**Not validating `iss`.** Accept tokens only from the issuer you configured. Without this check, a token from a different OAuth provider with the same signing algorithm could be accepted.

## Putting It Together: A Request Flow

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

app = FastAPI()
bearer = HTTPBearer()

JWKS = fetch_jwks("https://auth.example.com/.well-known/jwks.json")

def require_auth(token = Depends(bearer)):
    try:
        claims = jwt.decode(
            token.credentials,
            JWKS,
            algorithms=["RS256"],
            audience="https://api.example.com",
            issuer="https://auth.example.com",
        )
        return claims
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

@app.get("/orders")
def list_orders(claims = Depends(require_auth)):
    user_id = claims["sub"]
    return get_orders_for_user(user_id)
```

## Conclusion

OAuth 2.0 provides the framework for delegated authorization; JWT provides a compact, stateless format for expressing the resulting claims. Use the Authorization Code flow with PKCE for user-facing apps, and Client Credentials for service-to-service calls. Keep access tokens short-lived, rotate refresh tokens on use, validate the full set of claims (`sig`, `exp`, `iss`, `aud`) on every request, and never put sensitive data in a JWT payload. Together, these practices give you auth that's both secure and scalable without a session store on the critical path.
