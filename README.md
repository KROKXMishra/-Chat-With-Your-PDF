# 📚 Chat With Your PDF

A Retrieval-Augmented Generation (RAG) based PDF chatbot that allows users to upload PDF documents and interact with them using natural language. The application extracts text from uploaded PDFs, creates vector embeddings using Hugging Face models, stores them in ChromaDB, and uses Groq-powered LLMs to generate accurate and context-aware responses.

## 🚀 Features

* Upload PDF files directly from the web interface
* ChatGPT-style conversational UI
* Ask questions about uploaded PDFs
* Conversational memory for follow-up questions
* Semantic search using vector embeddings
* ChromaDB vector database
* Groq Llama 3.3 70B integration
* Completely free LLM and embedding stack
* Automatic PDF processing and indexing

## 🛠️ Tech Stack

* Python
* Streamlit
* LangChain
* Groq (Llama 3.3 70B)
* Hugging Face Embeddings
* ChromaDB
* PyPDF
* RAG (Retrieval-Augmented Generation)

## 📂 Project Structure

```text
pdf-rag-chatbot/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
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

Linux/Mac:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
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
Hugging Face Embeddings
    ↓
ChromaDB
    ↓
Context Retrieval
    ↓
Groq Llama 3.3 70B
    ↓
Answer Generation
```

## 🎯 Use Cases

* Chat with books and notes
* Analyze research papers
* Summarize large PDF documents
* Extract important points
* Interactive learning and revision

## 🌟 Highlights

* No OpenAI API required
* Fully free AI stack
* Supports large PDF documents
* Fast inference with Groq
* Easy deployment using Streamlit Cloud

## 👨‍💻 Author

Kallol Mishra

CSE Student, NIT Durgapur
