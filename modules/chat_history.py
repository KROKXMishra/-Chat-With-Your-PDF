import streamlit as st

from database.repository import (
    get_all_chats,
    get_conversation,
    get_messages,
    delete_chat,
    delete_all_chats,
    update_vectorstore_path,
    count_pdf_references
)

from services.rag_service import (
    load_vector_store,
    create_vector_store,
    save_vector_store,
    delete_vector_store
)

from services.pdf_service import (
    load_saved_pdf,
    delete_saved_pdf
)


# Reset the currently active conversation
def reset_active_chat():

    st.session_state.messages = []
    st.session_state.db = None
    st.session_state.pdf_hash = None
    st.session_state.pdf_docs = []
    st.session_state.pdf_chunks = []
    st.session_state.active_chat_id = None
    st.session_state.active_pdf_name = None
    st.session_state.selected_chat_id = 0
    st.session_state.upload_key += 1


# Delete original PDF only when no conversation uses it
def cleanup_pdf(pdf_path, user_id):

    if not pdf_path:
        return

    references = count_pdf_references(
        pdf_path,
        user_id
    )

    if references == 0:
        delete_saved_pdf(
            pdf_path,
            user_id
        )


# Open an existing conversation
def open_chat(chat_id):

    user = st.session_state.get("user")

    if not user:
        return

    user_id = user["id"]

    try:

        # Verify conversation ownership
        chat = get_conversation(
            chat_id,
            user_id
        )

        if not chat:
            st.error("Conversation not found.")
            return

        with st.spinner("Loading conversation..."):

            vectorstore_path = chat["vectorstore_path"]

            # Load existing FAISS index
            if vectorstore_path:

                db = load_vector_store(
                    vectorstore_path,
                    user_id
                )

            # Rebuild FAISS index if it is missing
            else:

                if not chat["pdf_path"]:
                    raise FileNotFoundError(
                        "Original PDF is unavailable."
                    )

                docs = load_saved_pdf(
                    chat["pdf_path"],
                    user_id
                )

                db, chunks = create_vector_store(docs)

                vectorstore_path = save_vector_store(
                    db,
                    user_id,
                    chat_id
                )

                updated = update_vectorstore_path(
                    chat_id,
                    user_id,
                    vectorstore_path
                )

                if not updated:
                    raise RuntimeError(
                        "Unable to save rebuilt vector store path."
                    )

            # Restore previous messages
            messages = get_messages(
                chat_id,
                user_id
            )

            # Update session state
            st.session_state.db = db

            st.session_state.messages = [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                for msg in messages
            ]

            st.session_state.pdf_hash = None
            st.session_state.pdf_docs = []
            st.session_state.pdf_chunks = []

            st.session_state.active_chat_id = chat_id
            st.session_state.active_pdf_name = chat["pdf_name"]
            st.session_state.selected_chat_id = chat_id

            st.session_state.upload_key += 1

        st.rerun()

    except Exception as e:

        st.error(
            f"Unable to open conversation: {e}"
        )


# Delete one conversation
def remove_chat(chat_id):

    user = st.session_state.get("user")

    if not user:
        return

    user_id = user["id"]

    try:

        # Get conversation details before deletion
        chat = get_conversation(
            chat_id,
            user_id
        )

        if not chat:
            st.warning("Conversation not found.")
            return

        # Delete conversation from database
        deleted = delete_chat(
            chat_id,
            user_id
        )

        if not deleted:
            st.warning(
                "Conversation could not be deleted."
            )
            return

        # Delete FAISS index independently
        if chat["vectorstore_path"]:

            try:

                delete_vector_store(
                    chat["vectorstore_path"],
                    user_id
                )

            except Exception as e:

                st.warning(
                    f"Conversation deleted, but vector index cleanup failed: {e}"
                )

        # Delete original PDF only if unused
        if chat["pdf_path"]:

            try:

                cleanup_pdf(
                    chat["pdf_path"],
                    user_id
                )

            except Exception as e:

                st.warning(
                    f"Conversation deleted, but PDF cleanup failed: {e}"
                )

        # Reset active conversation if it was deleted
        if st.session_state.active_chat_id == chat_id:
            reset_active_chat()

        st.session_state.delete_chat_id = None

        st.success("Conversation deleted.")

        st.rerun()

    except Exception as e:

        st.error(
            f"Unable to delete conversation: {e}"
        )


# Delete all conversations
def remove_all_chats():

    user = st.session_state.get("user")

    if not user:
        return

    user_id = user["id"]

    try:

        # Collect conversation details before deletion
        chats = get_all_chats(user_id)

        conversations = []

        for chat in chats:

            conversation = get_conversation(
                chat["id"],
                user_id
            )

            if conversation:
                conversations.append(conversation)

        # Delete all conversations from database
        delete_all_chats(user_id)

        # Collect unique PDF paths
        pdf_paths = set()

        # Clean up individual vector stores
        for conversation in conversations:

            if conversation["vectorstore_path"]:

                try:

                    delete_vector_store(
                        conversation["vectorstore_path"],
                        user_id
                    )

                except Exception as e:

                    st.warning(
                        f"Could not delete a vector index: {e}"
                    )

            if conversation["pdf_path"]:
                pdf_paths.add(conversation["pdf_path"])

        # Clean up original PDFs
        for pdf_path in pdf_paths:

            try:

                cleanup_pdf(
                    pdf_path,
                    user_id
                )

            except Exception as e:

                st.warning(
                    f"Could not delete a PDF: {e}"
                )

        # Reset active conversation
        reset_active_chat()

        st.session_state.confirm_delete_all = False
        st.session_state.delete_chat_id = None

        st.success("All conversations deleted.")

        st.rerun()

    except Exception as e:

        st.error(
            f"Unable to delete conversations: {e}"
        )


# Display conversation history
def show_chat_history():

    user = st.session_state.get("user")

    if not user:
        return

    user_id = user["id"]

    st.subheader("📚 Chat History")

    chats = get_all_chats(user_id)

    if not chats:

        st.info("No previous conversations.")

        return

    # Delete all conversations
    if st.button(
        "🗑️ Delete All Chats",
        key="delete_all_chats",
        use_container_width=True
    ):

        st.session_state.confirm_delete_all = True

    # Confirm delete all
    if st.session_state.get("confirm_delete_all", False):

        st.warning(
            "Are you sure you want to delete all conversations?"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Yes, delete all",
                key="confirm_delete_all_yes"
            ):

                remove_all_chats()

        with col2:

            if st.button(
                "Cancel",
                key="confirm_delete_all_no"
            ):

                st.session_state.confirm_delete_all = False

                st.rerun()

    st.divider()

    # Display individual conversations
    for chat in chats:

        chat_id = chat["id"]

        col1, col2 = st.columns([4, 1])

        # Open conversation
        with col1:

            if st.button(
                f"📄 {chat['pdf_name']}",
                key=f"open_chat_{chat_id}",
                use_container_width=True
            ):

                open_chat(chat_id)

        # Select conversation for deletion
        with col2:

            if st.button(
                "🗑️",
                key=f"delete_chat_{chat_id}"
            ):

                st.session_state.delete_chat_id = chat_id

        # Show deletion confirmation
        if st.session_state.get("delete_chat_id") == chat_id:

            st.warning(
                f"Delete conversation: {chat['pdf_name']}?"
            )

            confirm_col1, confirm_col2 = st.columns(2)

            with confirm_col1:

                if st.button(
                    "Confirm",
                    key=f"confirm_delete_{chat_id}"
                ):

                    remove_chat(chat_id)

            with confirm_col2:

                if st.button(
                    "Cancel",
                    key=f"cancel_delete_{chat_id}"
                ):

                    st.session_state.delete_chat_id = None

                    st.rerun()