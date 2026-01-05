# Deployment na Streamlit Cloud

## Krok 1: Przejdź na Streamlit Cloud
https://streamlit.io/cloud

## Krok 2: Zaloguj się przez GitHub
Użyj swojego konta GitHub

## Krok 3: Utwórz nową aplikację
- Kliknij "New app"
- Wybierz repozytorium: `iquarax/TickTickEisenhowerMatrixSwitch`
- Branch: `main`
- Main file path: `app.py`

## Krok 4: Dodaj sekrety (Secrets)
W ustawieniach aplikacji dodaj:

```toml
TICKTICK_CLIENT_ID = "twój_client_id"
TICKTICK_CLIENT_SECRET = "twój_client_secret"
TICKTICK_REDIRECT_URI = "https://twoja-aplikacja.streamlit.app"
```

⚠️ **WAŻNE:** Po deploymencie musisz zaktualizować REDIRECT_URI:
1. Skopiuj URL swojej aplikacji (np. `https://ticktickeisenhower.streamlit.app`)
2. Zaktualizuj `TICKTICK_REDIRECT_URI` w sekretach Streamlit Cloud
3. Dodaj ten sam URL w TickTick Developer Portal jako Redirect URI
4. Zrestartuj aplikację

## Krok 5: Deploy!
Kliknij "Deploy" i poczekaj kilka minut.

## Gotowe! 🎉
Twoja aplikacja będzie dostępna pod adresem typu:
`https://twoja-nazwa.streamlit.app`
