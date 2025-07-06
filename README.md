# RAG API Project

A Retrieval-Augmented Generation (RAG) system that allows you to ingest PDF and TXT documents, create vector embeddings, and query them using natural language. The system consists of a FastAPI backend for document processing and a Streamlit frontend for user interaction, all containerized with Docker.

## 🌐 Live Demo

**Try the application live:** [http://54.209.156.134:8501/](http://54.209.156.134:8501/)

## Features

- **Multi-format Document Support**: Upload PDF and TXT files
- **Vector Embeddings**: Uses OpenAI embeddings with FAISS vector store
- **RAG Pipeline**: Combines document retrieval with LLM generation using GPT-4o-mini
- **Conversation Memory**: Maintains chat history across sessions using LCEM History Aware Retrieval Chain
- **Modern Web Interface**: Streamlit app with tabbed interface for chat, history, and about sections
- **REST API**: FastAPI backend for programmatic access
- **Dockerized**: Easy deployment with Docker and Docker Compose
- **Cloud Deployed**: Running on AWS EC2 for public access

## Project Structure

```
rag_api_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI server with endpoints
│   ├── rag_pipeline.py      # Core RAG functionality with conversation memory
│   ├── data/                # Uploaded documents storage
│   │   └── ingested_text/   # Combined text output
│   └── streamlit_app.py     # Streamlit frontend with tabbed interface
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

The application features a modern tabbed interface:

#### 💬 Chat Tab
1. **Upload Documents**
   - Use the sidebar to upload PDF or TXT files
   - Click "Process Documents" to ingest them

2. **Query Documents**
   - Enter your question in the text input
   - Click "Query Documents" to get an answer
   - View source documents in expandable sections

#### 📜 Chat History Tab
- **Refresh History**: Click to view your conversation history
- **Clear History**: Remove all conversation memory
- View a summary of all previous interactions

#### ℹ️ About Tab
- Learn about the project features and technology stack
- Access useful commands and tips for better results

### Special Commands

- Type `history` in the chat to view conversation history
- Type `clear` in the chat to clear conversation history

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
  "message": "3 files ingested. You can now ask questions about your documents."
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

**Special Commands:**
- `q=history` - Get conversation history
- `q=clear` - Clear conversation history

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

## Deployment

### AWS EC2 Deployment

The application is currently deployed on AWS EC2 and accessible at:
- **Live Demo**: [http://54.209.156.134:8501/](http://54.209.156.134:8501/)

### Deployment Steps

1. **Launch EC2 Instance**
   - Use Ubuntu or Amazon Linux 2
   - Configure security groups to allow ports 8000 and 8501

2. **Install Docker and Docker Compose**
   ```bash
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **Deploy Application**
   ```bash
   git clone <repository-url>
   cd rag_api_project
   # Add your .env file with OPENAI_API_KEY
   docker-compose up -d
   ```

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

6. **Conversation history issues**
   - History is stored in memory and will be lost on container restart
   - Use the `history` command to check current conversation state

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
- `langchain-community` - Community integrations
- `openai` - OpenAI API client
- `faiss-cpu` - Vector similarity search
- `PyPDF2` - PDF text extraction
- `python-dotenv` - Environment variable management
- `requests` - HTTP client for inter-service communication

## Technology Stack

- **Backend**: FastAPI with Python
- **Frontend**: Streamlit with modern tabbed interface
- **AI/ML**: LangChain, OpenAI GPT-4o-mini, FAISS vector database
- **Document Processing**: PyPDF2 for PDF extraction
- **Cloud**: AWS EC2
- **Containerization**: Docker & Docker Compose

## License

MIT License

Copyright (c) 2025 Tilak Bhawsar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

