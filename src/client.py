import requests
import json

url = 'http://127.0.0.1:5021/gopt'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

data = [14086346]
# data = list(range(14004770, 14004740, -1))

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.content)