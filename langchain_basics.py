import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3

)
print("=== Part 1: Basic PromptTemplate ===")
template=PromptTemplate(
    input_variables=["topic","level"],
    template=""" Explain {topic} to a {level} developer.
    Use one analogy and one code example. Keep it under 100 words."""
)
chain1=template | llm | StrOutputParser()
result=chain1.invoke({"topic":"embeddings",
                      "level":"beginner"})
print(result)

time.sleep(5)

print("\n=== Part 2 : Chaining two LLM calls ===")
explain_template=ChatPromptTemplate.from_template(
    "Explain {concept} in exacty 2 sentences."
)
quiz_template=ChatPromptTemplate.from_template(
    "Based on this explanation: {explanation}\n"
    "Write one multiple-choice quiz question with 4 options. Mark the answer."
)
explain_chain=explain_template | llm | StrOutputParser()
quiz_chain=quiz_template | llm | StrOutputParser()

full_chain=(
    {"explanation": explain_chain, "concept": RunnablePassthrough()}
    | quiz_template
    | llm
    | StrOutputParser()
)
print("Quiz question about RAG:")
print(full_chain.invoke("RAG (Retrieval Augmented Generation)"))

time.sleep(5)

print("\n=== Part 3 : Reusable chain factory ===")
def make_explainer_chain(audience):
    prompt=ChatPromptTemplate.from_template(
        f"You are teaching {audience}. Explain {{topic}} simply,"
        "with a practical example they would care about under 80 words."
    )
    return prompt | llm | StrOutputParser()
student_chain=make_explainer_chain("a Btech student learning AI")
manager_chain=make_explainer_chain("a non-technical business manager")

topic="vector databases"
print(f"For students: {student_chain.invoke({'topic':topic})}")

time.sleep(5)

print(f"\nFor managers: {manager_chain.invoke({'topic': topic})}")