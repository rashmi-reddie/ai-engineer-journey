import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

load_dotenv

llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)

class SimpleState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]
    step:str
    
def node_a(state: SimpleState) -> dict:
    print(f" [Node A running] step={state['step']}")
    response=llm.invoke(state["messages"])
    return{
        "messages":[response],
        "step":"node_a_done"
    }
    
def node_b(state: SimpleState) -> dict:
    print(f" [Node B running] step={state['step']}")
    last_msg=state["messages"][-1].content
    summary=llm.invoke([
        HumanMessage(content=f"Summarize this in one sentence: {last_msg}")
        
    ])
    return{
        "messages":[summary],
        "step":"node_b_done"
    }
    
def should_continue(state: SimpleState) -> dict:
    print(f" [Node B running] step={state['step']}")
    last_msg=state["messages"][-1].content
    summary=llm.invoke([
        HumanMessage(content=f"Summarize this in one sentence: {last_msg}")
    ])
    return{
        "messages":[summary],
        "step":"node_b_done"
    }
    
def should_continue(state: SimpleState)->str:
    if state["step"]=="node_a_done":
        return "node_b"
    return END

graph=StateGraph(SimpleState)
graph.add_node("node_a",node_a)
graph.add_node("node_b",node_b)
graph.set_entry_point("node_a")
graph.add_conditional_edges("node_a",should_continue)
graph.add_edge("node_b",END)
app=graph.compile()

print("Running StateGraph with 2 nodes...\n")
result=app.invoke({
    "messages":[HumanMessage(content="Explain what LangGraph is in 3 sentences")],
    "step":"start"
})
print("\nFinal messages:")
for msg in result["messages"]:
    role="Human" if isinstance(msg,HumanMessage) else "AI"
    print(f" [{role}]: {msg.content[:100]}...")