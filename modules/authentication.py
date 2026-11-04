import streamlit as st

from services.auth_service import (
    register_user,
    authenticate_user
)


# Reset session data when switching accounts
def reset_user_session():

    st.session_state.messages = []
    st.session_state.db = None
    st.session_state.pdf_hash = None
    st.session_state.pdf_docs = []
    st.session_state.pdf_chunks = []

    st.session_state.active_chat_id = None
    st.session_state.active_pdf_name = None
    st.session_state.selected_chat_id = 0

    st.session_state.upload_key += 1

    st.session_state.confirm_delete_all = False
    st.session_state.delete_chat_id = None


# Login interface
def show_login():

    st.subheader("Login to your account")

    with st.form("login_form"):

        email = st.text_input(
            "Email address"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

        if submitted:

            if not email.strip() or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                success, user_data = authenticate_user(
                    email,
                    password
                )

                if success:

                    reset_user_session()

                    st.session_state.user = user_data

                    st.success("Login successful!")

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )


# Registration interface
def show_register():

    st.subheader("Create a new account")

    with st.form("register_form"):

        name = st.text_input(
            "Full name"
        )

        email = st.text_input(
            "Email address"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

        if submitted:

            if not name.strip() or not email.strip():

                st.error(
                    "Name and email are required."
                )

            elif not password:

                st.error(
                    "Password is required."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(message)

                    st.info(
                        "You can now log in using your credentials."
                    )

                else:

                    st.error(message)


# Main authentication interface
def show_authentication():

    st.title("📚 PDF Reader AI")

    st.write(
        "Upload your PDF documents and interact with them using AI."
    )

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    with login_tab:

        show_login()

    with register_tab:

        show_register()