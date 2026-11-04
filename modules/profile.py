import streamlit as st

from database.repository import get_user_by_id


# Logout current user
def logout():

    st.session_state.user = None

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

    st.rerun()


# Display profile information
def show_profile():

    user = st.session_state.get("user")

    if not user:
        return

    user_data = get_user_by_id(
        user["id"]
    )

    if not user_data:

        st.error(
            "User account not found."
        )

        return

    st.write(
        f"**Name:** {user_data['name']}"
    )

    st.write(
        f"**Email:** {user_data['email']}"
    )

    st.caption(
        f"User ID: {user_data['id']}"
    )

    if st.button(
        "Logout",
        use_container_width=True
    ):

        logout()