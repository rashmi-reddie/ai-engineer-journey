import streamlit as st
import requests
import uuid

BACKEND_URL="http://127.0.0.1:8000"

st.title("AI Chat -  Powered by FastAPI")
st.caption("Frontend -> Your API -> Gemini API")

if "session_id" not in st.session_state:
    st.session_state.session_id=str(uuid.uuid4())[:8]
    st.session_state.messages=[]
    
st.sidebar.write(f"Session ID: `{st.session_state.session_id}`")
st.sidebar.write(f"Turns: {len(st.session_state.messages)//2}")

system_prompt=st.sidebar.text_area(
    "System prompt",
    value="You are a helpful AI Assistant. Be concise and clear.",
    height=100
)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg['content'])
        
if prompt:=st.chat_input("Ask something..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Calling API..."):
            try:
                response=requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "session_id":st.session_state.session_id,
                        "message":prompt,
                        "system_prompt": system_prompt
                    }
                )
                
                data=response.json()
                reply=data["reply"]
                st.write(reply)
                st.session_state.messages.append(
                    {"role":"assistant","content":reply}
                )
                
            except Exception as e:
                st.error(f"API error: {e}")
        