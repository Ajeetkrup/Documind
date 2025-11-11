# DocuMind 🧠

**Intelligent Document Intelligence System** - Ask questions about your documents and get accurate, verified answers.

---

## What is DocuMind?

DocuMind is an AI-powered system that lets you upload documents and ask questions about them. It uses advanced AI to:
- Find relevant information in your documents
- Generate accurate answers
- Verify facts before responding
- Handle multiple documents at once

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the project root with your API keys:

```bash
HUGGINGFACE_API_TOKEN=your-token-here
GROQ_API_KEY=your-key-here
```

**Get your API keys:**
- [Hugging Face](https://huggingface.co/settings/tokens)
- [Groq](https://console.groq.com/keys)

### 3. Run the Application
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

---

## How to Use

1. **Upload Documents** - PDF, DOCX, TXT, or Markdown files
2. **Ask a Question** - Type your question in the text box
3. **Get Answer** - Click Submit to receive an accurate, verified answer

You can also try the example questions from the dropdown menu!

---

## Features

✅ **Multi-Document Support** - Upload and query multiple documents  
✅ **Fact Verification** - Answers are verified against source documents  
✅ **Relevance Checking** - Detects if questions are out of scope  
✅ **Hybrid Retrieval** - Uses both keyword and semantic search  
✅ **No Hallucinations** - Only answers based on your documents  

---

## Supported File Formats

- PDF (`.pdf`)
- Word Documents (`.docx`)
- Text Files (`.txt`)
- Markdown (`.md`)

---

## Technology Stack

- **Docling** - Document parsing
- **LangChain** - RAG framework
- **ChromaDB** - Vector database
- **Groq** - Fast LLM inference
- **Hugging Face** - Embeddings and models
- **Gradio** - Web interface

---

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.

---

## Contact

For questions or support, please open an issue on GitHub.
