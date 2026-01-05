"""
Skrypt testowy do sprawdzenia połączenia z TickTick API
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv("TICKTICK_ACCESS_TOKEN")

print("=" * 60)
print("🔍 Test połączenia z TickTick API")
print("=" * 60)
print()
print(f"Access Token: {access_token[:20]}...{access_token[-10:]}")
print()

# Test 1: Pobierz informacje o użytkowniku
print("Test 1: Pobieranie informacji o użytkowniku...")
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        "https://api.ticktick.com/open/v1/user",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Sukces!")
        print(f"Użytkownik: {response.json()}")
    else:
        print(f"❌ Błąd: {response.text}")
except Exception as e:
    print(f"❌ Wyjątek: {e}")

print()
print("-" * 60)
print()

# Test 2: Pobierz projekty
print("Test 2: Pobieranie projektów...")
try:
    response = requests.get(
        "https://api.ticktick.com/open/v1/project",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"✅ Sukces! Liczba projektów: {len(projects)}")
        for project in projects[:3]:
            print(f"  - {project.get('name', 'Bez nazwy')} (ID: {project.get('id')})")
    else:
        print(f"❌ Błąd: {response.text}")
except Exception as e:
    print(f"❌ Wyjątek: {e}")

print()
print("-" * 60)
print()

# Test 3: Pobierz zadania
print("Test 3: Pobieranie zadań...")
try:
    response = requests.get(
        "https://api.ticktick.com/open/v1/task",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Headers response: {dict(response.headers)}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"✅ Sukces! Liczba zadań: {len(tasks)}")
    else:
        print(f"❌ Błąd: {response.status_code}")
        print(f"Response text: {response.text}")
        print(f"Response content: {response.content}")
except Exception as e:
    print(f"❌ Wyjątek: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
