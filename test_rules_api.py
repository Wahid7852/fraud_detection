import requests
import json

def test_rules():
    try:
        response = requests.get("http://localhost:8000/api/rules")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Successfully fetched rules:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_rules()
