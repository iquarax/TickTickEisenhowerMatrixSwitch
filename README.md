# 🎯 TickTick Eisenhower Matrix Dashboard

Dashboard rozszerzający funkcjonalność aplikacji TickTick o możliwość definiowania wielu kontekstów (profili) dla Macierzy Eisenhowera.

## 🚀 Główne funkcje

- **🔐 Bezpieczne logowanie OAuth2**: Zaloguj się przez TickTick (w tym kontem Google) bezpośrednio w aplikacji
- **Dynamiczne Konteksty**: Przełączaj się między różnymi profilami (Praca, Dom, Deep Work, Weekend) jednym kliknięciem
- **Automatyczna Segregacja**: Zadania automatycznie sortowane do 4 ćwiartek na podstawie priorytetów
- **Integracja w czasie rzeczywistym**: Synchronizacja z TickTick API
- **Interaktywność**: Oznaczaj zadania jako wykonane bezpośrednio z dashboardu
- **Elastyczna konfiguracja**: Łatwo dodawaj nowe konteksty i reguły

## 📋 Wymagania

- Python 3.8+
- Konto TickTick (możesz zalogować się kontem Google)

## 🛠️ Instalacja

### 1. Sklonuj repozytorium lub pobierz pliki

### 2. Utwórz środowisko wirtualne

```bash
python -m venv venv
```

### 3. Aktywuj środowisko

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### 5. Konfiguracja API

#### ⚡ Szybki start (Rekomendowane)

Aplikacja ma **wbudowane logowanie OAuth2** - nie musisz niczego konfigurować przed pierwszym uruchomieniem!

1. Uzyskaj dane aplikacji z [TickTick Developer Portal](https://developer.ticktick.com/):
   - Utwórz nową aplikację
   - Zapisz `Client ID` i `Client Secret`
   - Ustaw Redirect URI na: `http://localhost:8501`

2. Utwórz plik `.env` z danymi:

```env
TICKTICK_CLIENT_ID=twój_client_id
TICKTICK_CLIENT_SECRET=twój_client_secret
TICKTICK_REDIRECT_URI=http://localhost:8501
```

3. Uruchom aplikację (patrz sekcja poniżej)
4. Przy pierwszym uruchomieniu kliknij **"Zaloguj się przez TickTick"**
5. Zaloguj się swoim kontem TickTick (możesz użyć konta Google)
6. Gotowe! 🎉

#### 🔧 Alternatywna metoda (dla zaawansowanych)

Jeśli wolisz używać stałego tokena lub już go masz, możesz użyć skryptu pomocniczego:

```bash
python oauth_helper.py
```

Lub dodać token bezpośrednio do `.env`:

```env
TICKTICK_ACCESS_TOKEN=twój_access_token
```

## 🎮 Uruchomienie

```bash
streamlit run app.py
```

Dashboard otworzy się automatycznie w przeglądarce pod adresem `http://localhost:8501`

### 🔐 Pierwsze logowanie

1. Przy pierwszym uruchomieniu zobaczysz ekran logowania
2. Kliknij **"Zaloguj się przez TickTick"**
3. Zostaniesz przekierowany do strony TickTick
4. Zaloguj się swoim kontem (możesz użyć Google jeśli Twoje konto TickTick jest połączone)
5. Zaakceptuj uprawnienia
6. Zostaniesz automatycznie przekierowany do dashboardu

**Bezpieczeństwo:** Token jest przechowywany tylko w sesji przeglądarki i znika po zamknięciu aplikacji.

## 📊 Struktura projektu

```
TickTickEisenhowerMatrixSwitchWorkspace/
├── app.py                  # Główna aplikacja Streamlit z OAuth2
├── auth.py                 # Moduł autoryzacji OAuth2
├── ticktick_api.py         # Moduł komunikacji z TickTick API
├── eisenhower_matrix.py    # Logika Macierzy Eisenhowera
├── config.py               # Konfiguracja kontekstów i ćwiartek
├── oauth_helper.py         # Skrypt pomocniczy (opcjonalny)
├── requirements.txt        # Zależności Python
├── .env.example           # Przykładowy plik konfiguracyjny
├── .gitignore             # Pliki ignorowane przez Git
└── README.md              # Ta dokumentacja
```

## 🎯 Jak to działa?

### Macierz Eisenhowera

Zadania są automatycznie segregowane do 4 ćwiartek na podstawie priorytetów:

| Ćwiartka | Priorytet TickTick | Opis |
|----------|-------------------|------|
| **Q1** 🔴 | High (5) | Ważne i Pilne - DO IT NOW |
| **Q2** 🟢 | Medium (3) | Ważne, Niepilne - SCHEDULE |
| **Q3** 🟡 | Low (1) | Nieważne, Pilne - DELEGATE |
| **Q4** ⚪ | None (0) | Nieważne, Niepilne - ELIMINATE |

### Konteksty

Predefiniowane konteksty (możesz dodać własne w `config.py`):

- **🌐 Wszystkie**: Wszystkie zadania bez filtrowania
- **💼 Praca**: Zadania służbowe (#praca, #biuro, #projekt)
- **🏠 Dom**: Zadania domowe (#dom, #rodzina, #zakupy)
- **🧠 Deep Work**: Zadania wymagające koncentracji (#deepwork, #nauka)
- **🎯 Weekend**: Aktywności weekendowe (#weekend, #hobby)
- **📊 Projekty**: Projekty poboczne (#projekt, #side-project)

## ⚙️ Dostosowanie

### Dodawanie nowych kontekstów

Edytuj plik `config.py`:

```python
CONTEXTS = {
    "TwojKontekst": {
        "name": "🎨 Twój Kontekst",
        "tags": ["#tag1", "#tag2", "#tag3"],
        "description": "Opis kontekstu"
    }
}
```

### Zmiana mapowania priorytetów

Możesz dostosować, które priorytety trafiają do których ćwiartek w `config.py`:

```python
PRIORITY_MAPPING = {
    5: "Q1",  # High → Ćwiartka 1
    3: "Q2",  # Medium → Ćwiartka 2
    1: "Q3",  # Low → Ćwiartka 3
    0: "Q4"   # None → Ćwiartka 4
}
```

## 🔧 Rozwiązywanie problemów

### "API nie jest skonfigurowane"
- Upewnij się, że plik `.env` istnieje i zawiera poprawne tokeny
- Sprawdź, czy tokeny są aktualne

### "Błąd pobierania zadań"
- Sprawdź połączenie internetowe
- Zweryfikuj poprawność tokenów w panelu TickTick Developer

### Brak zadań w kontekście
- Upewnij się, że zadania w TickTick mają odpowiednie tagi
- Sprawdź konfigurację tagów w `config.py`

## 📝 TODO / Przyszłe funkcje

- [ ] Edycja zadań bezpośrednio z dashboardu
- [ ] Tworzenie nowych zadań
- [ ] Export danych do CSV/Excel
- [ ] Tryb ciemny
- [ ] Statystyki i wykresy produktywności
- [ ] Wsparcie dla wielu użytkowników
- [ ] Powiadomienia o deadline'ach

## 🤝 Współpraca

Jeśli chcesz dodać nowe funkcje lub znaleźć błędy - mile widziane Pull Requesty!

## 📄 Licencja

MIT License - możesz swobodnie używać i modyfikować ten projekt.

## 🙏 Podziękowania

- [TickTick](https://ticktick.com/) za świetne API
- [Streamlit](https://streamlit.io/) za framework do tworzenia Data Apps
- Stephen Covey za Macierz Eisenhowera

---

**Autor**: Twoje Imię
**Kontakt**: twoj@email.com
**Wersja**: 1.0.0
