import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask(prompt,label=""):
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
        )
    print(f"\n{'='*50}")
    print(f"Technique: {label}")
    print(f"{'='*50}")
    print(response.text)
    
#Technique1 Vague vs specific
ask("Explain Python","VAGUE PROMPT")
ask("""Explain Python list Comprehensions to a BTech student, who knows basic for loops but has never seen compehensions.Use one real-world example involving student grades. Keep it under 80 words.""","SPECIFIC PROMPT")

#Technique2 : Role Prompting
ask("""You are a senior Google engineer with 10 years of Python experience. Explain why using a class is better than global variables for managing chatbot state. Be direct and technical.""","ROLE PROMPTING")

#Technique 3 : Few-shot(eamples in prompt)
ask("""Classify these user messages as : question,complaint, or request.
    Examples:
    "How do i reset my password?" -> question
    "This is broken and Iam frustrated" -> complaint
    "Please add a dark mode" -> request
    
    Now classify these:
    "Why does the API keep timing out?"
    "Can you add export to CSV?"
    "Your app deleted all my data!"
    ""","FEW-SHOT PROMPTING")
    
#Technique 4 : Chain of thought
ask("""
   A chatbot API receives 1000 requests per day. Each request uses on average 500 tokens.
    The model costs $0.001 per 1000 tokens.
    How much does it cost per month?
    Think step by step before giving the answer.
    """, "CHAIN OF THOUGHT")

#Technique 5 : Output format control
ask("""Analyze this python function and return your analysis as a JSON object with these exact keys:
    - "quality_score : integer from 1-10
    - "issues" : list of strings describing problems
    - "improvements" : list of strings with suggestions
    - "is_production_ready" :boolean
    
    Fuction to analyse:
    def chat(msg):
        r=client.generate(msg)
        return r
    ""","STRUCTURED OUTPUT")

#Technique 6 : Persona + constraints
ask("""You are a strict but kind Python tutor.
    Rules:
    - Never give the full solution directly
    - Ask one guiding question at a time
    - If student is wrong, say "not quite" and give a hint
    - End every response with "What do you think happens next"
    
    Student says: I donot understand why my list is empty after the loop.
    ""","PERSONA+ CONSTRAINTS")