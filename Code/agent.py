"""
Multi-Agent Research Assistant
Agents: Planner → Researcher → Summarizer → Critic
Uses LangGraph for orchestration + HuggingFace Inference API as LLM backend
"""

import os
import json
import re
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.messages import HumanMessage, AIMessage
import operator

# ── Config ──────────────────────────────────────────────────────────────────
HF_TOKEN = os.environ.get("HF_TOKEN")  # set in your environment
MODEL_ID  = "mistralai/Mistral-7B-Instruct-v0.3"

llm = HuggingFaceEndpoint(
    repo_id=MODEL_ID,
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=512,
    temperature=0.4,
)

# ── Shared State ─────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    topic:      str
    plan:       str
    research:   str
    summary:    str
    critique:   str
    final:      str
    messages:   Annotated[list, operator.add]

# ── Agent Nodes ──────────────────────────────────────────────────────────────

def planner_agent(state: AgentState) -> AgentState:
    """Breaks the topic into a structured research plan."""
    prompt = f"""You are a research planner. Given the topic below, create a concise 3-step research plan.
Output ONLY the numbered plan, no preamble.

Topic: {state['topic']}
"""
    plan = llm.invoke(prompt)
    print(f"\n[Planner]\n{plan}")
    return {
        **state,
        "plan": plan,
        "messages": [AIMessage(content=f"[Planner] {plan}")]
    }


def researcher_agent(state: AgentState) -> AgentState:
    """Executes the plan and gathers key findings."""
    prompt = f"""You are a research analyst. Using the plan below, write detailed research findings.
Be factual, structured, and thorough. Use bullet points.

Research Plan:
{state['plan']}

Topic: {state['topic']}
"""
    research = llm.invoke(prompt)
    print(f"\n[Researcher]\n{research}")
    return {
        **state,
        "research": research,
        "messages": [AIMessage(content=f"[Researcher] {research}")]
    }


def summarizer_agent(state: AgentState) -> AgentState:
    """Distills research into a clear, concise summary."""
    prompt = f"""You are a technical writer. Summarize the research below into 3-4 clear paragraphs
suitable for a professional audience. Be precise and avoid fluff.

Research:
{state['research']}
"""
    summary = llm.invoke(prompt)
    print(f"\n[Summarizer]\n{summary}")
    return {
        **state,
        "summary": summary,
        "messages": [AIMessage(content=f"[Summarizer] {summary}")]
    }


def critic_agent(state: AgentState) -> AgentState:
    """Reviews the summary and produces a final polished version."""
    prompt = f"""You are a critical reviewer. Review the summary below for:
1. Accuracy and completeness
2. Clarity and conciseness
3. Any gaps or improvements

Then rewrite an improved FINAL VERSION incorporating your feedback.
Clearly label your output as: CRITIQUE: ... and FINAL VERSION: ...

Summary:
{state['summary']}
"""
    critique_and_final = llm.invoke(prompt)
    print(f"\n[Critic]\n{critique_and_final}")

    # Split critique from final version
    final = critique_and_final
    if "FINAL VERSION:" in critique_and_final:
        parts = critique_and_final.split("FINAL VERSION:")
        critique = parts[0].replace("CRITIQUE:", "").strip()
        final    = parts[1].strip()
    else:
        critique = critique_and_final

    return {
        **state,
        "critique": critique,
        "final":    final,
        "messages": [AIMessage(content=f"[Critic] {critique_and_final}")]
    }

# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner",    planner_agent)
    graph.add_node("researcher", researcher_agent)
    graph.add_node("summarizer", summarizer_agent)
    graph.add_node("critic",     critic_agent)

    graph.set_entry_point("planner")
    graph.add_edge("planner",    "researcher")
    graph.add_edge("researcher", "summarizer")
    graph.add_edge("summarizer", "critic")
    graph.add_edge("critic",     END)

    return graph.compile()

# ── Runner ────────────────────────────────────────────────────────────────────

def run(topic: str) -> dict:
    app = build_graph()
    initial_state: AgentState = {
        "topic":    topic,
        "plan":     "",
        "research": "",
        "summary":  "",
        "critique": "",
        "final":    "",
        "messages": [HumanMessage(content=topic)],
    }
    result = app.invoke(initial_state)
    return result


if __name__ == "__main__":
    topic = "The impact of large language models on software engineering productivity"
    result = run(topic)

    print("\n" + "="*60)
    print("FINAL OUTPUT")
    print("="*60)
    print(result["final"])

    # Save output
    with open("output.json", "w") as f:
        json.dump({
            "topic":    result["topic"],
            "plan":     result["plan"],
            "research": result["research"],
            "summary":  result["summary"],
            "critique": result["critique"],
            "final":    result["final"],
        }, f, indent=2)
    print("\nSaved to output.json")
