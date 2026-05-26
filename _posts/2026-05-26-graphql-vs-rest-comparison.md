---
layout: post
title: "GraphQL vs REST: A Practical Comparison"
date: "2026-05-26 00:00:00 +0530"
slug: graphql-vs-rest-comparison
description: "A practical look at GraphQL vs REST — what each is good at, where each struggles, and how to choose between them for your next API project."
categories: ["wiki", "Programming"]
tags: ["graphql", "rest", "api", "backend", "queries", "mutations", "json", "comparison", "performance", "schema"]
---

GraphQL was hyped as the REST killer when Facebook open-sourced it in 2015. A decade later, REST is still alive and thriving, but GraphQL has found a genuine niche where it genuinely shines. The question isn't which one is better — it's which one fits your situation.

## How REST Works

REST treats your API as a collection of resources, each with its own URL. You use standard HTTP methods to act on those resources:

```bash
# Get a user
$ curl https://api.example.com/users/123
{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com",
  "avatar_url": "...",
  "bio": "...",
  "follower_count": 4201,
  "plan": "pro"
}

# Get that user's posts
$ curl https://api.example.com/users/123/posts
[
  {"id": 1, "title": "Hello world", "created_at": "..."},
  {"id": 2, "title": "REST vs GraphQL", "created_at": "..."}
]
```

Two endpoints, two round trips. If you want posts with author info, you might need three trips: one for the post, one for the author, one for the comments. This is the **N+1 problem** REST is famous for.

## How GraphQL Works

GraphQL uses a single endpoint (`POST /graphql`) and a query language to describe exactly what data you want:

```graphql
query GetUserWithPosts {
  user(id: "123") {
    name
    email
    posts(first: 5) {
      title
      publishedAt
      commentCount
    }
  }
}
```

The server responds with exactly that shape — no more, no less:

```json
{
  "data": {
    "user": {
      "name": "Alice",
      "email": "alice@example.com",
      "posts": [
        { "title": "Hello world", "publishedAt": "2024-01-10", "commentCount": 12 },
        { "title": "REST vs GraphQL", "publishedAt": "2024-03-02", "commentCount": 47 }
      ]
    }
  }
}
```

One request. Exactly the fields you asked for.

## The Over-Fetching and Under-Fetching Problem

REST endpoints return whatever the server decided to include. Your mobile app might only need `name` and `avatar_url`, but the endpoint returns 15 fields. That's **over-fetching** — wasted bandwidth on constrained connections.

**Under-fetching** is the opposite: you need data from multiple resources but each endpoint only gives you part of it, forcing multiple round trips.

GraphQL solves both: ask for what you need, get exactly that, in one request.

```graphql
# Mobile app only needs the basics
query MobileProfile {
  user(id: "123") {
    name
    avatarUrl
  }
}

# Admin dashboard needs everything
query AdminProfile {
  user(id: "123") {
    name
    email
    plan
    followerCount
    bio
    createdAt
    lastLoginAt
  }
}
```

Both queries hit the same schema. No new endpoints needed.

## Setting Up a Simple GraphQL Server

Using Python with Strawberry:

```python
import strawberry
from typing import Optional

@strawberry.type
class User:
    id: int
    name: str
    email: str

@strawberry.type
class Post:
    id: int
    title: str
    author: User

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        return db.get_user(id)

    @strawberry.field
    def posts(self) -> list[Post]:
        return db.get_posts()

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_post(self, title: str, author_id: int) -> Post:
        return db.create_post(title=title, author_id=author_id)

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

The schema is the contract. Any client can introspect it to discover what's available:

```bash
$ curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

## Where GraphQL Genuinely Wins

**1. Multiple clients with different data needs.** Web, iOS, and Android apps typically need different subsets of data. With REST, you either bloat the response or maintain separate endpoints per client. GraphQL lets each client query exactly what it needs.

**2. Rapid product iteration.** Adding a new field to a GraphQL schema is non-breaking — old clients keep working. With REST, you often version entire endpoints or add optional fields that clients have to ignore.

**3. Developer experience.** The introspection system enables excellent tooling: auto-complete in GraphiQL, type-safe query generation, schema validation in CI. Developers know exactly what's available before writing a line of code.

**4. Nested data relationships.** Social graphs, dashboards, and content management systems naturally have deeply nested data. GraphQL's nested query syntax maps directly onto that.

## Where REST Genuinely Wins

**1. Caching.** HTTP caching is built around URLs. Every REST response at `/posts/123` can be cached by CDN, browser, or proxy automatically. GraphQL uses POST requests to a single URL — CDN caching is effectively impossible without additional tooling (persisted queries, GET-based caching).

```bash
# REST: CDN caches this automatically
$ curl https://api.example.com/posts/123
# Response cached at edge for 60 seconds

# GraphQL: POST body varies per query — CDN can't cache
$ curl -X POST https://api.example.com/graphql \
  -d '{"query": "{ post(id: 123) { title } }"}'
```

**2. File uploads.** REST handles multipart form uploads naturally. GraphQL's spec has no standard for binary uploads — you need workarounds like the `graphql-multipart-request-spec` or a separate REST endpoint.

**3. Simple CRUD APIs.** A basic API with 5 resources and standard operations is much simpler to build and understand with REST. GraphQL's schema definition, resolvers, and DataLoader patterns add overhead that's not justified.

**4. Interoperability.** REST over HTTP is universal — every language, framework, and tool understands it. GraphQL requires a client library or knowledge of the query syntax.

## The N+1 Problem (It Exists in GraphQL Too)

GraphQL solves the client-side N+1 problem but introduces a server-side one. A query like this:

```graphql
query {
  posts {
    title
    author {
      name
    }
  }
}
```

Without batching, for 100 posts this fires 101 database queries: 1 for posts, then 1 per post to fetch the author. The solution is **DataLoader**, which batches and deduplicates database calls:

```python
from strawberry.dataloader import DataLoader

async def load_users(ids: list[int]) -> list[User]:
    users = await db.fetch_all("SELECT * FROM users WHERE id = ANY($1)", ids)
    return [users_by_id.get(id) for id in ids]

user_loader = DataLoader(load_fn=load_users)
```

Now the 100 author lookups become a single batched query. But this complexity doesn't exist in REST — it's a GraphQL-specific problem you have to solve.

## Choosing Between Them

**Use REST when:**
- You're building a public API (simpler for consumers)
- CDN caching is important
- Your API is simple CRUD
- You need file upload support
- You want maximum interoperability

**Use GraphQL when:**
- You have multiple clients (web/iOS/Android) with different data needs
- Your data model is graph-like with many relationships
- You're building an internal API and developer experience matters
- You need to iterate quickly without versioning

## Conclusion

REST's simplicity, cacheability, and universal support make it the right default for most APIs — especially public-facing ones. GraphQL earns its complexity when you have heterogeneous clients or deeply relational data that causes painful over-fetching and under-fetching with REST. Neither is universally better; the best teams use REST for external APIs and selectively adopt GraphQL for internal services where its flexibility pays off.
