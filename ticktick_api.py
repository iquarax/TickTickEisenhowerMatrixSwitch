"""
Moduł komunikacji z TickTick Open API
"""

import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from config import TICKTICK_API_BASE_URL

load_dotenv()


class TickTickAPI:
    """Klasa obsługująca połączenie z TickTick API"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Inicjalizacja klienta API
        
        Args:
            access_token: Token dostępu (jeśli None, pobiera z .env)
        """
        self.access_token = access_token or os.getenv("TICKTICK_ACCESS_TOKEN")
        self.base_url = TICKTICK_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def is_configured(self) -> bool:
        """Sprawdza czy API jest poprawnie skonfigurowane"""
        return bool(self.access_token and self.access_token != "your_access_token_here")
    
    def get_tasks(self) -> List[Dict]:
        """
        Pobiera wszystkie zadania z TickTick (ze wszystkich projektów)
        
        Returns:
            Lista zadań w formacie JSON
        """
        all_tasks = []
        
        try:
            # Najpierw pobierz listę projektów
            projects = self.get_projects()
            
            if not projects:
                print("Brak projektów do pobrania")
                return []
            
            # Następnie pobierz zadania z każdego projektu
            for project in projects:
                project_id = project.get("id")
                if project_id:
                    try:
                        project_tasks = self.get_project_tasks(project_id)
                        all_tasks.extend(project_tasks)
                    except Exception as e:
                        print(f"Błąd pobierania zadań z projektu {project.get('name', project_id)}: {e}")
                        continue
            
            return all_tasks
            
        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania zadań: {e}")
            return []
    
    def get_project_tasks(self, project_id: str) -> List[Dict]:
        """
        Pobiera zadania z konkretnego projektu
        
        Args:
            project_id: ID projektu w TickTick
            
        Returns:
            Lista zadań z danego projektu
        """
        try:
            # Pobierz szczegóły projektu, które zawierają zadania
            response = requests.get(
                f"{self.base_url}/project/{project_id}/data",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            project_data = response.json()
            
            # Wyciągnij zadania z danych projektu
            tasks = project_data.get("tasks", [])
            return tasks
            
        except requests.exceptions.RequestException as e:
            # Spróbuj alternatywnego endpointa
            try:
                response = requests.get(
                    f"{self.base_url}/project/{project_id}",
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                project_data = response.json()
                tasks = project_data.get("tasks", [])
                return tasks
            except:
                print(f"Błąd pobierania zadań projektu: {e}")
                return []
    
    def complete_task(self, task_id: str, project_id: str) -> bool:
        """
        Oznacza zadanie jako wykonane
        
        Args:
            task_id: ID zadania
            project_id: ID projektu
            
        Returns:
            True jeśli sukces, False w przeciwnym razie
        """
        try:
            response = requests.post(
                f"{self.base_url}/project/{project_id}/task/{task_id}/complete",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Błąd oznaczania zadania jako wykonane: {e}")
            return False
    
    def get_projects(self) -> List[Dict]:
        """
        Pobiera listę wszystkich projektów użytkownika
        
        Returns:
            Lista projektów
        """
        try:
            response = requests.get(
                f"{self.base_url}/project",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Błąd pobierania projektów: {e}")
            return []
    
    def update_task_tags(self, task_id: str, project_id: str, new_tags: List[str], original_task: Dict = None) -> Optional[Dict]:
        """
        Aktualizuje tagi zadania
        
        Args:
            task_id: ID zadania
            project_id: ID projektu
            new_tags: Lista nowych tagów (bez #)
            original_task: Oryginalne dane zadania (aby zachować inne pola)
            
        Returns:
            Zaktualizowane dane zadania jeśli sukces, None w przeciwnym razie
        """
        try:
            # Dane do aktualizacji - zachowaj ważne pola z oryginalnego zadania
            data = {
                "id": task_id,
                "projectId": project_id,
                "tags": new_tags
            }
            
            # Jeśli mamy oryginalne zadanie, zachowaj ważne pola
            if original_task:
                # Zachowaj datę bez zmiany czasu
                if "startDate" in original_task:
                    data["startDate"] = original_task["startDate"]
                if "dueDate" in original_task:
                    data["dueDate"] = original_task["dueDate"]
                # Zachowaj flagę "isAllDay" jeśli istnieje
                if "isAllDay" in original_task:
                    data["isAllDay"] = original_task["isAllDay"]
                # Zachowaj tytuł i inne podstawowe pola
                if "title" in original_task:
                    data["title"] = original_task["title"]
                if "content" in original_task:
                    data["content"] = original_task["content"]
            
            print(f"DEBUG: Aktualizacja tagów zadania {task_id}")
            print(f"DEBUG: Nowe tagi: {new_tags}")
            print(f"DEBUG: isAllDay: {data.get('isAllDay', 'brak')}")
            print(f"DEBUG: URL: {self.base_url}/task/{task_id}")
            
            response = requests.post(
                f"{self.base_url}/task/{task_id}",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            print(f"DEBUG: Status odpowiedzi: {response.status_code}")
            print(f"DEBUG: Treść odpowiedzi: {response.text[:200]}")
            
            response.raise_for_status()
            return response.json()  # Zwracamy zaktualizowane dane zadania
        except requests.exceptions.RequestException as e:
            print(f"Błąd aktualizacji tagów zadania: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"DEBUG: Treść błędu: {e.response.text}")
            return None
    
    def update_task_date(self, task_id: str, project_id: str, new_date: str, original_task: Dict = None) -> Optional[Dict]:
        """
        Aktualizuje datę zadania (startDate i dueDate)
        
        Args:
            task_id: ID zadania
            project_id: ID projektu
            new_date: Nowa data w formacie ISO (YYYY-MM-DDTHH:MM:SS.000+0000)
            original_task: Oryginalne dane zadania (aby zachować inne pola)
            
        Returns:
            Zaktualizowane dane zadania jeśli sukces, None w przeciwnym razie
        """
        try:
            # Dane do aktualizacji - zachowaj wszystkie ważne pola
            data = {
                "id": task_id,
                "projectId": project_id,
                "startDate": new_date,
                "dueDate": new_date
            }
            
            # Jeśli mamy oryginalne zadanie, zachowaj wszystkie pozostałe pola
            if original_task:
                # Zachowaj podstawowe pola
                if "title" in original_task:
                    data["title"] = original_task["title"]
                if "content" in original_task:
                    data["content"] = original_task["content"]
                if "desc" in original_task:
                    data["desc"] = original_task["desc"]
                
                # Zachowaj ustawienia czasu
                if "timeZone" in original_task:
                    data["timeZone"] = original_task["timeZone"]
                if "isAllDay" in original_task:
                    data["isAllDay"] = original_task["isAllDay"]
                
                # Zachowaj priorytet i status
                if "priority" in original_task:
                    data["priority"] = original_task["priority"]
                if "status" in original_task:
                    data["status"] = original_task["status"]
                
                # Zachowaj tagi
                if "tags" in original_task:
                    data["tags"] = original_task["tags"]
                
                # Zachowaj przypomnienia
                if "reminders" in original_task:
                    data["reminders"] = original_task["reminders"]
            
            print(f"DEBUG: Aktualizacja daty zadania {task_id}")
            print(f"DEBUG: Nowa data: {new_date}")
            
            response = requests.post(
                f"{self.base_url}/task/{task_id}",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            print(f"DEBUG: Status odpowiedzi: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Błąd aktualizacji daty zadania: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"DEBUG: Treść błędu: {e.response.text}")
            return None


def parse_task_tags(task: Dict) -> List[str]:
    """
    Wyciąga tagi z zadania TickTick
    
    Args:
        task: Słownik z danymi zadania
        
    Returns:
        Lista tagów (z #)
    """
    tags = task.get("tags", [])
    return [f"#{tag}" for tag in tags]


def get_task_priority(task: Dict) -> int:
    """
    Pobiera priorytet zadania
    
    Args:
        task: Słownik z danymi zadania
        
    Returns:
        Priorytet (0, 1, 3, 5)
    """
    return task.get("priority", 0)


def is_task_completed(task: Dict) -> bool:
    """
    Sprawdza czy zadanie jest wykonane
    
    Args:
        task: Słownik z danymi zadania
        
    Returns:
        True jeśli wykonane
    """
    return task.get("status", 0) == 2  # Status 2 = completed


def move_task_to_quadrant(api: 'TickTickAPI', task: Dict, target_quadrant: str) -> Optional[Dict]:
    """
    Przenosi zadanie do innej ćwiartki poprzez aktualizację tagów
    
    Args:
        api: Instancja TickTickAPI
        task: Słownik z danymi zadania
        target_quadrant: Docelowa ćwiartka (Q1, Q2, Q3, Q4)
        
    Returns:
        Zaktualizowane dane zadania jeśli sukces, None w przeciwnym razie
    """
    # Mapowanie ćwiartek na tagi
    quadrant_tags = {
        "Q1": "fast",
        "Q2": "important",
        "Q3": "think",
        "Q4": None  # Brak tagu specjalnego
    }
    
    task_id = task.get("id")
    project_id = task.get("projectId")
    task_title = task.get("title", "")
    
    print(f"\n=== PRZENOSZENIE ZADANIA ===")
    print(f"Zadanie: {task_title}")
    print(f"Task ID: {task_id}")
    print(f"Project ID: {project_id}")
    print(f"Docelowa ćwiartka: {target_quadrant}")
    
    if not task_id or not project_id:
        print("BŁĄD: Brak task_id lub project_id")
        return None
    
    # Pobierz aktualne tagi (bez #)
    current_tags = task.get("tags", [])
    print(f"Aktualne tagi: {current_tags}")
    
    # Usuń stare tagi ćwiartek
    special_tags = {"fast", "important", "think"}
    new_tags = [tag for tag in current_tags if tag not in special_tags]
    
    # Dodaj nowy tag (jeśli nie jest Q4)
    target_tag = quadrant_tags.get(target_quadrant)
    if target_tag:
        new_tags.append(target_tag)
    
    print(f"Nowe tagi: {new_tags}")
    
    # Aktualizuj w TickTick - przekaż oryginalne zadanie aby zachować wszystkie pola
    updated_task = api.update_task_tags(task_id, project_id, new_tags, original_task=task)
    print(f"Wynik aktualizacji: {updated_task is not None}")
    return updated_task
