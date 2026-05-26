---
layout: post
title: "CSS Flexbox Cheat Sheet: Every Property with Examples"
date: "2026-05-26 00:00:00 +0530"
slug: css-flexbox-cheat-sheet
description: "A complete CSS Flexbox reference with visual examples — every container and item property explained, with common layout patterns you'll use every day."
categories: ["wiki", "Programming"]
tags: ["css", "flexbox", "frontend", "cheatsheet", "layout", "web development", "responsive design", "html", "javascript"]
---

Flexbox transformed CSS layout from a collection of hacks into something that actually makes sense. It's the go-to tool for one-dimensional layouts — rows or columns — and it handles alignment, spacing, and wrapping in ways that used to require JavaScript. This is a reference you can return to; every property is here with a working example.

## The Two Roles: Container and Items

Flexbox works by designating one element as the **flex container** (where you put `display: flex`) and its direct children become **flex items**. Container properties control how items are laid out; item properties control individual item behavior.

```css
.container {
    display: flex; /* or display: inline-flex */
}
```

```html
<div class="container">
    <div class="item">1</div>
    <div class="item">2</div>
    <div class="item">3</div>
</div>
```

## Container Properties

### `flex-direction`

Sets the main axis — the direction items flow.

```css
.container { flex-direction: row; }            /* → default: left to right */
.container { flex-direction: row-reverse; }    /* ← right to left */
.container { flex-direction: column; }         /* ↓ top to bottom */
.container { flex-direction: column-reverse; } /* ↑ bottom to top */
```

### `flex-wrap`

Controls whether items wrap to a new line when they overflow the container.

```css
.container { flex-wrap: nowrap; }       /* default: all items in one line, may overflow */
.container { flex-wrap: wrap; }         /* items wrap to next line */
.container { flex-wrap: wrap-reverse; } /* wraps in reverse order */
```

### `flex-flow`

Shorthand for `flex-direction` + `flex-wrap`.

```css
.container { flex-flow: row wrap; }
.container { flex-flow: column nowrap; }
```

### `justify-content`

Aligns items along the **main axis** (horizontal for row, vertical for column).

```css
.container { justify-content: flex-start; }    /* items at start (default) */
.container { justify-content: flex-end; }      /* items at end */
.container { justify-content: center; }        /* items centered */
.container { justify-content: space-between; } /* equal gaps between items */
.container { justify-content: space-around; }  /* equal space around items */
.container { justify-content: space-evenly; }  /* equal space including edges */
```

`space-between` is the most useful for navigation bars and card grids:

```css
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
```

### `align-items`

Aligns items along the **cross axis** (vertical for row, horizontal for column).

```css
.container { align-items: stretch; }     /* items stretch to fill container height (default) */
.container { align-items: flex-start; }  /* items align to top */
.container { align-items: flex-end; }    /* items align to bottom */
.container { align-items: center; }      /* items vertically centered */
.container { align-items: baseline; }    /* items align by text baseline */
```

`align-items: center` + `justify-content: center` is the classic "center anything" trick:

```css
.centered {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}
```

### `align-content`

Controls spacing between **rows** when flex wraps. Only applies when `flex-wrap: wrap` and there are multiple rows.

```css
.container {
    flex-wrap: wrap;
    align-content: flex-start;   /* rows packed to top */
    align-content: flex-end;     /* rows packed to bottom */
    align-content: center;       /* rows centered */
    align-content: space-between;
    align-content: space-around;
    align-content: stretch;      /* rows stretch to fill (default) */
}
```

### `gap`

Sets spacing between flex items (does not add margin at the edges).

```css
.container {
    display: flex;
    gap: 16px;           /* same gap in both directions */
    gap: 16px 24px;      /* row-gap column-gap */
    row-gap: 16px;
    column-gap: 24px;
}
```

`gap` replaced the old hack of adding margin to items and then negative margin to the container. Use it.

## Item Properties

### `flex-grow`

How much an item grows relative to others when there's extra space. Default is `0` (don't grow).

```css
.item { flex-grow: 0; }  /* don't grow (default) */
.item { flex-grow: 1; }  /* grow to fill available space */

/* Two items — second gets twice the extra space */
.item-a { flex-grow: 1; }
.item-b { flex-grow: 2; }
```

### `flex-shrink`

How much an item shrinks when there's not enough space. Default is `1` (shrink equally).

```css
.item { flex-shrink: 1; }  /* shrink proportionally (default) */
.item { flex-shrink: 0; }  /* never shrink — maintain original size */
.item { flex-shrink: 2; }  /* shrink twice as fast as others */
```

### `flex-basis`

The initial size of an item before growing or shrinking.

```css
.item { flex-basis: auto; }    /* use item's natural size (default) */
.item { flex-basis: 200px; }   /* start at exactly 200px */
.item { flex-basis: 33.33%; }  /* start at 1/3 of container */
.item { flex-basis: 0; }       /* ignore content size — distribute purely by flex-grow */
```

### `flex` shorthand

`flex: grow shrink basis` — use this instead of the individual properties.

```css
.item { flex: 0 1 auto; }  /* default: don't grow, can shrink, auto basis */
.item { flex: 1; }          /* shorthand for flex: 1 1 0 — grow equally, basis 0 */
.item { flex: none; }       /* flex: 0 0 auto — fixed size, don't grow or shrink */
.item { flex: auto; }       /* flex: 1 1 auto — grow and shrink based on content */
```

`flex: 1` on all items gives equal widths:

```css
.tab { flex: 1; }  /* all tabs are equal width regardless of text length */
```

### `order`

Changes the visual order without changing HTML source order. Default is `0`.

```css
.first  { order: -1; }  /* comes before order: 0 items */
.last   { order: 1; }   /* comes after */
.normal { order: 0; }   /* default */
```

### `align-self`

Overrides `align-items` for a single item.

```css
.item { align-self: auto; }        /* inherit from container (default) */
.item { align-self: flex-start; }
.item { align-self: flex-end; }
.item { align-self: center; }
.item { align-self: stretch; }
```

## Common Patterns

### Horizontal nav with logo left, links right

```css
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    height: 64px;
}
```

### Card grid with equal-height cards

```css
.card-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
}

.card {
    flex: 1 1 280px;   /* grow, shrink, minimum 280px wide */
    display: flex;
    flex-direction: column;
}

.card-body {
    flex: 1;  /* pushes footer to bottom of card */
}
```

### Sticky footer layout

```css
body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

main {
    flex: 1;  /* grows to push footer down */
}
```

### Vertically centered hero

```css
.hero {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    text-align: center;
}
```

### Media object (image left, text right)

```css
.media {
    display: flex;
    gap: 16px;
    align-items: flex-start;
}

.media-image {
    flex-shrink: 0;  /* don't let the image shrink */
    width: 64px;
}

.media-body {
    flex: 1;
}
```

## Conclusion

Flexbox excels at one-dimensional layouts — either a row or a column — with alignment and spacing that used to require careful margin math. The properties you'll use constantly are `display: flex`, `flex-direction`, `justify-content`, `align-items`, `gap`, and `flex: 1` on items. For two-dimensional layouts (rows and columns simultaneously), reach for CSS Grid instead.
