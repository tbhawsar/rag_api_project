from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI, OpenAIEmbeddings
import os
from PyPDF2 import PdfReader

class RAGPipeline:
    def __init__(self, embedding_model_name="text-embedding-ada-002", \
        chunk_size=500, chunk_overlap=50, faiss_index_path="faiss_index"):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embeddings = OpenAIEmbeddings(model=embedding_model_name)
        self.faiss_index_path = faiss_index_path
        self.vectorstore = None
        self.documents = None
        self.qa_chain = None

    def load_files(self, file_paths):
        texts = []
        for file in file_paths:
            if file.lower().endswith('.pdf'):
                texts.append(self._extract_text_from_pdf(file))
            elif file.lower().endswith('.txt'):
                with open(file, 'r', encoding='utf-8') as f:
                    texts.append(f.read())
            else:
                raise ValueError(f"Unsupported file type: {file}")

        # Combine all texts into one document list for chunking
        self.documents = self.text_splitter.create_documents(texts)

        # Write combined text to a .txt file in the 'ingested_text' folder
        output_dir = "app/data/ingested_text"
        os.makedirs(output_dir, exist_ok=True)
        combined_text = "\n\n".join(texts)
        output_path = os.path.join(output_dir, "combined_ingest.txt")
        print(f"Saving combined ingested text to: {os.path.abspath(output_path)}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(combined_text)

        return self.documents

    def _extract_text_from_pdf(self, file_path):
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def embed_and_store(self):
        if not self.documents:
            raise ValueError("No documents loaded. Call load_text_file() first.")
        self.vectorstore = FAISS.from_documents(self.documents, self.embeddings)

    def save_index(self):
        if not self.vectorstore:
            raise ValueError("No FAISS index to save. Call embed_and_store() first.")
        self.vectorstore.save_local(self.faiss_index_path)

    def load_index(self):
        if not os.path.exists(self.faiss_index_path):
            raise FileNotFoundError(f"FAISS index not found at {self.faiss_index_path}")
        self.vectorstore = FAISS.load_local(
            self.faiss_index_path, 
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

        print("FAISS Index loaded successfully.")
        return f"FAISS index loaded successfully from {self.faiss_index_path}."

    def query(self, query_text, k=100):
        if not self.vectorstore:
            raise ValueError("No FAISS index loaded. \
                Call load_index() or embed_and_store() first.")
        results = self.vectorstore.similarity_search(query_text, k=k)
        return [doc.page_content for doc in results]

    def create_qa_chain(self):
        
        if not self.vectorstore:
            raise ValueError("No FAISS index loaded. \
                Call load_index() or embed_and_store() first.")

        try:
            retriever = self.vectorstore.as_retriever()
            llm = OpenAI(temperature=0)

            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                return_source_documents=True,
            )

        except Exception as e:
            print("Error creating QA chain:", e)
            return None
        
        return self.qa_chain
    
    def answer_question(self, query):
        if not self.qa_chain:
            raise ValueError("QA chain not created, call create_qa_chain() first.")
         
        try:
            result = self.qa_chain({"query": query})
            return result
        except Exception as e:
            print("Error answering question:", e)
            return None

   
