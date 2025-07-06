import streamlit as st
import requests

# Initialize session state for storing responses
if 'ingest_response' not in st.session_state:
    st.session_state.ingest_response = None
if 'query_response' not in st.session_state:
    st.session_state.query_response = None
if 'success_message' not in st.session_state:
    st.session_state.success_message = None

st.set_page_config(
        page_title="Chat With Your Documents",
        page_icon=":books:",
    )

# Create tabs for main chat, history, and about
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📜 Chat History", "ℹ️ About"])

with tab1:
    st.header("Upload documents to chat with them.") 

    with st.form("query_form"):
        query = st.text_input("Ask a question about your documents:")
        submit_button = st.form_submit_button("Query Documents")
        
        if submit_button:
            with st.spinner("Querying..."):
                res = requests.get(f"http://rag_fastapi:8000/query?q={query}")
                st.session_state.query_response = res.json()

    # Display query response in the chat tab
    if st.session_state.query_response:
        if "answer" in st.session_state.query_response:
            # Display just the answer in a chat-like format
            st.markdown("### 🤖 Assistant:")
            st.markdown(st.session_state.query_response["answer"])
            
            # Optionally show source documents if available
            if "source" in st.session_state.query_response and st.session_state.query_response["source"]:
                with st.expander("📚 View Source Documents"):
                    for i, source in enumerate(st.session_state.query_response["source"], 1):
                        st.markdown(f"**Source {i}:**")
                        st.markdown(source)
                        st.markdown("---")
        elif "error" in st.session_state.query_response:
            st.error(f"❌ Error: {st.session_state.query_response['error']}")
        else:
            # Fallback to JSON if structure is unexpected
            st.json(st.session_state.query_response)

with tab2:
    st.header("Chat History")
    
    # Add buttons for history management
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh History"):
            with st.spinner("Loading chat history..."):
                res = requests.get(f"http://rag_fastapi:8000/query?q=history")
                st.session_state.history_response = res.json()
    
    with col2:
        if st.button("🗑️ Clear History"):
            with st.spinner("Clearing chat history..."):
                res = requests.get(f"http://rag_fastapi:8000/query?q=clear")
                st.session_state.history_response = res.json()
                # Also clear the main chat response
                st.session_state.query_response = None
    
    # Display chat history
    if 'history_response' in st.session_state and st.session_state.history_response:
        if "answer" in st.session_state.history_response:
            st.markdown("### Conversation History:")
            st.markdown(st.session_state.history_response["answer"])
        elif "error" in st.session_state.history_response:
            st.error(f"❌ Error: {st.session_state.history_response['error']}")
    else:
        st.info("Click 'Refresh History' to view your conversation history.")

with tab3:
    st.header("About This Project")
    
    st.markdown("""
    ### 🤖 RAG-Powered Document Chat
    
    This application allows you to upload documents (PDFs and TXT files) and have intelligent conversations about their content using Retrieval-Augmented Generation (RAG) technology.
    
    ### ✨ Features
    
    - **Document Upload**: Support for PDF and TXT files
    - **Intelligent Q&A**: Ask questions about your documents and get contextual answers
    - **Conversation Memory**: The AI remembers your conversation history
    - **Source Citations**: See which parts of your documents were used to answer questions
    - **Chat History**: View and manage your conversation history
    
    ### 🛠️ How It Works
    
    1. **Upload Documents**: Use the sidebar to upload your PDF or TXT files
    2. **Process Documents**: Click "Process Documents" to create a searchable index
    3. **Ask Questions**: Type your questions in the chat interface
    4. **Get Answers**: Receive intelligent responses based on your document content
    
    ### 🔧 Technology Stack
    
    - **Backend**: FastAPI with Python
    - **Frontend**: Streamlit
    - **AI/ML**: LangChain, OpenAI GPT-4, FAISS vector database
    - **Document Processing**: PyPDF2 for PDF extraction
    - **Cloud**: AWS EC2
    - **Containerization**: Docker

    ### 📚 Useful Commands
    
    - Type `history` in the chat to view conversation history
    - Type `clear` in the chat to clear conversation history
    
    ### 🔗 Links
    
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📖 GitHub Repository**  
        [View Source Code](https://github.com/tbhawsar/rag_api_project)
        """)
    
    with col2:
        st.markdown("""
        **📄 README**  
        [Project Documentation](https://github.com/tbhawsar/rag_api_project/blob/main/README.md)
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🚀 Getting Started
    
    If you're new to this application:
    
    1. **First Time**: Upload some documents and click "Process Documents"
    2. **Ask Questions**: Start with simple questions like "What is this document about?"
    3. **Explore**: Try asking follow-up questions to dive deeper into the content
    
    ### 💡 Tips for Better Results
    
    - Test out the Assitant's knowledge by asking vague or indirectly worded questions to see how it responds
    - Upload multiple related documents for comprehensive answers
    - Use the chat history to continue conversations about specific topics
    """)

with st.sidebar:
    st.subheader("Your Documents")
    docs = st.file_uploader("Upload PDFs or TXT files here and click the process button", accept_multiple_files=True, type=["pdf", "txt"])
    if docs:
        files = [
            ("files", (doc.name, doc, doc.type)) for doc in docs
        ]
    
    if st.button("Process Documents"):
        with st.spinner("Processing..."):
            res = requests.post(f"http://rag_fastapi:8000/ingest", files=files)
            st.session_state.ingest_response = res.json()

# Display ingest response on main page
if st.session_state.ingest_response:
    if "message" in st.session_state.ingest_response:
        # Set success message
        st.session_state.success_message = st.session_state.ingest_response['message']
        # # Clear the ingest response to prevent it from reappearing
        # st.session_state.ingest_response = None
        st.toast(f"{st.session_state.success_message}", icon="✅")
    else:
        st.json(st.session_state.ingest_response)
