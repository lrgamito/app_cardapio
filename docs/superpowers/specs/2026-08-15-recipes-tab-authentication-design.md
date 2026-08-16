# Design Spec: Simple Authentication for Recipes Tab

## 1. Overview
Introduce lightweight authentication to protect recipe management operations (creating, editing, deleting, importing recipes) in the Streamlit application while keeping the weekly menu generation tab public and accessible.

## 2. Requirements & User Experience

### 2.1 Public Access (Cardápio Semanal)
- The "Cardápio semanal" tab remains completely public.
- Any user can access the page, view instructions, and click "Gerar cardápio semanal" without logging in.

### 2.2 Protected Access (Receitas Tab)
- When the user opens the "Receitas" tab:
  - **If unauthenticated:**
    - A clear login form is presented with fields for username and password.
    - An informational banner clarifies that authentication is required to manage recipes.
    - Error messages appear on invalid credentials.
  - **If authenticated:**
    - The recipe management view is displayed (search, add, edit, delete, export, import).
    - An auth status bar or header appears with the active session user and a "Sair" (Logout) button.
    - Clicking "Sair" clears the authentication session state and returns to the login prompt.

### 2.3 Credential Storage & Configuration
- Credentials are read from `.streamlit/secrets.toml` under a dedicated `[auth]` section:
  ```toml
  [auth]
  username = "admin"
  password = "password123"
  ```
- If `secrets.toml` is not present, fall back to environment variables `APP_AUTH_USERNAME` and `APP_AUTH_PASSWORD`, or default developer credentials (`admin` / `admin`) with a warning in local dev.
- Provide a `.streamlit/secrets.toml.example` template file for easy setup and onboarding.

## 3. Architecture & Components

### 3.1 `cardapio/auth.py`
A modular authentication helper module with minimal surface area:
- `is_authenticated() -> bool`: Returns whether current session state has active authentication.
- `get_auth_credentials() -> tuple[str, str]`: Retrieves expected username and password from Streamlit secrets / environment fallback.
- `login(username, password) -> bool`: Validates credentials against expected values and sets `st.session_state["authenticated_user"]`.
- `logout() -> None`: Clears auth session keys and triggers `st.rerun()`.
- `render_login_form() -> bool`: Renders the UI login form within the tab and handles submission.

### 3.2 UI Integration (`app.py`)
- Inside `render_recipes_tab(recipes)`:
  - Check `is_authenticated()`.
  - If false, call `render_login_form()` and return early.
  - If true, display the logout control and user status at the top or inside the tab, then render the existing recipe management and import/export UI.

## 4. Testing & Verification
- Unit test coverage for `cardapio/auth.py` (credential validation, login success/failure, logout state handling).
- Manual verification of Streamlit UI flow:
  1. Open app -> check "Cardápio semanal" works without login.
  2. Switch to "Receitas" -> verify login form is shown and recipe editing is hidden.
  3. Attempt invalid login -> verify error message.
  4. Submit valid login -> verify recipe table, form, and import/export are visible.
  5. Click "Sair" -> verify user is logged out and login form is shown again.
