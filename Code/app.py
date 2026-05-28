"""
FastAPI server — exposes the multi-agent pipeline via REST API
Run: uvicorn app:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run
import uvicorn

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="LangGraph + HuggingFace powered research pipeline with 4 specialized agents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    topic: str

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "The impact of large language models on software engineering"
            }
        }


class ResearchResponse(BaseModel):
    topic:    str
    plan:     str
    research: str
    summary:  str
    critique: str
    final:    str


@app.get("/")
def root():
    return {
        "service": "Multi-Agent Research Assistant",
        "agents":  ["Planner", "Researcher", "Summarizer", "Critic"],
        "docs":    "/docs"
    }


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    try:
        result = run(request.topic)
        return ResearchResponse(
            topic=result["topic"],
            plan=result["plan"],
            research=result["research"],
            summary=result["summary"],
            critique=result["critique"],
            final=result["final"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
