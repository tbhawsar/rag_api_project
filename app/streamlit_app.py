import streamlit as st
import requests

st.set_page_config(
        page_title="PDF-GPT",
        page_icon=":books:",
    )

st.header("Upload documents to query them.") 
st.text_input("Ask your documents a question:")

with st.sidebar:
    st.subheader("Your Documents")
    docs = st.file_uploader("Upload PDFs or TXT files here and click the process button", accept_multiple_files=True, type=["pdf", "txt"])
    files = [
        ("files", (doc.name, doc, doc.type)) for doc in docs
    ]
    
    if st.button("Process Documents"):
        with st.spinner("Processing..."):
            res = requests.post(f"http://localhost:8000/ingest", files=files)
            st.write(res.json())
    
    query = st.text_input("Ask a question about your documents:")
    if st.button("Query Documents"):
        with st.spinner("Querying..."):
            res = requests.get(f"http://localhost:8000/query?q={query}")
            st.write(res.json())