# 🚀 WordPress to Jekyll Migration - Complete Setup Guide

> **Your Jekyll site is ready!** This guide will walk you through the complete process of migrating your WordPress site to GitHub Pages.

**Date:** March 7, 2026  
**Site:** mukulkadel.github.io  
**WordPress Site:** mukulkadel.com

---

## 📋 What You're Getting

A complete Jekyll static site with:

✅ **Professional Design**
- Clean, modern, responsive layout
- Mobile-friendly design
- Fast loading times
- SEO optimized

✅ **Ready to Deploy**
- GitHub Pages configured
- Automatic HTTPS
- Free hosting
- Custom domain support

✅ **Automatic Migration Tools**
- Python script to export WordPress posts
- HTML to Markdown conversion
- Metadata preservation (dates, categories, tags)
- Shell scripts for easy execution

✅ **Complete Documentation**
- This guide
- QUICKSTART.md - 5-minute setup
- README.md - Full documentation
- WORDPRESS_MIGRATION.md - Detailed migration guide
- MIGRATION_CHECKLIST.md - Step-by-step checklist

---

## 🎯 Three-Step Process

### STEP 1️⃣: Setup Local Environment (5 min)

```bash
cd ~/Documents/Projects/Apps/mukulkadel/mukulkadel.github.io
./setup.sh
```

This will:
- ✓ Check Ruby installation
- ✓ Install Bundler gem manager
- ✓ Download Jekyll and dependencies
- ✓ Prepare your local environment

### STEP 2️⃣: Migrate WordPress Content (10 min)

```bash
./run-migration.sh https://mukulkadel.com
```

This will:
- ✓ Download all posts from WordPress REST API
- ✓ Convert HTML to Markdown
- ✓ Extract categories and tags
- ✓ Create Jekyll-compatible files
- ✓ Save to `_posts/` directory

### STEP 3️⃣: Deploy to GitHub Pages (2 min)

```bash
git add .
git commit -m "Migrate from WordPress to Jekyll"
git push origin main
```

That's it! Your site will be live at `https://mukulkadel.github.io`

---

## 📁 Your Project Structure

```
mukulkadel.github.io/
│
├── 📄 Configuration Files
│   ├── _config.yml          # Site configuration
│   ├── Gemfile              # Ruby dependencies
│   └── .gitignore           # Git ignore rules
│
├── 📝 Content
│   ├── index.md             # Home page
│   ├── _posts/              # Blog posts (converted from WordPress)
│   ├── _pages/              # Static pages (About, Contact, Projects)
│   └── blog/                # Blog listing page
│
├── 🎨 Design & Styling
│   ├── _layouts/            # Page templates
│   │   ├── default.html     # Main template
│   │   ├── post.html        # Blog post template
│   │   └── page.html        # Page template
│   ├── _includes/           # Reusable components
│   │   ├── header.html      # Navigation header
│   │   └── footer.html      # Footer
│   └── assets/              # Static files
│       ├── css/style.css    # Stylesheet (900+ lines)
│       ├── js/main.js       # JavaScript
│       └── images/          # Images (will populate during migration)
│
├── 🔄 Tools & Scripts
│   ├── setup.sh             # Initial setup script
│   ├── run-migration.sh     # Migration runner
│   └── migrate.py           # WordPress exporter (Python)
│
├── 🔗 SEO & Feeds
│   ├── sitemap.xml          # Search engine sitemap
│   ├── feed.xml             # RSS feed
│   └── robots.txt           # Search engine directives
│
└── 📚 Documentation
    ├── README.md                    # Complete reference
    ├── QUICKSTART.md               # 5-minute setup
    ├── WORDPRESS_MIGRATION.md      # Detailed migration guide
    └── MIGRATION_CHECKLIST.md      # Step-by-step checklist
```

---

## ⚙️ Detailed Setup Instructions

### Prerequisites

Before starting, ensure you have:

- **macOS/Linux:** (Windows also works with Git Bash)
- **Ruby 3.0+**: `ruby --version`
- **Git**: `git --version`
- **Text Editor**: VS Code, Sublime Text, or any editor
- **Terminal Access**: Basic command line knowledge helpful

### Step 1: Verify Ruby Installation

```bash
# Check Ruby version
ruby --version
# Should output: ruby 3.x.x ...

# If Ruby is not installed:
# macOS with Homebrew:
brew install ruby
```

### Step 2: Run Setup Script

```bash
# Navigate to your Jekyll directory
cd ~/Documents/Projects/Apps/mukulkadel/mukulkadel.github.io

# Run setup
./setup.sh
```

The script will:
1. Verify Ruby is installed
2. Install/verify Bundler
3. Install all gem dependencies (Jekyll, plugins, etc.)
4. Confirm everything is ready

**Expected output:**
```
✓ Ruby found: ruby 3.x.x ...
✓ Bundler found: Bundler version x.x.x
✓ Jekyll installed successfully
✅ Setup complete!
```

### Step 3: Test Local Server

Before migrating, test that Jekyll works:

```bash
# Start the development server
bundle exec jekyll serve

# Open browser to:
# http://localhost:4000
```

You should see:
- ✓ Homepage with welcome message
- ✓ Sample blog post
- ✓ Navigation menu at top
- ✓ Footer at bottom
- ✓ Mobile responsive design

Press `Ctrl+C` to stop the server.

---

## 🔄 WordPress Migration Steps

### Prerequisites for Migration

1. **WordPress REST API must be enabled** (default in WP 4.7+)

   Test it:
   ```bash
   curl -s https://mukulkadel.com/wp-json/wp/v2/posts | head -20
   ```

   If you see JSON data, REST API is enabled ✓

2. **Python 3.6+** must be installed

   ```bash
   python3 --version
   # Should show: Python 3.x.x
   ```

3. **requests library** for Python

   The migration script will auto-install if missing

### Run Migration

```bash
# Start migration
./run-migration.sh https://mukulkadel.com

# The script will:
# 1. Fetch all posts from WordPress
# 2. Convert HTML to Markdown
# 3. Extract metadata (dates, categories, tags)
# 4. Create Jekyll-compatible markdown files
# 5. Save to _posts/ directory
```

**Expected process:**
```
==========================================
WordPress to Jekyll Migration
==========================================

Source WordPress URL: https://mukulkadel.com

✓ Python found: Python 3.x.x
Fetching posts (page 1)...
✓ Fetching posts (page 1)...
Converting posts...
✓ Created: 2025-01-15-first-post.md
✓ Created: 2025-02-20-second-post.md
✓ Successfully converted 15/15 posts

Migration Complete!
```

### Post-Migration: Download Media Files

WordPress media files (images, documents) need to be downloaded separately:

```bash
# Create images directory
mkdir -p assets/images

# Download images from WordPress
wget -r -P assets/images \
  -A jpg,jpeg,png,gif,webp \
  -R "*.js,*.css,*.html" \
  https://mukulkadel.com/wp-content/uploads/

# Or use curl if wget is not available:
curl -r https://mukulkadel.com/wp-content/uploads/ \
  -o assets/images/
```

### Review Converted Posts

```bash
# List converted posts
ls -la _posts/

# View a post
cat _posts/2025-01-15-first-post.md

# Expected format:
# ---
# layout: post
# title: Post Title
# date: 2025-01-15 10:00:00 +0545
# categories: [category1, category2]
# tags: [tag1, tag2]
# excerpt: "Post preview text"
# ---
#
# Post content here...
```

### Fix Image Paths

Update image URLs in your posts:

**Before (WordPress):**
```markdown
![Image](https://mukulkadel.com/wp-content/uploads/2025/01/image.jpg)
```

**After (Jekyll):**
```markdown
![Image](/assets/images/image.jpg)
```

Use find and replace in your editor:
- **Find:** `https://mukulkadel.com/wp-content/uploads/`
- **Replace:** `/assets/images/`

---

## 🧪 Testing Your Site Locally

Before deploying, thoroughly test locally:

```bash
# Start development server
bundle exec jekyll serve

# Open http://localhost:4000 in browser
```

### Test Checklist

- [ ] **Homepage** loads with correct title and content
- [ ] **Blog page** (`/blog/`) shows all migrated posts
- [ ] **Individual posts** render correctly with formatting
- [ ] **Navigation** menu works and links are clickable
- [ ] **Images** load properly (if already downloaded)
- [ ] **Responsive design** works on mobile (F12 → toggle device)
- [ ] **No console errors** (F12 → Console tab)
- [ ] **Links are not broken** (click through various pages)
- [ ] **Footer** displays with correct information
- [ ] **Post metadata** (date, categories, tags) shows correctly

### Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Posts not showing | Check `_posts/` filenames follow YYYY-MM-DD format |
| Build error | Run `bundle exec jekyll build --trace` for details |
| Images missing | Download media to `assets/images/` and update paths |
| Styles not loading | Clear browser cache (Ctrl+Shift+Delete) |
| 404 errors | Verify post/page permalinks in front matter |

---

## 🎨 Customizing Your Site

### Update Site Information

Edit `_config.yml`:

```yaml
title: Mukul Kadel
description: "A personal portfolio and blog"
author:
  name: Mukul Kadel
  email: your-email@example.com
  twitter: your_twitter_handle  # Update this
  github: mukulkadel             # Already set
  linkedin: your-linkedin-profile # Update this

url: "https://mukulkadel.github.io"
timezone: Asia/Kathmandu
```

### Change Color Scheme

Edit `assets/css/style.css` - update the `:root` CSS variables:

```css
:root {
    --color-primary: #2c3e50;      /* Main navy blue */
    --color-secondary: #3498db;    /* Link blue */
    --color-accent: #e74c3c;       /* Red accent */
    --color-bg: #ecf0f1;           /* Light gray */
    --color-text: #34495e;         /* Dark gray text */
    --color-light-text: #7f8c8d;   /* Light text */
}
```

### Update Navigation Menu

Edit `_includes/header.html`:

```html
<a href="/" class="nav-link">Home</a>
<a href="/blog/" class="nav-link">Blog</a>
<a href="/about/" class="nav-link">About</a>
<a href="/contact/" class="nav-link">Contact</a>
<!-- Add more links as needed -->
```

### Modify Footer

Edit `_includes/footer.html`:

```html
<p>&copy; 2026 Mukul Kadel. All rights reserved.</p>
```

---

## 📤 Deploying to GitHub Pages

### Push Your Changes

```bash
# See what changed
git status

# Add all changes
git add .

# Create a commit
git commit -m "Migrate WordPress to Jekyll and customize site"

# Push to GitHub (main branch)
git push origin main

# Wait 1-2 minutes for GitHub Actions to build and deploy
```

### Verify Deployment

1. **Check GitHub Actions:**
   - Go to https://github.com/mukulkadel/mukulkadel.github.io
   - Click "Actions" tab
   - Should see a successful build

2. **Visit your live site:**
   - https://mukulkadel.github.io
   - Should match your local testing

### Enable Custom Domain (Optional)

To use `mukulkadel.com` instead of `mukulkadel.github.io`:

1. **Create CNAME file:**
   ```bash
   echo "mukulkadel.com" > CNAME
   ```

2. **Update DNS at your domain registrar:**
   - Option A: Change nameservers to GitHub Pages nameservers
   - Option B: Add CNAME record pointing to `mukulkadel.github.io`

3. **Enable HTTPS in GitHub:**
   - Repository → Settings → Pages
   - Check "Enforce HTTPS"
   - Wait 1 hour for HTTPS certificate

---

## 🔍 SEO Setup

Your site includes SEO features:

### Automatic Features

- ✓ XML Sitemap (`sitemap.xml`)
- ✓ RSS Feed (`feed.xml`)
- ✓ Meta tags and Open Graph
- ✓ robots.txt for search engines

### Submit to Search Engines

1. **Google Search Console:**
   - Visit https://search.google.com/search-console
   - Add property for your domain
   - Submit sitemap.xml
   - Monitor indexing and errors

2. **Bing Webmaster Tools:**
   - Visit https://www.bing.com/webmasters
   - Add your site
   - Submit sitemap

### SEO Best Practices

- Use descriptive post titles
- Write meaningful excerpts
- Use categories and tags appropriately
- Include relevant keywords naturally
- Add alt text to images
- Link to related posts
- Keep URLs simple and descriptive

---

## 📚 File Reference

### Key Configuration File: `_config.yml`

```yaml
# Site Settings
title: Mukul Kadel
tagline: Developer, Writer, Creator
description: Personal website featuring blog posts and portfolio
baseurl: ""
url: "https://mukulkadel.github.io"

# Author Information
author:
  name: Mukul Kadel
  email: your-email@example.com
  twitter: your_handle
  github: mukulkadel
  linkedin: your-profile

# Build Settings
markdown: kramdown
highlighter: rouge

# Plugins
plugins:
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-sitemap
  - jekyll-paginate-v2
  - jekyll-redirect-from

# Collections
collections:
  posts:
    permalink: /blog/:year/:month/:day/:slug/
```

### Key Layout Files

**`_layouts/default.html`** - Master template for all pages
**`_layouts/post.html`** - Template for blog posts (extends default)
**`_layouts/page.html`** - Template for static pages (extends default)

### Key Include Files

**`_includes/header.html`** - Navigation bar
**`_includes/footer.html`** - Site footer

---

## 🆘 Troubleshooting

### Problem: "bundle: command not found"

**Solution:**
```bash
gem install bundler
```

### Problem: Posts not showing in `/blog/`

**Solution:**
1. Check `_posts/` directory has files
2. Verify filename format: `YYYY-MM-DD-slug.md`
3. Check front matter has `layout: post`
4. Verify date is not in the future
5. Run: `bundle exec jekyll build --trace`

### Problem: Images show as broken

**Solution:**
1. Download images to `assets/images/`
2. Update image paths in posts to: `/assets/images/filename.jpg`
3. Clear browser cache
4. Restart Jekyll server

### Problem: Site doesn't update after push

**Solution:**
1. Wait 1-2 minutes for GitHub Actions
2. Check Actions tab for build errors
3. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
4. Clear browser cache

### Problem: Need to reinstall gems

**Solution:**
```bash
rm Gemfile.lock
bundle install
```

### Problem: Port 4000 already in use

**Solution:**
```bash
# Run on different port
bundle exec jekyll serve --port 4001

# Then visit: http://localhost:4001
```

---

## 📞 Getting Help

### Documentation Files in Your Repo

1. **README.md** - Complete feature documentation
2. **QUICKSTART.md** - 5-minute quick start
3. **WORDPRESS_MIGRATION.md** - Detailed migration guide
4. **MIGRATION_CHECKLIST.md** - Step-by-step checklist

### Official Resources

- **Jekyll Docs:** https://jekyllrb.com/docs/
- **GitHub Pages:** https://pages.github.com/
- **GitHub Pages Docs:** https://docs.github.com/en/pages
- **Markdown Guide:** https://www.markdownguide.org/

### Common Commands Reference

```bash
# Setup
./setup.sh                              # Install dependencies

# Development
bundle exec jekyll serve                # Run local server
bundle exec jekyll serve --draft        # Include draft posts
bundle exec jekyll build                # Build site to _site/

# Migration
./run-migration.sh https://yourdomain   # Migrate WordPress content

# Git
git add .                               # Stage changes
git commit -m "Description"             # Create commit
git push origin main                    # Push to GitHub
git status                              # See what changed
git log --oneline                       # View commit history

# Cleanup
rm Gemfile.lock && bundle install       # Reinstall gems
rm -rf _site/ .jekyll-cache/            # Clear build cache
```

---

## ✨ You're All Set!

Your Jekyll site is completely set up and ready to deploy. 

### Quick Summary

✅ **Jekyll project created with:**
- Professional responsive design
- Blog functionality with categories and tags
- Static pages (About, Contact, Projects)
- SEO optimization (sitemap, RSS, meta tags)
- CSS styling (900+ lines)

✅ **WordPress migration tools provided:**
- Python script to export all content
- Automatic HTML to Markdown conversion
- Category and tag preservation
- Easy-to-use shell scripts

✅ **Complete documentation:**
- Setup instructions (this file)
- Quick start guide
- Detailed migration guide
- Step-by-step checklist

### Next Steps

1. **Now:** Run `./setup.sh` to install dependencies
2. **Then:** Test locally with `bundle exec jekyll serve`
3. **Next:** Run `./run-migration.sh https://mukulkadel.com`
4. **Finally:** Deploy with `git push origin main`

### Need Help?

Refer to:
- QUICKSTART.md for 5-minute setup
- WORDPRESS_MIGRATION.md for detailed migration steps
- MIGRATION_CHECKLIST.md for task tracking
- README.md for complete reference

---

**Happy blogging! 🚀**

Created: March 7, 2026  
For: mukulkadel.github.io  
Repository: https://github.com/mukulkadel/mukulkadel.github.io
