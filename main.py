"""FastAPI application serving the Python/SymPy reasoning engine and built React UI."""
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .engine import analyze, public_case
from .discovery import discovery_case, source_document, check_conclusion
from .cases import get_case as get_research_case, case_catalog
from .research import analyze_research
from .benchmarks import run_evaluation, latest_evaluation
from .relationships import validate_connection
from .math_challenges import challenge_catalog, grade_challenge, progress_status, verified_work

app=FastAPI(title="Case: Null | Discrete Mathematics Investigation",version="2.0")
allowed_origins = [origin.strip().rstrip('/') for origin in os.getenv('CASE_NULL_CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if origin.strip()]
app.add_middleware(CORSMiddleware,allow_origins=allowed_origins,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])

@app.get('/api/health')
def health():
    return {'status': 'ok'}
class Request(BaseModel):
    selected:list[str]=[]
    conflicting:bool=False
    unknown:bool=False
@app.get('/api/case')
def get_case(): return public_case()
@app.post('/api/analyze')
def analyze_case(req:Request):
    try: return analyze(req.selected,req.conflicting,req.unknown)
    except ValueError as e: raise HTTPException(status_code=422,detail=str(e))

class ConclusionRequest(BaseModel):
    candidate: str
    documents: list[str] = Field(default_factory=list, max_length=6)
    reasoning: str = Field(default='', max_length=5000)
    math_work: list[dict] = Field(default_factory=list, max_length=5)

class MathProgressRequest(BaseModel):
    work: list[dict] = Field(default_factory=list, max_length=5)
    discovered: list[str] = Field(default_factory=list, max_length=6)

class MathAnswerRequest(MathProgressRequest):
    challenge_id: str = Field(max_length=30)
    answers: dict = Field(default_factory=dict)

@app.get('/api/discovery/math/challenges')
def math_challenges():
    return challenge_catalog()

@app.post('/api/discovery/math/progress')
def math_progress(req: MathProgressRequest):
    return progress_status(req.work, req.discovered)

@app.post('/api/discovery/math/check')
def math_check(req: MathAnswerRequest):
    try:
        return grade_challenge(req.challenge_id, req.answers, req.work, req.discovered)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

@app.get('/api/discovery/case')
def get_discovery_case():
    return discovery_case()

@app.get('/api/discovery/records/{document_id}')
def get_source_document(document_id: str):
    try: return source_document(document_id)
    except ValueError as e: raise HTTPException(status_code=404, detail=str(e))

class RelationshipRequest(BaseModel):
    account: str
    document_id: str
    discovered: list[str] = Field(default_factory=list, max_length=6)

@app.post('/api/discovery/relationships/verify')
def verify_relationship(req: RelationshipRequest):
    try: return validate_connection(req.account, req.document_id, req.discovered)
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))

@app.post('/api/discovery/conclusion')
def submit_conclusion(req: ConclusionRequest):
    if len(verified_work(req.math_work, req.documents)) != 5:
        return {'accepted': False, 'status': 'insufficient', 'message': 'Complete all five mathematics challenges and cite their four source records before submitting your conclusion.'}
    try: return check_conclusion(req.candidate, req.documents, req.reasoning)
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))

class ResearchRequest(BaseModel):
    case_id: str = 'CASE-001'
    selected: list[str] = Field(default_factory=list, max_length=6)
    provisional: list[str] = Field(default_factory=list, max_length=6)
    conflicting: bool | None = None
    unknown: bool = False

@app.get('/api/research/cases')
def research_cases():
    return case_catalog()

@app.get('/api/research/cases/{case_id}')
def research_case(case_id: str):
    try: return get_research_case(case_id)
    except ValueError as e: raise HTTPException(status_code=404, detail=str(e))

@app.post('/api/research/analyze')
def research_analysis(req: ResearchRequest):
    try: return analyze_research(**req.model_dump())
    except ValueError as e: raise HTTPException(status_code=422, detail=str(e))

@app.get('/api/research/evaluation')
def evaluation_results():
    return latest_evaluation()

@app.post('/api/research/evaluation')
def evaluate_cases():
    return run_evaluation(save=True)

DIST=Path(__file__).resolve().parent.parent/'frontend'/'dist'
if DIST.exists():
    app.mount('/assets',StaticFiles(directory=DIST/'assets'),name='assets')
    @app.get('/{path:path}')
    def spa(path:str):
        file=(DIST/path).resolve()
        if file.is_file() and DIST.resolve() in file.parents:
            return FileResponse(file)
        return FileResponse(DIST/'index.html')
