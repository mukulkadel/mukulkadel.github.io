import requests
import json

DEST_FOLDER = "wordpress-dump"

def save_to_file(data, filename):
    with open(f"{DEST_FOLDER}/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f)

def fetch_all_posts(site_url):
    posts = []
    page = 1
    while True:
        response = requests.get(f"{site_url}/wp-json/wp/v2/posts", params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        posts.extend(data)
        page += 1
    return posts

def fetch_all_pages(site_url):
    pages = []
    page = 1
    while True:
        response = requests.get(f"{site_url}/wp-json/wp/v2/pages", params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        pages.extend(data)
        page += 1
    return pages

def fetch_all_categories(site_url):
    categories = []
    page = 1
    while True:
        response = requests.get(f"{site_url}/wp-json/wp/v2/categories", params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        categories.extend(data)
        page += 1
    return categories

def fetch_all_tags(site_url):
    tags = []
    page = 1
    while True:
        response = requests.get(f"{site_url}/wp-json/wp/v2/tags", params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        tags.extend(data)
        page += 1
    return tags

def fetch_all_users(site_url):
    users = []
    page = 1
    while True:
        response = requests.get(f"{site_url}/wp-json/wp/v2/users", params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        users.extend(data)
        page += 1
    return users

def fetch_all_media(site_url):
    media = []
    page = 1
    while True:
        response = requests.get(f"{site_url}/wp-json/wp/v2/media", params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        media.extend(data)
        page += 1
    return media

def fetch_all_comments(site_url):
    comments = []
    page = 1
    while True:
        response = requests.get(f"{site_url}/wp-json/wp/v2/comments", params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        comments.extend(data)
        page += 1
    return comments

def fetch_all_custom_post_types(site_url):
    custom_post_types = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/types")
    if response.status_code == 200:
        data = response.json()
        for post_type in data:
            if post_type not in ["post", "page", "attachment", "revision", "nav_menu_item"]:
                custom_post_types.append(post_type)
    return custom_post_types

def fetch_all_custom_taxonomies(site_url):
    custom_taxonomies = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/taxonomies")
    if response.status_code == 200:
        data = response.json()
        for taxonomy in data:
            if taxonomy not in ["category", "post_tag", "nav_menu"]:
                custom_taxonomies.append(taxonomy)
    return custom_taxonomies

def fetch_all_custom_fields(site_url):
    custom_fields = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/fields")
    if response.status_code == 200:
        data = response.json()
        for field in data:
            custom_fields.append(field)
    return custom_fields

def fetch_all_custom_menus(site_url):
    custom_menus = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/menus")
    if response.status_code == 200:
        data = response.json()
        for menu in data:
            custom_menus.append(menu)
    return custom_menus

def fetch_all_custom_widgets(site_url):
    custom_widgets = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/widgets")
    if response.status_code == 200:
        data = response.json()
        for widget in data:
            custom_widgets.append(widget)
    return custom_widgets

def fetch_all_custom_shortcodes(site_url):
    custom_shortcodes = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/shortcodes")
    if response.status_code == 200:
        data = response.json()
        for shortcode in data:
            custom_shortcodes.append(shortcode)
    return custom_shortcodes

def fetch_all_custom_blocks(site_url):
    custom_blocks = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/blocks")
    if response.status_code == 200:
        data = response.json()
        for block in data:
            custom_blocks.append(block)
    return custom_blocks

def fetch_all_custom_endpoints(site_url):
    custom_endpoints = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/endpoints")
    if response.status_code == 200:
        data = response.json()
        for endpoint in data:
            custom_endpoints.append(endpoint)
    return custom_endpoints

def fetch_all_custom_settings(site_url):
    custom_settings = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/settings")
    if response.status_code == 200:
        data = response.json()
        for setting in data:
            custom_settings.append(setting)
    return custom_settings

def fetch_all_custom_options(site_url):
    custom_options = []
    response = requests.get(f"{site_url}/wp-json/wp/v2/options")
    if response.status_code == 200:
        data = response.json()
        for option in data:
            custom_options.append(option)
    return custom_options

def main():
    site_url = "https://mukulkadel.com"
    posts = fetch_all_posts(site_url)
    pages = fetch_all_pages(site_url)
    categories = fetch_all_categories(site_url)
    tags = fetch_all_tags(site_url)
    users = fetch_all_users(site_url)
    media = fetch_all_media(site_url)
    comments = fetch_all_comments(site_url)
    custom_post_types = fetch_all_custom_post_types(site_url)
    custom_taxonomies = fetch_all_custom_taxonomies(site_url)
    custom_fields = fetch_all_custom_fields(site_url)
    custom_menus = fetch_all_custom_menus(site_url)
    custom_widgets = fetch_all_custom_widgets(site_url)
    custom_shortcodes = fetch_all_custom_shortcodes(site_url)
    custom_blocks = fetch_all_custom_blocks(site_url)
    custom_endpoints = fetch_all_custom_endpoints(site_url)
    custom_settings = fetch_all_custom_settings(site_url)
    custom_options = fetch_all_custom_options(site_url)

    save_to_file(posts, "posts.json")
    save_to_file(pages, "pages.json")
    save_to_file(categories, "categories.json")
    save_to_file(tags, "tags.json")
    save_to_file(users, "users.json")
    save_to_file(media, "media.json")
    save_to_file(comments, "comments.json")
    save_to_file(custom_post_types, "custom_post_types.json")
    save_to_file(custom_taxonomies, "custom_taxonomies.json")
    save_to_file(custom_fields, "custom_fields.json")
    save_to_file(custom_menus, "custom_menus.json")
    save_to_file(custom_widgets, "custom_widgets.json")
    save_to_file(custom_shortcodes, "custom_shortcodes.json")
    save_to_file(custom_blocks, "custom_blocks.json")
    save_to_file(custom_endpoints, "custom_endpoints.json")
    save_to_file(custom_settings, "custom_settings.json")
    save_to_file(custom_options, "custom_options.json")
    print("Data has been saved to JSON files.")

if __name__ == "__main__":
    main()
