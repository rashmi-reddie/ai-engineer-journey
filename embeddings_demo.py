import os
from dotenv import load_dotenv
import math
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings_model=GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

def get_embedding(text):
    return embeddings_model.embed_query(text)

def cosine_similarity(vec1,vec2):
    dot=sum(a*b for a,b in zip(vec1,vec2))
    mag1=math.sqrt(sum(a**2 for a in vec1))
    mag2=math.sqrt(sum(b**2 for b in vec2))
    if mag1==0 or mag2==0:
        return 0
    return dot/(mag1*mag2)

def compare(text1,text2):
    e1=get_embedding(text1)
    e2=get_embedding(text2)
    score=cosine_similarity(e1,e2)
    print(f"\n'{text1[:40]}...' vs")
    print(f"'{text2[:40]}...'")
    print(f"Similarity: {score:.4f} ({score*100:.1f}%)")
    return score

print("=== Embedding similarity demo ===")
print(f"Embedding size: {len(get_embedding('hello'))} dimensions\n")

compare("Python is a programming language",
        "Python is used for coding")

compare("Python is a Programming language",
        "I love eating pizza")

compare("FastAPI is a Python web framework",
        "Django is also a Python web framework")

compare("The cat sat on the mat",
        "Machine learning model training")

compare("How do I install Python?",
        "Steps to set up Python on my computer")

print("\n--- Key insight ---")
print("Similar meanings = high score(close to 1.0)")
print("Different meanings = low score (close to 0.0)")