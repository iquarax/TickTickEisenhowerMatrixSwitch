"""
Konfiguracja kontekstów i reguł dla Macierzy Eisenhowera
"""

# Definicje kontekstów (profili)
CONTEXTS = {
    "Wszystkie": {
        "name": "🌐 Wszystkie zadania",
        "tags": [],  # Pusty = wszystkie
        "description": "Wyświetla wszystkie zadania bez filtrowania"
    },
    "Praca": {
        "name": "💼 Praca",
        "tags": ["#praca", "#biuro", "#projekt", "#klient", "#spotkanie"],
        "description": "Zadania służbowe i zawodowe"
    },
    "Dom": {
        "name": "🏠 Dom",
        "tags": ["#dom", "#fast", "#zakupy", "#sprzątanie", "#naprawa"],
        "description": "Zadania domowe i rodzinne"
    },
    "Deep Work": {
        "name": "🧠 Deep Work",
        "tags": ["#deepwork", "#nauka", "#rozwój", "#czytanie", "#kurs"],
        "description": "Zadania wymagające głębokiej koncentracji"
    },
    "Weekend": {
        "name": "🎯 Weekend",
        "tags": ["#weekend", "#hobby", "#relaks", "#sport", "#przyjaciele"],
        "description": "Aktywności weekendowe i rekreacyjne"
    },
    "Projekty": {
        "name": "📊 Projekty",
        "tags": ["#projekt", "#startup", "#side-project"],
        "description": "Projekty poboczne i inicjatywy"
    }
}

# Mapowanie priorytetów TickTick na ćwiartki Macierzy Eisenhowera
# TickTick Priority: 0 = None, 1 = Low, 3 = Medium, 5 = High
PRIORITY_MAPPING = {
    5: "Q1",  # High Priority → Q1 (Ważne i Pilne)
    3: "Q2",  # Medium Priority → Q2 (Ważne, Niepilne)
    1: "Q3",  # Low Priority → Q3 (Nieważne, Pilne)
    0: "Q4"   # No Priority → Q4 (Nieważne, Niepilne)
}

# Konfiguracja ćwiartek
QUADRANTS = {
    "Q1": {
        "name": "🔴 Ćwiartka 1: Pilne i Ważne",
        "description": "DO IT NOW - Crisis, Deadlines",
        "color": "#ff4444",
        "action": "Wykonaj natychmiast!"
    },
    "Q2": {
        "name": "🟢 Ćwiartka 2: Niepilne, ale Ważne",
        "description": "SCHEDULE - Planning, Development",
        "color": "#44ff44",
        "action": "Zaplanuj czas"
    },
    "Q3": {
        "name": "🟡 Ćwiartka 3: Pilne, ale Nieważne",
        "description": "DELEGATE - Interruptions, Meetings",
        "color": "#ffaa44",
        "action": "Deleguj jeśli możliwe"
    },
    "Q4": {
        "name": "⚪ Ćwiartka 4: Niepilne i Nieważne",
        "description": "ELIMINATE - Time Wasters",
        "color": "#cccccc",
        "action": "Usuń lub ogranicz"
    }
}

# TickTick API Configuration
TICKTICK_API_BASE_URL = "https://api.ticktick.com/open/v1"
