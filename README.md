# 🍛 AI Food Search Engine — Swiggy-Style Hybrid Retrieval System

> A production-style AI search engine that lets users naturally search food like:
> “chicken biryani under ₹200” — and actually gets correct, ranked results.

This is not a chatbot.  
This is a **retrieval + ranking + constraint-aware recommendation system**.

---

## ⚡ Why I Built This

Food delivery apps are powerful, but their search UX is still broken.

Users don’t think in filters.

They think in intent:

- “cheap paneer dishes”
- “chicken fried rice under 200”
- “best chicken biryani below 250 rupees”

But reality?

❌ Manual filters  
❌ Endless scrolling  
❌ Price comparison across restaurants  
❌ No intelligent ranking

So I built something closer to a **real search engine for food**.

---

## 🚀 What This System Does

A user can type natural queries like:

- chicken biryani under 200  
- paneer dishes  
- veg meals below 150  
- mutton biryani cheap  

And the system:

✔ Understands intent  
✔ Handles typos  
✔ Applies strict constraints (price, veg/non-veg, protein)  
✔ Retrieves relevant dishes  
✔ Ranks results intelligently  
✔ Prevents hallucinated outputs  

---

## 🧠 Core Idea

Instead of building a chatbot…

I built a **search engine pipeline**:

> Retrieval → Filtering → Ranking → Evaluation

---

## 🏗️ System Architecture

### 🔍 Hybrid Retrieval Layer
- FAISS → semantic similarity search  
- BM25 → keyword-based retrieval  
- Reciprocal Rank Fusion (RRF) → merges both signals  

### 🧾 Query Understanding Layer
- Rule-based parsing (fast path)
- LLM fallback (Groq Llama 3.3 70B)
- Structured JSON filter extraction

### 📊 Ranking Layer
Final ranking uses:

- Rating score (quality)
- Price efficiency (affordability)
- Relevance score (query match)

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Streamlit
- LangChain
- FAISS
- BM25
- HuggingFace Embeddings
- Groq (Llama 3.3 70B)
- RapidFuzz

---

## 📦 Project Structure

```bash
swiggy_agent/
├── menu_api.py          → Menu API (serves dataset)
├── app.py               → FastAPI backend
│
├── req.txt              → Dependencies
│
├── agent/
│   └── meal_agent.py    → Core reasoning engine
│
├── rag/
│   └── vector_store.py  → FAISS + BM25 hybrid retrieval
│
├── tools/
│   └── menu_tools.py    → Search + filtering logic
│
├── data/
│   └── menu.json        → Food dataset
│
└── ui/
    └── streamlit_app.py → Swiggy-style UI
```
----

## ✨ Key Features

### 🔎 Smart Search Engine
- Natural language food queries
- Typo-tolerant retrieval using fuzzy matching

### 🎯 Constraint-Aware System
- Price filtering (under/above X)
- Veg / Non-veg filtering
- Protein-based search

### ⚡ Hybrid Retrieval Engine
- Combines semantic + keyword search
- RRF-based ranking fusion

### 🧮 Ranking Intelligence
- Rating + affordability scoring
- Relevance-first ordering

### 📡 Production-Style Design
- FastAPI backend
- Streamlit frontend
- Modular agent + tools architecture

---

## 📊 Evaluation Layer (Real Engineering Signal)

Unlike most GenAI demos, this system is evaluated using:

- Precision@K
- Recall@K
- Hit Rate
- Latency benchmarking

Why this matters:

👉 This is not just generation  
👉 This is **measuring retrieval quality like real search systems**

---


## 💡 What I Learned

This project goes beyond LLM APIs.

It taught me:

- How real search systems are built
- Hybrid retrieval (dense + sparse)
- Ranking systems used in production
- Evaluation of retrieval pipelines
- Designing AI systems with constraints

---

## 🚀 Why This Matters

Most GenAI projects today:

❌ Chatbots  
❌ Prompt wrappers  
❌ Demo apps  

This project focuses on:

✔ Retrieval systems  
✔ Ranking logic  
✔ Real-world constraints  
✔ Evaluation metrics  
✔ Production-style architecture  

---

## 🔮 Future Improvements

- Personalization layer (user-based ranking)
- Real Swiggy API integration
- Click-through based learning
- Feedback-driven ranking system
- Multi-city expansion

---

## 🏷️ Tags

`AI` `GenAI` `RAG` `LangChain` `FAISS` `FastAPI`  
`Search Engine` `Recommendation System` `Python`  
`Hybrid Retrieval` `LLM Systems` `Build in Public`

---

## 👨‍💻 Author

Built by Akila 🚀  
Building AI systems that feel like real products, not demos.
