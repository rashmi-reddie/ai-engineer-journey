import os
import hashlib
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb

load_dotenv()

# ==========================================
# 1. THE OPEN-BOOK EXAM PROMPT
# ==========================================
# This prompt establishes strict guardrails. It turns the AI into a pure 
# fact-checking machine and strips out its ability to make things up (hallucinate).

system_template = """You are an expert, precise resume screening assistant. 
Your task is to answer the user's question clearly based on the resume text chunks provided below..

Guidelines:
1. Base your answer strictly on the provided context facts. Do not assume extra milestones.
2. If the text does not contain relevant information to answer the question, say exactly: 'I could not find this in the document'.
"""

human_template = """Excerpts from Resume Context:
------------
{context}
------------

Question: {question}

Answer:"""

ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template(human_template)
])




class RAGEngine:
# ==========================================
    # 2. INITIALIZATION (__init__)
# ==========================================
    
    
    def __init__(self,collection_name="rag_documents"):
        # Connects to Google's vectorization model
        self.embeddings=GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        # Sets up the Gemini LLM with low temperature (0.1) to make it creative-averse and factual.
        self.llm=ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1
        )
        # Creates the production pipeline using LangChain Expression Language (LCEL)
        self.answer_chain= ANSWER_PROMPT | self.llm | StrOutputParser()
        
        # Configures our smart recursive text splitter
        self.splitter=RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n","\n",". "," ",""]
        )
        # Sets up a local persistent database directory folder called './rag_db'
        self.chroma=chromadb.PersistentClient(path="./rag_db")
        self.collection=self.chroma.get_or_create_collection(collection_name)
        self.loaded_docs=set()
        
# ==========================================
    # 3. HELPER: DEDUPLICATION METADATA
    # ==========================================
    # Generates a unique 12-character fingerprint for every file path.
    # This prevents the exact same file from being added to your database twice.
        
    def _doc_id(self,filepath):
        return hashlib.md5(filepath.encode()).hexdigest()[:12]

# ==========================================
    # 4. DATA INGESTION: PARSING PDFs
# ==========================================
    def load_pdf(self,filepath):
        doc_hash=self._doc_id(filepath)
        existing=self.collection.get(where={"doc_id":doc_hash})
        if existing["ids"]:
            count=len(existing["ids"])
            print(f"Document already loaded ({count} chunks). Skipping.")
            self.loaded_docs.add(doc_hash)
            return count
        
        print(f"Loading: {filepath}")
        loader=PyPDFLoader(filepath)
        pages=loader.load() # Reads the PDF file into separate pages
        print(f"Pages loaded: {len(pages)}")
        
        chunks=self.splitter.split_documents(pages) # Splits pages into 800-character blocks
        print(f"Chunks created: {len(chunks)}")
        
        print("Generating embeddings (this may take a moment)...")
        batch_size=10
        stored=0
        
        # Batching processing avoids overloading APIs with massive files
        for i in range(0,len(chunks),batch_size):
            batch=chunks[i:i + batch_size]
            texts=[c.page_content for c in batch]
            
            # Converts raw texts into mathematical numerical vectors
            embeddings=self.embeddings.embed_documents(texts)
            ids =[f"{doc_hash}_chunk_{i+j}" for j in range(len(batch))]
            metadatas=[{
                "doc_id": doc_hash,
                "page":c.metadata.get("page",0),
                "source":os.path.basename(filepath),
                "chunk_index":i+j
            } for j,c in enumerate(batch)]  
            
            
            # Save texts, mathematical meanings, and original source metadata to the database
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )    
            stored+=len(batch)
            print(f"Stored {stored}/{len(chunks)} chunks...") 
        self.loaded_docs.add(doc_hash)
        print(f"Done. {len(chunks)} chunks stored.")
        return len(chunks)
    
    # ==========================================
    # 5. DATA INGESTION: PASTE PLAIN TEXT
    # ==========================================
    def load_text(self,text,source_name="pasted_text"):
        doc_hash=self._doc_id(source_name+text[:50])
        
        # Verify if text is already present to prevent duplicate loads
        chunks=self.splitter.split_text(text)
        embeddings=self.embeddings.embed_documents(chunks)
        ids=[f"{doc_hash}_chunk_{i}" for i in range(len(chunks))]
        metadatas=[{"doc_id":doc_hash,"source":source_name,
                    "page":0,"chunk_index":i} for i in range(len(chunks))]
        self.collection.add(
            documents=chunks,embeddings=embeddings,
            ids=ids,metadatas=metadatas
        ) 
        print(f"Loaded {len(chunks)} chunks from text.")
        return len(chunks)
    
    # ==========================================
    # 6. SEMANTIC SEARCH & INFERENCE (ASK)
    # ==========================================
    def ask(self,question,n_results=4):
        total_docs = self.collection.count()
        if total_docs == 0:
            return "No documents loaded yet. Please load a PDF or paste text first."
       
        # Step 1: Turn the user's question into a mathematical vector coordinate
        q_embedding=self.embeddings.embed_query(question)
        safe_n_results=max(1,min(n_results,total_docs))
        # Step 2: Query database to find the closest matching text chunks
        results=self.collection.query(
            query_embeddings=[q_embedding],
            n_results=safe_n_results
        )
        print("\n=== DEBUG: RETRIEVED CHROMA SNIPPETS ===")
        print(results.get("documents"))
        print("=========================================\n")
        
        if not results.get("documnets") or  len(results["documents"][0])==0:
            return "No relevant content found"
        
        # Step 3: Format the context metadata into a clear structure for the LLM
#        results = {
#     "documents": [
#         ["Text Chunk A", "Text Chunk B", "Text Chunk C"]  # <-- This is Index 0!
#     ],
#     "metadatas": [
#         [
#             {"source": "python_facts", "page": 0}, 
#             {"source": "python_facts", "page": 0},
#             {"source": "python_facts", "page": 0}
#         ]                                                 # <-- This is Index 0!
#     ]
# }
        context_parts = []
        documents_list = results["documents"][0]
        metadatas_list = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
        
        for i, doc in enumerate(documents_list):
            meta = metadatas_list[i] if i < len(metadatas_list) else {}
            source = meta.get("source", "Uploaded Document") if meta else "Uploaded Document"
            page = meta.get("page", 0) if meta else 0
            
            # CRITICAL FIX: Preserve the raw string formatting (newlines, lists, tabs)
            # Just strip empty leading/trailing spaces
            clean_doc = doc.strip() 
            
            context_parts.append(f"=== Snippet {i+1} [Source: {source} | Page: {page+1}] ===\n{clean_doc}")
            
        context = "\n\n".join(context_parts)
        
        # Print context to your API terminal to ensure it isn't empty!
        print("\n=== SENT TO LLM CONTEXT ===")
        print(context)
        print("===========================\n")
        
        
        # Step 4: Stream context and question into the prompt/LLM pipeline execution
        try:
            answer = self.answer_chain.invoke({
                "context": context,
                "question": question
            })
            return answer
        except Exception as e:
            return f"Error generating answer from LLM: {str(e)}"
    
    def get_stats(self):
        total=self.collection.count()
        return {"total_chunks":total,"collection":self.collection.name}
    
    def reset(self):
        """Safely deletes and recreates the collection."""
        try:
            self.chroma.delete_collection(self.collection.name)
        except Exception:
            pass  # If it doesn't exist, ignore
        # Recreate an empty collection
        self.collection = self.chroma.get_or_create_collection(self.collection.name)
        self.loaded_docs = set()
        
# ==========================================
# 7. EXECUTION
# ==========================================  
if __name__=="__main__":
    engine=RAGEngine()
    print("RAG Engine ready.")
    print(f"Stats: {engine.get_stats()}")
    
    sample="""
    Python was created by Guido van Rossum and first released in 1991.
    Python's design philosophy emphasizes code readibility and simplicity.
    Python supports multiple programming paradigms including procedural,
    object-oriented and functional programming.
    Python is widely used in data science, AI, web development, and automation.
    The Python Package Index (PyPI) hosts over 400,000 packages.
    """
    engine.load_text(sample,"python_facts")
    
    # These two will succeed because the text chunks have the answers
    print("\nQ: Who created Python?")
    print(engine.ask("who created Python?"))
    
    print("\nQ: What year was Python released?")
    print(engine.ask("What year was Python released?"))
    
    # This will cleanly fail due to our strict system prompt rule!
    print("\nQ: What is the capital of France?")
    print(engine.ask("What is the capital of France?"))
 