import requests
import json

url = "http://127.0.0.1:8000/admins/bulk-assign"
data = {
    "admin_id": 3,
    "hostel_ids": [5, 1],
    "permission_level": "read"
}

response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
