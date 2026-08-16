from __future__ import annotations

import os

import streamlit as st

_ENV_USERNAME = "APP_AUTH_USERNAME"
_ENV_PASSWORD = "APP_AUTH_PASSWORD"
_DEFAULT_USERNAME = "admin"
_DEFAULT_PASSWORD = "admin"


def get_auth_credentials() -> tuple[str, str]:
    try:
        username = st.secrets["auth"]["username"]
        password = st.secrets["auth"]["password"]
        return username, password
    except Exception:
        username = os.environ.get(_ENV_USERNAME) or _DEFAULT_USERNAME
        password = os.environ.get(_ENV_PASSWORD) or _DEFAULT_PASSWORD
        return username, password


def is_authenticated() -> bool:
    return st.session_state.get("authenticated_user") is not None


def login(username: str, password: str) -> bool:
    expected_username, expected_password = get_auth_credentials()
    if username == expected_username and password == expected_password:
        st.session_state["authenticated_user"] = username
        return True
    return False


def logout() -> None:
    if "authenticated_user" in st.session_state:
        del st.session_state["authenticated_user"]
    st.rerun()


def render_login_form() -> bool:
    st.subheader("Acesso restrito")
    st.info("Faça login para gerenciar (cadastrar, editar e excluir) receitas.")

    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", type="primary")

    if submitted:
        if login(username, password):
            st.rerun()
            return True
        st.error("Usuário ou senha inválidos.")
    return False