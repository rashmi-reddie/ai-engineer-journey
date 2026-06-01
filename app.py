import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(dotenv_path=".env")

st.title("AI Engineering Mentor")
st.caption("Your personal python and AI tutor")

if "history" not in st.session_state:
    st.session_state.history=[]

client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
config=types.GenerateContentConfig(
    system_instruction="""You are a helpful AI engineering mentor for a BTech graduate
learning Python and AI. Explaining any difficult concept in a very easy and understandable way is your strength. Not just teaching theory, but also providing practical examples to illustrate your points.
Be encouraging, practical, and concise.
Always give a code example when explaining a concept"""
)

for msg in st.session_state.history:
    role="user" if msg.role=="user" else "model"
    with st.chat_message(role):
        st.write(msg.parts[0].text)
        
if prompt:=st.chat_input("Ask me anything about Python or AI engineering!"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.history.append(
        types.Content(
           role="user",
           parts=[types.Part.from_text(text=prompt)] 
        )
    )
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response=client.models.generate_content(
                model="gemini-2.5-flash",
                config=config,
                contents=st.session_state.history
            )
            reply=response.text
            st.write(reply)
    
    st.session_state.history.append(
        types.Content(
            role="model",
            parts=[types.Part.from_text(text=reply)]
        )
    )