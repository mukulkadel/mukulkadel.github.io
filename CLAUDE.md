# CLAUDE.md — mukulkadel.github.io

Personal blog and portfolio for Mukul Kadel, hosted at **mukulkadel.com** via GitHub Pages.

## Stack

- **Jekyll 4.3** with kramdown (GFM input) and `jekyll-paginate-v2`
- **Syntax highlighting**: highlight.js (CDN, loaded in `_layouts/default.html`) — `highlighter: none` in `_config.yml`, so do NOT use Jekyll's built-in Rouge highlighter
- **Diagrams**: mermaid.js (CDN)
- **Deployment**: GitHub Actions → GitHub Pages (push to `main` triggers build)

## Project layout

```
_config.yml          Site-wide settings (GA, AdSense, pagination, plugins)
_layouts/            default, home, page, post, app
_includes/           head.html, header.html, footer.html, post-card.html
_posts/              Blog posts (Markdown)
_pages/              Static pages as a Jekyll collection (permalink /:slug/)
assets/css/main.css  All styles — single file, CSS custom properties, dark mode via prefers-color-scheme
assets/js/main.js    Reading progress bar, copy-code buttons, highlight.js + mermaid init
tools/               Self-contained static mini-apps (e.g. image-to-base64)
```

## Post front matter

Every post must have:

```yaml
---
layout: post
title: "Human-readable title"
date: "YYYY-MM-DD 00:00:00 +0530"
slug: url-slug-here           # controls the permalink (/:slug/)
description: "SEO description used by jekyll-seo-tag"
categories: ["Cat1", "Cat2"]  # shown as chips in the post header
tags: ["tag1", "tag2"]        # shown at the bottom of the post
---
```

File naming: `_posts/YYYY-MM-DD-slug.md` — the date in the filename must match `date:`.

## Code blocks

Use fenced code blocks with the language identifier. Mermaid diagrams use the `mermaid` language identifier. Do NOT wrap mermaid code in a nested code block.

````markdown
```bash
brew install go
```

```mermaid
graph TD
  A --> B
```
````

## Styles

- CSS lives entirely in `assets/css/main.css` — no preprocessor, no separate partials.
- Design tokens are CSS custom properties on `:root`; dark-mode values override them in `@media (prefers-color-scheme: dark)`.
- Max content width: `--max-width: 860px`.
- Monospace font: JetBrains Mono (Google Fonts).
- Do not add inline `<style>` blocks to posts or pages — use existing utility classes or extend `main.css`.

## Running locally

```bash
bundle exec jekyll serve --livereload
```

The site builds to `_site/`. That directory is git-ignored; never edit files inside it.

## Deployment

Push to `main` → GitHub Actions runs `bundle exec jekyll build` → deploys to GitHub Pages. No manual deploy step needed.

## Analytics & AdSense

IDs live in `_config.yml` (`google_analytics`, `google_adsense_client`). They are injected into every page via `_includes/head.html` and into post bodies via `_layouts/post.html`. Do not hard-code IDs elsewhere.

## Adding content

- **New post**: create `_posts/YYYY-MM-DD-slug.md` with required front matter above.
- **New page**: create `_pages/name.md` with `layout: page`, `title:`, `permalink:`, and `description:`.
- **New mini-app**: drop static build output into `tools/your-app/` and add a card in `_pages/apps.md`.

## Blogging patterns

### Posting cadence

Posts arrive in bursts separated by ~4-month gaps, not at a steady cadence. Observed active windows: Aug–Sep 2023, Jan–Feb 2024, Jun 2024, Oct 2024. Multiple posts on the same date is normal. The last post is from Oct 2024; there is a long gap since then.

### Content categories (with typical category/tag usage)

| Type | Description | Common categories |
|---|---|---|
| **Tutorial / How-to** | Command walkthrough with real terminal output | `Programming`, `Tutorials`, `unix`, `git` |
| **Cheat sheet / Reference** | Organized lists of properties or commands with code examples | `wiki`, or topic-specific |
| **Explainer / Wiki** | Conceptual deep-dive on a technology or system concept | `wiki` |
| **Event coverage** | News recap with images (e.g. WWDC) | `Technology News`, `Tech Reviews`, `Product Announcements` |
| **Book / philosophy review** | Personal reflection with Amazon affiliate links | `Book`, `Review` |

Many early posts were left as `categories: ["Uncategorized"]` during the WordPress migration. New posts should use a specific category.

### Categories vs tags

- **Categories** (1–4): broad topic buckets shown as chips on the post — e.g. `Programming`, `wiki`, `Book`, `unix`, `SQL`.
- **Tags** (3–12): granular SEO keywords — e.g. `["cheatsheet", "nginx", "proxy", "tutorial"]`. Tags can be numerous; err toward more rather than fewer.

---

## Writing style

### Post structure

1. **Opening paragraph** — 2–4 sentences introducing the topic in plain language, no heading before it. Sets the "why this matters" before diving in.
2. **Body sections** — `##` for major sections, `###` for sub-sections. Never uses `#` inside post content (the title is already `h1`).
3. **Closing section** — almost every post ends with a `## Conclusion` (or `#### Conclusion:` in shorter posts) that summarizes key takeaways in 2–5 sentences.

### Tone and voice

- Conversational and direct — uses "we'll", "Let's", "you can", "I" freely.
- Practical over theoretical: explains *what* and *how*, then briefly *why*. Avoids academic depth.
- Approachable analogies for hard concepts (e.g. "CPU throttling is like a marathon runner slowing down to catch their breath").
- Confident but not condescending — assumes the reader is a developer, not a beginner.

### Inline formatting

- Backtick inline code for all commands, flags, filenames, function names, config keys, and technical terms the first time they appear.
- **Bold** (`**term**`) for key concepts inside list items or when defining a term.
- *Italics* used sparingly — mostly for book titles or soft emphasis.

### Code examples

- Every technical post has at least one fenced code block.
- Bash examples show the `$` prompt and include realistic output below the command — not just the command alone.
- Code is self-contained and runnable; no placeholder logic like `// TODO`.
- Language identifier always specified (`bash`, `python`, `sql`, `nginx`, `javascript`, etc.).

### Lists

- **Bullet lists** for feature enumerations, property references, and non-sequential items.
- **Numbered lists** for step-by-step procedures where order matters.
- List items are typically 1–2 lines; avoid nesting beyond one level.

### Resource links

Book review and reference posts end with affiliate/resource links (Amazon India, Amazon, YouTube, online tutorials) as plain Markdown links, not in a special callout block.

### Images

Local images live in `assets/images/` and are referenced with an absolute path: `![alt text](/assets/images/filename.jpg)`. Images are used sparingly — only for event/news posts or when a screenshot genuinely adds value.

### Description field

Should be a complete, standalone sentence (not truncated with "…"). Used by `jekyll-seo-tag` for `<meta name="description">` — aim for 120–155 characters.

---

## What to avoid

- Do not enable Jekyll's built-in `highlighter` — highlight.js handles it client-side.
- Do not create per-category or per-tag page files; the categories page (`_pages/categories.md`) aggregates everything with Liquid.
- Do not commit anything inside `_site/`, `vendor/`, `.bundle/`, `.jekyll-cache/`, or `.venv/`.
- Do not add `published: false` drafts to `_posts/` — use a separate `_drafts/` folder if needed.
