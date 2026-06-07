from langchain_text_splitters import(
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter
)

sample_text="""FastAPI is a modern, fast web framework for building APIs with python.
It is based on standard Python type hints and provides automatic documentation.

Key features of FastAPI include high performance, easy to learn syntax, and automatic data validation using Pydantic models. FastAPI generates OpenAPI documentation automatically, which means your API is self-documenting.
When building AI applications, FastAPI is commonly used as the backend
framework because it handles async requests efficiently. This is important when making calls to LLM APIs which can take several seconds to respond.

The combination of FastAPI with LangChain and ChromaDB creates a powerful stack for
building RAG (Retrieval Augmented Generation) applications.
Each component plays a specific role: FastAPI handles HTTP routing, LangChain orchestrates the AI pipeline, and ChromaDB stores the embeddings.

""" * 3
print(" === Strategy 1 : Fixed character splitting ===")
splitter1=CharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    separator="\n"
)
chunks1 = splitter1.split_text(sample_text)
print(f"Chunks: {len(chunks1)}")
print(f"First chunk:\n{chunks1[0]}")
print(f"Last chunk:\n{chunks1[-1]}")

print("\n=== Strategy 2: Recursive splitting (RECOMMENDED) ===")
splitter2=RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n","\n",". "," ",""]
)
chunks2=splitter2.split_text(sample_text)
print(f"Chunks: {len(chunks2)}")
print(f"First chunk:\n{chunks2[0]}")
print(f"\nOverlap demo - end of chunk 1:\n...{chunks2[0][-50:]}")
print(f"Start of chunk 2:\n{chunks2[1][:50]}...")

print("\n=== Strategy 3: Token-based splitting ===")
splitter3=TokenTextSplitter(chunk_size=100,chunk_overlap=10)
chunks3=splitter3.split_text(sample_text)
print(f"Chunks: {len(chunks3)}")
print(f"Average chunk length: {sum(len(c) for c in chunks3)//len(chunks3)} chars")

print("\n=== Key insight ===")
print("RecursiveCharacterTextSplitter is best for more use cases.")
print("It tries paragraph breaks first, then sentences, then words.")
print("Overlap ensures context is not lost at chunk boundaries.")