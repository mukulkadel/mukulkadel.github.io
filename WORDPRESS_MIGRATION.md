# WordPress Migration Instructions

This document provides detailed instructions for migrating your WordPress site to Jekyll.

## Prerequisites

### Required
- Python 3.6+
- `requests` library (`pip install requests`)
- Your WordPress site must have REST API enabled (default in WordPress 4.7+)

### Optional
- `pandoc` for advanced HTML to Markdown conversion
- `wpdb` credentials if you need direct database access

## Step 1: Prepare Your WordPress Site

### Check REST API Access

Test if your WordPress REST API is accessible:

```bash
curl -s https://mukulkadel.com/wp-json/wp/v2/posts | head -20
```

You should see JSON response with post data. If you see an error, REST API may be disabled.

### Enable REST API (if disabled)

1. Log in to WordPress admin
2. Go to Settings → Permalinks
3. Choose a permalink structure other than "Plain"
4. Save changes

## Step 2: Run Migration Script

### Basic Migration

```bash
python3 migrate.py https://mukulkadel.com ./
```

This will:
- Fetch all posts from WordPress
- Convert them to Jekyll markdown
- Save files to `_posts/` directory
- Extract categories and tags

### What Gets Migrated

- ✅ **Posts** - All blog posts with dates, content, categories, tags
- ✅ **Pages** - All static pages
- ✅ **Metadata** - Author, dates, categories, tags
- ✅ **HTML to Markdown** - Converts HTML formatting to markdown
- ⚠️ **Media** - Links preserved, but need to download separately
- ⚠️ **Custom Fields** - May need manual adjustment
- ⚠️ **Comments** - Not included (consider using Disqus)

## Step 3: Download Media Files

### Option 1: Using wget (Automatic)

```bash
# Create images directory
mkdir -p assets/images

# Download all images from WordPress
wget -r -P assets/images \
  -A jpg,jpeg,png,gif,webp \
  -R "*.js,*.css,*.html" \
  https://mukulkadel.com/wp-content/uploads/
```

### Option 2: Using Python

```python
import os
import requests
from pathlib import Path

def download_wordpress_media(site_url, output_dir):
    """Download all media from WordPress uploads folder"""
    uploads_url = f"{site_url}/wp-content/uploads/"
    output_path = Path(output_dir) / "assets" / "images"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # You'll need to implement recursive download logic
    # or use a tool like wget/curl
    pass
```

## Step 4: Review and Fix Converted Content

### Check File Format

```bash
# List converted posts
ls -la _posts/

# View a post
cat _posts/2026-03-01-sample-post.md
```

### Common Fixes Needed

1. **Image References**
   ```markdown
   # Before
   ![image](https://mukulkadel.com/wp-content/uploads/2025/01/image.jpg)
   
   # After
   ![image](/assets/images/image.jpg)
   ```

2. **Code Blocks**
   ```markdown
   # Before
   <pre>code here</pre>
   
   # After
   ```language
   code here
   ```
   ```

3. **Embedded Media**
   - YouTube: Keep as embed or convert to link
   - Galleries: May need manual recreation
   - Shortcodes: Replace with markdown equivalent

4. **Custom HTML**
   - Tables: Check markdown table formatting
   - Divs: Convert to markdown div if needed
   - Spans: Simplify to markdown formatting

## Step 5: Update Configuration

Edit `_config.yml`:

```yaml
# Update these fields
title: Mukul Kadel
description: "Your site description"
author:
  name: Mukul Kadel
  email: your-email@example.com
  twitter: your_twitter
  github: mukulkadel
  linkedin: your-linkedin

# Update URL
url: "https://mukulkadel.github.io"
# or for custom domain:
url: "https://mukulkadel.com"
```

## Step 6: Test Locally

```bash
# Install dependencies
bundle install

# Run local server
bundle exec jekyll serve

# Open in browser
open http://localhost:4000
```

Check:
- ✓ All posts display correctly
- ✓ Navigation works
- ✓ Images load properly
- ✓ Links are not broken
- ✓ Formatting looks good
- ✓ Categories and tags work

## Step 7: Set Up Redirects (Optional)

Redirect old WordPress URLs to new Jekyll URLs to prevent broken links:

```yaml
---
layout: post
title: My Post
date: 2026-03-07
redirect_from:
  - /my-old-post/
  - /2025/03/old-slug/
---
```

## Step 8: Deploy to GitHub Pages

```bash
# Add all changes
git add .

# Commit
git commit -m "Migrate from WordPress to Jekyll"

# Push to main branch
git push origin main
```

GitHub Actions will automatically build and deploy your site.

## Advanced Migration Options

### Using WordPress Export File

If REST API is not available, export from WordPress:

1. Go to Tools → Export in WordPress admin
2. Select "All content"
3. Download XML file
4. Use a converter like `wordpress-to-jekyll-exporter`

### Direct Database Migration

If you have WordPress database access:

```bash
# Install wordpress-to-jekyll-exporter
gem install wordpress-to-jekyll-exporter

# Run with MySQL credentials
ruby -r wordpress-to-jekyll-exporter \
  --mysql-user=wordpress_user \
  --mysql-password=password \
  --mysql-host=localhost \
  --mysql-database=wordpress_db
```

## Troubleshooting

### Migration script hangs or times out

- Check your internet connection
- Reduce the `per_page` parameter in `migrate.py`
- Try migrating in smaller batches

### HTML to Markdown conversion issues

For better conversion, install `pandoc`:

```bash
# macOS
brew install pandoc

# Then use in script
import subprocess
result = subprocess.run(['pandoc', '-f', 'html', '-t', 'markdown'], 
                       input=html_content, 
                       capture_output=True, 
                       text=True)
markdown = result.stdout
```

### Missing images or broken links

1. Download media files separately
2. Update image paths in posts
3. Test all links before deploying

### Character encoding issues

Ensure all files are saved as UTF-8:

```bash
# Convert files to UTF-8 if needed
iconv -f ISO-8859-1 -t UTF-8 file.md > file_utf8.md
```

## SEO Considerations

After migration:

1. **Set up redirects** - Avoid 404 errors
2. **Update sitemap** - Submit to Google Search Console
3. **Verify robots.txt** - Allow search engine crawling
4. **Set canonical URLs** - Prevent duplicate content issues
5. **Update DNS records** - Point domain to GitHub Pages
6. **Monitor Analytics** - Track traffic after migration

## Post-Migration Checklist

- [ ] All posts migrated and displaying
- [ ] All pages migrated and displaying
- [ ] Images downloaded and paths updated
- [ ] Navigation menus working
- [ ] Categories and tags functional
- [ ] Search console verification
- [ ] Redirects set up for old URLs
- [ ] DNS updated for custom domain
- [ ] HTTPS enabled and verified
- [ ] Local tests pass
- [ ] Deployed to GitHub Pages
- [ ] Live site tested thoroughly

## Getting Help

- Check Jekyll documentation: https://jekyllrb.com/docs/
- GitHub Pages help: https://docs.github.com/en/pages
- Test HTML to Markdown: https://pandoc.org/try/

---

**Happy migrating!** 🎉
