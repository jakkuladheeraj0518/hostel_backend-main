import requests
import json

url = "http://127.0.0.1:8000/admins/"
data = {
    "admin_name": "nagendra",
    "email": "nagendrareddy1017@gmail.com",
    "is_active": True
}

response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
