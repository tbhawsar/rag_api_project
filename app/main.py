from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from .rag_pipeline import RAGPipeline
import os
import shutil

load_dotenv()

app = FastAPI()
pipeline = RAGPipeline()

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

    return {"message": f"{len(files)} files ingested and index created."}

@app.get("/query")
async def query(q: str):
    print("Received query:", q)
    
    try:
        # Load vector store if not already loaded
        print("Loading index...")
        pipeline.load_index()
        print("Vector store loaded.")

        # Load QA chain if not already loaded
        print("Loading QA chain...")
        pipeline.create_qa_chain()
        print("QA chain loaded.")

        # Answer the question
        print("Answering question...")
        result = pipeline.answer_question(q)
        if not result:
            raise ValueError("No answer generated.")
        
        print("Generated Answer:", result["result"])
        return {"answer": result["result"],
                "source": [doc.page_content for doc in result["source_documents"]]
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

    