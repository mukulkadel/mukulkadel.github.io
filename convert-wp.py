#!/usr/bin/env python3
"""Convert WordPress JSON dump to Jekyll Markdown posts and pages.

Usage:
  python3 convert-wp.py

Requires: pip install beautifulsoup4
"""

import html
import json
import os
import re
import sys
import urllib.request
import urllib.parse
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ImportError:
    print("Error: beautifulsoup4 not found. Run: pip3 install beautifulsoup4")
    sys.exit(1)

# ── Load data ──────────────────────────────────────────────────────────────────

DUMP_DIR = Path("wordpress-dump")
POSTS_OUT = Path("_posts")
PAGES_OUT = Path("_pages")
IMAGES_OUT = Path("assets/images")

with open(DUMP_DIR / "posts.json") as f:
    posts = json.load(f)
with open(DUMP_DIR / "pages.json") as f:
    pages = json.load(f)
with open(DUMP_DIR / "categories.json") as f:
    categories = json.load(f)
with open(DUMP_DIR / "tags.json") as f:
    tags = json.load(f)
with open(DUMP_DIR / "media.json") as f:
    media = json.load(f)

cat_map = {c["id"]: c for c in categories}
tag_map = {t["id"]: t for t in tags}
media_map = {m["id"]: m for m in media}

POSTS_OUT.mkdir(exist_ok=True)
PAGES_OUT.mkdir(exist_ok=True)
IMAGES_OUT.mkdir(parents=True, exist_ok=True)

# ── Media URL helpers ──────────────────────────────────────────────────────────

WP_UPLOAD_BASE = "https://mukulkadel.com/wp-content/uploads/"

images_to_download: list[tuple[str, str]] = []  # (url, local_path)


def local_image_path(url: str) -> str:
    """Convert a WP upload URL to a local /assets/images/ path."""
    # Strip query params and size suffixes like -1024x572
    parsed = urllib.parse.urlparse(url)
    filename = Path(parsed.path).name
    # Remove size suffix e.g. macos-1024x576.jpg -> macos.jpg
    filename = re.sub(r"-\d+x\d+(\.[a-zA-Z]+)$", r"\1", filename)
    # Remove -scaled suffix
    filename = re.sub(r"-scaled(\.[a-zA-Z]+)$", r"\1", filename)
    return f"/assets/images/{filename}"


def normalize_image_url(url: str) -> str:
    """Replace WP upload URLs with local paths and queue for download."""
    if not url:
        return url
    if WP_UPLOAD_BASE in url:
        local = local_image_path(url)
        # Queue highest-res version for download
        images_to_download.append((url, local))
        return local
    return url

# ── Code Block Pro extractor ───────────────────────────────────────────────────

def extract_code_blocks(soup: BeautifulSoup) -> dict[str, tuple[str, str]]:
    """Replace Code Block Pro divs with markers, return mapping to (lang, code)."""
    replacements: dict[str, tuple[str, str]] = {}
    blocks = soup.find_all("div", class_=lambda c: c and "wp-block-kevinbatdorf-code-block-pro" in c)
    for i, div in enumerate(blocks):
        # Language: first direct child span with background-color in style and no role
        language = ""
        for span in div.children:
            if not isinstance(span, Tag):
                continue
            style = span.get("style", "")
            if "background-color" in style and not span.get("role"):
                language = span.get_text(strip=True)
                break

        # Code: span with data-code attribute (the copy-button's hidden data)
        code_span = div.find("span", attrs={"data-code": True})
        if code_span:
            raw_code = html.unescape(code_span["data-code"])
        else:
            # Fallback: pre > code text
            pre = div.find("pre")
            if pre:
                code_el = pre.find("code")
                raw_code = code_el.get_text() if code_el else pre.get_text()
            else:
                raw_code = ""

        marker = f"__CODE_BLOCK_{i}__"
        replacements[marker] = (language, raw_code)
        div.replace_with(marker)

    return replacements


# ── HTML → Markdown converter ─────────────────────────────────────────────────

def children_to_md(node, indent: int = 0) -> str:
    return "".join(node_to_md(c, indent) for c in node.children)


def node_to_md(node, indent: int = 0) -> str:
    if isinstance(node, NavigableString):
        text = str(node)
        if text == "\n":
            return ""
        return text

    if not isinstance(node, Tag):
        return ""

    tag = node.name

    # ── Block headings ──
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        inner = children_to_md(node).strip()
        inner = re.sub(r"\*+", "", inner)  # strip bold inside headings
        return f"\n{'#' * level} {inner}\n"

    # ── Paragraph ──
    if tag == "p":
        inner = children_to_md(node).strip()
        if not inner:
            return "\n"
        return f"\n{inner}\n"

    # ── Lists ──
    if tag == "ul":
        items = []
        for li in node.find_all("li", recursive=False):
            content = children_to_md(li).strip()
            content = re.sub(r"\n+", " ", content)
            items.append(f"{'  ' * indent}- {content}")
        return "\n" + "\n".join(items) + "\n"

    if tag == "ol":
        items = []
        for i, li in enumerate(node.find_all("li", recursive=False), 1):
            content = children_to_md(li).strip()
            content = re.sub(r"\n+", " ", content)
            items.append(f"{'  ' * indent}{i}. {content}")
        return "\n" + "\n".join(items) + "\n"

    if tag == "li":
        return children_to_md(node)

    # ── Inline formatting ──
    if tag in ("strong", "b"):
        inner = children_to_md(node).strip()
        if not inner:
            return ""
        return f"**{inner}**"

    if tag in ("em", "i"):
        inner = children_to_md(node).strip()
        if not inner:
            return ""
        return f"*{inner}*"

    if tag == "s" or tag == "del":
        inner = children_to_md(node).strip()
        return f"~~{inner}~~" if inner else ""

    # ── Inline code ──
    if tag == "code" and node.parent and node.parent.name != "pre":
        return f"`{node.get_text()}`"

    # ── Pre / fenced code ──
    if tag == "pre":
        code_el = node.find("code")
        if code_el:
            classes = code_el.get("class", [])
            lang_class = next((c for c in classes if c.startswith("language-")), "")
            lang = lang_class.replace("language-", "") if lang_class else ""
            return f"\n```{lang}\n{code_el.get_text()}\n```\n"
        return f"\n```\n{node.get_text()}\n```\n"

    # ── Links ──
    if tag == "a":
        href = node.get("href", "")
        inner = children_to_md(node).strip()
        if not inner:
            inner = href
        return f"[{inner}]({href})"

    # ── Images ──
    if tag == "img":
        src = node.get("src", "")
        # Prefer src over srcset
        alt = node.get("alt", "")
        src = normalize_image_url(src)
        return f"![{alt}]({src})"

    # ── Figure / figcaption ──
    if tag == "figure":
        inner = children_to_md(node).strip()
        return f"\n{inner}\n"

    if tag == "figcaption":
        text = node.get_text().strip()
        return f"\n*{text}*\n" if text else ""

    # ── Blockquote ──
    if tag == "blockquote":
        inner = children_to_md(node).strip()
        lines = inner.splitlines()
        return "\n" + "\n".join(f"> {l}" for l in lines) + "\n"

    # ── Table ──
    if tag == "table":
        return convert_table(node)

    # ── Horizontal rule ──
    if tag == "hr":
        return "\n---\n"

    # ── Line break ──
    if tag == "br":
        return "  \n"

    # ── Ignored tags ──
    if tag in ("script", "style", "noscript", "svg", "button", "input"):
        return ""

    # ── Pass-through containers ──
    return children_to_md(node, indent)


def convert_table(table: Tag) -> str:
    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        rows.append(cells)
    if not rows:
        return ""
    max_cols = max(len(r) for r in rows)
    # Pad rows
    rows = [r + [""] * (max_cols - len(r)) for r in rows]
    header = "| " + " | ".join(rows[0]) + " |"
    sep = "| " + " | ".join(["---"] * max_cols) + " |"
    result = ["\n", header, sep]
    for row in rows[1:]:
        result.append("| " + " | ".join(row) + " |")
    return "\n".join(result) + "\n"


# ── Convert code block markers back to fenced blocks ─────────────────────────

LANG_ALIASES = {
    "bash": "bash",
    "shell": "bash",
    "sh": "bash",
    "go": "go",
    "golang": "go",
    "python": "python",
    "py": "python",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "sql": "sql",
    "nginx": "nginx",
    "yaml": "yaml",
    "yml": "yaml",
    "json": "json",
    "markdown": "markdown",
    "md": "markdown",
    "mermaid": "mermaid",
    "html": "html",
    "css": "css",
    "text": "text",
    "plaintext": "text",
}


def make_fenced_block(language: str, code: str) -> str:
    lang_key = language.lower().strip()
    fence_lang = LANG_ALIASES.get(lang_key, lang_key)
    # Use more backticks than the maximum run inside the code
    max_run = max((len(m.group()) for m in re.finditer(r"`+", code)), default=0)
    fence = "`" * max(3, max_run + 1)
    return f"\n{fence}{fence_lang}\n{code}\n{fence}\n"


# ── Front matter builder ──────────────────────────────────────────────────────

def yaml_str(value: str) -> str:
    """Emit a YAML string, quoting if needed."""
    if not value:
        return '""'
    # Use double-quoted if special chars present
    if any(c in value for c in [':', '#', "'", '"', '[', ']', '{', '}', '&', '*', '!', '|', '>', '\n']):
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value


def build_front_matter(data: dict) -> str:
    lines = ["---"]
    for k, v in data.items():
        if isinstance(v, list):
            if v:
                items = ", ".join(f'"{i}"' for i in v)
                lines.append(f"{k}: [{items}]")
            else:
                lines.append(f"{k}: []")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, str):
            lines.append(f"{k}: {yaml_str(v)}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


# ── Convert a single post/page ────────────────────────────────────────────────

def convert_item(item: dict) -> tuple[str, str]:
    """Return (filename_stem, markdown_content)."""
    slug = item["slug"]
    date_str = item["date"][:10]  # YYYY-MM-DD
    title = html.unescape(item["title"]["rendered"])

    # SEO description (prefer Yoast, fall back to excerpt)
    yoast = item.get("yoast_head_json") or {}
    description = yoast.get("description", "")
    if not description:
        excerpt_html = (item.get("excerpt") or {}).get("rendered", "")
        if excerpt_html:
            description = BeautifulSoup(excerpt_html, "html.parser").get_text().strip()
    description = description.replace("\n", " ").strip()

    # Categories / tags
    post_cats = [cat_map[c]["name"] for c in item.get("categories", []) if c in cat_map]
    post_tags = [tag_map[t]["name"] for t in item.get("tags", []) if t in tag_map]

    # Convert content HTML
    content_html = item["content"]["rendered"]
    soup = BeautifulSoup(content_html, "html.parser")

    # Extract Code Block Pro blocks first
    code_blocks = extract_code_blocks(soup)

    # Convert remaining HTML to markdown
    md_body = children_to_md(soup)

    # Restore code blocks
    for marker, (language, code) in code_blocks.items():
        fenced = make_fenced_block(language, code)
        md_body = md_body.replace(marker, fenced)

    # Clean up: collapse 3+ blank lines to 2
    md_body = re.sub(r"\n{3,}", "\n\n", md_body.strip())

    # Front matter
    fm: dict = {
        "layout": "post" if item["type"] == "post" else "page",
        "title": title,
        "date": f"{date_str} 00:00:00 +0530",
        "slug": slug,
    }
    if description:
        fm["description"] = description
    if post_cats:
        fm["categories"] = post_cats
    if post_tags:
        fm["tags"] = post_tags

    return slug, f"{build_front_matter(fm)}\n\n{md_body}\n"


# ── Download media ────────────────────────────────────────────────────────────

def download_images():
    """Download queued images to assets/images/."""
    seen: set[str] = set()
    errors = []
    for url, local in images_to_download:
        dest = Path(local.lstrip("/"))
        if dest.name in seen:
            continue
        seen.add(dest.name)
        if dest.exists():
            print(f"  [skip] {dest.name} (already exists)")
            continue
        print(f"  [dl]   {url} → {dest}")
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; site-migration/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(r.read())
        except Exception as e:
            print(f"  [err]  {url}: {e}")
            errors.append((url, str(e)))
    return errors


# ── Run ───────────────────────────────────────────────────────────────────────

def main():
    # Convert posts
    print(f"Converting {len(posts)} posts...")
    for post in posts:
        if post["status"] != "publish":
            continue
        slug, content = convert_item(post)
        date_str = post["date"][:10]
        filename = POSTS_OUT / f"{date_str}-{slug}.md"
        filename.write_text(content, encoding="utf-8")
        print(f"  [post] {filename.name}")

    # Convert pages (skip WP meta pages)
    skip_slugs = {"blogs", "categories"}  # replaced by proper Jekyll pages
    print(f"\nConverting {len(pages)} pages...")
    for page in pages:
        if page["status"] != "publish":
            continue
        if page["slug"] in skip_slugs:
            print(f"  [skip] {page['slug']} (replaced by Jekyll page)")
            continue

        # image-to-base64 is now a native HTML tool, skip
        if page["slug"] == "image-to-base64-converter":
            print(f"  [skip] {page['slug']} (native HTML tool at /tools/image-to-base64/)")
            continue

        slug, content = convert_item(page)
        # Override layout for pages
        content = content.replace("\nlayout: post\n", "\nlayout: page\n")
        filename = PAGES_OUT / f"{slug}.md"
        filename.write_text(content, encoding="utf-8")
        print(f"  [page] {filename.name}")

    # Download images
    if images_to_download:
        print(f"\nDownloading {len(set(p for _, p in images_to_download))} images...")
        errors = download_images()
        if errors:
            print(f"\n  Warning: {len(errors)} image(s) failed to download.")
    else:
        print("\nNo images to download.")

    print("\nDone! Run `bundle exec jekyll serve` to preview.")


if __name__ == "__main__":
    main()
