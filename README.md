# Mukul Kadel's Personal Website

A modern, responsive personal website built with Jekyll and hosted on GitHub Pages.

## 🚀 Features

- **Static Site Generation** using Jekyll
- **Responsive Design** that works on all devices
- **Fast Performance** with optimized CSS and minimal JavaScript
- **SEO Optimized** with meta tags and XML sitemap
- **Blog** with categories and tags
- **Portfolio** showcase
- **Contact** page
- **Clean, Modern Design** with easy customization

## 📁 Project Structure

```
.
├── _posts/              # Blog posts in markdown
├── _pages/              # Static pages (About, Contact, etc.)
├── _layouts/            # HTML templates (default, post, page)
├── _includes/           # Reusable HTML components (header, footer)
├── assets/
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Images and media
├── _config.yml         # Jekyll configuration
├── Gemfile             # Ruby dependencies
└── migrate.py          # WordPress migration script
```

## 🛠️ Installation & Setup

### Prerequisites

- Ruby 3.0 or higher
- Bundler (`gem install bundler`)
- Git

### Local Development

1. **Install dependencies:**
   ```bash
   bundle install
   ```

2. **Run the local server:**
   ```bash
   bundle exec jekyll serve
   ```

3. **Visit the site:**
   Open `http://localhost:4000` in your browser

The site will automatically rebuild when you make changes.

## 📝 Creating Blog Posts

Create a new markdown file in the `_posts/` directory with the naming convention: `YYYY-MM-DD-title-slug.md`

Example: `_posts/2026-03-07-my-first-post.md`

```markdown
---
layout: post
title: My First Blog Post
date: 2026-03-07 10:00:00 +0545
categories: [blogging, jekyll]
tags: [jekyll, tutorial]
excerpt: "A brief description of your post"
---

Your content here in markdown format.

## Subheading

More content...
```

## 📄 Creating Pages

Create new pages in the `_pages/` directory:

```markdown
---
layout: page
title: My Page Title
permalink: /my-page/
---

Page content here...
```

## 🎨 Customization

### Site Configuration

Edit `_config.yml` to customize:
- Site title and description
- Author information
- Social media links
- URL structure
- Plugins and features

### Styling

Edit `assets/css/style.css` to modify:
- Colors and fonts
- Layout and spacing
- Responsive breakpoints
- Component styles

## 🔄 WordPress Migration

To migrate content from your WordPress site:

1. **Run the migration script:**
   ```bash
   python3 migrate.py https://mukulkadel.com ./
   ```

2. **The script will:**
   - Fetch all posts from WordPress REST API
   - Convert them to Jekyll markdown format
   - Create proper front matter with metadata
   - Save files to `_posts/` directory

3. **Review and adjust:**
   - Check converted files for formatting
   - Download media files separately
   - Update image references if needed
   - Verify categories and tags

### Migration Details

The migration script:
- Extracts posts, pages, categories, and tags
- Converts HTML to markdown
- Preserves post metadata and dates
- Creates proper Jekyll front matter
- Handles special characters and HTML entities

**Note:** Complex HTML (tables, custom shortcodes) may need manual adjustment.

## 📤 Deployment to GitHub Pages

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

2. **Push to GitHub:**
   ```bash
   git push origin main
   ```

3. **Verify deployment:**
   - GitHub Actions will automatically build your site
   - Visit `https://mukulkadel.github.io` to see your live site
   - Check GitHub Actions tab for build status

### GitHub Pages Settings

Your repository should be configured with:
- **Repository name:** `mukulkadel.github.io`
- **Branch:** `main`
- **Build source:** GitHub Actions (automatic with Jekyll)

## 🔗 URL Structure

The site uses the following URL patterns:

- Home: `/`
- Blog: `/blog/`
- Individual posts: `/blog/YYYY/MM/DD/slug/`
- Pages: `/page-title/`
- Categories: `/categories/#category-name`
- Tags: `/tags/#tag-name`

To redirect old WordPress URLs, add redirects to post front matter:
```yaml
redirect_from:
  - /old-wordpress-url/
```

## 🌐 Domain Configuration

To use a custom domain (mukulkadel.com):

1. **Add `CNAME` file:**
   Create a file named `CNAME` in the root directory:
   ```
   mukulkadel.com
   ```

2. **Update DNS settings** in your domain registrar:
   - Update nameservers to GitHub Pages nameservers, OR
   - Add CNAME record pointing to `mukulkadel.github.io`

3. **Enable HTTPS:**
   - Go to repository Settings → Pages
   - Enable "Enforce HTTPS"

## 📚 Plugins & Features

This Jekyll site uses:

- **jekyll-feed** - RSS feed generation
- **jekyll-seo-tag** - SEO meta tags
- **jekyll-sitemap** - XML sitemap for search engines
- **jekyll-paginate-v2** - Pagination for blog archives
- **jekyll-redirect-from** - URL redirects from old URLs

## 🚨 Troubleshooting

### Site not building?
- Check `_config.yml` syntax (use valid YAML)
- Look at GitHub Actions logs for build errors
- Ensure all required gems are in `Gemfile`

### Posts not showing?
- Check filename format: `YYYY-MM-DD-slug.md`
- Ensure front matter is valid YAML
- Check that `layout: post` is specified
- Verify the date is not in the future

### Styling issues?
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Check CSS file paths use relative_url filter
- Verify CSS syntax in `assets/css/style.css`

## 📖 Additional Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Markdown Guide](https://www.markdownguide.org/)
- [YAML Syntax](https://yaml.org/spec/1.2/spec.html)

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Mukul Kadel**
- GitHub: [@mukulkadel](https://github.com/mukulkadel)
- Email: your-email@example.com

---

**Last Updated:** March 7, 2026

For questions or suggestions, feel free to reach out!