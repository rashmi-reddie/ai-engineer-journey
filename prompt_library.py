import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class PromptLibrary:
    def __init__(self):
        self.client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.prompts={
            "summarize": """You are a concise summarizer.
            summarize the following text into exactly {num_bullets} bullet points.
            Each bullet must start with a dash (-) and be under 15 words.
            Text : {text}""",
            
            "explain_concept": """You are an expert teacher explaining to a Btech student with basic Python knowledge.
            Explain {concept} using:
            1. A one-sentence definition
            2. A real-world analogy
            3.A 5-line Python code example
            keep total response under 150 words""",
            
            "code_review": """You are a senior engineer doing a code review.
            Analyze this code and respond with a JSON object containing:
            - "score" : integer 1-10
            - "good_parts : list of 2-3 things done well
            - "issues" : list of problems found
            - "fixed_code" : the improved version as a string
            
            Code to review:
            {code}""",
            
            "generate_questions": """You are a technical interviewer at a top AI Company.
            Generate {num_questions} interview questions about {topic}.
            Difficulty: {difficulty} (easy/medium/hard)
            Format : numbered list. Include the expected answer after each question.""",
            
            "debug_helper": """You are a patient Python debugging assistant.
            The user has this error: {error}
            In this code: {code}
            
            Explain:
            1. What caused this error (in simple terms)
            2. How to fix it (with corrected code)
            3. How to avoid this error in future"""
            }
    def get(self,name,**kwargs):
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found. Available: {list(self.prompts.keys())}")
        return self.prompts[name].format(**kwargs)
    
    def run(self,name,**kwargs):
        prompt=self.get(name,**kwargs)
        response=self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        )
        return response.text
    
    def add(self,name,template):
        self.prompts[name]=template
        print(f"Prompt '{name}' added to library.")
        
    def list_prompts(self):
        return list(self.prompts.keys())
    
if __name__=="__main__":
    lib=PromptLibrary()
    print("Testing explain_concept:")
    print(lib.run("explain_concept",concept="Python decorators"))
    print("\nTesting  generate_questions:")
    print(lib.run("generate_questions",
                  topic="FastAPI",
                  num_questions=3,
                  difficulty="medium"))
    print("\nAvailable prompts:",lib.list_prompts())
    