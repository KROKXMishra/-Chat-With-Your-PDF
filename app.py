from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
import streamlit as st

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

st.set_page_config(page_title="PDF Chatbot")
st.title("📚 Chat With Your PDF")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "db" not in st.session_state:
    st.session_state.db = None

if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    if st.session_state.current_pdf != uploaded_file.name:

        with st.spinner("Processing PDF..."):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp_file:

                tmp_file.write(
                    uploaded_file.getbuffer()
                )

                pdf_path = tmp_file.name

            loader = PyPDFLoader(pdf_path)
            docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=100
            )

            chunks = splitter.split_documents(docs)

            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            st.session_state.db = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings
            )

            os.remove(pdf_path)

            st.session_state.current_pdf = uploaded_file.name
            st.session_state.messages = []

        st.sidebar.success("PDF Ready For Chat")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
        context += doc.page_content + "\n\n"

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
1. Use previous conversation for follow-up questions.
2. Use PDF context whenever possible.
3. If asked for summary, overview, key points, or important topics, generate them from the context.
4. If the answer is unavailable in the PDF context, say:
'I could not find that information in the PDF.'
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

if st.sidebar.button("Clear Chat"):

    st.session_state.messages = []
    st.rerun()