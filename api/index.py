from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.agent import analyze, rewrite_bullets, generate_cover_letter, validate_access_code, ensure_gemini

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = [
    "https://resumeboost.vercel.app",
    "https://*.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class RewriteRequest(BaseModel):
    bullets: List[str]
    jd_text: str

class CoverLetterRequest(BaseModel):
    resume_text: str
    jd_text: str

def verify_access(x_access_code: Optional[str] = Header(None)):
    if not validate_access_code(x_access_code):
        raise HTTPException(status_code=403, detail="Invalid or missing Access Code")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/analyze")
@limiter.limit("20/hour")
async def analyze_resume(
    request: Request,
    resume_file: UploadFile = File(None),
    resume_text: Optional[str] = Form(None),
    jd_text: str = Form(...),
    x_access_code: Optional[str] = Header(None)
):
    verify_access(x_access_code)
    
    MAX_FILE_SIZE = 5 * 1024 * 1024
    MAX_JD_LENGTH = 10000
    
    if jd_text and len(jd_text) > MAX_JD_LENGTH:
        raise HTTPException(status_code=400, detail="Job description too long. Maximum 10,000 characters.")
    
    final_resume_text = ""
    
    if resume_file:
        content = await resume_file.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
        
        filename = resume_file.filename.lower()
        if filename.endswith(".pdf"):
            try:
                import pypdf
                import io
                pdf_reader = pypdf.PdfReader(io.BytesIO(content))
                final_resume_text = ""
                for page in pdf_reader.pages:
                    final_resume_text += page.extract_text() + "\n"
            except ImportError:
                raise HTTPException(status_code=500, detail="pypdf not installed on server")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
        else:
            try:
                final_resume_text = content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="Could not decode file as UTF-8")
    elif resume_text:
        final_resume_text = resume_text
    else:
        raise HTTPException(status_code=400, detail="Must provide resume_file or resume_text")

    try:
        # We pass empty bullets initially for the full analysis
        result = analyze(final_resume_text, jd_text, [])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download-docx")
async def download_docx(
    request: Request,
    x_access_code: Optional[str] = Header(None)
):
    verify_access(x_access_code)
    try:
        data = await request.json()
        text = data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
            
        from src.docx_utils import markdown_to_docx
        docx_io = markdown_to_docx(text)
        
        return Response(
            content=docx_io.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=tailored_resume.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rewrite")
def rewrite_bullets_endpoint(req: RewriteRequest, x_access_code: Optional[str] = Header(None)):
    verify_access(x_access_code)
    try:
        model = ensure_gemini()
        rewritten = rewrite_bullets(model, req.bullets, req.jd_text)
        return {"rewritten_bullets": rewritten}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cover-letter")
def cover_letter_endpoint(req: CoverLetterRequest, x_access_code: Optional[str] = Header(None)):
    verify_access(x_access_code)
    try:
        model = ensure_gemini()
        letter = generate_cover_letter(model, req.resume_text, req.jd_text)
        return {"cover_letter": letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
