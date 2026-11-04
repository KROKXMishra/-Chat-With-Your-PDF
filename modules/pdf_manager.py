import hashlib
import streamlit as st

from services.pdf_service import (
    extract_pdf,
    save_uploaded_pdf,
    delete_saved_pdf
)

from services.rag_service import (
    create_vector_store,
    save_vector_store,
    delete_vector_store
)

from database.repository import (
    create_conversation,
    update_conversation_pdf_path,
    update_vectorstore_path,
    delete_chat,
    count_pdf_references
)


MAX_PDF_SIZE = 50 * 1024 * 1024


def cleanup_failed_processing(
    chat_id,
    user_id,
    pdf_path,
    vectorstore_path
):

    # Delete the partially created vector store
    if vectorstore_path:
        try:
            delete_vector_store(
                vectorstore_path,
                user_id
            )
        except Exception as e:
            st.warning(
                f"Could not clean up vector store: {e}"
            )

    # Delete the partially created conversation
    if chat_id:
        try:
            delete_chat(
                chat_id,
                user_id
            )
        except Exception as e:
            st.warning(
                f"Could not clean up conversation: {e}"
            )

    # Delete the original PDF only if no conversation uses it
    if pdf_path:
        try:
            references = count_pdf_references(
                pdf_path,
                user_id
            )

            if references == 0:
                delete_saved_pdf(
                    pdf_path,
                    user_id
                )

        except Exception as e:
            st.warning(
                f"Could not clean up uploaded PDF: {e}"
            )


def show_pdf_manager():

    st.subheader("📄 Upload your PDF")

    user = st.session_state.get("user")

    if not user:
        return

    user_id = user["id"]

    # PDF uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        key=f"pdf_uploader_{st.session_state.upload_key}"
    )

    if uploaded_file is None:
        return

    file_bytes = uploaded_file.getvalue()

    # Validate file
    if not file_bytes:
        st.warning("The uploaded PDF is empty.")
        return

    if len(file_bytes) > MAX_PDF_SIZE:
        st.error("PDF size must not exceed 50 MB.")
        return

    # Generate SHA-256 hash
    pdf_hash = hashlib.sha256(file_bytes).hexdigest()

    # Check whether this PDF is already active
    if pdf_hash == st.session_state.pdf_hash:
        st.info("This PDF is already loaded.")
        return

    st.write(f"**Selected file:** {uploaded_file.name}")

    # Process PDF
    if st.button(
        "Process PDF",
        type="primary",
        use_container_width=True
    ):

        chat_id = None
        pdf_path = None
        vectorstore_path = None

        try:

            with st.spinner("Processing your PDF..."):

                # 1. Extract PDF text
                docs = extract_pdf(file_bytes)

                if not docs:
                    raise ValueError(
                        "No readable content found in the PDF."
                    )

                # 2. Create FAISS vector store
                db, chunks = create_vector_store(docs)

                # 3. Create conversation in SQLite
                chat_id = create_conversation(
                    user_id,
                    uploaded_file.name
                )

                # 4. Save original PDF
                pdf_path = save_uploaded_pdf(
                    file_bytes,
                    user_id,
                    pdf_hash
                )

                # 5. Save FAISS vector store
                vectorstore_path = save_vector_store(
                    db,
                    user_id,
                    chat_id
                )

                # 6. Save PDF path in database
                pdf_updated = update_conversation_pdf_path(
                    chat_id,
                    user_id,
                    pdf_path
                )

                if not pdf_updated:
                    raise RuntimeError(
                        "Unable to save PDF path in database."
                    )

                # 7. Save vector store path in database
                vector_updated = update_vectorstore_path(
                    chat_id,
                    user_id,
                    vectorstore_path
                )

                if not vector_updated:
                    raise RuntimeError(
                        "Unable to save vector store path in database."
                    )

                # 8. Update Streamlit session state
                st.session_state.db = db
                st.session_state.pdf_hash = pdf_hash
                st.session_state.pdf_docs = docs
                st.session_state.pdf_chunks = chunks
                st.session_state.active_chat_id = chat_id
                st.session_state.active_pdf_name = uploaded_file.name
                st.session_state.messages = []
                st.session_state.selected_chat_id = chat_id

                st.success("PDF processed successfully!")

                st.rerun()

        except Exception as e:

            # Clean up partially created resources
            cleanup_failed_processing(
                chat_id,
                user_id,
                pdf_path,
                vectorstore_path
            )

            st.error(
                f"Unable to process PDF: {e}"
            )