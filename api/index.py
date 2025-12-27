from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form, Body, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.agent import analyze, rewrite_bullets, generate_cover_letter, ensure_gemini

# Auth imports
from .database import engine, get_db, Base
from .models import User
from .schemas import UserCreate, Token, UserLogin, UserBase
from .auth import create_access_token, get_current_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
from datetime import timedelta

# Initialize DB tables
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = [
    "https://resumeboost.vercel.app",
    "https://*.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class RewriteRequest(BaseModel):
    bullets: List[str]
    jd_text: str

class CoverLetterRequest(BaseModel):
    resume_text: str
    jd_text: str

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# --- Auth Routes ---

@app.post("/api/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-login after registration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Protected Routes ---

@app.post("/api/analyze")
@limiter.limit("20/hour")
async def analyze_resume(
    request: Request,
    resume_file: UploadFile = File(None),
    resume_text: Optional[str] = Form(None),
    jd_text: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.analysis_count >= 2:
        raise HTTPException(
            status_code=403,
            detail="Usage limit exceeded. You can only perform 2 analyses."
        )

    current_user.analysis_count += 1
    db.commit()
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
    current_user: User = Depends(get_current_user)
):
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
def rewrite_bullets_endpoint(req: RewriteRequest, current_user: User = Depends(get_current_user)):
    try:
        model = ensure_gemini()
        rewritten = rewrite_bullets(model, req.bullets, req.jd_text)
        return {"rewritten_bullets": rewritten}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cover-letter")
def cover_letter_endpoint(req: CoverLetterRequest, current_user: User = Depends(get_current_user)):
    try:
        model = ensure_gemini()
        letter = generate_cover_letter(model, req.resume_text, req.jd_text)
        return {"cover_letter": letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
