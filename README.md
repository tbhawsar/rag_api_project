# RAG API Project

A Retrieval-Augmented Generation (RAG) system that allows you to ingest PDF and TXT documents, create vector embeddings, and query them using natural language. The system consists of a FastAPI backend for document processing and a Streamlit frontend for user interaction, all containerized with Docker.

## Features

- **Multi-format Document Support**: Upload PDF and TXT files
- **Vector Embeddings**: Uses OpenAI embeddings with FAISS vector store
- **RAG Pipeline**: Combines document retrieval with LLM generation
- **Web Interface**: Streamlit app for easy document upload and querying
- **REST API**: FastAPI backend for programmatic access
- **Dockerized**: Easy deployment with Docker and Docker Compose

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
├── requirements.txt         # Python dependencies
├── fastapi.Dockerfile       # FastAPI container configuration
├── streamlit.Dockerfile     # Streamlit container configuration
├── docker-compose.yml       # Multi-container orchestration
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag_api_project
   ```

2. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Build and start the containers**
   ```bash
   docker-compose up --build
   ```

4. **Access the applications**
   - **Streamlit UI**: http://localhost:8501
   - **FastAPI**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## Usage

### Using the Streamlit Interface

1. **Upload Documents**
   - Open http://localhost:8501 in your browser
   - Use the sidebar to upload PDF or TXT files
   - Click "Process Documents" to ingest them

2. **Query Documents**
   - Enter your question in the text input
   - Click "Query Documents" to get an answer

### Using the API Directly

The FastAPI server provides REST endpoints for programmatic access:

#### POST `/ingest`
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

#### GET `/query`
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

## Docker Commands

### Start the services
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs fastapi
docker-compose logs streamlit
```

### Stop the services
```bash
docker-compose down
```

### Rebuild after code changes
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Access container shell
```bash
# FastAPI container
docker-compose exec fastapi bash

# Streamlit container
docker-compose exec streamlit bash
```

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

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered in containers

### File Storage

- **Uploaded files**: Stored in `app/data/` (persisted via Docker volumes)
- **Combined text**: Saved to `app/data/ingested_text/combined_ingest.txt`
- **Vector index**: Stored in `faiss_index/` (persisted via Docker volumes)

## Troubleshooting

### Common Issues

1. **Container startup failures**
   - Check that your `.env` file exists and contains a valid `OPENAI_API_KEY`
   - Ensure Docker and Docker Compose are properly installed
   - Check container logs: `docker-compose logs`

2. **OpenAI API errors**
   - Verify your API key is set correctly in the `.env` file
   - Check your OpenAI account has sufficient credits
   - Ensure the API key has the necessary permissions

3. **File upload issues**
   - Ensure files are PDF or TXT format
   - Check file size limits
   - Verify the `app/data/` directory has proper permissions

4. **Vector store not found**
   - Make sure documents have been ingested before querying
   - Check that the `faiss_index` directory exists and is writable

5. **Port conflicts**
   - Ensure ports 8000 and 8501 are not already in use
   - Modify the port mappings in `docker-compose.yml` if needed

### Debug Mode

To see detailed processing information, check the container logs:
```bash
docker-compose logs -f fastapi
```

## Development

### Making Code Changes

1. **For Python code changes**: Rebuild the affected container
   ```bash
   docker-compose build fastapi  # or streamlit
   docker-compose up -d
   ```

2. **For dependency changes**: Rebuild with no cache
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Running Tests

```bash
docker-compose exec fastapi python -m pytest tests/
```

## Dependencies

Key dependencies include:
- `fastapi` - Web framework
- `streamlit` - Web interface
- `langchain` - RAG framework
- `langchain-openai` - OpenAI integration
- `openai` - OpenAI API client
- `faiss-cpu` - Vector similarity search
- `PyPDF2` - PDF text extraction
- `python-dotenv` - Environment variable management

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
