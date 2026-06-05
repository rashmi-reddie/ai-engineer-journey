import os
import json

from datetime import datetime
from dotenv import load_dotenv
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

NOTES_FILE="notes_backup.json"

embeddings_model=GoogleGenerativeAIEmbeddings(
    model="gemini-embeddings-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)
llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2
)

chroma_client=chromadb.PersistentClient(path="./notes_db")
collection=chroma_client.get_or_create_collection("my notes")

answer_prompt=ChatPromptTemplate.from_template("""You are a helpful assistant answering questions based only on the provided notes.
                                               If the answer is not in the notes, say so clearly.
                                               Relevant notes:
                                               {context}
                                               Question : {question}
                                               Answer concisely based on the notes above:
                                               """)
answer_chain=answer_prompt | llm | StrOutputParser()

def add_note(content,tag="general"):
    note_id=f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    embedding=embeddings_model.embed_query(content)
    collection.add(
        documents=[content],
        embeddings=[embedding],
        ids=[note_id],
        metadatas=[{"tag":tag,"date":datetime.now().strftime('%Y-%m-%d')}]
    )
    print(f"Note saved: {note_id}")
    return note_id

def search_notes(query,n=3):
    if collection.count()==0:
        print("No notes yet. Add some first.")
        return []
    query_embedding=embeddings_model.embed_query(query)
    results=collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n,collection.count())
    )
    return results["documents"][0] if results["documents"] else []

def ask_notes(question):
    relevant=search_notes(question,n=4)
    if not relevant:
        print("No relevant notes found.")
        return
    context="\n\n".join([f"Note: {doc}" for doc in relevant])
    answer=answer_chain.invoke({
        "context":context,
        "question":question
    })
    print(f"\nAnswer: {answer}")
    print(f"\nBased on {len(relevant)} relevant notes.")
    
def show_all():
    if collection.count()==0:
        print("No notes yet.")
        return
    results=collection.get()
    print(f"\nTotal notes: {collection.count()}")
    for i,(doc,meta) in enumerate(zip(results["documents"],results["metadatas"])):
        print(f"\n[{i+1}] [{meta.get('tag','general')}] {meta.get('date','')}:")
        print(f" {doc[:100]}{'...' if len(doc)>100 else ''}")

def handle_add():
    content=input("Note Content: ").strip()
    tag = input("Tag (python/ai/fastapi/general): ").strip() or "general"
    if content:
        add_note(content, tag)

def handle_search():
    query = input("Search query: ").strip()
    if query:
        results = search_notes(query)
        print(f"\nTop {len(results)} results for '{query}' : ")
        for i, r in enumerate(results, 1):
            print(f" {i}. {r}")
            
def handle_ask():
    question = input("Your question: ").strip()
    if question:
        ask_notes(question)   

def main():
    print("Smart Notes - semantic search + AI answers")
    print("Commands: add, search, ask, show, quit\n")
    
    add_note("Python list comprehension: [x*2 for x in range(10)] creates a list of doubled numbers", "python")
    add_note("FastAPI route: @app.post('/chat') defines a POST endpoint at /chat", "fastapi")
    add_note("Embeddings convert text to numbers that capture semantic meaning", "ai")
    add_note("ChromaDB is a vector database that stores embeddings locally for free", "ai")
    add_note("git add . stages all changed files, git commit saves them, git push uploads", "git")
    print("Sample notes loaded.\n")
    
    while True:
        cmd=input("Command: ").strip().lower()
        if cmd=="quit":
            break
        elif cmd == "add":
            handle_add()
        elif cmd=="search":
            handle_search()
        elif cmd=="ask":
            handle_ask()
        elif cmd=="show":
            show_all()
        else:
            print("Commands: add, search, ask, show, quit")

if __name__=="__main__":
    main()        