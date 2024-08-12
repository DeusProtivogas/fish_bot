import os

import requests


def get_products(domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    # url = f'https://<YOUR_DOMAIN>/api/<YOUR_CT>'
    r = requests.get(f'http://{domain}/api/products', headers=headers)
    return r.json()


def get_description(id, domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.get(f'http://{domain}/api/products/{id}', headers=headers)
    return r.json().get('data').get('attributes').get('Description')


def create_cart(user_id, domain):
    # url_template = 'http://localhost:1337/api/restaurants'
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.post(
        f'http://{domain}/api/carts',
        headers=headers,
        json={
            'data': {
                "User": str(user_id),
            }
        },
    )
    return r.json()


def create_product_quantity(prod_id, quant, domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.post(
        f'http://{domain}/api/product-quantities',
        headers=headers,
        json={
            'data': {
                "Quantity": str(quant),
                "product": [prod_id],
            }
        },
    )
    return r.json()


def add_product_to_cart(cart_id, prod_quant_id, domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.put(
        f'http://{domain}/api/carts/{int(cart_id)}',
        headers=headers,
        json={
            'data': {
                "product_quantities": {
                    'connect': [prod_quant_id],
                }
            }
        },
    )
    return r.json()


def get_cart(user_id, domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.get(
        f'http://{domain}/api/carts',
        headers=headers,
        params={
            'filters[User][$eq]': str(user_id),
            'populate[product_quantities][populate][0]': 'product',
        }
    )
    return r.json()


def get_product(id, domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.get(f'http://{domain}/api/products/{id}?populate=Picture', headers=headers)
    return r.json().get('data')


def remove_item_from_cart(item_id, domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.delete(
        f'http://{domain}/api/product-quantities/{item_id}',
        headers=headers
    )


def save_email(user_id, email, domain):
    headers = {"Authorization": f"Bearer {os.getenv('STRAPI_TOKEN')}"}
    r = requests.post(
        f'http://{domain}/api/clients',
        headers=headers,
        json={
            'data': {
                "tg_id": str(user_id),
                "Email": email,
            }
        },
    )
    print("TESTING EMAIL: ", r.json())
