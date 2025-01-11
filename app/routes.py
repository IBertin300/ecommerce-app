from flask import Blueprint, session, redirect, render_template, jsonify
from app.models import Product
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Contentful credentials
CONTENTFUL_SPACE_ID = os.getenv("CONTENTFUL_SPACE_ID")
CONTENTFUL_ENVIRONMENT = os.getenv("CONTENTFUL_ENVIRONMENT")
CONTENTFUL_ACCESS_TOKEN = os.getenv("CONTENTFUL_ACCESS_TOKEN")

main = Blueprint('main', __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/about")
def about():
    return render_template("about.html")


@main.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return redirect('/cart')


@main.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)


@main.route('/entry/<entry_id>')
def get_contentful_entry(entry_id):
    url = f"https://cdn.contentful.com/spaces/{CONTENTFUL_SPACE_ID}/environments/{CONTENTFUL_ENVIRONMENT}/entries/{entry_id}"
    headers = {
        "Authorization": f"Bearer {CONTENTFUL_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        entry_data = response.json()
        return render_template('entry.html', entry=entry_data)
    else:
        return f"Error: {response.status_code} - {response.text}", response.status_code


def fetch_all_entries(content_type):
    url = f"https://cdn.contentful.com/spaces/{CONTENTFUL_SPACE_ID}/environments/{CONTENTFUL_ENVIRONMENT}/entries"
    params = {
        "access_token": CONTENTFUL_ACCESS_TOKEN,
        "content_type": content_type,
        "limit": 100,
        "skip": 0
    }

    all_entries = []
    asset_map = {}

    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        data = response.json()
        all_entries.extend(data['items'])

        # Map assets for resolving images
        if 'includes' in data and 'Asset' in data['includes']:
            for asset in data['includes']['Asset']:
                asset_id = asset['sys']['id']
                asset_url = asset['fields']['file']['url']
                asset_map[asset_id] = asset_url

        if len(all_entries) >= data['total']:
            break

        params['skip'] += params['limit']

    # Resolve image links and parse descriptions
    for entry in all_entries:
        if 'image' in entry['fields']:
            image_id = entry['fields']['image']['sys']['id']
            entry['fields']['image_url'] = asset_map.get(image_id, '')

        if 'description' in entry['fields']:
            entry['fields']['description_text'] = parse_rich_text(
                entry['fields']['description'])

    return all_entries


def parse_rich_text(rich_text):
    """Parse Contentful's rich text document into plain text or HTML."""
    if rich_text['nodeType'] == 'document':
        paragraphs = []
        for content in rich_text['content']:
            if content['nodeType'] == 'paragraph':
                paragraph_text = ''.join(
                    [node['value'] for node in content['content']
                        if node['nodeType'] == 'text']
                )
                paragraphs.append(paragraph_text)
        return '\n\n'.join(paragraphs)
    return ''


@main.route('/all-products')
def all_products():
    try:
        entries = fetch_all_entries(content_type="product")
        print(entries)
        return render_template('products.html', entries=entries)
    except Exception as e:
        return str(e), 500
