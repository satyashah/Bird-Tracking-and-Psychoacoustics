import requests

url = "http://10.104.107.70:8080/switch"
response = requests.get(url)

if response.status_code == 200:
    print("Request successful")
else:
    print("Request failed with status code:", response.status_code)