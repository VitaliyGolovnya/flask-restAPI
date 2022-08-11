import requests

HOST = 'http://127.0.0.1:5000'



response = requests.post(f'{HOST}/ads/',
                         json={'title': 'demo_title',
                               'text': 'demo_text',
                               'owner': 'demo_owner'})
print(response.status_code)
print(response.text)

response = requests.get(f'{HOST}/ads/1')
print(response.status_code)
print(response.text)

response = requests.patch(f'{HOST}/ads/1', json={'title': 'demo_title_v2'})
print(response.status_code)
print(response.text)

response = requests.delete(f'{HOST}/ads/1')
print(response.status_code)
print(response.text)