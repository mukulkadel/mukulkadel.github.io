#!/usr/bin/env python3
"""
WordPress to Jekyll Migration Script
This script exports content from a WordPress site and converts it to Jekyll format.
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path
import re
import html

class WordPressMigrator:
    def __init__(self, wordpress_url, output_dir):
        """
        Initialize the migrator.
        
        Args:
            wordpress_url: Base URL of the WordPress site (e.g., https://mukulkadel.com)
            output_dir: Directory to save Jekyll posts
        """
        self.wordpress_url = wordpress_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.posts_dir = self.output_dir / '_posts'
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_posts(self, per_page=100):
        """
        Fetch all posts from WordPress REST API.
        
        Args:
            per_page: Number of posts to fetch per request
            
        Returns:
            List of post dictionaries
        """
        posts = []
        page = 1
        
        while True:
            url = f"{self.wordpress_url}/wp-json/wp/v2/posts"
            params = {
                'per_page': per_page,
                'page': page,
                'orderby': 'date',
                'order': 'asc',
                '_embed': True
            }
            
            print(f"Fetching posts (page {page})...")
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                page_posts = response.json()
                
                if not page_posts:
                    break
                    
                posts.extend(page_posts)
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching posts: {e}")
                break
                
        return posts
    
    def fetch_pages(self, per_page=100):
        """
        Fetch all pages from WordPress REST API.
        
        Args:
            per_page: Number of pages to fetch per request
            
        Returns:
            List of page dictionaries
        """
        pages = []
        page = 1
        
        while True:
            url = f"{self.wordpress_url}/wp-json/wp/v2/pages"
            params = {
                'per_page': per_page,
                'page': page,
                'orderby': 'date',
                'order': 'asc',
                '_embed': True
            }
            
            print(f"Fetching pages (page {page})...")
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                page_pages = response.json()
                
                if not page_pages:
                    break
                    
                pages.extend(page_pages)
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching pages: {e}")
                break
                
        return pages
    
    def fetch_categories(self):
        """Fetch all categories from WordPress."""
        url = f"{self.wordpress_url}/wp-json/wp/v2/categories"
        params = {'per_page': 100}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching categories: {e}")
            return []
    
    def fetch_tags(self):
        """Fetch all tags from WordPress."""
        url = f"{self.wordpress_url}/wp-json/wp/v2/tags"
        params = {'per_page': 100}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching tags: {e}")
            return []
    
    def convert_html_to_markdown(self, html_content):
        """
        Convert HTML content to markdown (basic conversion).
        For complex conversions, consider using html2text or pandoc.
        
        Args:
            html_content: HTML string
            
        Returns:
            Markdown string
        """
        # Unescape HTML entities
        content = html.unescape(html_content)
        
        # Basic conversions
        content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
        content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
        content = re.sub(r'<b>(.*?)</b>', r'**\1**', content)
        content = re.sub(r'<i>(.*?)</i>', r'*\1*', content)
        content = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', content)
        content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content)
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<h1>(.*?)</h1>', r'# \1\n\n', content)
        content = re.sub(r'<h2>(.*?)</h2>', r'## \1\n\n', content)
        content = re.sub(r'<h3>(.*?)</h3>', r'### \1\n\n', content)
        content = re.sub(r'<h4>(.*?)</h4>', r'#### \1\n\n', content)
        content = re.sub(r'<ul>(.*?)</ul>', lambda m: self._convert_list(m.group(1), False), content, flags=re.DOTALL)
        content = re.sub(r'<ol>(.*?)</ol>', lambda m: self._convert_list(m.group(1), True), content, flags=re.DOTALL)
        content = re.sub(r'<li>(.*?)</li>', r'- \1', content)
        content = re.sub(r'<img\s+src="(.*?)"\s+alt="(.*?)"', r'![\2](\1)', content)
        
        # Remove remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\n+', '\n\n', content)
        
        return content.strip()
    
    def _convert_list(self, list_content, ordered=False):
        """Helper to convert list items."""
        items = re.findall(r'<li>(.*?)</li>', list_content, re.DOTALL)
        prefix = "1. " if ordered else "- "
        return '\n'.join(f"{prefix}{item.strip()}" for item in items) + '\n\n'
    
    def get_category_names(self, post, categories_map):
        """Extract category names from post data."""
        if '_embedded' in post and 'wp:term' in post['_embedded']:
            for term_group in post['_embedded']['wp:term']:
                if term_group and term_group[0].get('taxonomy') == 'category':
                    return [term['name'] for term in term_group]
        return []
    
    def get_tag_names(self, post):
        """Extract tag names from post data."""
        if '_embedded' in post and 'wp:term' in post['_embedded']:
            for term_group in post['_embedded']['wp:term']:
                if term_group and term_group[0].get('taxonomy') == 'post_tag':
                    return [term['name'] for term in term_group]
        return []
    
    def create_jekyll_post(self, post, post_type='post'):
        """
        Convert a WordPress post to a Jekyll markdown file.
        
        Args:
            post: WordPress post dictionary
            post_type: 'post' or 'page'
        """
        # Extract data
        title = post.get('title', {}).get('rendered', 'Untitled')
        content = post.get('content', {}).get('rendered', '')
        published = post.get('date', datetime.now().isoformat())
        slug = post.get('slug', 'untitled')
        excerpt = post.get('excerpt', {}).get('rendered', '')
        
        # Parse date
        date_obj = datetime.fromisoformat(published.replace('Z', '+00:00'))
        date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S %z')
        date_path = date_obj.strftime('%Y-%m-%d')
        
        # Get categories and tags
        categories = self.get_category_names(post, {})
        tags = self.get_tag_names(post)
        
        # Convert content
        markdown_content = self.convert_html_to_markdown(content)
        markdown_excerpt = self.convert_html_to_markdown(excerpt)
        
        # Create front matter
        front_matter = f"""---
layout: {post_type}
title: {title}
date: {date_str}
slug: {slug}
excerpt: "{markdown_excerpt[:100]}"
"""
        
        if categories:
            front_matter += f"categories: {json.dumps(categories)}\n"
        
        if tags:
            front_matter += f"tags: {json.dumps(tags)}\n"
        
        front_matter += "---\n\n"
        
        # Create filename
        filename = f"{date_path}-{slug}.md"
        filepath = self.posts_dir / filename
        
        # Write file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(front_matter)
                f.write(markdown_content)
            print(f"✓ Created: {filename}")
            return True
        except Exception as e:
            print(f"✗ Error creating {filename}: {e}")
            return False
    
    def migrate(self):
        """Run the full migration process."""
        print(f"\n=== WordPress to Jekyll Migration ===")
        print(f"Source: {self.wordpress_url}")
        print(f"Output: {self.output_dir}\n")
        
        # Fetch content
        print("Fetching content from WordPress...\n")
        posts = self.fetch_posts()
        pages = self.fetch_pages()
        categories = self.fetch_categories()
        tags = self.fetch_tags()
        
        print(f"\nFound {len(posts)} posts and {len(pages)} pages\n")
        
        # Create categories map
        categories_map = {cat.get('id'): cat.get('name') for cat in categories}
        
        # Convert posts
        print("Converting posts...")
        post_count = 0
        for post in posts:
            if self.create_jekyll_post(post, 'post'):
                post_count += 1
        
        print(f"\n✓ Successfully converted {post_count}/{len(posts)} posts\n")
        
        # Convert pages
        print("Converting pages...")
        page_count = 0
        for page in pages:
            if self.create_jekyll_post(page, 'page'):
                page_count += 1
        
        print(f"\n✓ Successfully converted {page_count}/{len(pages)} pages\n")
        print("Migration complete!")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <wordpress_url> [output_dir]")
        print("Example: python migrate.py https://mukulkadel.com ./")
        sys.exit(1)
    
    wordpress_url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './'
    
    migrator = WordPressMigrator(wordpress_url, output_dir)
    migrator.migrate()


if __name__ == '__main__':
    main()
