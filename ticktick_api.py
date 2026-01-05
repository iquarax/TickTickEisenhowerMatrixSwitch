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
