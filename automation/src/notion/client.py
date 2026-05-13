import os
import requests

notion_token = os.environ['NOTION_TOKEN']

headers = {
    'Authorization': f'Bearer {notion_token}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}


def find_pages(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    body = {
        "filter": {
            "and": [
                {
                    "property": "승인여부",
                    "checkbox": {
                        "equals": False
                    }
                },
                {
                    "property": "반려여부",
                    "checkbox": {
                        "equals": False
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        print(response.text)
        return None

    return response.json()


def find_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id.replace('-', '')}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(response.text)
        return None

    return response.json()


def update_property(page_id, body):
    url = f"https://api.notion.com/v1/pages/{page_id.replace('-', '')}"

    response = requests.patch(url, headers=headers, json=body)

    if response.status_code != 200:
        print(response.text)
        return None

    return response.json()