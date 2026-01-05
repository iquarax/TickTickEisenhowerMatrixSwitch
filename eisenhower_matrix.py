"""
Logika Macierzy Eisenhowera
"""

from typing import List, Dict
from config import TAG_MAPPING, CONTEXTS, date_filter_function
from ticktick_api import parse_task_tags, is_task_completed


def filter_tasks_by_context(tasks: List[Dict], context_key: str) -> List[Dict]:
    """
    Filtruje zadania według wybranego kontekstu (na podstawie daty)
    
    Args:
        tasks: Lista wszystkich zadań
        context_key: Klucz kontekstu z config.CONTEXTS
        
    Returns:
        Przefiltrowana lista zadań
    """
    if context_key not in CONTEXTS:
        return tasks
    
    # Pobierz funkcję filtrującą dla tego kontekstu
    filter_func = date_filter_function(context_key)
    
    # Filtruj zadania używając funkcji
    filtered = [task for task in tasks if filter_func(task)]
    
    return filtered


def categorize_tasks_to_quadrants(tasks: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Segreguje zadania do odpowiednich ćwiartek Macierzy Eisenhowera na podstawie tagów
    
    Args:
        tasks: Lista zadań do kategoryzacji
        
    Returns:
        Słownik z kluczami Q1, Q2, Q3, Q4 zawierającymi listy zadań
    """
    quadrants = {
        "Q1": [],
        "Q2": [],
        "Q3": [],
        "Q4": []
    }
    
    for task in tasks:
        # Pomiń zadania już wykonane
        if is_task_completed(task):
            continue
        
        # Pobierz tagi zadania
        task_tags = parse_task_tags(task)
        
        # Kategoryzuj na podstawie tagów (priorytet: fast > important > think > bez tagów)
        if "#fast" in task_tags:
            quadrants["Q1"].append(task)
        elif "#important" in task_tags:
            quadrants["Q2"].append(task)
        elif "#think" in task_tags:
            quadrants["Q3"].append(task)
        else:
            # Zadania bez tagów lub z innymi tagami
            quadrants["Q4"].append(task)
    
    return quadrants


def get_quadrant_stats(quadrants: Dict[str, List[Dict]]) -> Dict[str, int]:
    """
    Oblicza statystyki dla ćwiartek
    
    Args:
        quadrants: Słownik z zadaniami w ćwiartkach
        
    Returns:
        Słownik z liczbą zadań w każdej ćwiartce
    """
    return {
        quadrant: len(tasks)
        for quadrant, tasks in quadrants.items()
    }


def sort_tasks_by_deadline(tasks: List[Dict]) -> List[Dict]:
    """
    Sortuje zadania według deadline (najstarsze najpierw)
    
    Args:
        tasks: Lista zadań
        
    Returns:
        Posortowana lista zadań
    """
    # Zadania z deadline na górze
    with_deadline = [t for t in tasks if t.get("dueDate")]
    without_deadline = [t for t in tasks if not t.get("dueDate")]
    
    # Sortuj zadania z deadline
    with_deadline.sort(key=lambda x: x.get("dueDate", ""))
    
    return with_deadline + without_deadline
