---
layout: post
title: "Next.js App Router vs Pages Router: What Changed and Why"
date: "2026-05-26 00:00:00 +0530"
slug: nextjs-app-router-vs-pages-router
description: "A practical comparison of Next.js App Router and Pages Router — file conventions, data fetching, layouts, server components, and when to migrate."
categories: ["Programming", "wiki"]
tags: ["nextjs", "react", "app router", "pages router", "frontend", "javascript", "ssr", "static site", "comparison"]
---

Next.js 13 introduced the App Router as a new way to build applications, coexisting with the Pages Router that had been the foundation since Next.js was created. By Next.js 14 and 15, the App Router became the recommended default. If you've been building with Pages Router and are wondering what actually changed — and whether the migration is worth it — this is the practical comparison you need.

## Two Directories, Two Paradigms

The most visible difference is directory structure:

**Pages Router:**
```
pages/
├── index.tsx          → route: /
├── about.tsx          → route: /about
├── blog/
│   ├── index.tsx      → route: /blog
│   └── [slug].tsx     → route: /blog/:slug
├── _app.tsx           → global layout wrapper
└── _document.tsx      → HTML document customization
```

**App Router:**
```
app/
├── page.tsx           → route: /
├── layout.tsx         → root layout (replaces _app.tsx)
├── about/
│   └── page.tsx       → route: /about
└── blog/
    ├── page.tsx       → route: /blog
    └── [slug]/
        └── page.tsx   → route: /blog/:slug
```

In the App Router, routes are defined by folders, and the file named `page.tsx` inside that folder is what renders. This adds more files per route, but also unlocks co-location of components, tests, and utilities next to the routes that use them.

## Server Components vs Client Components

This is the biggest conceptual shift. In the App Router, **every component is a React Server Component (RSC) by default.** Server Components run on the server, have no client-side JavaScript, and can directly `await` data without exposing API keys or database credentials.

```tsx
// app/blog/[slug]/page.tsx — Server Component by default
// This runs on the server — no "use client" needed

async function BlogPost({ params }: { params: { slug: string } }) {
    // Direct DB access, no API layer needed
    const post = await db.query(
        'SELECT * FROM posts WHERE slug = $1',
        [params.slug]
    );

    return (
        <article>
            <h1>{post.title}</h1>
            <p>{post.content}</p>
        </article>
    );
}

export default BlogPost;
```

To use hooks, event handlers, or browser APIs, you must opt in to client-side rendering with `"use client"` at the top of the file:

```tsx
'use client';

import { useState } from 'react';

export function LikeButton({ postId }: { postId: string }) {
    const [liked, setLiked] = useState(false);

    return (
        <button onClick={() => setLiked(l => !l)}>
            {liked ? '❤️' : '🤍'} Like
        </button>
    );
}
```

The pattern that works well: keep Server Components for data-heavy, read-only rendering; push `"use client"` to the smallest interactive leaf components.

## Data Fetching: Then and Now

In the Pages Router, you chose a data fetching strategy per page:

```tsx
// pages/blog/[slug].tsx — Pages Router
export async function getStaticProps({ params }) {
    const post = await fetchPost(params.slug);
    return { props: { post }, revalidate: 60 };
}

export async function getStaticPaths() {
    const slugs = await fetchAllSlugs();
    return { paths: slugs.map(s => ({ params: { slug: s } })), fallback: 'blocking' };
}

export default function BlogPost({ post }) {
    return <article>{post.content}</article>;
}
```

In the App Router, you just `await` inside async Server Components. The equivalent:

```tsx
// app/blog/[slug]/page.tsx — App Router
import { notFound } from 'next/navigation';

export async function generateStaticParams() {
    const slugs = await fetchAllSlugs();
    return slugs.map(slug => ({ slug }));
}

export default async function BlogPost({ params }: { params: { slug: string } }) {
    const post = await fetchPost(params.slug);
    if (!post) notFound();
    return <article>{post.content}</article>;
}
```

To control caching, you use `fetch` options or Next.js's `unstable_cache`:

```tsx
// Cached for 60 seconds (like revalidate: 60)
const post = await fetch(`/api/posts/${slug}`, {
    next: { revalidate: 60 }
}).then(r => r.json());

// Never cached
const data = await fetch('/api/live', { cache: 'no-store' });
```

## Layouts

Pages Router layouts require wrapping in `_app.tsx`:

```tsx
// pages/_app.tsx
export default function App({ Component, pageProps }) {
    return (
        <Layout>
            <Component {...pageProps} />
        </Layout>
    );
}
```

App Router layouts are hierarchical — each folder can have its own `layout.tsx`, and they nest automatically:

```tsx
// app/layout.tsx — root layout, wraps everything
export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body>
                <Header />
                {children}
                <Footer />
            </body>
        </html>
    );
}

// app/dashboard/layout.tsx — only wraps /dashboard/* routes
export default function DashboardLayout({ children }) {
    return (
        <div className="dashboard">
            <Sidebar />
            <main>{children}</main>
        </div>
    );
}
```

Layouts persist across navigation — the `DashboardLayout` doesn't re-mount when you navigate between `/dashboard/settings` and `/dashboard/profile`. This was painful to implement in Pages Router.

## Special Files

App Router introduces a richer set of file conventions per route segment:

| File | Purpose |
|------|---------|
| `page.tsx` | The route's UI |
| `layout.tsx` | Persistent wrapper, doesn't re-render on navigation |
| `loading.tsx` | Shown while page data loads (React Suspense) |
| `error.tsx` | Error boundary for this segment |
| `not-found.tsx` | Shown when `notFound()` is called |
| `route.ts` | API route handler (replaces `pages/api/`) |

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
    return <div className="spinner">Loading dashboard...</div>;
}
```

The loading UI streams automatically while the page's async data resolves — no manual Suspense boundaries needed.

## API Routes

Pages Router put API routes at `pages/api/`:

```tsx
// pages/api/users.ts
export default function handler(req, res) {
    if (req.method === 'GET') {
        res.json({ users: [] });
    }
}
```

App Router uses Route Handlers at `app/api/users/route.ts`:

```tsx
// app/api/users/route.ts
export async function GET(request: Request) {
    const users = await db.getUsers();
    return Response.json(users);
}

export async function POST(request: Request) {
    const body = await request.json();
    const user = await db.createUser(body);
    return Response.json(user, { status: 201 });
}
```

Route Handlers use the standard Web `Request`/`Response` API — no Next.js-specific wrappers.

## When to Use Which

**Stay on Pages Router if:**
- You have a large existing codebase and migration cost is high
- Your team is unfamiliar with React Server Components
- You rely heavily on `getServerSideProps` / `getStaticProps` patterns that work well

**Use App Router for new projects because:**
- Server Components reduce client-side JavaScript significantly
- Nested layouts solve a real problem cleanly
- Streaming and Suspense are first-class
- It's the direction Next.js is investing in

You can run both routers simultaneously during migration — files in `pages/` and `app/` coexist.

## Conclusion

The App Router isn't just a different directory — it's a fundamentally different mental model built on React Server Components. Data fetching moves from special functions (`getStaticProps`) to `async/await` directly in components; layouts nest hierarchically without wrapper component gymnastics; and interactive code is an explicit opt-in with `"use client"`. For new Next.js projects, App Router is the clear choice. For existing projects, migration can be incremental since both routers can coexist.
