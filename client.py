import requests


data = requests.post('http://127.0.0.1:5000/advertisement/',
                     json={
                         'title': 'advertisement_1',
                         'description': 'description_1',
                         'owner': 'user_1'
                     })
print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/advertisement/1')
print(data.status_code)
print(data.text)

data = requests.patch('http://127.0.0.1:5000/advertisement/1', json={'title': 'advertisement_1!!!'})
print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/advertisement/1')
print(data.status_code)
print(data.text)

data = requests.delete('http://127.0.0.1:5000/advertisement/1')
print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/advertisement/1')
print(data.status_code)
print(data.text)
