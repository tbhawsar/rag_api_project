import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
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
        # Initialize memory for conversation history
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    def _extract_text_from_pdf(self, file_path):

        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

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

    def create_qa_chain(self):
        
        if not self.vectorstore:
            raise ValueError("No FAISS index loaded. \
                Call load_index() or embed_and_store() first.")

        try:
            retriever = self.vectorstore.as_retriever()
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
            
            # Create history-aware retriever using LCEL and rephrase prompt
            history_aware_retriever = create_history_aware_retriever(
                llm, retriever, rephrase_prompt
            )
            
            # Create the document combination chain using qa chat prompt
            retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
            combine_docs_chain = create_stuff_documents_chain(
                llm, retrieval_qa_chat_prompt
            )
            
            # Create the final retrieval chain with history awareness
            self.qa_chain = create_retrieval_chain(
                history_aware_retriever, combine_docs_chain
            )

        except Exception as e:
            print("Error creating QA chain:", e)
            return None
        
        return self.qa_chain
    
    def answer_question(self, query):
        if not self.qa_chain:
            raise ValueError("QA chain not created, call create_qa_chain() first.")
         
        try:
            # Get conversation history from memory
            chat_history = self.memory.chat_memory.messages
            
            # Invoke the LCEL chain with input and chat history
            result = self.qa_chain.invoke({
                "input": query,
                "chat_history": chat_history
            })
            
            # Update memory with the conversation
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(result["answer"])
            
            return result
        except Exception as e:
            print("Error answering question:", e)
            return None

    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.memory.chat_memory.clear()
        print("Conversation history cleared.")

    def get_conversation_history(self):
        """Get the current conversation history"""
        return self.memory.chat_memory.messages

    def get_conversation_summary(self):
        """Get a summary of the conversation history"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No conversation history yet."
        
        summary = f"Conversation has {len(messages)} messages:\n"
        for i, message in enumerate(messages, 1):
            role = message.type
            # Replace role names with more user-friendly labels
            if role == "human":
                role = "Me"
            elif role == "ai":
                role = "Documents"
            
            content = str(message.content)
            content_preview = content[:100] + "..." if len(content) > 500 else content
            summary += f"{i}. {role}: {content_preview}\n"
        return summary
