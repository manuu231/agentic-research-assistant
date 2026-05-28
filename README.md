# 🤖 Multi-Agent Research Assistant

A production-style **agentic AI pipeline** built with **LangGraph** and **HuggingFace Inference API** (Mistral-7B). Four specialized agents collaborate in a directed graph to take any research topic from raw question to polished final report — with no human in the loop.

---

## Architecture

```
User Topic
    │
    ▼
┌─────────┐     ┌────────────┐     ┌────────────┐     ┌────────┐
│ Planner │────▶│ Researcher │────▶│ Summarizer │────▶│ Critic │──▶ Final Output
└─────────┘     └────────────┘     └────────────┘     └────────┘
```

| Agent | Role |
|---|---|
| **Planner** | Decomposes the topic into a structured 3-step research plan |
| **Researcher** | Executes the plan and produces detailed, bullet-pointed findings |
| **Summarizer** | Distills findings into 3-4 professional paragraphs |
| **Critic** | Reviews, critiques, and rewrites a final polished version |

All agents share a typed `AgentState` object passed through the LangGraph graph. Each node reads from and writes to state — no side effects, fully reproducible.

---

## Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — stateful multi-agent orchestration
- **[HuggingFace Inference API](https://huggingface.co/inference-api)** — zero-cost LLM backend (Mistral-7B-Instruct)
- **[LangChain](https://github.com/langchain-ai/langchain)** — prompt management and LLM abstraction
- **[FastAPI](https://fastapi.tiangolo.com/)** — REST API serving the pipeline

---

## Quickstart

### 1. Clone & install

```bash
git clone https://github.com/<your-username>/agentic-research-assistant.git
cd agentic-research-assistant
pip install -r requirements.txt
```

### 2. Set your HuggingFace token

```bash
export HF_TOKEN=hf_your_token_here
```

Get a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

### 3. Run the agent directly

```bash
python agent.py
```

Output is printed step-by-step and saved to `output.json`.

### 4. Run the API server

```bash
uvicorn app:app --reload
```

Then open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

**Example request:**

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "The impact of LLMs on software engineering productivity"}'
```

---

## Sample Output

**Topic:** *The impact of large language models on software engineering productivity*

```
[Planner]   1. Review empirical studies on LLM-assisted coding...
            2. Analyze productivity metrics from GitHub Copilot adoption...
            3. Identify risks: over-reliance, hallucinations, security...

[Researcher] • Studies show 30–55% faster task completion with AI pair programmers...
             • Code review time reduced by ~40% in enterprise settings...

[Summarizer] Large language models have meaningfully accelerated software development...

[Critic]    CRITIQUE: The summary lacks nuance on security trade-offs...
            FINAL VERSION: LLMs represent a step-change in developer productivity...
```

---

## Key Concepts Demonstrated

- **Stateful multi-agent graphs** with typed shared state (`TypedDict`)
- **LangGraph directed edges** — deterministic agent sequencing
- **HuggingFace Inference API** as a zero-cost LLM backend
- **FastAPI** deployment with Pydantic request/response validation
- **Agent memory** — each node reads the full accumulated state
- **Separation of concerns** — one agent, one responsibility

---

## Extending This Project

- Add a **web search tool** via `langchain_community.tools.TavilySearchResults`
- Add **conditional edges** in LangGraph to loop the Critic back to Researcher if quality is low
- Swap Mistral-7B for **Llama 3** or any other HuggingFace model with one line change
- Add **MLflow tracking** to log each agent's output per run
- Wrap in **Docker** for portable deployment

---

## Author

**Manpreet Kaur** — LLM / GenAI Engineer  
[LinkedIn](https://linkedin.com/in/manpreetkaurmahal) · [HuggingFace](https://huggingface.co/Manpreet02) · [GitHub](https://github.com/manuu231)

---

## License

MIT
