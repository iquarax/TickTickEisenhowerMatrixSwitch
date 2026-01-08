"""
Test aktualizacji daty zadania w TickTick API
"""
import json
import time
from ticktick_api import TickTickAPI
from datetime import datetime

# Inicjalizacja API
api = TickTickAPI()

# ID zadania do testowania
task_id = "67a35844d5bf3b00000003bb"

print("=" * 60)
print("KROK 1: Pobieranie oryginalnego zadania")
print("=" * 60)

# Pobierz wszystkie zadania i znajdź nasze
all_tasks = api.get_tasks()
original_task = None
for task in all_tasks:
    if task.get("id") == task_id:
        original_task = task
        break

if not original_task:
    print(f"❌ Nie znaleziono zadania o ID: {task_id}")
    exit(1)

print(f"✅ Znaleziono zadanie: {original_task.get('title')}")
print(f"Obecna data: {original_task.get('dueDate')}")
print("\nPełne dane zadania:")
print(json.dumps(original_task, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("KROK 2: Aktualizacja daty na 28 stycznia 2026")
print("=" * 60)

# Przygotuj nową datę (28 stycznia 2026, ta sama godzina co oryginał)
new_date = "2026-01-28T07:30:00.000+0000"

# Dane do aktualizacji - zachowaj wszystkie ważne pola
update_data = {
    "id": task_id,
    "projectId": original_task["projectId"],
    "title": original_task["title"],
    "startDate": new_date,
    "dueDate": new_date,
    "timeZone": original_task.get("timeZone", "Europe/Warsaw"),
    "isAllDay": original_task.get("isAllDay", False),
    "priority": original_task.get("priority", 0),
    "status": original_task.get("status", 0),
}

# Zachowaj content/desc jeśli istnieją
if "content" in original_task:
    update_data["content"] = original_task["content"]
if "desc" in original_task:
    update_data["desc"] = original_task["desc"]

# Zachowaj tagi jeśli istnieją
if "tags" in original_task:
    update_data["tags"] = original_task["tags"]

# Zachowaj przypomnienia jeśli istnieją
if "reminders" in original_task:
    update_data["reminders"] = original_task["reminders"]

print(f"Wysyłanie aktualizacji do TickTick API...")
print(f"URL: {api.base_url}/task/{task_id}")

import requests
response = requests.post(
    f"{api.base_url}/task/{task_id}",
    headers=api.headers,
    json=update_data,
    timeout=10
)

print(f"Status odpowiedzi: {response.status_code}")

if response.status_code == 200:
    updated_data = response.json()
    print(f"✅ Zadanie zaktualizowane pomyślnie!")
    print(f"Nowa data: {updated_data.get('dueDate')}")
else:
    print(f"❌ Błąd aktualizacji: {response.text}")
    exit(1)

print("\n" + "=" * 60)
print("KROK 3: Oczekiwanie 15 sekund...")
print("=" * 60)

for i in range(15, 0, -1):
    print(f"⏳ Pozostało {i} sekund...", end="\r")
    time.sleep(1)
print("\n✅ Oczekiwanie zakończone!")

print("\n" + "=" * 60)
print("KROK 4: Pobieranie zaktualizowanego zadania")
print("=" * 60)

# Pobierz ponownie wszystkie zadania
all_tasks = api.get_tasks()
updated_task = None
for task in all_tasks:
    if task.get("id") == task_id:
        updated_task = task
        break

if not updated_task:
    print(f"❌ Nie znaleziono zadania o ID: {task_id}")
    exit(1)

print(f"✅ Zadanie pobrane ponownie!")
print("\n" + "=" * 60)
print("PORÓWNANIE WYNIKÓW")
print("=" * 60)

print("\n📅 DATY:")
print(f"  Przed: {original_task.get('dueDate')}")
print(f"  Po:    {updated_task.get('dueDate')}")

print("\n📋 PEŁNE DANE ZAKTUALIZOWANEGO ZADANIA:")
print(json.dumps(updated_task, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("TEST ZAKOŃCZONY")
print("=" * 60)
