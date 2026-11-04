# 📚 PDF Reader AI — RAG-Based PDF Chatbot

An AI-powered PDF assistant that allows users to upload PDF documents, ask questions about their content, and receive intelligent, context-aware answers using **Retrieval-Augmented Generation (RAG)**.

Built using Python, Streamlit, LangChain, FAISS, HuggingFace Embeddings, and Groq LLMs.

---

## 🚀 Features

- **User Authentication:** Secure registration and login using bcrypt password hashing.
- **PDF Upload & Processing:** Upload PDF documents and extract their textual content.
- **Text Chunking:** Split extracted content into smaller chunks for efficient retrieval.
- **Semantic Search:** Generate embeddings using HuggingFace Sentence Transformers.
- **Vector Search:** Store and retrieve document embeddings using FAISS.
- **AI-Powered Question Answering:** Generate context-aware responses using Groq-hosted LLMs.
- **Conversation History:** Store conversations and messages using SQLite.
- **Persistent Conversations:** Reopen previous conversations and continue chatting with previously uploaded PDFs.
- **Multi-User Support:** Maintain separate conversations and document storage for different users.
- **PDF Export:** Download chat conversations as formatted PDF documents with Markdown-style formatting.

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| LLM | Groq — GPT-OSS-20B |
| LLM Framework | LangChain |
| Embedding Model | Sentence Transformers — all-MiniLM-L6-v2 |
| Vector Database | FAISS |
| Database | SQLite |
| Authentication | bcrypt |
| PDF Extraction | PyPDFLoader |
| PDF Generation | ReportLab |
| Environment Management | python-dotenv |

---

## 🏗️ System Architecture

The application follows a modular architecture that separates the user interface, business logic, database operations, and AI processing.

```text
                 User
                   |
                   v
            Streamlit Frontend
                   |
          +--------+--------+
          |                 |
          v                 v
     Authentication     PDF Upload
          |                 |
          v                 v
     SQLite Database    PDF Extraction
                            |
                            v
                      Text Cleaning
                            |
                            v
                       Text Chunking
                            |
                            v
                  HuggingFace Embeddings
                            |
                            v
                      FAISS Index
                            |
                            v
                    Similarity Search
                            |
                            v
                    Relevant Context
                            |
                            v
                     Groq LLM
                            |
                            v
                    Generated Answer
                            |
                  +---------+---------+
                  |                   |
                  v                   v
             SQLite Storage       Streamlit Chat
                                      |
                                      v
                                  PDF Export
```

---

## 📂 Project Structure

```text
pdf-rag-chatbot/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
├── runtime.txt
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── models.py
│   └── repository.py
│
├── modules/
│   ├── __init__.py
│   ├── authentication.py
│   ├── profile.py
│   ├── chat.py
│   ├── pdf_manager.py
│   └── chat_history.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── pdf_service.py
│   ├── rag_service.py
│   └── llm_service.py
│
├── utils/
│   ├── __init__.py
│   ├── text_cleaner.py
│   └── pdf_export.py
│
├── assets/
│   └── style.css
│
├── uploads/
├── vectorstores/
└── chat_history.db
```

**Note:** The `uploads/`, `vectorstores/`, and `chat_history.db` entries represent runtime-generated data. They are excluded from Git tracking.

---

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd pdf-rag-chatbot
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository's actual URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Get your API key from the Groq developer console:

https://console.groq.com/

**Important:** Never commit your `.env` file or expose your API key publicly.

### 6. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

---

## 🔍 How RAG Works in This Project

The application uses Retrieval-Augmented Generation to answer questions based on uploaded PDF documents.

**Step 1 — Document Loading**

PyPDFLoader extracts textual content from the uploaded PDF.

**Step 2 — Text Splitting**

RecursiveCharacterTextSplitter divides the extracted text into smaller chunks with overlapping content.

**Step 3 — Embedding Generation**

The HuggingFace model `sentence-transformers/all-MiniLM-L6-v2` converts text chunks into numerical vector representations.

**Step 4 — Vector Storage**

FAISS stores the generated embeddings and enables efficient similarity-based retrieval.

**Step 5 — Relevant Document Retrieval**

When a user asks a question, the application retrieves the most relevant document chunks using semantic similarity search.

**Step 6 — Answer Generation**

The retrieved context and user question are passed to the Groq-hosted LLM through LangChain.

The LLM generates an answer grounded in the retrieved PDF content.

---

## 🗄️ Database Design

The application uses SQLite to maintain user accounts and conversation history.

| Table | Purpose |
|---|---|
| `users` | Stores user account details and password hashes |
| `conversations` | Stores conversation information and document paths |
| `messages` | Stores user questions and AI-generated answers |

Foreign key relationships maintain the association between users, conversations, and messages.

---

## 🔐 Security Considerations

- Passwords are hashed using bcrypt instead of storing plaintext passwords.
- SQL queries use parameterized statements.
- Conversation retrieval checks user ownership.
- PDF and vector-store paths are validated before accessing stored files.
- API credentials are loaded through environment variables.
- Uploaded documents and generated vector indexes are kept outside Git tracking.

---

## 🔮 Future Improvements

- OCR support for scanned PDF documents.
- Improved conversational retrieval using query rewriting.
- Support for multiple document formats.
- Advanced Markdown and table rendering in PDF exports.
- Streaming LLM responses.
- Cloud-based document and vector storage.
- Deployment with persistent storage.

---

## 👨‍💻 Author

**Kallol Mishra**

B.Tech — Computer Science and Engineering  
National Institute of Technology Durgapur

---

## ⭐ Acknowledgements

- [LangChain](https://www.langchain.com/)
- [Streamlit](https://streamlit.io/)
- [Groq](https://groq.com/)
- [Hugging Face](https://huggingface.co/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [ReportLab](https://www.reportlab.com/)

If you find this project interesting, consider giving the repository a ⭐ on GitHub!