import os

import requests


def get_products(domain, token):
    # os.getenv('STRAPI_TOKEN')
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f'http://{domain}/api/products', headers=headers)
    r.raise_for_status()
    return r.json()


def get_description(id, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f'http://{domain}/api/products/{id}', headers=headers)
    r.raise_for_status()
    return r.json().get('data').get('attributes').get('Description')


def create_cart(user_id, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f'http://{domain}/api/carts',
        headers=headers,
        json={
            'data': {
                "User": str(user_id),
            }
        },
    )
    r.raise_for_status()
    return r.json()


def create_product_quantity(prod_id, quant, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
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
    r.raise_for_status()
    return r.json()


def add_product_to_cart(cart_id, prod_quant_id, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
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
    r.raise_for_status()
    return r.json()


def get_cart(user_id, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f'http://{domain}/api/carts',
        headers=headers,
        params={
            'filters[User][$eq]': str(user_id),
            'populate[product_quantities][populate][0]': 'product',
        }
    )
    r.raise_for_status()
    return r.json()


def get_product(id, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f'http://{domain}/api/products/{id}?populate=Picture', headers=headers)
    r.raise_for_status()
    return r.json().get('data')


def remove_item_from_cart(item_id, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(
        f'http://{domain}/api/product-quantities/{item_id}',
        headers=headers
    )
    r.raise_for_status()


def save_email(user_id, email, domain, token):
    headers = {"Authorization": f"Bearer {token}"}
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
    r.raise_for_status()
    print("TESTING EMAIL: ", r.json())
