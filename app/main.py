from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import RedirectResponse
from .rag_pipeline import RAGPipeline
import os
import shutil

load_dotenv()

app = FastAPI()
pipeline = RAGPipeline()


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):

    # Save the uploaded file to the disk
    data_dir = "app/data"
    os.makedirs(data_dir, exist_ok=True)
    
    file_paths = []

    for idx, file in enumerate(files):
        if not file.filename:
            raise ValueError(f"No filename provided for file at index {idx}")
        file_path = os.path.join(data_dir, file.filename)
        file_paths.append(file_path)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # Load and split text
    pipeline.load_files(file_paths)

    # Build vector store
    pipeline.embed_and_store()

    # Save index
    pipeline.save_index()

    print("Type 'history' as the query to see the conversation history, or 'clear' to clear the conversation history:\n")
    return {"message": f"{len(files)} files ingested. You can now ask questions about your documents."}

@app.get("/query")
async def query(q: str):
    print("Received query:", q)
    
    # Handle special commands first
    if q.lower() == 'history':
        try:
            pipeline.load_index()
            history_summary = pipeline.get_conversation_summary()
            return {"answer": history_summary, "source": []}
        except Exception as e:
            return {"error": f"Error getting history: {str(e)}"}
    
    if q.lower() == 'clear':
        try:
            pipeline.load_index()
            pipeline.clear_conversation_history()
            return {"answer": "Conversation history cleared.", "source": []}
        except Exception as e:
            return {"error": f"Error clearing history: {str(e)}"}
    
    try:
        # Load vector store if not already loaded
        print("Loading index...")
        pipeline.load_index()
        print("Vector store loaded.")

        # Load QA chain if not already loaded
        print("Loading QA chain...")
        pipeline.create_qa_chain()
        print("QA chain loaded. Starting conversation...")

        # Answer the question
        print("Answering question...")
        result = pipeline.answer_question(q)
        if not result:
            raise ValueError("No answer generated.")
            
        return {"answer": result["answer"],
                "source": [doc.page_content for doc in result["context"]]
        }

    except FileNotFoundError as e:
        print("Index file not found:", e)
        return {"error": "FAISS index file not found. Please ingest data first."}
    except ValueError as e:
        print("ValueError:", e)
        return {"error": str(e)}
    except Exception as e:
        print("Unexpected error:", e)
        return {"error": "An unexpected error occurred."}