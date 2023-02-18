import requests
import json

response = requests.get('http://localhost:8000/2aic', params={
    'name': 'Веб-дизайн и разработка 1 (гр.215-8-1)',
    'dt': '2023-02-16'
})
r_json = response.json()
r_json = json.loads(r_json)
print(r_json['text'])
