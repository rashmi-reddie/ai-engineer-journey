# AI Engineer Journey

## Day 1 — CLI Chatbot with Gemini API

A command-line chatbot built with Python and Google Gemini.

# What it does
- Takes user input and gets a response from an LLM
- Uses a system prompt to create a specialized assistant

# How to run
pip install google-generativeai python-dotenv
python chatbot.py

# What I learned today
- How to call an LLM API from Python
- What system prompts are and why they matter
- How to manage API keys with .env files

##Day 2 of my 90-day AI Engineering journey.

Today I built 3 things:
- An AI interview simulator that scores my answers
- Refactored my chatbot into clean, reusable functions  
- Turned my Python chatbot into a real web app using Streamlit

Biggest insight: a system prompt is how you give an AI
its personality. Change the prompt, change the entire
behavior — no retraining needed.

Day 1 was a CLI script. Day 2 is a web app.
Day 90 will be something I'm proud to show.

#AIEngineering #Python #Streamlit #90DayChallenge

##Day 3 of my 90-day AI Engineering journey.

Today I stopped using AI tools and started building them.

I built a production-style AI backend with FastAPI:
- POST /chat — AI conversation with session memory
- POST /summarize — summarize any text to bullet points
- DELETE /sessions — clear conversation history
- Auto-generated API docs at /docs

Then connected a Streamlit frontend to call my own API.

This is how real AI products are built:
frontend → your API → AI model

Day 1: CLI script
Day 2: Web app  
Day 3: Backend API with 4 endpoints

###Day 10 — I found my resume gaps and closed 3 of them today.

My AI resume analyzer told me I was missing:
TypeScript, Docker, and CI/CD.

So I built all three in one day.

TypeScript: rewrote my Python data models with types.
Found out immediately why companies use it —
VS Code caught 4 errors before I ran a single line.

Docker: containerized my FastAPI resume analyzer.
One command builds it. One command runs it.
Same everywhere. No more "works on my machine."

CI/CD: GitHub Actions pipeline that triggers on every push.
3 jobs: code quality check → Docker build → Python tests.
All green. Screenshot in comments.

My resume analyzer score went from X to Y after adding these.

That is the feedback loop I have built:
Build → Analyze → Close gaps → Repeat.

Day 10. Still going.
![CI](https://github.com/rashmi-reddie/ai-engineer-journey/actions/workflows/ci.yml/badge.svg)
