# RAG API Project

A Retrieval-Augmented Generation (RAG) system that allows you to ingest PDF and TXT documents, create vector embeddings, and query them using natural language. The system consists of a FastAPI backend for document processing and a Streamlit frontend for user interaction.

## Features

- **Multi-format Document Support**: Upload PDF and TXT files
- **Vector Embeddings**: Uses OpenAI embeddings with FAISS vector store
- **RAG Pipeline**: Combines document retrieval with LLM generation
- **Web Interface**: Streamlit app for easy document upload and querying
- **REST API**: FastAPI backend for programmatic access

## Project Structure

```
rag_api_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI server with endpoints
│   ├── rag_pipeline.py      # Core RAG functionality
│   ├── data/                # Uploaded documents storage
│   │   └── ingested_text/   # Combined text output
│   └── streamlit_app.py     # Streamlit frontend
├── tests/
│   └── test_api.py          # API tests
├── faiss_index/             # Vector store index
├── requirements.txt
├── Dockerfile
└── README.md
```

## Prerequisites

- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag_api_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Starting the FastAPI Server

1. **Activate your virtual environment** (if using one)
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

2. **Start the FastAPI server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The server will be available at `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Starting the Streamlit App

1. **In a new terminal, start Streamlit**
   ```bash
   streamlit run app/streamlit_app.py
   ```

   The Streamlit app will be available at `http://localhost:8501`

## API Endpoints

### POST `/ingest`
Upload and process documents.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Multiple files with field name `"files"`

**Response:**
```json
{
  "message": "3 files ingested and index created."
}
```

**Example with curl:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt"
```

### GET `/query`
Query the ingested documents.

**Request:**
- Method: `GET`
- Parameters: `q` (query string)

**Response:**
```json
{
  "answer": "Generated answer based on documents",
  "source": ["source document chunks..."]
}
```

**Example:**
```bash
curl "http://localhost:8000/query?q=What%20are%20the%20main%20points%20of%20the%20documents?"
```

## Using the Streamlit Interface

1. **Upload Documents**
   - Use the sidebar to upload PDF or TXT files
   - Click "Process Documents" to ingest them

2. **Query Documents**
   - Enter your question in the text input
   - Click "Query Documents" to get an answer

## Configuration

### RAG Pipeline Settings

You can modify the RAG pipeline parameters in `app/rag_pipeline.py`:

```python
pipeline = RAGPipeline(
    embedding_model_name="text-embedding-ada-002",  # OpenAI embedding model
    chunk_size=500,                                  # Text chunk size
    chunk_overlap=50,                                # Overlap between chunks
    faiss_index_path="faiss_index"                  # Index storage location
)
```

### File Storage

- **Uploaded files**: Stored in `app/data/`
- **Combined text**: Saved to `app/data/ingested_text/combined_ingest.txt`
- **Vector index**: Stored in `faiss_index/`

## Troubleshooting

### Common Issues

1. **"No module named 'app'" error**
   - Make sure you're running commands from the project root directory
   - Check that your virtual environment is activated

2. **OpenAI API errors**
   - Verify your API key is set in the `.env` file
   - Check your OpenAI account has sufficient credits

3. **File upload issues**
   - Ensure files are PDF or TXT format
   - Check file size limits

4. **Vector store not found**
   - Make sure documents have been ingested before querying
   - Check that the `faiss_index` directory exists

### Debug Mode

To see detailed processing information, check the FastAPI server terminal for debug output during ingestion and querying.

## Dependencies

Key dependencies include:
- `fastapi` - Web framework
- `streamlit` - Web interface
- `langchain` - RAG framework
- `openai` - OpenAI API client
- `faiss-cpu` - Vector similarity search
- `PyPDF2` - PDF text extraction
- `python-dotenv` - Environment variable management

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
