"""
Główna aplikacja Streamlit - Dashboard Macierzy Eisenhowera dla TickTick
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
from ticktick_api import TickTickAPI, move_task_to_quadrant
from eisenhower_matrix import (
    filter_tasks_by_context,
    categorize_tasks_to_quadrants,
    get_quadrant_stats,
    sort_tasks_by_deadline
)
from config import CONTEXTS, QUADRANTS, get_context_description, POLAND_TZ
from auth import TickTickAuth, init_auth_from_env, handle_oauth_callback
import os

# Konfiguracja strony
st.set_page_config(
    page_title="TickTick Eisenhower Matrix",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS
st.markdown("""
<style>
    .task-card {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
    }
    .task-title {
        font-weight: bold;
        font-size: 14px;
    }
    .task-meta {
        font-size: 12px;
        color: #666;
    }
    .quadrant-header {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        text-align: center;
        font-weight: bold;
    }
    .stats-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Inicjalizacja session state"""
    # OAuth i autentykacja
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "auth_client" not in st.session_state:
        # Spróbuj załadować z .env, ale nie wymagaj tego
        st.session_state.auth_client = init_auth_from_env()
    
    # Dane konfiguracji aplikacji (Client ID/Secret)
    if "client_id" not in st.session_state:
        st.session_state.client_id = os.getenv("TICKTICK_CLIENT_ID", "")
    if "client_secret" not in st.session_state:
        st.session_state.client_secret = os.getenv("TICKTICK_CLIENT_SECRET", "")
    if "redirect_uri" not in st.session_state:
        st.session_state.redirect_uri = os.getenv("TICKTICK_REDIRECT_URI", "http://localhost:8501")
    
    # API i dane
    if "api" not in st.session_state:
        st.session_state.api = None
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = None
    if "tasks_cache" not in st.session_state:
        st.session_state.tasks_cache = []


def render_login_page():
    """Renderuje stronę logowania OAuth2"""
    st.title("🔐 Logowanie do TickTick")
    
    # Sprawdź czy mamy potrzebne dane konfiguracyjne
    if not st.session_state.auth_client:
        st.error("⚠️ Brak konfiguracji OAuth2!")
        st.info("""
        Aby użyć logowania przez TickTick, dodaj do pliku `.env`:
        
        ```
        TICKTICK_CLIENT_ID=twój_client_id
        TICKTICK_CLIENT_SECRET=twój_client_secret
        TICKTICK_REDIRECT_URI=http://localhost:8501
        ```
        
        Client ID i Secret możesz uzyskać z [TickTick Developer Portal](https://developer.ticktick.com/).
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Alternatywnie: użyj tokena bezpośrednio")
        
        with st.form("manual_token_form"):
            manual_token = st.text_input(
                "Access Token", 
                type="password",
                help="Wklej swój access token z TickTick"
            )
            submit = st.form_submit_button("Zaloguj się tokenem")
            
            if submit and manual_token:
                st.session_state.access_token = manual_token
                st.session_state.authenticated = True
                st.session_state.api = TickTickAPI(manual_token)
                st.success("✅ Zalogowano pomyślnie!")
                st.rerun()
        
        return
    
    # OAuth2 Flow
    st.markdown("""
    ### Jak się zalogować?
    
    1. Kliknij przycisk poniżej
    2. Zostaniesz przekierowany do strony TickTick
    3. Zaloguj się swoim kontem (możesz użyć konta Google jeśli masz je połączone)
    4. Zaakceptuj uprawnienia dla aplikacji
    5. Zostaniesz automatycznie przekierowany z powrotem
    """)
    
    # Wygeneruj URL autoryzacji
    auth_url = st.session_state.auth_client.get_authorization_url()
    
    # Przycisk logowania - użyj natywnego Streamlit
    st.link_button(
        "🔐 Zaloguj się przez TickTick",
        auth_url,
        use_container_width=True
    )
    
    st.markdown("---")
    st.info("💡 Twoje dane logowania nie są przechowywane na dysku - tylko w sesji przeglądarki.")


def handle_authentication():
    """Obsługuje proces autoryzacji OAuth2"""
    # Sprawdź czy mamy kod autoryzacyjny w URL
    auth_code = handle_oauth_callback()
    
    if auth_code and not st.session_state.authenticated:
        st.info("🔄 Przetwarzam autoryzację...")
        
        try:
            # Wymień kod na token
            token_data = st.session_state.auth_client.exchange_code_for_token(auth_code)
            
            # Zapisz tokeny w session state
            st.session_state.access_token = token_data.get("access_token")
            st.session_state.refresh_token = token_data.get("refresh_token")
            st.session_state.authenticated = True
            
            # Inicjalizuj API z tokenem
            st.session_state.api = TickTickAPI(st.session_state.access_token)
            
            # Wyczyść parametry URL (dla Streamlit 1.29.0)
            st.experimental_set_query_params()
            
            st.success("✅ Zalogowano pomyślnie!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Błąd podczas autoryzacji: {e}")
            st.session_state.authenticated = False
            return False
    
    return st.session_state.authenticated


def render_sidebar():
    """Renderuje panel boczny z kontrolkami"""
    with st.sidebar:
        st.title("🎯 TickTick Matrix")
        st.markdown("---")
        
        # Informacje o użytkowniku i przycisk wylogowania
        if st.session_state.authenticated:
            st.success("✅ Zalogowano")
            if st.button("🚪 Wyloguj się", use_container_width=True):
                # Wyczyść dane sesji
                st.session_state.access_token = None
                st.session_state.refresh_token = None
                st.session_state.authenticated = False
                st.session_state.api = None
                st.session_state.tasks_cache = []
                st.session_state.last_refresh = None
                st.rerun()
            st.markdown("---")
        
        # Sprawdzenie konfiguracji API
        if not st.session_state.api or not st.session_state.api.is_configured():
            st.error("⚠️ API nie jest skonfigurowane!")
            st.stop()
        
        # Przycisk odświeżania
        if st.button("🔄 Odśwież dane", use_container_width=True):
            with st.spinner("Pobieranie zadań..."):
                st.session_state.tasks_cache = st.session_state.api.get_tasks()
                st.session_state.last_refresh = datetime.now()
                st.success("Dane odświeżone!")
                st.rerun()
        
        # Wybór kontekstu
        st.markdown("### 📂 Wybierz Kontekst")
        context_options = {key: value["name"] for key, value in CONTEXTS.items()}
        
        # Znajdź index "Jutrzejsze" jako domyślny
        context_keys = list(context_options.keys())
        default_index = context_keys.index("Jutrzejsze") if "Jutrzejsze" in context_keys else 0
        
        selected_context = st.selectbox(
            "Profil",
            options=context_keys,
            format_func=lambda x: context_options[x],
            index=default_index,
            key="context_selector"
        )
        
        # Opis kontekstu
        if selected_context in CONTEXTS:
            st.info(get_context_description(selected_context))
        
        st.markdown("---")
        
        # Informacje o ostatnim odświeżeniu
        if st.session_state.last_refresh:
            st.caption(f"Ostatnie odświeżenie: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        st.markdown("### ℹ️ Info")
        st.caption("Dashboard Macierzy Eisenhowera")
        st.caption("Wersja: 1.0.0")
        
        return selected_context


def render_task_card(task: Dict, quadrant_key: str):
    """
    Renderuje kartę zadania
    
    Args:
        task: Słownik z danymi zadania
        quadrant_key: Klucz ćwiartki (Q1, Q2, Q3, Q4)
    """
    title = task.get("title", "Bez tytułu")
    content = task.get("content", "")
    due_date = task.get("dueDate", "")
    tags = task.get("tags", [])
    task_id = task.get("id", "")
    
    # Formatowanie daty
    due_str = ""
    current_date_obj = None
    if due_date:
        try:
            # TickTick zwraca datę w UTC, konwertujemy na polską strefę czasową
            dt_utc = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            dt_poland = dt_utc.astimezone(POLAND_TZ)
            current_date_obj = dt_poland.date()
            due_str = f"📅 {dt_poland.strftime('%d.%m.%Y')}"
        except:
            due_str = f"📅 {due_date}"
    
    # Tagi
    tags_str = " ".join([f"`#{tag}`" for tag in tags]) if tags else ""
    
    # Przyciski do przenoszenia
    quadrant_icons = {"Q1": "🏎️", "Q2": "❗", "Q3": "🧠", "Q4": "🧩"}
    available_quadrants = [q for q in ["Q1", "Q2", "Q3", "Q4"] if q != quadrant_key]
    
    # Layout kompaktowy - dodajemy +1 dla ikony kalendarza
    num_buttons = len(available_quadrants) + 1 + (1 if content else 0)  # +1 dla kalendarza, +1 dla opisu jeśli istnieje
    col_task, *col_buttons = st.columns([4] + [0.3] * num_buttons)
    
    with col_task:
        st.markdown(f"""
        <div class="task-card">
            <div class="task-title">{title}</div>
            <div class="task-meta">
                {due_str} {tags_str}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Kompaktowe przyciski obok zadania
    for idx, target_q in enumerate(available_quadrants):
        with col_buttons[idx]:
            if st.button(
                quadrant_icons[target_q],
                key=f"move_{task_id}_{target_q}",
                help=f"{QUADRANTS[target_q]['name']}",
                use_container_width=True
            ):
                # Przenieś zadanie
                with st.spinner("⏳"):
                    updated_task = move_task_to_quadrant(st.session_state.api, task, target_q)
                    if updated_task:
                        # Zaktualizuj zadanie w cache lokalnie
                        for i, cached_task in enumerate(st.session_state.tasks_cache):
                            if cached_task.get("id") == task_id:
                                st.session_state.tasks_cache[i] = updated_task
                                break
                        
                        st.session_state.last_refresh = datetime.now()
                        st.rerun()
                    else:
                        st.error("Błąd")
    
    # Przycisk kalendarza do zmiany daty
    with col_buttons[len(available_quadrants)]:
        date_key = f"date_picker_{task_id}"
        if st.button(
            "📆",
            key=f"show_date_{task_id}",
            help="Zmień datę",
            use_container_width=True
        ):
            # Toggle widoczności date pickera w session state
            if date_key not in st.session_state:
                st.session_state[date_key] = False
            st.session_state[date_key] = not st.session_state[date_key]
    
    # Pokaż date picker jeśli jest aktywny
    if st.session_state.get(date_key, False):
        col_date, col_date_btn = st.columns([3, 1])
        with col_date:
            new_date = st.date_input(
                "Nowa data",
                value=current_date_obj if current_date_obj else datetime.now().date(),
                key=f"date_input_{task_id}",
                label_visibility="collapsed"
            )
        with col_date_btn:
            if st.button("✅", key=f"confirm_date_{task_id}", help="Potwierdź zmianę daty"):
                # Konwertuj wybraną datę na format TickTick
                # Zachowaj oryginalną godzinę jeśli istnieje, w przeciwnym razie ustaw 12:00
                if due_date:
                    try:
                        dt_utc = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        # Zachowaj godzinę z oryginalnej daty
                        new_datetime = datetime.combine(new_date, dt_utc.time())
                    except:
                        new_datetime = datetime.combine(new_date, datetime.min.time().replace(hour=12))
                else:
                    new_datetime = datetime.combine(new_date, datetime.min.time().replace(hour=12))
                
                # Konwertuj na UTC i format ISO
                from zoneinfo import ZoneInfo
                poland_tz = ZoneInfo("Europe/Warsaw")
                dt_poland = new_datetime.replace(tzinfo=poland_tz)
                dt_utc_new = dt_poland.astimezone(ZoneInfo("UTC"))
                new_date_str = dt_utc_new.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
                
                # Aktualizuj datę w TickTick
                with st.spinner("⏳ Aktualizuję datę..."):
                    project_id = task.get("projectId")
                    updated_task = st.session_state.api.update_task_date(
                        task_id, 
                        project_id, 
                        new_date_str, 
                        original_task=task
                    )
                    
                    if updated_task:
                        # Zaktualizuj zadanie w cache lokalnie
                        for i, cached_task in enumerate(st.session_state.tasks_cache):
                            if cached_task.get("id") == task_id:
                                st.session_state.tasks_cache[i] = updated_task
                                break
                        
                        # Zamknij date picker
                        st.session_state[date_key] = False
                        st.session_state.last_refresh = datetime.now()
                        st.success("✅ Data zaktualizowana!")
                        st.rerun()
                    else:
                        st.error("❌ Błąd aktualizacji daty")
    
    # Przycisk opisu (jeśli zadanie ma opis)
    if content:
        with col_buttons[len(available_quadrants) + 1]:
            desc_key = f"desc_{task_id}"
            if st.button(
                "📝",
                key=f"show_desc_{task_id}",
                help="Pokaż opis",
                use_container_width=True
            ):
                # Toggle widoczności opisu w session state
                if desc_key not in st.session_state:
                    st.session_state[desc_key] = False
                st.session_state[desc_key] = not st.session_state[desc_key]
        
        # Pokaż opis jeśli jest aktywny
        if st.session_state.get(desc_key, False):
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                border-left: 4px solid #6c757d;
                padding: 12px 16px;
                margin: 8px 0;
                border-radius: 4px;
                font-size: 0.9em;
                color: #495057;
            ">
                <strong>📄 Opis:</strong><br>
                {content.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)


def render_quadrant(quadrant_key: str, tasks: List[Dict]):
    """
    Renderuje pojedynczą ćwiartkę
    
    Args:
        quadrant_key: Klucz ćwiartki (Q1, Q2, Q3, Q4)
        tasks: Lista zadań w tej ćwiartce
    """
    quadrant_info = QUADRANTS[quadrant_key]
    
    st.markdown(f"""
    <div class="quadrant-header" style="background-color: {quadrant_info['color']}33; border-left: 5px solid {quadrant_info['color']};">
        {quadrant_info['name']}<br>
        <small>{quadrant_info['description']}</small><br>
        <small>👉 {quadrant_info['action']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Zadań: **{len(tasks)}**")
    
    if not tasks:
        st.info("Brak zadań w tej ćwiartce")
        return
    
    # Sortuj zadania po deadline
    sorted_tasks = sort_tasks_by_deadline(tasks)
    
    # Renderuj zadania
    for task in sorted_tasks:
        render_task_card(task, quadrant_key)


def render_stats(stats: Dict[str, int], total_tasks: int):
    """
    Renderuje statystyki
    
    Args:
        stats: Słownik z liczbą zadań w każdej ćwiartce
        total_tasks: Całkowita liczba zadań
    """
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="stats-box" style="background-color: #e8f4f8;">
            <h2>{total_tasks}</h2>
            <p>Wszystkich zadań</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-box" style="background-color: #ffe8e8;">
            <h2>{stats.get('Q1', 0)}</h2>
            <p>Ćwiartka 1</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-box" style="background-color: #e8ffe8;">
            <h2>{stats.get('Q2', 0)}</h2>
            <p>Ćwiartka 2</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-box" style="background-color: #fff4e8;">
            <h2>{stats.get('Q3', 0)}</h2>
            <p>Ćwiartka 3</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="stats-box" style="background-color: #f0f0f0;">
            <h2>{stats.get('Q4', 0)}</h2>
            <p>Ćwiartka 4</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Główna funkcja aplikacji"""
    init_session_state()
    
    # Obsługa autoryzacji OAuth2
    if not st.session_state.authenticated:
        # Sprawdź czy jest callback z kodem
        if not handle_authentication():
            # Pokaż stronę logowania
            render_login_page()
            return
    
    # Jeśli zalogowany, pokaż dashboard
    # Sidebar z kontrolkami
    selected_context = render_sidebar()
    
    # Nagłówek
    st.title("🎯 Macierz Eisenhowera - TickTick Dashboard")
    
    # Automatyczne pobieranie danych przy pierwszym uruchomieniu
    if not st.session_state.tasks_cache:
        with st.spinner("Pobieranie zadań z TickTick..."):
            st.session_state.tasks_cache = st.session_state.api.get_tasks()
            st.session_state.last_refresh = datetime.now()
    
    # Filtrowanie zadań według kontekstu
    filtered_tasks = filter_tasks_by_context(
        st.session_state.tasks_cache,
        selected_context
    )
    
    # Kategoryzacja do ćwiartek
    quadrants = categorize_tasks_to_quadrants(filtered_tasks)
    stats = get_quadrant_stats(quadrants)
    total_tasks = sum(stats.values())
    
    # Wyświetl statystyki
    render_stats(stats, total_tasks)
    
    st.markdown("---")
    
    # Macierz 2x2
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    with row1_col1:
        render_quadrant("Q1", quadrants["Q1"])
    
    with row1_col2:
        render_quadrant("Q2", quadrants["Q2"])
    
    with row2_col1:
        render_quadrant("Q3", quadrants["Q3"])
    
    with row2_col2:
        render_quadrant("Q4", quadrants["Q4"])


if __name__ == "__main__":
    main()
