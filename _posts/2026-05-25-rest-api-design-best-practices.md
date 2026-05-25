---
layout: post
title: "REST API Design Best Practices: Versioning, Errors, and Pagination"
date: "2026-05-25 00:00:00 +0530"
slug: rest-api-design-best-practices
description: "A practical guide to REST API design covering resource naming, HTTP status codes, versioning strategies, structured error formats, and cursor-based pagination."
categories: ["Programming", "wiki"]
tags: ["rest", "api", "api design", "versioning", "pagination", "http", "json", "backend", "best practices", "status codes"]
---

A well-designed REST API is easy to understand, predictable, and hard to misuse. A poorly designed one generates a stream of support tickets and breaking changes that haunt your team for years. Most of the common mistakes — inconsistent naming, overloaded status codes, opaque errors, and fragile pagination — have well-established solutions. We'll cover the ones that matter most in production.

## Resource Naming

REST APIs organize around resources (nouns), not actions (verbs). The HTTP method expresses the action.

**Do this:**

```
GET    /users              # list users
POST   /users              # create a user
GET    /users/{id}         # get a specific user
PUT    /users/{id}         # replace a user
PATCH  /users/{id}         # partial update
DELETE /users/{id}         # delete a user
```

**Avoid this:**

```
GET  /getUser?id=123
POST /createUser
POST /deleteUser?id=123
```

Use **plural nouns** for collections and **kebab-case** for multi-word resources:

```
/blog-posts        ✓
/blogPosts         ✗
/blog_posts        ✗  (underscores disappear in hyperlinks)
```

Nest resources only when the child is genuinely owned by the parent and always accessed through it:

```
GET /users/{id}/addresses      ✓  a user's addresses
GET /orders/{id}/line-items    ✓  order line items

GET /users/{id}/orders         ✗  (orders are queryable independently)
```

## HTTP Status Codes

Use status codes semantically. Clients and API gateways route on them.

| Code | Meaning | When to use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST that creates a resource |
| 204 | No Content | Successful DELETE or action with no response body |
| 400 | Bad Request | Validation failure, malformed JSON, missing required fields |
| 401 | Unauthorized | Not authenticated (no or invalid token) |
| 403 | Forbidden | Authenticated but not authorized for this resource |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource, optimistic locking failure |
| 422 | Unprocessable Entity | Semantically invalid request (e.g., `end_date` before `start_date`) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server failure |

Never return `200 OK` with `{ "success": false }` in the body. That defeats the purpose of HTTP status codes and breaks clients that inspect status before parsing the body.

## Error Response Format

Errors should be structured, consistent, and machine-readable:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "must be a valid email address"
      },
      {
        "field": "age",
        "message": "must be greater than 0"
      }
    ],
    "request_id": "req_9f3k2mxp"
  }
}
```

Key elements:
- **`code`**: a machine-readable string constant (not an HTTP status integer). Clients can `switch` on this without parsing the message.
- **`message`**: human-readable, appropriate for logs or developer displays.
- **`details`**: field-level errors for validation failures. An array, not a map — order matters when rendering to users.
- **`request_id`**: ties the error to a specific request in your logs. Invaluable for support.

## Versioning

You will need to make breaking changes eventually. Plan for it from day one.

### URL path versioning (recommended for most APIs)

```
GET /v1/users
GET /v2/users
```

Simple, explicit, and easy to route at the load balancer level. Clients can see which version they're on without inspecting headers.

### Header versioning

```
GET /users
Accept: application/vnd.myapi.v2+json
```

Keeps URLs clean but requires disciplined header management in every client. Harder to test in a browser or with curl.

### Query parameter versioning

```
GET /users?version=2
```

Easy to test, easy to accidentally ignore. Generally avoided for public APIs.

For most teams, URL versioning is the right call. Ship `v1`, maintain it as long as clients depend on it, and introduce `v2` only for genuinely breaking changes. New optional fields, new endpoints, and new query parameters don't require a version bump.

## Pagination

Never return unbounded lists. Three common strategies:

### Offset pagination

```
GET /users?page=3&per_page=20
```

```json
{
  "data": [...],
  "pagination": {
    "page": 3,
    "per_page": 20,
    "total": 847,
    "total_pages": 43
  }
}
```

Simple, supports jumping to any page. Degrades at large offsets — `OFFSET 10000 LIMIT 20` in SQL scans 10,020 rows. Records can duplicate or skip if data changes between pages.

### Cursor-based pagination (preferred for large datasets)

The client receives an opaque cursor and passes it back to fetch the next page. The cursor encodes position (often a timestamp or ID).

```
GET /events?limit=20
```

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzNDU2fQ==",
    "has_more": true
  }
}
```

Next page:

```
GET /events?limit=20&cursor=eyJpZCI6MTIzNDU2fQ==
```

On the server, the cursor decodes to an ID or timestamp and the query uses a `WHERE id > cursor_id` clause:

```sql
SELECT * FROM events
WHERE id > 123456
ORDER BY id ASC
LIMIT 21;   -- fetch one extra to determine has_more
```

Cursor pagination is stable — inserts and deletes between pages don't affect results already fetched. It doesn't support random access, but for feeds and audit logs, sequential access is all you need.

### Keyset pagination

Similar to cursors but exposes the key directly:

```
GET /users?after_id=789&limit=20
```

Simpler to implement and debug than opaque cursors; trade-off is exposing internal IDs.

## Filtering, Sorting, and Searching

Use query parameters for filtering:

```
GET /orders?status=pending&customer_id=user123
GET /products?min_price=100&max_price=5000&category=electronics
```

Sorting via a dedicated parameter:

```
GET /orders?sort=created_at:desc
GET /orders?sort=-created_at        # minus prefix for descending
```

Full-text search as a separate `q` parameter:

```
GET /products?q=gaming+chair
```

## Response Envelope

Wrap responses in a consistent envelope so you can add metadata later without breaking existing clients:

```json
{
  "data": {
    "id": "user123",
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

For lists:

```json
{
  "data": [...],
  "pagination": { "next_cursor": "...", "has_more": true },
  "meta": { "request_id": "req_9f3k2mxp" }
}
```

## Idempotency Keys

For POST endpoints that trigger payments, emails, or other side effects, support an `Idempotency-Key` header. If a client retries a timed-out request, the server recognizes the key and returns the original response rather than double-processing:

```
POST /payments
Idempotency-Key: 7f3b9e2a-1234-4abc-8def-0987654321ab
Content-Type: application/json

{ "amount": 4999, "currency": "INR" }
```

Store the key and response in a fast store (Redis) keyed by `Idempotency-Key`, with an expiry window of 24–48 hours.

## Conclusion

Good REST API design is mostly about consistency and predictability: consistent naming, consistent error shapes, consistent pagination, and consistent versioning. The patterns here — plural resource names, semantic status codes, structured errors with `request_id`, URL versioning, and cursor pagination — are each battle-tested solutions to specific failure modes. Follow them from the start, and your API will be much easier to evolve and consume without surprises.
