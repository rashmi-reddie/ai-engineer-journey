import streamlit as st
import requests

API_URL="http://127.0.0.1:8002"

st.set_page_config(page_title="Document Q&A",layout="wide")
st.title("Document Q&A - powered by RAG")
st.caption("Upload a PDF or paste text, then ask questions about it")

with st.sidebar:
    st.header("Load documents")
    tab1,tab2=st.tabs(["Upload PDF","Paste text"])
    
    with tab1:
        pdf_file=st.file_uploader("Choose a PDF",type="pdf")
        if pdf_file and st.button("Load PDF"):
            with st.spinner("Processing PDF..."):
                response=requests.post(
                    f"{API_URL}/upload",
                    files={"file": (pdf_file.name,pdf_file,"application/pdf")}
                    
                )
                if response.status_code==200:
                    data=response.json()
                    st.success(f"Loaded {data['chunks']} chunks from {data['filename']}")
                else:
                    st.error(response.json().get("detail","Upload failed"))
    with tab2:
        pasted_text=st.text_area("Paste any text",height=200)
        source_name=st.text_input("Source name",value="pasted_text")
        if st.button("Load text"):
            if pasted_text.strip():
                with st.spinner("Processing text..."):
                    response=requests.post(f"{API_URL}/load-text",
                        json={"text":pasted_text,"source_name":source_name})
                    if response.status_code==200:
                        st.success(f"Loaded {response.json()['chunks']} chunks")
                    else:
                        st.error("Failed to load text")
    st.divider()
    try:
        stats = requests.get(f"{API_URL}/stats")
        if stats.status_code == 200:
            stats = stats.json()
            st.metric("Total chunks stored", stats.get("total_chunks", 0))
        else:
            st.metric("Total chunks stored", "Error fetching stats")
    except requests.exceptions.ConnectionError:
        st.metric("Total chunks stored", "Offline (API down)")
        
    if st.button("Reset all documents"):
        try:
            requests.delete(f"{API_URL}/reset")
            st.success("Reset complete")
            st.rerun()
        except requests.exceptions.ConnectionError:
            st.error("API server is offline")
            
if "messages" not in st.session_state:
    st.session_state.messages=[]
    
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
if question := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append(
        {"role":"user","content":question}
    )
    with st.chat_message("user"):
        st.write(question)
        
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                response=requests.post(f"{API_URL}/ask",
                    json={"question":question,"n_results":4})
                if response.status_code==200:
                    answer=response.json()["answer"]
                    st.write(answer)
                    st.session_state.messages.append(
                        {"role":"assistant","content":answer}
                    )
                else:
                    st.error("Could not get answer from API")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend API server. Make sure your FastAPI code is running!")
        