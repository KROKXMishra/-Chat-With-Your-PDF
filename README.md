# 📚 PDF Chatbot using RAG

A Retrieval-Augmented Generation (RAG) based chatbot that allows users to upload PDF documents and interact with them using natural language. The application extracts text from uploaded PDFs, generates embeddings using OpenAI, stores them in ChromaDB, and retrieves relevant context to answer user queries accurately.

## 🚀 Features

- Upload PDF files directly from the web interface
- ChatGPT-style conversational UI
- Context-aware question answering
- Conversational memory for follow-up questions
- Semantic search using vector embeddings
- ChromaDB vector database integration
- OpenAI GPT-4o-mini powered responses
- Automatic PDF processing and indexing

## 🛠️ Tech Stack

- Python
- LangChain
- OpenAI GPT-4o-mini
- OpenAI Embeddings
- ChromaDB
- Streamlit
- PyPDF
- RAG (Retrieval-Augmented Generation)

## 📂 Project Structure

```text
pdf-rag-chatbot/
│
├── app.py
├── requirements.txt
├── .env
└── README.md
```

## ⚙️ Installation

### Clone the Repository

```bash
git clone <repository-url>
cd pdf-rag-chatbot
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

Linux / Mac:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

## ▶️ Run the Application

```bash
streamlit run app.py
```

## 📖 How It Works

```text
PDF Upload
    ↓
Text Extraction
    ↓
Chunking
    ↓
OpenAI Embeddings
    ↓
ChromaDB
    ↓
Context Retrieval
    ↓
GPT-4o-mini
    ↓
Answer Generation
```

## 🎯 Use Cases

- Chat with books and notes
- Ask questions about research papers
- Summarize large PDF documents
- Extract key insights
- Interactive learning and revision

## 📸 Demo

Upload any PDF and start asking questions in natural language through the chat interface.

## 👨‍💻 Author

Kallol
NIT Durgapur | CSE