import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError

load_dotenv(dotenv_path=".env")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing! Please check your .env file.")

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT="""You are a senior AI Engineering interviewer at a top tech company.
Your job is to conduct a realistic technical interview with the candidate.

Rules:
- Ask ONE question at a time. Never ask multiple questions together.
- Start with an easy warmup question about Python or AI basics.
- After each answer, give brief feedback: what was good, what was missing.
- Then ask the next question, slightly harder than the previous.
- After 5 questions, give a final score out of 10 and detailed feedback.
- Be strict but encouraging. Real interviews are tough — prepare them for that.
- Track what topics you have already covered and don't repeat.

Topics to cover across 5 questions:
1. Python basics
2. What is an LLM / how does it work
3. What is an API / REST
4. A simple coding problem (write a function)
5. A scenario: "How would you build X using AI?"

Start by greeting the candidate and asking question 1."""

config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)

conversation_history=[]

print("===AI Engineering Interview Simulator===")
print("Type 'quit' to end. Type 'score' to get feedback anytime.\n")

response=client.models.generate_content(
    model="gemini-2.5-flash",
    config=config,
    contents=[
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="start the interview")])
    ]
)
print(f"Interviewer:{response.text}\n")
conversation_history.append(
    types.Content(
        role="user",
        parts=[types.Part.from_text(text="start the interview")]
    )
)
conversation_history.append(
    types.Content(
        role="model",
        parts=[types.Part.from_text(text=response.text)]
    )
)

while True:
    user_input=input("You:")
    if user_input.lower()=="quit":
        break
    if user_input.lower()=="score":
        user_input="Please give me feedback and a score on my performance so far."
    conversation_history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        )
    )

    retries = 3
    for attempt in range(retries):
        try:
            reply = client.models.generate_content(
                model="gemini-2.5-flash",
                config=config,
                contents=conversation_history
            )
            
            # If successful, save the reply and break out of the retry loop
            conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=reply.text)]
                )
            )
            print(f"Interviewer: {reply.text}\n")
            break
            
        except ServerError:
            if attempt < retries - 1:
                print("\n[System: Server busy. Retrying in 2 seconds...]")
                time.sleep(2)
            else:
                print("\nInterviewer: The connection seems unsteady right now. Please try submitting your last answer again.")