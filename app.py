import os
import tempfile
import hashlib
import streamlit as st

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

load_dotenv()

st.set_page_config(page_title="PDF Chatbot")
st.title("📚 Chat With Your PDF")

@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

@st.cache_resource
def get_llm():

    api_key = None

    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        api_key = os.getenv("GROQ_API_KEY")

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if "db" not in st.session_state:
    st.session_state.db = None

if "pdf_hash" not in st.session_state:
    st.session_state.pdf_hash = None

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    current_hash = hashlib.md5(
        uploaded_file.getvalue()
    ).hexdigest()

    if current_hash != st.session_state.pdf_hash:

        st.session_state.db = None
        st.session_state.messages = []
        st.session_state.pdf_hash = current_hash

        progress = st.progress(0)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp_file:

            tmp_file.write(
                uploaded_file.getbuffer()
            )

            pdf_path = tmp_file.name

        progress.progress(20)

        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        st.sidebar.write("Preview:")
        st.sidebar.write(
            docs[0].page_content[:300]
        )

        progress.progress(40)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=100
        )

        chunks = splitter.split_documents(
            docs
        )

        st.sidebar.write(
            f"📄 Pages: {len(docs)}"
        )

        st.sidebar.write(
            f"🧩 Chunks: {len(chunks)}"
        )

        progress.progress(60)

        embeddings = get_embeddings()

        progress.progress(80)

        st.session_state.db = FAISS.from_documents(
            chunks,
            embeddings
        )

        progress.progress(100)

        os.remove(pdf_path)

        st.sidebar.success(
            "✅ PDF Ready For Chat"
        )

llm = get_llm()

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )

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

    docs = st.session_state.db.similarity_search(
        question,
        k=8
    )

    context = ""

    for doc in docs:

        context += (
            doc.page_content
            + "\n\n"
        )

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
3. If asked for summary, overview, key points or important topics, generate them from the PDF.
4. If answer is unavailable in the PDF, say:
'I could not find that information in the PDF.'
"""

    response = llm.invoke(
        prompt
    )

    answer = response.content

    with st.chat_message(
        "assistant"
    ):
        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

if st.sidebar.button(
    "Clear Chat"
):

    st.session_state.messages = []
    st.session_state.db = None
    st.session_state.pdf_hash = None

    st.rerun()