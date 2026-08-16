from __future__ import annotations

import os
import unittest

import streamlit as st

from cardapio.auth import (
    get_auth_credentials,
    is_authenticated,
    login,
    logout,
)


class AuthTests(unittest.TestCase):
    def tearDown(self) -> None:
        st.session_state.pop("authenticated_user", None)
        os.environ.pop("APP_AUTH_USERNAME", None)
        os.environ.pop("APP_AUTH_PASSWORD", None)

    def test_credentials_fallback_order_env_then_default(self) -> None:
        os.environ["APP_AUTH_USERNAME"] = "leandro"
        os.environ["APP_AUTH_PASSWORD"] = "segredo"
        self.assertEqual(("leandro", "segredo"), get_auth_credentials())

    def test_credentials_defaults_when_no_env(self) -> None:
        self.assertEqual(("admin", "admin"), get_auth_credentials())

    def test_login_success_sets_session_user(self) -> None:
        os.environ["APP_AUTH_USERNAME"] = "leandro"
        os.environ["APP_AUTH_PASSWORD"] = "segredo"
        self.assertTrue(login("leandro", "segredo"))
        self.assertEqual("leandro", st.session_state["authenticated_user"])
        self.assertTrue(is_authenticated())

    def test_login_failure_does_not_set_user(self) -> None:
        os.environ["APP_AUTH_USERNAME"] = "leandro"
        os.environ["APP_AUTH_PASSWORD"] = "segredo"
        self.assertFalse(login("leandro", "errada"))
        self.assertFalse(is_authenticated())

    def test_login_defaults_when_no_env(self) -> None:
        self.assertTrue(login("admin", "admin"))
        self.assertTrue(is_authenticated())

    def test_logout_clears_session_user(self) -> None:
        os.environ["APP_AUTH_USERNAME"] = "leandro"
        os.environ["APP_AUTH_PASSWORD"] = "segredo"
        login("leandro", "segredo")
        logout()
        self.assertFalse(is_authenticated())


if __name__ == "__main__":
    unittest.main()