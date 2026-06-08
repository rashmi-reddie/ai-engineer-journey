import os
import json
import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool
from langchain_tavily import TavilySearch


load_dotenv()

llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
    temperature=0.2
)
PROFILE = {
    "name": "Rashmitha",
    "background": "BTech CSE 2026 graduate from Hyderabad",
    "skills": ["Python", "FastAPI", "LangChain", "RAG", "ChromaDB",
               "Streamlit", "React", "Node.js", "MongoDB", "Gemini API"],
    "building": "AI engineering portfolio — 90 day challenge, Day 8",
    "target_roles": ["AI Engineer", "ML Engineer", "Full Stack AI Developer"],
    "location": "Hyderabad, India"
}

CAREER_FILE="career_notes".json

def load_career_data():
    try:
        with open("CAREER_FILE","r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"appliactions":[],"notes":[],"skills_to_learn":[]}
    
def save_career_data(data):
    with open(CAREER_FILE,"w") as f:
        json.dump(data,f,indent=2)

@tool
def get_my_profile(dummy: str="")->str:
    """Get the user's professional profile, skills, and career goals."""
    return json.dumps(PROFILE,indent=2)

@tool
def save_career_note(note: str) -> str:
    """Save an important career note, company to apply to, or skill to learn.
    Format: 'type:content' where type is note/company/skill.
    Example: 'company:Google AI Engineer role - apply before Dec 31'"""
    data=load_career_data()
    parts=note.split(":",1)
    note_type=parts[0].strip() if len(parts) > 1 else "note"
    content=parts[1].strip() if len(parts) > 1 else note
    
    if note_type=="company":
        data["applications"].append(content)
    elif note_type=="skill":
        data["skills_to_learn"].append(content)
    else:
        data["notes"].append(content)
        
    save_career_data(data)
    return f"Saved {note_type}: {content}"

@tool
def get_career_notes(dummy: str = "") -> str:
    """Retrieve all saved career notes, companies to apply to, and skills to learn."""
    data = load_career_data()
    result = []
    if data["applications"]:
        result.append("Companies/roles to apply:\n" +
                      "\n".join(f"• {a}" for a in data["applications"]))
    if data["skills_to_learn"]:
        result.append("Skills to learn:\n" +
                      "\n".join(f"• {s}" for s in data["skills_to_learn"]))
    if data["notes"]:
        result.append("Notes:\n" +
                      "\n".join(f"• {n}" for n in data["notes"]))

@tool
def analyze_skill_gap(target_role: str) -> str:
    """Analyze the skill gap between the user's current skills and a target role.
    Input should be the job role name like 'AI Engineer' or 'ML Engineer'."""
    my_skills = set(s.lower() for s in PROFILE["skills"])
    role_requirements = {
        "ai engineer": ["python", "langchain", "rag", "fastapi", "docker",
                        "aws", "typescript", "vector databases", "ci/cd"],
        "ml engineer": ["python", "pytorch", "tensorflow", "scikit-learn",
                        "docker", "mlflow", "aws", "sql", "statistics"],
        "full stack ai developer": ["python", "react", "typescript", "fastapi",
                                    "node.js", "docker", "postgresql", "redis"],
    }
    required = role_requirements.get(target_role.lower(),
                                     ["python", "docker", "aws", "sql"])
    have = [r for r in required if r in my_skills]
    missing = [r for r in required if r not in my_skills]
    score = int(len(have) / len(required) * 100)
    return (f"Role: {target_role}\n"
            f"Match score: {score}%\n"
            f"Skills you have: {', '.join(have)}\n"
            f"Missing skills: {', '.join(missing)}\n"
            f"Priority to learn: {missing[0] if missing else 'none'}")
    
search=TavilySearch(
        max_results=3,
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
tools = [get_my_profile, save_career_note, get_career_notes,
         analyze_skill_gap, search]

agent_executor=create_agent(
    model=llm,
    tools=tools,
    checkpointer=InMemorySaver(),
    system_prompt="""You are a personalized AI career counselor for Rashmitha,
a BTech CSE 2026 graduate from Hyderabad targeting AI Engineer roles.
Always use tools to get her profile and give specific, actionable advice.
Be encouraging but honest. Keep responses concise."""
)

config = {"configurable": {"thread_id": "rashmitha_career"}}

def invoke(message: str)->str:
    result=agent_executor.invoke(
        {"messages":[{"role":"user","content":message}]},
        config=config
    )
    return result["messages"][-1].content

print("AI Career Counselor — personalized for Rashmitha")
print("Ask me about: job market, skill gaps, companies to target,")
print("salary expectations, interview prep, what to learn next.")
print("Type 'quit' to exit.\n")

starter = agent_executor.invoke(
    "Greet me by name, check my profile, "
              "and give me 3 most important career actions for this week "
              "based on my skills and target roles."
              )

print(f"Agent: {starter['output']}\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        break
    if not user_input:
        continue
    result = agent_executor.invoke({"input": user_input})
    print(f"Agent: {result['output']}\n")
    