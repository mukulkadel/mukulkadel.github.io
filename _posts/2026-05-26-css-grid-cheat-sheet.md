---
layout: post
title: "CSS Grid Cheat Sheet: Real Layouts with Examples"
date: "2026-05-26 00:00:00 +0530"
slug: css-grid-cheat-sheet
description: "A complete CSS Grid reference — grid-template-columns, grid-template-areas, auto-fill vs auto-fit, and real layouts like dashboards and card grids with working code."
categories: ["wiki", "Programming"]
tags: ["css", "css grid", "frontend", "layout", "cheatsheet", "web development", "responsive design", "html", "grid areas"]
---

CSS Grid solves the two-dimensional layout problem — think dashboards, magazine layouts, card grids, and page skeletons where you need to control both rows and columns simultaneously. Where Flexbox thinks in a single axis, Grid thinks in terms of a defined coordinate system. Once it clicks, you'll stop reaching for float hacks, negative margins, and JavaScript for layout work.

## Defining a Grid

Any element with `display: grid` becomes a grid container. Its direct children are grid items.

```css
.container {
    display: grid;
}
```

On its own this doesn't do much — you need to define the tracks.

## `grid-template-columns` and `grid-template-rows`

The most fundamental properties. They define the columns and rows of your grid.

```css
/* Three equal columns */
.grid { grid-template-columns: 200px 200px 200px; }

/* Three columns using fr (fraction unit) */
.grid { grid-template-columns: 1fr 1fr 1fr; }

/* Sidebar + main + aside layout */
.grid { grid-template-columns: 240px 1fr 200px; }

/* Three rows of specific heights */
.grid { grid-template-rows: 80px 1fr 60px; }
```

The `fr` unit is grid-specific — it means "take this fraction of the remaining available space after fixed-size tracks are placed."

### `repeat()`

Avoid repetition with `repeat()`:

```css
/* These are identical */
.grid { grid-template-columns: 1fr 1fr 1fr 1fr; }
.grid { grid-template-columns: repeat(4, 1fr); }

/* Mixed: sidebar + 3 equal content columns */
.grid { grid-template-columns: 200px repeat(3, 1fr); }
```

### `auto-fill` and `auto-fit`

These create as many columns as fit in the container — the key to responsive grids without media queries.

```css
/* auto-fill: creates tracks even if no items fill them */
.grid { grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); }

/* auto-fit: collapses empty tracks, stretching items to fill */
.grid { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
```

`minmax(250px, 1fr)` means each column is at least 250px wide, but grows to fill available space. This single line replaces most responsive grid media queries.

## `gap`

Spacing between grid tracks:

```css
.grid {
    gap: 24px;           /* same horizontal and vertical gap */
    gap: 16px 24px;      /* row-gap column-gap */
    row-gap: 16px;
    column-gap: 24px;
}
```

## Placing Items

By default, grid auto-places items into the next available cell. You can override this.

### `grid-column` and `grid-row`

Control which cells an item occupies using line numbers (lines start at 1):

```css
/* Span from column line 1 to line 3 (occupies 2 columns) */
.item { grid-column: 1 / 3; }

/* Shorthand for span */
.item { grid-column: span 2; }

/* Full-width item */
.item { grid-column: 1 / -1; }  /* -1 = last line */

/* Tall item — spans 2 rows */
.item { grid-row: 1 / 3; }
```

### `grid-area` with `grid-template-areas`

The most readable way to define complex layouts — name areas, then place items by name:

```css
.page {
    display: grid;
    grid-template-columns: 240px 1fr;
    grid-template-rows: 64px 1fr 48px;
    grid-template-areas:
        "header  header"
        "sidebar main"
        "footer  footer";
    min-height: 100vh;
}

.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

```html
<div class="page">
    <header class="header">Header</header>
    <nav class="sidebar">Sidebar</nav>
    <main class="main">Main</main>
    <footer class="footer">Footer</footer>
</div>
```

Each quoted string in `grid-template-areas` is a row. Repeated names span multiple columns. A `.` means an empty cell.

## Alignment

Grid has two alignment axes: inline (horizontal) and block (vertical).

### Container-level alignment

```css
/* Align all items horizontally within their cells */
.grid { justify-items: start | end | center | stretch; }

/* Align all items vertically within their cells */
.grid { align-items: start | end | center | stretch; }

/* When grid is smaller than container, align the whole grid */
.grid { justify-content: start | end | center | space-between | space-around | space-evenly; }
.grid { align-content: start | end | center | space-between | space-around | space-evenly; }
```

### Item-level alignment

Override container alignment for individual items:

```css
.item { justify-self: start | end | center | stretch; }
.item { align-self: start | end | center | stretch; }

/* place-self shorthand: align-self / justify-self */
.item { place-self: center; }
.item { place-self: start end; }
```

## `minmax()`

Defines a size range for a track:

```css
/* Column is at least 200px, at most 400px */
.grid { grid-template-columns: minmax(200px, 400px) 1fr; }

/* Column is at least 100px, grows to fill */
.grid { grid-template-columns: minmax(100px, 1fr) minmax(100px, 1fr); }
```

## `grid-auto-rows` and `grid-auto-columns`

Set the size of implicitly created tracks (rows or columns that appear because items overflow the defined grid):

```css
.grid {
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 200px;    /* every auto-created row is 200px tall */
}

/* More commonly, use minmax so content isn't clipped */
.grid { grid-auto-rows: minmax(120px, auto); }
```

## Real Layouts

### Responsive card grid (no media queries)

```css
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
}
```

Cards are at least 280px wide. The browser figures out how many columns fit. On a 1200px container you get 4 columns; on 600px you get 2.

### Dashboard layout

```css
.dashboard {
    display: grid;
    grid-template-columns: 260px 1fr;
    grid-template-rows: 64px 1fr;
    grid-template-areas:
        "sidebar topbar"
        "sidebar content";
    height: 100vh;
}

.sidebar { grid-area: sidebar; overflow-y: auto; }
.topbar  { grid-area: topbar; }
.content { grid-area: content; overflow-y: auto; }
```

### Holy grail layout

```css
.holy-grail {
    display: grid;
    grid-template:
        "header header header" 64px
        "nav    main   aside"  1fr
        "footer footer footer" 48px
        / 180px 1fr 180px;
    min-height: 100vh;
}
```

The `grid-template` shorthand combines `grid-template-areas`, `grid-template-rows`, and `grid-template-columns` in one declaration.

### Masonry-style grid (fixed columns, variable row height)

```css
.masonry {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 8px;          /* tiny row unit */
    gap: 16px 16px;
}

/* Each card specifies how many row units it spans based on its height */
.card { grid-row: span 30; }      /* short card */
.card-tall { grid-row: span 45; } /* taller card */
```

True CSS masonry requires JavaScript to measure content and set spans dynamically. CSS Grid Level 3 adds `masonry` as a `grid-template-rows` value, but browser support is still limited.

## Grid vs Flexbox: When to Use Which

| Use Grid when | Use Flexbox when |
|---------------|-----------------|
| Two-dimensional layout (rows + columns) | One-dimensional layout (row OR column) |
| Defining layout from the container | Letting content drive size |
| Named template areas | Simple alignment within a row |
| Complex page structure | Component-level layout (nav, card internals) |

In practice: use Grid for page-level structure, Flexbox for component internals. They compose well — a Grid item can itself be a flex container.

## Conclusion

CSS Grid's power is in `grid-template-columns`, `grid-template-areas`, and the `fr` unit. The `repeat(auto-fill, minmax())` pattern alone replaces most responsive grid media queries. For page-level structure — dashboards, app shells, editorial layouts — Grid gives you explicit control over both dimensions that no other CSS layout mechanism can match.
