import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(dotenv_path=".env")

def create_client():
    api_key=os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def create_config(system_prompt):
    return types.GenerateContentConfig(system_instruction=system_prompt)

def save_conversation(history):
    with open("conversationv2.txt","w",encoding="utf-8") as f:
        for turn in history:
            role="You" if turn.role=="user" else "AI"
            f.write(f"{role}: {turn.parts[0].text}n\n")
    print("Saved to conversationv2.txt\n")
    
def get_ai_response(client,config,history):
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=config,
        contents=history
    )
    return response.text
def run_chatbot():
    client=create_client()
    config=create_config(""" You are a helpful Python and AI engineering mentor.
Keep answers under 100 words. End with one follow-up question. """)
    history=[]
    
    print("Chatbot v2 ready. Type 'quit' to 'save' .\n")
    while True:
        user_input=input("You:").strip()
        if not user_input:
            continue
        if user_input.lower()=="quit":
            break
        if user_input.lower()=="save":
            save_conversation(history)
            continue
        history.append(
            types.Content(role="user",
                          parts=[types.Part.from_text(text=user_input)]
                          ))
        reply=get_ai_response(client,config,history)
        history.append(
            types.Content(role="model",
                          parts=[types.Part.from_text(text=reply)]
                          ))
        print(f"\nAI: {reply}\n")
        
if __name__=="__main__":
    run_chatbot()