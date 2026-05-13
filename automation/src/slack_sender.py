import requests

headers = {
    'Content-Type': 'application/json'
}

def send_message(response_url, message):
    requests.post(response_url, headers=headers, json=message)

def update_message(response_url, message):
    message['replace_original'] = True

    requests.post(response_url, headers=headers, json=message)

def delete_message(response_url):
    payload = {
        "delete_original": True
    }

    requests.post(response_url, headers=headers, json=payload)
