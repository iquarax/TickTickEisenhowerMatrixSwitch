# Deployment na Streamlit Cloud

## ✅ Status Deploymentu

Aplikacja jest już wdrożona i działa pod adresem:
**https://ticktickeisenhowermatrixswitch-kwpwgdgkqyyuugg8h3jkdc.streamlit.app**

---

## 🌐 Konfiguracja Własnej Domeny

Aby udostępnić aplikację pod adresem **https://isenhowermatrix.iquarax.pl**:

### Krok 1: Konfiguracja DNS w Netlify

1. Zaloguj się do panelu Netlify (gdzie zarządzasz domeną `iquarax.pl`)
2. Przejdź do **Domain management** → **DNS**
3. Dodaj nowy rekord **CNAME**:
   - **Name/Host**: `isenhowermatrix`
   - **Value/Target**: `ticktickeisenhowermatrixswitch-kwpwgdgkqyyuugg8h3jkdc.streamlit.app`
   - **TTL**: 3600 (lub Auto)
4. Zapisz zmiany

### Krok 2: Aktualizacja OAuth Redirect URI

#### W Streamlit Cloud:
1. Przejdź do ustawień aplikacji → **Secrets**
2. Zaktualizuj `TICKTICK_REDIRECT_URI`:

```toml
TICKTICK_CLIENT_ID = "twój_client_id"
TICKTICK_CLIENT_SECRET = "twój_client_secret"
TICKTICK_REDIRECT_URI = "https://isenhowermatrix.iquarax.pl"
```

3. Zapisz i zrestartuj aplikację

#### W TickTick Developer Portal:
1. Przejdź do https://developer.ticktick.com/
2. Edytuj swoją aplikację
3. W sekcji **Redirect URIs** dodaj:
   - `https://isenhowermatrix.iquarax.pl`
   - (możesz zostawić też stary adres Streamlit dla testów)
4. Zapisz zmiany

### Krok 3: Poczekaj na propagację DNS

DNS może potrzebować 5-30 minut na propagację zmian. Po tym czasie aplikacja powinna być dostępna pod:
**https://isenhowermatrix.iquarax.pl** 🎉

### ⚠️ Ważne uwagi

- Streamlit Cloud nie obsługuje bezpośrednio własnych domen
- CNAME w Netlify działa jako przekierowanie
- Użytkownicy będą widzieć adres Streamlit w pasku przeglądarki po przekierowaniu
- Jeśli chcesz pełną integrację z własną domeną (bez przekierowania), rozważ Railway.app lub Render.com

---

## 📝 Pierwotne Instrukcje Deploymentu (dla odniesienia)

<details>
<summary>Kliknij aby rozwinąć instrukcje początkowego deploymentu</summary>

### Krok 1: Przejdź na Streamlit Cloud
https://streamlit.io/cloud

### Krok 2: Zaloguj się przez GitHub
Użyj swojego konta GitHub

### Krok 3: Utwórz nową aplikację
- Kliknij "New app"
- Wybierz repozytorium: `iquarax/TickTickEisenhowerMatrixSwitch`
- Branch: `main`
- Main file path: `app.py`

### Krok 4: Dodaj sekrety (Secrets)
W ustawieniach aplikacji dodaj:

```toml
TICKTICK_CLIENT_ID = "twój_client_id"
TICKTICK_CLIENT_SECRET = "twój_client_secret"
TICKTICK_REDIRECT_URI = "https://twoja-aplikacja.streamlit.app"
```

⚠️ **WAŻNE:** Po deploymencie musisz zaktualizować REDIRECT_URI:
1. Skopiuj URL swojej aplikacji
2. Zaktualizuj `TICKTICK_REDIRECT_URI` w sekretach Streamlit Cloud
3. Dodaj ten sam URL w TickTick Developer Portal jako Redirect URI
4. Zrestartuj aplikację

### Krok 5: Deploy!
Kliknij "Deploy" i poczekaj kilka minut.

</details>
