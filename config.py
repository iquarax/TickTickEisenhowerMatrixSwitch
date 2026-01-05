"""
Konfiguracja kontekstów i reguł dla Macierzy Eisenhowera
"""
from datetime import datetime, timedelta, date, timezone

def get_today():
    """Zwraca dzisiejszą datę jako string YYYY-MM-DD"""
    return datetime.now().date()

def get_yesterday():
    """Zwraca wczorajszą datę jako string YYYY-MM-DD"""
    return (datetime.now() - timedelta(days=1)).date()

def get_tomorrow():
    """Zwraca jutrzejszą datę jako string YYYY-MM-DD"""
    return (datetime.now() + timedelta(days=1)).date()

def get_task_date(task):
    """
    Pobiera datę zadania z pola dueDate i zwraca jako date object.
    Zwraca None jeśli zadanie nie ma daty.
    Konwertuje z UTC na lokalną strefę czasową.
    """
    due_date_str = task.get("dueDate", "")
    if not due_date_str:
        return None
    
    try:
        # TickTick używa ISO format UTC, np. "2026-01-05T23:00:00.000+0000"
        # Parsujemy jako UTC datetime
        dt_utc = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        # Konwertujemy na lokalną strefę czasową
        dt_local = dt_utc.astimezone()
        # Zwracamy tylko datę (bez czasu)
        return dt_local.date()
    except:
        return None

def date_filter_function(context_key):
    """
    Zwraca funkcję filtrującą zadania według daty dla danego kontekstu.
    Funkcja przyjmuje zadanie i zwraca True jeśli zadanie pasuje do kontekstu.
    """
    today = get_today()
    
    if context_key == "Wszystkie":
        return lambda task: True
    
    elif context_key == "Dzisiejsze":
        return lambda task: get_task_date(task) == today
    
    elif context_key == "Wczorajsze":
        yesterday = get_yesterday()
        return lambda task: get_task_date(task) == yesterday
    
    elif context_key == "Jutrzejsze":
        tomorrow = get_tomorrow()
        return lambda task: get_task_date(task) == tomorrow
    
    elif context_key == "Zaległe":
        return lambda task: get_task_date(task) is not None and get_task_date(task) < today
    
    elif context_key == "Przyszłe":
        return lambda task: get_task_date(task) is not None and get_task_date(task) > today
    
    else:
        # Domyślnie zwróć wszystkie
        return lambda task: True

def get_context_description(context_key):
    """
    Zwraca dynamiczny opis kontekstu z aktualną datą.
    """
    today = get_today()
    yesterday = get_yesterday()
    tomorrow = get_tomorrow()
    
    descriptions = {
        "Wszystkie": "Wyświetla wszystkie zadania bez filtrowania",
        "Dzisiejsze": f"Zadania z datą dzisiejszą ({today.strftime('%d.%m.%Y')})",
        "Wczorajsze": f"Zadania z datą wczorajszą ({yesterday.strftime('%d.%m.%Y')})",
        "Jutrzejsze": f"Zadania z datą jutrzejszą ({tomorrow.strftime('%d.%m.%Y')})",
        "Zaległe": "Zadania z datami wcześniejszymi niż dzisiaj",
        "Przyszłe": "Zadania z datami późniejszymi niż dzisiaj"
    }
    
    return descriptions.get(context_key, "")

# Definicje kontekstów (profili)
CONTEXTS = {
    "Wszystkie": {
        "name": "🌐 Wszystkie zadania",
        "tags": [],  # Pusty = wszystkie
        "description": "Wyświetla wszystkie zadania bez filtrowania"
    },
    "Dzisiejsze": {
        "name": "📅 Dzisiejsze zadania",
        "tags": [],
        "description": "Zadania z datą dzisiejszą (5 stycznia 2026)"
    },
    "Wczorajsze": {
        "name": "⏮️ Wczorajsze zadania",
        "tags": [],
        "description": "Zadania z datą wczorajszą (4 stycznia 2026)"
    },
    "Jutrzejsze": {
        "name": "⏭️ Jutrzejsze zadania",
        "tags": [],
        "description": "Zadania z datą jutrzejszą (6 stycznia 2026)"
    },
    "Zaległe": {
        "name": "⚠️ Zaległe zadania",
        "tags": [],
        "description": "Zadania z datami wcześniejszymi niż dzisiaj"
    },
    "Przyszłe": {
        "name": "🔮 Przyszłe zadania",
        "tags": [],
        "description": "Zadania z datami późniejszymi niż dzisiaj"
    }
}

# Mapowanie tagów TickTick na ćwiartki Macierzy Eisenhowera
TAG_MAPPING = {
    "fast": "Q1",       # Tag #fast → Q1 (Szybkie)
    "important": "Q2",  # Tag #important → Q2 (Ważne)
    "think": "Q3",      # Tag #think → Q3 (Myślenie)
}
# Zadania bez tych tagów trafiają do Q4 (Zarządzanie)

# Konfiguracja ćwiartek
QUADRANTS = {
    "Q1": {
        "name": "🏎️ Ćwiartka 1: Szybkie",
        "description": "DO IT NOW",
        "color": "#ffec44",
        "action": "Wykonaj szybko!"
    },
    "Q2": {
        "name": "❗ Ćwiartka 2: Ważne",
        "description": "DO IT",
        "color": "#fc0303",
        "action": "Wykonaj"
    },
    "Q3": {
        "name": "🧠 Ćwiartka 3: Myślenie",
        "description": "THINK",
        "color": "#080cf1",
        "action": "Przemyśl"
    },
    "Q4": {
        "name": "🧩 Ćwiartka 4: Zarządzanie",
        "description": "MANAGE",
        "color": "#cccccc",
        "action": "Zarządź"
    }
}

# TickTick API Configuration
TICKTICK_API_BASE_URL = "https://api.ticktick.com/open/v1"
