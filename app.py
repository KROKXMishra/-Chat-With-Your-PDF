from dotenv import load_dotenv

# Load environment variables before application modules
load_dotenv()

import streamlit as st

from database.connection import init_db
from modules.authentication import show_authentication
from modules.profile import show_profile
from modules.pdf_manager import show_pdf_manager
from modules.chat_history import show_chat_history
from modules.chat import show_chat


# Configure Streamlit page
st.set_page_config(
    page_title="PDF Reader AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
def initialize_session_state():

    defaults = {
        "user": None,
        "messages": [],
        "db": None,
        "pdf_hash": None,
        "pdf_docs": [],
        "pdf_chunks": [],
        "active_chat_id": None,
        "active_pdf_name": None,
        "selected_chat_id": 0,
        "upload_key": 0,
        "confirm_delete_all": False,
        "delete_chat_id": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# Main application
def main():

    # Initialize database
    init_db()

    # Initialize session state
    initialize_session_state()

    # Show login and registration
    if st.session_state.user is None:

        show_authentication()

        return

    # Main application interface
    st.title("📚 PDF Reader AI")

    st.caption(
        "Upload your PDF, ask questions, and manage your conversations."
    )

    # Sidebar
    with st.sidebar:

        st.title("👤 Account")

        show_profile()

        st.divider()

        show_chat_history()

    # Main content
    show_pdf_manager()

    st.divider()

    show_chat()


if __name__ == "__main__":
    main()