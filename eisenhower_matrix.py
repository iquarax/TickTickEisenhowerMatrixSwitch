"""
Logika Macierzy Eisenhowera
"""

from typing import List, Dict
from config import PRIORITY_MAPPING, CONTEXTS
from ticktick_api import parse_task_tags, get_task_priority, is_task_completed


def filter_tasks_by_context(tasks: List[Dict], context_key: str) -> List[Dict]:
    """
    Filtruje zadania według wybranego kontekstu
    
    Args:
        tasks: Lista wszystkich zadań
        context_key: Klucz kontekstu z config.CONTEXTS
        
    Returns:
        Przefiltrowana lista zadań
    """
    if context_key not in CONTEXTS:
        return tasks
    
    context_tags = CONTEXTS[context_key]["tags"]
    
    # Jeśli kontekst nie ma tagów (np. "Wszystkie"), zwróć wszystkie
    if not context_tags:
        return tasks
    
    filtered = []
    for task in tasks:
        task_tags = parse_task_tags(task)
        # Sprawdź czy którykolwiek tag zadania jest w tagach kontekstu
        if any(tag in context_tags for tag in task_tags):
            filtered.append(task)
    
    return filtered


def categorize_tasks_to_quadrants(tasks: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Segreguje zadania do odpowiednich ćwiartek Macierzy Eisenhowera
    
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
        
        priority = get_task_priority(task)
        quadrant = PRIORITY_MAPPING.get(priority, "Q4")
        quadrants[quadrant].append(task)
    
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
