import streamlit as st

from services.rag_service import generate_answer
from database.repository import save_message
from utils.pdf_export import generate_chat_pdf


# Format recent messages for the LLM
def format_chat_history(messages):

    history = []

    # Use the last 6 messages
    for msg in messages[-6:]:

        if msg["role"] == "user":
            role = "User"
        else:
            role = "Assistant"

        history.append(
            f"{role}: {msg['content']}"
        )

    return "\n".join(history)


# Display chat interface
def show_chat():

    st.subheader("💬 Chat with your PDF")

    db = st.session_state.get("db")

    chat_id = st.session_state.get("active_chat_id")

    user = st.session_state.get("user")

    # Check whether a PDF is loaded
    if db is None or chat_id is None:

        st.info(
            "Upload and process a PDF to start chatting."
        )

        return

    if not user:
        return

    user_id = user["id"]

    # Display active PDF name
    pdf_name = st.session_state.active_pdf_name

    st.caption(f"Currently chatting with: {pdf_name}")

    # Display previous messages
    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):

            st.markdown(msg["content"])

    # Chat input
    question = st.chat_input(
        "Ask something about your PDF..."
    )

    if question:

        # Prepare previous conversation history
        chat_history = format_chat_history(
            st.session_state.messages
        )

        # Display user question
        with st.chat_message("user"):
            st.markdown(question)

        # Save user question in SQLite
        try:

            save_message(
                chat_id,
                user_id,
                "user",
                question
            )

            st.session_state.messages.append({
                "role": "user",
                "content": question
            })

        except Exception as e:

            st.error(
                f"Unable to save your question: {e}"
            )

            st.stop()

        # Generate AI response
        with st.chat_message("assistant"):

            with st.spinner("Searching the PDF and generating an answer..."):

                try:

                    answer = generate_answer(
                        db,
                        question,
                        chat_history
                    )

                    # Save assistant response
                    save_message(
                        chat_id,
                        user_id,
                        "assistant",
                        answer
                    )

                    # Update session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                    st.markdown(answer)

                except Exception as e:

                    st.error(
                        f"Unable to generate an answer: {e}"
                    )


    # Download conversation as PDF
    if st.session_state.messages:

        st.divider()

        pdf_data = generate_chat_pdf(
            pdf_name,
            st.session_state.messages
        )

        st.download_button(
            label="📥 Download Chat as PDF",
            data=pdf_data,
            file_name="chat_conversation.pdf",
            mime="application/pdf",
            use_container_width=True
        )