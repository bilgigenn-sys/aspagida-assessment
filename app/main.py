from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from pathlib import Path
from datetime import datetime, date

from .database import Base, engine, get_db
from .models import User, Assessment, SMTPSettings
from .schemas import LoginIn, TokenOut, AssessmentIn, SMTPIn, SMTPOut, StatsOut
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .emailer import send_mail, get_smtp_settings
from .pdfgen import build_pdf
from .config import settings

# Initialize DB
Base.metadata.create_all(bind=engine)

# Seed admin if missing
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session as _Session
with _Session(bind=engine) as db:
    admin = db.query(User).filter(User.email == str(settings.ADMIN_EMAIL)).first()
    if not admin:
        admin = User(email=str(settings.ADMIN_EMAIL), password_hash=hash_password(settings.ADMIN_PASSWORD))
        db.add(admin)
        db.commit()

app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.APP_NAME})

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "app_name": settings.APP_NAME})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "app_name": settings.APP_NAME})

# ------------- Auth -------------
@app.post("/api/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token)

@app.get("/api/auth/me")
def me(current=Depends(get_current_user)):
    return {"email": current.email}

# ------------- Assessments -------------
@app.post("/api/assessments")
def create_assessment(data: AssessmentIn, request: Request, db: Session = Depends(get_db)):
    # persist
    row = Assessment(
        full_name=data.full_name,
        company=data.company,
        email=str(data.email),
        phone=data.phone,
        tax_id=data.tax_id,
        answers=data.answers,
        meta=data.meta or {}
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    # build PDF
    output_dir = Path("storage/pdfs")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"assessment_{row.id}.pdf"
    payload = {
        "full_name": row.full_name,
        "company": row.company,
        "email": row.email,
        "phone": row.phone,
        "answers": row.answers,
        "meta": row.meta or {},
    }
    build_pdf(str(pdf_path), payload)
    row.pdf_path = str(pdf_path)
    db.commit()

    # email PDF
    try:
        send_mail(
            db,
            subject=f"[Assessment] {row.full_name} - {row.company or ''}",
            body=f"Yeni assessment oluşturuldu. ID: {row.id}",
            attachments=[{"path": str(pdf_path), "name": f"assessment_{row.id}.pdf", "mime": "application/pdf"}]
        )
    except Exception as e:
        # don't block; report back
        return {"ok": True, "id": row.id, "pdf": str(pdf_path), "email_error": str(e)}

    return {"ok": True, "id": row.id, "pdf": str(pdf_path)}

@app.get("/api/assessments")
def list_assessments(current=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Assessment).order_by(Assessment.created_at.desc()).all()
    res = []
    for a in q:
        res.append({
            "id": a.id,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
            "full_name": a.full_name,
            "company": a.company,
            "email": a.email,
            "phone": a.phone,
            "tax_id": a.tax_id,
        })
    return res

@app.get("/api/assessments/{aid}")
def get_assessment(aid: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Assessment).filter(Assessment.id == aid).first()
    if not a:
        raise HTTPException(404, "Not found")
    return {
        "id": a.id,
        "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
        "full_name": a.full_name,
        "company": a.company,
        "email": a.email,
        "phone": a.phone,
        "tax_id": a.tax_id,
        "answers": a.answers,
        "meta": a.meta,
        "pdf_path": a.pdf_path
    }

@app.get("/api/assessments/{aid}/pdf")
def download_pdf(aid: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Assessment).filter(Assessment.id == aid).first()
    if not a or not a.pdf_path:
        raise HTTPException(404, "PDF not found")
    return FileResponse(a.pdf_path, media_type="application/pdf", filename=f"assessment_{aid}.pdf")

# ------------- SMTP settings -------------
@app.get("/api/smtp", response_model=SMTPOut)
def get_smtp(current=Depends(get_current_user), db: Session = Depends(get_db)):
    cfg = get_smtp_settings(db)
    return SMTPOut(host=cfg.host, port=cfg.port, username=cfg.username, use_tls=cfg.use_tls)

@app.put("/api/smtp", response_model=SMTPOut)
def update_smtp(payload: SMTPIn, current=Depends(get_current_user), db: Session = Depends(get_db)):
    cfg = get_smtp_settings(db)
    cfg.host = payload.host
    cfg.port = payload.port
    cfg.username = payload.username
    if payload.password:  # optional change
        cfg.password = payload.password
    cfg.use_tls = payload.use_tls
    db.add(cfg)
    db.commit()
    return SMTPOut(host=cfg.host, port=cfg.port, username=cfg.username, use_tls=cfg.use_tls)

# ------------- Stats -------------
@app.get("/api/stats", response_model=StatsOut)
def stats(current=Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(func.count(Assessment.id)).scalar() or 0
    today = db.query(func.count(Assessment.id)).filter(func.date(Assessment.created_at) == date.today()).scalar() or 0
    companies = db.query(func.count(distinct(Assessment.company))).scalar() or 0
    return StatsOut(total_tests=total, todays_tests=today, companies=companies)

# ------------- Embedding for iFrame -------------
@app.get("/embed/form", response_class=HTMLResponse)
def embed_form(request: Request):
    # a minimal form-only page to be used in iFrames
    return templates.TemplateResponse("embed.html", {"request": request, "app_name": settings.APP_NAME})
