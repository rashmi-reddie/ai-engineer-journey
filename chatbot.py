import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(dotenv_path=".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in environment variables!")
    print("Please check that your .env file exists and contains the correct key.")
    exit(1)

client=genai.Client(api_key=api_key)

config = types.GenerateContentConfig(
    system_instruction="""You are a strict but helpful coding mentor.
You only answer questions about Python and AI engineering.
Keep answers under 100 words. Always end with one 
follow-up question to push the student deeper."""
)

conversation_history=[]

# chat = client.chats.create(model="gemini-2.5-flash", config=config)

print("AI Chatbot ready ! Type 'quit' to exit.\n")
while True:
    user_input=input("You : ")
    if user_input.lower()=="quit":
        break
    if user_input.lower()=="save":
        with open("conversation.txt","w") as f:
            f.write("\n".join(conversation_history))
            for turn in conversation_history:
                role="You" if turn["role"]=="user" else "AI"
                f.write(f"{role}: {turn['parts']}\n")
        print("Conversation saved to conversation.txt\n")
        continue
    conversation_history.append({"role": "user", "parts": [user_input]})

    response=client.models.generate_content(
        model="gemini-2.5-flash",
        config=config,
        contents=conversation_history
    )
    conversation_history.append({"role": "model", "parts": [response.text]})
    print(f"AI : {response.text}\n")