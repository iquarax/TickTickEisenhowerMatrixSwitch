"""
Test różnych endpointów TickTick API
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv("TICKTICK_ACCESS_TOKEN")
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

endpoints_to_test = [
    "https://api.ticktick.com/open/v1/task",
    "https://api.ticktick.com/api/v2/task",
    "https://api.ticktick.com/api/v2/batch/check/0",
    "https://ticktick.com/api/v2/batch/check/0",
    "https://api.ticktick.com/open/v1/project",
]

print("=" * 70)
print("🔍 Test różnych endpointów TickTick API")
print("=" * 70)
print()

for endpoint in endpoints_to_test:
    print(f"Testing: {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Sukces! Typ danych: {type(data)}")
            if isinstance(data, list):
                print(f"  Liczba elementów: {len(data)}")
            elif isinstance(data, dict):
                print(f"  Klucze: {list(data.keys())[:5]}")
        else:
            print(f"  ❌ Błąd: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ Wyjątek: {str(e)[:100]}")
    print()
