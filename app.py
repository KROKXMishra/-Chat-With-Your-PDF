from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

st.set_page_config(page_title="PDF Chatbot")
st.title("📚 Chat With Your PDF")

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "db" not in st.session_state:
    st.session_state.db = None

if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None

# Upload PDF
uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    if st.session_state.current_pdf != uploaded_file.name:

        with st.spinner("Processing PDF..."):

            # Save PDF temporarily
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp_file:

                tmp_file.write(
                    uploaded_file.getbuffer()
                )

                pdf_path = tmp_file.name

            # Load PDF
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()

            # Split PDF
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

            chunks = splitter.split_documents(docs)

            # Embeddings
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small"
            )

            # Create Chroma in memory
            st.session_state.db = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings
            )

            # Delete temporary PDF
            os.remove(pdf_path)

            st.session_state.current_pdf = uploaded_file.name
            st.session_state.messages = []

        st.sidebar.success("PDF Ready For Chat")

# LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# Display Chat History
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
question = st.chat_input(
    "Ask anything from the PDF..."
)

if question:

    if st.session_state.db is None:

        st.warning(
            "Please upload a PDF first."
        )

        st.stop()

    with st.chat_message("user"):
        st.markdown(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    retriever = st.session_state.db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8}
    )

    docs = retriever.invoke(question)

    context = ""

    for doc in docs:
        context += doc.page_content
        context += "\n\n"

    history = ""

    for msg in st.session_state.messages[-6:]:

        history += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    prompt = f"""
You are a helpful PDF assistant.

Previous Conversation:
{history}

PDF Context:
{context}

Current Question:
{question}

Rules:
1. Use previous conversation to understand follow-up questions.
2. Use PDF context whenever possible.
3. If user asks for summary, important points, key topics or overview, generate them from the context.
4. If answer is unavailable in the context, say:
"I could not find that information in the PDF."
"""

    response = llm.invoke(prompt)

    answer = response.content

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# Clear Chat
if st.sidebar.button("Clear Chat"):

    st.session_state.messages = []
    st.rerun()