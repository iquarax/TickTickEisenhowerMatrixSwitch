"""
Moduł autoryzacji OAuth2 dla TickTick - zintegrowany ze Streamlit
"""

import requests
import base64
from urllib.parse import urlencode, parse_qs, urlparse
from typing import Optional, Dict
import streamlit as st


class TickTickAuth:
    """Klasa obsługująca autoryzację OAuth2 dla TickTick"""
    
    AUTHORIZATION_URL = "https://ticktick.com/oauth/authorize"
    TOKEN_URL = "https://ticktick.com/oauth/token"
    DEFAULT_SCOPE = "tasks:read tasks:write"
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Inicjalizacja klienta OAuth2
        
        Args:
            client_id: Client ID z TickTick Developer Portal
            client_secret: Client Secret z TickTick Developer Portal
            redirect_uri: URL przekierowania (musi być zgodny z ustawieniami aplikacji)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generuje URL autoryzacji OAuth2
        
        Args:
            state: Opcjonalny parametr state dla zabezpieczenia CSRF
            
        Returns:
            URL do autoryzacji użytkownika
        """
        params = {
            "client_id": self.client_id,
            "scope": self.DEFAULT_SCOPE,
            "state": state or "streamlit_auth",
            "redirect_uri": self.redirect_uri,
            "response_type": "code"
        }
        
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict[str, str]:
        """
        Wymienia kod autoryzacyjny na access token
        
        Args:
            code: Kod autoryzacyjny z callback URL
            
        Returns:
            Słownik z tokenami (access_token, refresh_token, expires_in, token_type)
            
        Raises:
            requests.exceptions.HTTPError: W przypadku błędu HTTP
        """
        # Przygotuj Basic Authentication
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "scope": self.DEFAULT_SCOPE,
            "redirect_uri": self.redirect_uri
        }
        
        response = requests.post(
            self.TOKEN_URL,
            headers=headers,
            data=data
        )
        
        response.raise_for_status()
        return response.json()
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Odświeża access token używając refresh token
        
        Args:
            refresh_token: Refresh token otrzymany podczas pierwszej autoryzacji
            
        Returns:
            Słownik z nowymi tokenami
            
        Raises:
            requests.exceptions.HTTPError: W przypadku błędu HTTP
        """
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(
            self.TOKEN_URL,
            headers=headers,
            data=data
        )
        
        response.raise_for_status()
        return response.json()


def init_auth_from_env() -> Optional[TickTickAuth]:
    """
    Inicjalizuje obiekt TickTickAuth z danych ze zmiennych środowiskowych lub Streamlit secrets
    
    Returns:
        Obiekt TickTickAuth lub None jeśli brak wymaganych zmiennych
    """
    import os
    from dotenv import load_dotenv
    
    # Próbuj najpierw Streamlit secrets (dla Streamlit Cloud)
    try:
        client_id = st.secrets.get("TICKTICK_CLIENT_ID")
        client_secret = st.secrets.get("TICKTICK_CLIENT_SECRET")
        redirect_uri = st.secrets.get("TICKTICK_REDIRECT_URI", "http://localhost:8501")
        
        if client_id and client_secret:
            return TickTickAuth(client_id, client_secret, redirect_uri)
    except Exception:
        pass
    
    # Fallback na .env (dla lokalnego uruchomienia)
    load_dotenv()
    
    client_id = os.getenv("TICKTICK_CLIENT_ID")
    client_secret = os.getenv("TICKTICK_CLIENT_SECRET")
    redirect_uri = os.getenv("TICKTICK_REDIRECT_URI", "http://localhost:8501")
    
    if not client_id or not client_secret:
        return None
    
    return TickTickAuth(client_id, client_secret, redirect_uri)


def extract_code_from_url(url: str) -> Optional[str]:
    """
    Wyciąga kod autoryzacyjny z URL callback
    
    Args:
        url: URL zawierający parametr 'code'
        
    Returns:
        Kod autoryzacyjny lub None jeśli nie znaleziono
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("code", [None])[0]


def handle_oauth_callback() -> Optional[str]:
    """
    Obsługuje callback OAuth2 w Streamlit
    Sprawdza query parameters w URL i zwraca kod autoryzacyjny jeśli istnieje
    
    Returns:
        Kod autoryzacyjny lub None
    """
    try:
        # Dla Streamlit 1.29.0 i starszych
        query_params = st.experimental_get_query_params()
        code = query_params.get("code")
        if code:
            # Query params zwracają zawsze listę
            if isinstance(code, list) and len(code) > 0:
                return code[0]
            return code
    except Exception as e:
        # Ciche niepowodzenie - nie ma query params
        pass
    
    return None
