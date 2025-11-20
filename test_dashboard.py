import requests

response = requests.get("http://127.0.0.1:8000/api/v1/dashboard/")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
