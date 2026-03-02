# 🧠 Multi-Agent Blog Writer (LangGraph + Streamlit)

A production-grade multi-agent blog generation system built using **LangGraph**, **LangChain**, and **Streamlit**.

This system dynamically routes tasks through multiple AI agents to generate structured, research-backed, image-rich technical blogs with automated PDF export and full observability via LangSmith.



## 🏗 Architecture Overview

The system follows a structured multi-agent workflow:

Router → (Research?) → Orchestrator → Parallel Workers → Reducer → Image Planner → Final Output

### 1️⃣ Router Agent
- Decides if research is required
- Selects execution mode:
  - `closed_book`
  - `hybrid`
  - `open_book`

### 2️⃣ Research Agent (Optional)
- Uses Tavily Search API
- Filters by recency
- Extracts structured evidence

### 3️⃣ Orchestrator Agent
- Generates a structured blog plan
- Creates 5–9 section tasks
- Assigns tags and constraints

### 4️⃣ Worker Agents (Parallel)
- Each worker generates one blog section
- Supports:
  - Citations
  - Code blocks
  - News-roundup mode restrictions

### 5️⃣ Reducer Subgraph
- Merges sections
- Decides image placements
- Generates diagrams using Stable Diffusion (HuggingFace)
- Embeds images into Markdown

### 6️⃣ Final Output
- Markdown preview
- PDF export
- Image downloads

---

## 🛠 Tech Stack

- **LangGraph** – Multi-agent orchestration
- **LangChain** – LLM abstractions
- **OpenAI GPT-4o / GPT-4o-mini** – Content generation
- **Tavily API** – Web research
- **Stable Diffusion XL (HF Inference API)** – Diagram generation
- **Streamlit** – Frontend UI
- **ReportLab** – PDF rendering
- **LangSmith** – Observability & tracing

---

## 📊 Features

✅ Multi-agent architecture  
✅ Dynamic research routing  
✅ Recency-aware news mode  
✅ Structured blog planning  
✅ Parallel section generation  
✅ AI-generated technical diagrams  
✅ Markdown + PDF export  
✅ LangSmith tracing  
✅ Streamlit Cloud deployment  

---

## 💰 Observability

Full tracing enabled via LangSmith:

- Node-level execution traces
- Token usage
- Latency metrics
- Error monitoring
- State transitions

---

