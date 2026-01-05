"""
Skrypt pomocniczy do uzyskania Access Token z TickTick API przez OAuth2
"""

import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import base64
import os
from dotenv import load_dotenv, set_key

# Ładuj istniejące zmienne z .env
load_dotenv()

def get_authorization_url(client_id: str, redirect_uri: str, scope: str = "tasks:read tasks:write") -> str:
    """
    Generuje URL autoryzacji dla użytkownika
    
    Args:
        client_id: Client ID z TickTick Developer Portal
        redirect_uri: URL przekierowania (musi być taki sam jak w ustawieniach aplikacji)
        scope: Zakres uprawnień
        
    Returns:
        URL do autoryzacji
    """
    params = {
        "client_id": client_id,
        "scope": scope,
        "state": "random_state_string",
        "redirect_uri": redirect_uri,
        "response_type": "code"
    }
    
    base_url = "https://ticktick.com/oauth/authorize"
    return f"{base_url}?{urlencode(params)}"


def exchange_code_for_token(client_id: str, client_secret: str, code: str, 
                            redirect_uri: str, scope: str = "tasks:read tasks:write") -> dict:
    """
    Wymienia kod autoryzacyjny na access token
    
    Args:
        client_id: Client ID
        client_secret: Client Secret
        code: Kod autoryzacyjny z callback URL
        redirect_uri: URL przekierowania
        scope: Zakres uprawnień
        
    Returns:
        Słownik z danymi tokena
    """
    # Przygotuj Basic Auth
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "scope": scope,
        "redirect_uri": redirect_uri
    }
    
    response = requests.post(
        "https://ticktick.com/oauth/token",
        headers=headers,
        data=data
    )
    
    response.raise_for_status()
    return response.json()


def save_token_to_env(access_token: str, env_path: str = ".env"):
    """
    Zapisuje access token do pliku .env
    
    Args:
        access_token: Access token do zapisania
        env_path: Ścieżka do pliku .env
    """
    set_key(env_path, "TICKTICK_ACCESS_TOKEN", access_token)
    print(f"✅ Access token zapisany do {env_path}")


def main():
    """Główna funkcja interaktywna"""
    print("=" * 60)
    print("🎯 TickTick OAuth2 - Pomocnik autoryzacji")
    print("=" * 60)
    print()
    
    # Krok 1: Pobierz dane od użytkownika
    print("📋 Krok 1: Podaj dane aplikacji z TickTick Developer Portal")
    print("   (https://developer.ticktick.com/)")
    print()
    
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    redirect_uri = input("Redirect URI (np. http://localhost:8080/callback): ").strip()
    
    # Zapisz Client ID i Secret do .env
    set_key(".env", "TICKTICK_CLIENT_ID", client_id)
    set_key(".env", "TICKTICK_CLIENT_SECRET", client_secret)
    print()
    print("✅ Client ID i Secret zapisane do .env")
    print()
    
    # Krok 2: Wygeneruj URL autoryzacji
    print("=" * 60)
    print("📋 Krok 2: Autoryzacja")
    print("=" * 60)
    print()
    
    auth_url = get_authorization_url(client_id, redirect_uri)
    print("Otwieram przeglądarkę z URL autoryzacji...")
    print()
    print("Jeśli przeglądarka się nie otworzy, skopiuj ten URL:")
    print(auth_url)
    print()
    
    # Otwórz URL w przeglądarce
    try:
        webbrowser.open(auth_url)
    except:
        pass
    
    print("Po zaakceptowaniu autoryzacji zostaniesz przekierowany do:")
    print(f"{redirect_uri}?code=AUTHORIZATION_CODE&state=...")
    print()
    
    # Krok 3: Pobierz kod autoryzacyjny
    print("=" * 60)
    print("📋 Krok 3: Podaj kod autoryzacyjny")
    print("=" * 60)
    print()
    print("Opcja A: Wklej cały URL przekierowania")
    print("Opcja B: Wklej tylko kod (parametr 'code' z URL)")
    print()
    
    user_input = input("URL lub kod: ").strip()
    
    # Spróbuj wyciągnąć kod z URL lub użyj bezpośrednio
    if user_input.startswith("http"):
        parsed_url = urlparse(user_input)
        query_params = parse_qs(parsed_url.query)
        code = query_params.get("code", [None])[0]
        if not code:
            print("❌ Nie znaleziono kodu w URL!")
            return
    else:
        code = user_input
    
    print()
    print(f"Kod autoryzacyjny: {code[:20]}...")
    print()
    
    # Krok 4: Wymień kod na token
    print("=" * 60)
    print("📋 Krok 4: Wymiana kodu na Access Token")
    print("=" * 60)
    print()
    print("Wysyłam żądanie do TickTick API...")
    
    try:
        token_response = exchange_code_for_token(
            client_id, 
            client_secret, 
            code, 
            redirect_uri
        )
        
        access_token = token_response.get("access_token")
        
        if not access_token:
            print("❌ Nie udało się uzyskać access token!")
            print("Odpowiedź serwera:", token_response)
            return
        
        print()
        print("✅ Access Token otrzymany!")
        print(f"Token: {access_token[:20]}...{access_token[-10:]}")
        print()
        
        # Zapisz token do .env
        save_token_to_env(access_token)
        
        print()
        print("=" * 60)
        print("🎉 Konfiguracja zakończona!")
        print("=" * 60)
        print()
        print("Możesz teraz uruchomić aplikację:")
        print("  streamlit run app.py")
        print()
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Błąd HTTP: {e}")
        print(f"Odpowiedź: {e.response.text}")
    except Exception as e:
        print(f"❌ Błąd: {e}")


if __name__ == "__main__":
    main()
