---
layout: post
title: "Webhooks vs Polling: Which One and When"
date: "2026-05-25 00:00:00 +0530"
slug: webhooks-vs-polling
description: "Compare webhooks and polling for API integrations — understand the trade-offs in latency, reliability, complexity, and security, with code examples for both approaches."
categories: ["wiki", "Programming"]
tags: ["webhooks", "polling", "api", "real-time", "backend", "event-driven", "http", "integration", "comparison"]
---

When you're integrating two services — say, a payment processor and your backend — you need a way to get notified when something happens on the other side. Two approaches dominate: **polling** (your server asks repeatedly) and **webhooks** (the other service pushes to you). Neither is universally better, and the wrong choice creates either unnecessary latency or a reliability nightmare. Here's how to reason through the decision.

## How Polling Works

Your server calls the remote API on a fixed interval to check for new data:

```python
import time
import httpx

def poll_payment_status(payment_id: str):
    while True:
        response = httpx.get(
            f"https://payments.example.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        data = response.json()

        if data["status"] in ("succeeded", "failed"):
            handle_payment_result(data)
            break

        time.sleep(5)
```

Polling is simple: no public endpoint required, no signature verification, no event delivery guarantees to think about. You control exactly when you check and can handle transient failures in a straightforward loop.

The problems:
- **Latency**: if a payment completes one second after your poll, you wait the full interval before finding out
- **Wasted requests**: most polls return "nothing changed"
- **Rate limits**: heavy polling burns through your API quota
- **Scale problems**: tracking 10,000 pending orders requires 10,000 polling loops or complex batching

## How Webhooks Work

You register an HTTPS endpoint with the external service. When an event occurs, the service sends an HTTP POST to your endpoint with the event payload:

```
Payment service  ──POST /webhooks/payments──▶  Your server
                   { "type": "payment.succeeded", "data": {...} }
```

```python
from fastapi import FastAPI, Request, Header, HTTPException
import hmac, hashlib

app = FastAPI()
WEBHOOK_SECRET = "your-webhook-signing-secret"

@app.post("/webhooks/payments")
async def handle_payment_webhook(
    request: Request,
    x_signature: str = Header(None),
):
    body = await request.body()

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected}", x_signature):
        raise HTTPException(400, "Invalid signature")

    event = await request.json()

    if event["type"] == "payment.succeeded":
        await mark_order_paid(event["data"]["payment_id"])
    elif event["type"] == "payment.failed":
        await handle_payment_failure(event["data"]["payment_id"])

    return {"received": True}
```

The key advantages over polling:
- **Low latency**: the event arrives within milliseconds of occurring
- **Efficient**: no wasted requests — you only receive calls when something changes
- **Scales naturally**: 10,000 pending orders don't require 10,000 polling loops

The new complexity:
- **Your endpoint must be publicly reachable**: HTTPS required; local dev needs a tunnel (ngrok, Cloudflare Tunnel)
- **Delivery is not guaranteed**: the service retries on failure, but if your endpoint is down for a long window, events may be dropped
- **Events can arrive out of order or more than once**
- **Signature verification is non-negotiable**

## Signature Verification

Anyone who discovers your endpoint URL can POST fake events. Without signature verification, an attacker could trigger order confirmations, refunds, or user-tier changes.

The standard pattern: the service computes `HMAC-SHA256(secret, raw_body)` and includes it in a header. You recompute and compare:

```python
import hmac
import hashlib

def verify_signature(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

Use `hmac.compare_digest` rather than `==` to prevent timing attacks.

## Handling Duplicate Delivery

Webhook providers guarantee **at-least-once delivery**. If your endpoint returns a non-2xx status, they'll retry — which means your handler can be invoked multiple times for the same event. Make your handler idempotent:

```python
async def handle_payment_webhook(event: dict):
    event_id = event["id"]

    already_processed = await db.fetchval(
        "SELECT 1 FROM processed_events WHERE event_id = $1", event_id
    )
    if already_processed:
        return {"received": True}

    # process the event...

    await db.execute(
        "INSERT INTO processed_events (event_id, processed_at) VALUES ($1, NOW())",
        event_id,
    )
```

Also make the underlying state change idempotent:

```python
async def mark_order_paid(payment_id: str):
    await db.execute("""
        UPDATE orders SET status = 'paid', paid_at = NOW()
        WHERE payment_id = $1 AND status != 'paid'
    """, payment_id)
```

## Respond Fast, Process Later

Webhook providers have short timeout windows — often 5–30 seconds. If your endpoint doesn't respond in time, they treat it as a failure and retry. Don't do heavy work synchronously in the handler:

```python
@app.post("/webhooks/payments")
async def handle_payment_webhook(request: Request):
    body = await request.body()
    verify_or_raise(body, request.headers)

    await queue.enqueue("process_payment_event", body)
    return {"received": True}
```

Acknowledge immediately, process asynchronously. This also makes your webhook handler trivially fast and highly available.

## Testing Webhooks Locally

Use ngrok or Cloudflare Tunnel to expose your local server:

```bash
$ ngrok http 8000
```

```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

Register `https://abc123.ngrok.io/webhooks/payments` with the service, then trigger test events from their dashboard. Most major providers (Stripe, GitHub, Razorpay) have a "resend event" button in their dashboard for exactly this.

## When to Use Polling

Polling is still the right choice in certain situations:

- **The external service doesn't support webhooks**: some APIs are polling-only
- **Querying current state, not changes**: `GET /orders/{id}` before displaying to a user is polling — and that's correct
- **Simple scripts or local tooling**: no need for a public endpoint
- **Long-running job status with infrequent checks**: polling a background job every 10 seconds is simpler than wiring up webhooks for a one-off task
- **You control both sides**: when polling your own services, you can add proper change-notification infrastructure gradually

## When to Use Webhooks

- **Near-real-time requirements**: payment confirmations, shipping updates, identity verification
- **High event volume**: polling thousands of records every few seconds doesn't scale; webhooks scale at the provider's cost
- **Third-party integrations**: payment processors, version control, CRMs — they support webhooks because it's the right model
- **Reducing API quota usage**: webhooks only fire when something happens

## Side-by-Side Comparison

| Factor | Polling | Webhooks |
|---|---|---|
| Latency | Interval-dependent | Near-instant |
| Complexity | Low | Higher |
| Public endpoint needed | No | Yes |
| Missed events | Unlikely (you're checking) | Possible if endpoint is down |
| Rate limit usage | High | Low |
| Idempotency required | No | Yes |
| Scales with event volume | Poorly | Well |
| Best for | Queries, simple integrations | Event-driven integrations |

## Don't Rely on Webhooks Alone

Even with webhooks, implement a periodic reconciliation job that scans for inconsistencies. If your endpoint was down during a deployment window, some events may not have been retried. A nightly job that checks for orders stuck in `pending` state acts as a safety net:

```python
async def reconcile_pending_payments():
    stale_orders = await db.fetch("""
        SELECT payment_id FROM orders
        WHERE status = 'pending'
          AND created_at < NOW() - INTERVAL '30 minutes'
    """)
    for order in stale_orders:
        status = await payments_api.get_status(order["payment_id"])
        if status != "pending":
            await update_order_status(order["payment_id"], status)
```

This hybrid approach — webhooks for speed, polling for correctness — is what most production payment integrations use.

## Conclusion

Webhooks are the right default for event-driven integrations with external services: they're faster, cheaper on API quota, and scale without polling loops. Polling is simpler to set up and better when you need current state on demand or when the other side doesn't support webhooks. Whichever you use, build for reliability — verify signatures, handle duplicates, respond fast and process asynchronously, and add a reconciliation job to catch events your webhook handler may have missed.
