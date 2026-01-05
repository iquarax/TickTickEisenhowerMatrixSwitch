"""
Test zaktualizowanego pobierania zadań
"""

from ticktick_api import TickTickAPI

print("=" * 60)
print("🔍 Test pobierania zadań z wszystkich projektów")
print("=" * 60)
print()

api = TickTickAPI()

print("Pobieranie zadań...")
tasks = api.get_tasks()

print(f"✅ Pobrano {len(tasks)} zadań")
print()

if tasks:
    print("Przykładowe zadania:")
    for i, task in enumerate(tasks[:5], 1):
        title = task.get("title", "Bez tytułu")
        priority = task.get("priority", 0)
        tags = task.get("tags", [])
        print(f"{i}. {title}")
        print(f"   Priorytet: {priority}, Tagi: {tags}")
        print()
else:
    print("⚠️ Brak zadań")
