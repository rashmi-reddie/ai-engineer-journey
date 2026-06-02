# AI Engineer Journey

## Day 1 — CLI Chatbot with Gemini API

A command-line chatbot built with Python and Google Gemini.

### What it does
- Takes user input and gets a response from an LLM
- Uses a system prompt to create a specialized assistant

### How to run
pip install google-generativeai python-dotenv
python chatbot.py

### What I learned today
- How to call an LLM API from Python
- What system prompts are and why they matter
- How to manage API keys with .env files

## Day 3: Building a Full-Stack AI Architecture (FastAPI + Streamlit)

###  What I Learned Today
Today, I transitioned from running isolated scripts to engineering a distributed, full-stack AI application by separating backend logic from frontend presentation.

#### 1. The Backend Ecosystem: FastAPI, Pydantic, & Uvicorn
I explored how these three tools collaborate to create high-performance, enterprise-ready web services:
* **Uvicorn:** Functions as the lightning-fast ASGI web server that listens on local network ports (e.g., `8000`), handles raw incoming HTTP packets, and forwards them to the application.
* **FastAPI:** Serves as the web framework layer, using Python decorators (like `@app.post()`) to route incoming requests to specific executable Python functions.
* **Pydantic:** Acts as the data validation gatekeeper. By utilizing Python type hints, it automatically parses incoming JSON payloads, validates data integrity, handles type coercion, and filters outgoing data before it leaves the server.

#### 2. The Power of Web APIs
I learned that APIs (Application Programming Interfaces) serve as a secure, standardized bridge between a backend system and the outside world. Instead of keeping core code trapped locally on a single machine, hosting an API exposes structured endpoints (`/chat`, `/sessions`), making the application securely accessible to any client platform—whether it's a web browser, a mobile app, or another backend system.

#### 3. CORS Middleware (Cross-Origin Resource Sharing)
I configured `CORSMiddleware`, which functions as a security checkpoint at the entrance of the API server. By default, web browsers block frontend clients from reading data from a backend hosted on a different port or domain. Setting up CORS allows the backend to inject the necessary headers to safely authorize cross-origin communication, preventing runtime browser blocks.

#### 4. Streamlit for Rapid UI Development
I explored **Streamlit** to quickly assemble an interactive, production-ready frontend for the AI chatbot. I learned its reactive execution model (re-running the script from top to bottom on user interaction) and how to leverage `st.session_state` to persist stateful conversation memory across those re-runs.

#### 5. Programmatic API Testing
Instead of manually clicking through a web browser to verify endpoints, I implemented an automated testing script using the Python `requests` library. This allows me to simulate a real client payload, verify health statuses, and programmatically validate that the chatbot preserves conversation state across multiple turns in a separate runtime shell.

---

### Technical Implementation Milestones
* **Decoupled Architecture:** Reorganized the project directory into structured `backend/`, `frontend/`, and `tests/` directories to follow professional software development conventions.
* **Multi-Session Memory:** Maintained stateful user interactions by mapping individual conversation logs using an in-memory pointer system linked to unique `session_id` tokens.
* **Integration:** Connected a local Streamlit interface directly to a FastAPI server powered by Google's `gemini-2.5-flash` model.
