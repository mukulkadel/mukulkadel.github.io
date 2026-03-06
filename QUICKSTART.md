# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Initial Setup

```bash
# Make setup script executable
chmod +x setup.sh run-migration.sh

# Run setup
./setup.sh
```

This will:
- Check Ruby installation
- Install Bundler
- Install all required gems

### 2. Migrate Your WordPress Content

```bash
# Run migration from your WordPress site
./run-migration.sh https://mukulkadel.com
```

This will:
- Download all posts from WordPress
- Convert HTML to Markdown
- Create Jekyll-compatible files
- Save to `_posts/` directory

### 3. Test Locally

```bash
# Start the local development server
bundle exec jekyll serve
```

Then open `http://localhost:4000` in your browser.

### 4. Review Your Content

Check that:
- ✓ All posts appear on `/blog/`
- ✓ Navigation works
- ✓ Formatting looks good
- ✓ No broken links

### 5. Deploy to GitHub Pages

```bash
# Add all changes
git add .

# Create commit
git commit -m "Migrate from WordPress to Jekyll"

# Push to GitHub
git push origin main
```

Your site will be live at `https://mukulkadel.github.io` in a few seconds!

---

## 📝 Adding New Posts

Create a new file in `_posts/` with this format: `YYYY-MM-DD-title.md`

```markdown
---
layout: post
title: Your Post Title
date: 2026-03-07 10:00:00 +0545
categories: [category1, category2]
tags: [tag1, tag2]
excerpt: "Brief description of your post"
---

# Your Content

Start writing your post in markdown format.

## Subheading

More content here...
```

---

## 🎨 Customizing Your Site

### Update Site Info

Edit `_config.yml`:
```yaml
title: Your Site Title
description: Your site description
author:
  name: Your Name
  email: your-email@example.com
```

### Change Colors

Edit `assets/css/style.css` and modify the CSS variables:
```css
:root {
    --color-primary: #2c3e50;      /* Main color */
    --color-secondary: #3498db;    /* Link color */
    --color-accent: #e74c3c;       /* Highlight color */
}
```

### Update Navigation Menu

Edit `_includes/header.html`:
```html
<a href="/your-page/" class="nav-link">Your Page</a>
```

---

## ❓ Common Questions

### Where do I put images?

Save images to `assets/images/` and reference them in posts:
```markdown
![Alt text](/assets/images/my-image.jpg)
```

### How do I create a new page?

Create a file in `_pages/`:
```markdown
---
layout: page
title: My New Page
permalink: /my-new-page/
---

Page content here...
```

### How do I add a category to posts?

Add to the front matter:
```yaml
categories: [category1, category2]
```

Posts with the same category will be grouped together.

### How do I use a custom domain?

1. Create a `CNAME` file in the root with your domain:
   ```
   mukulkadel.com
   ```

2. Update your domain's DNS settings to point to GitHub Pages

3. Enable HTTPS in repository Settings → Pages

### Why aren't my posts showing?

Check:
- File is in `_posts/` directory
- Filename follows format: `YYYY-MM-DD-slug.md`
- Front matter is valid YAML
- Date is not in the future

---

## 📚 Learn More

- **Jekyll Docs:** https://jekyllrb.com/docs/
- **GitHub Pages:** https://pages.github.com/
- **Markdown Guide:** https://www.markdownguide.org/
- **Migration Guide:** See `WORDPRESS_MIGRATION.md`

---

## 🆘 Troubleshooting

### Posts won't build?
```bash
bundle exec jekyll build --trace
```

### Need to reinstall gems?
```bash
rm Gemfile.lock
bundle install
```

### Want to start over?
```bash
rm -rf _site/ .jekyll-cache/
bundle exec jekyll serve
```

---

**Questions?** Check the full documentation in `README.md` and `WORDPRESS_MIGRATION.md`
