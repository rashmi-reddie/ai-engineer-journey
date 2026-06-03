import os 
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class AIChatbot:
    def __init__(self,name,system_prompt):
        self.name=name
        self.system_prompt=system_prompt
        self.conversation_history=[]
        self.turn_count=0
        self.client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.config=types.GenerateContentConfig(
            system_instruction=self.system_prompt
        )
        print(f"{self.name} is ready.")
        
    def chat(self,user_message):
        self.conversation_history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )
        response=self.client.models.generate_content(
            model="gemini-2.5-flash",
            config=self.config,
            contents=self.conversation_history
        )
        reply=response.text
        self.conversation_history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=reply)]
            )
        )
        self.turn_count+=1
        return reply
    
    def get_stats(self):
        return{
            "name":self.name,
            "turns":self.turn_count,
            "messages_in_memory":len(self.conversation_history)
        }
        
    def reset(self):
        self.conversation_history=[]
        self.turn_count=0
        print(f"{self.name} memory cleared")
        
    def __repr__(self):
        return f"AIChatbot (name={self.name}, turns={self.turn_count})"
    
if __name__=="__main__":
    mentor=AIChatbot(
        name="CodeMentor",
        system_prompt="You are a Python Mentor. Keep answers under 60 words. Be concise and clear."
    )
    interviewer=AIChatbot(
        name="Interviewer",
        system_prompt="You are a strict but helpful Technical INterviewer. Ask hard questions and prepare for realtime interviews."
    )
    
    print(mentor.chat(("what is python decorator?")))
    print(mentor.get_stats())
    print(interviewer.chat("What should I know about Python OOP?"))
    print(repr(mentor))
    
class SpecializedBot(AIChatbot):
    def __init__(self,name,domain):
        system_prompt=f"""You are an expert in {domain}. Answer questions related to {domain} concisely and clearly.
        Always give a practical example with your answer."""
        super().__init__(name,system_prompt)
        self.domain=domain
        self.questions_answered=0
        
    def chat(self,user_message):
        self.questions_answered+=1
        reply=super().chat(user_message)
        return f"[{self.domain} Expert]: {reply}"
    
    def get_stats(self):
        base_stats=super().get_stats()
        base_stats["domain"]=self.domain
        base_stats["questions_answered"]=self.questions_answered
        return base_stats
    
python_bot=SpecializedBot("PyBot","Python Programming")
ai_bot=SpecializedBot("AIBot","Artificial Intelligence")
print(python_bot.chat("What is list Comprehension?"))
print(ai_bot.chat("What is a vector database?"))
print(python_bot.get_stats())