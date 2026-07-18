import requests
import json

url = "http://localhost:8080/api/v1/chat/stream"
headers = {"Content-Type": "application/json"}
payload = {
    "query": "What is 2+2?",
    "session_id": "test-123"
}

print("Sending request to chat/stream...")
response = requests.post(url, headers=headers, json=payload, stream=True)
print(f"Status: {response.status_code}")

for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        print(decoded_line)

