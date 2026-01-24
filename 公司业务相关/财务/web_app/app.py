from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
import shutil
import os
import sys
from pathlib import Path
import tempfile
import zipfile
from typing import List
import logging
from datetime import datetime

# Add parent directory to path to import expense_agent
sys.path.append(str(Path(__file__).parent.parent))

# Lazy import - will be imported when actually needed
# This prevents startup crash if expense_agent has issues
process_reimbursement = None
def get_process_reimbursement():
    global process_reimbursement
    if process_reimbursement is None:
        try:
            from expense_agent.main import process_reimbursement as _pr
            process_reimbursement = _pr
        except Exception as e:
            logging.error(f"Failed to import expense_agent: {e}")
            raise
    return process_reimbursement

from web_app.database import create_db_and_tables, get_session, engine
from web_app.models import ReimbursementPolicy, WorkflowTemplate, ReimbursementRecord, User, GlobalSettings
from web_app.ai_wizard import get_ai_response
from web_app.auth import (
    UserRegister, UserLogin, Token, UserResponse,
    register_user, authenticate_user, create_access_token,
    get_current_user, require_auth
)
from pydantic import BaseModel

app = FastAPI(title="Reimbursement Agent")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev/testing. In prod restricting this is recommended.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest, session: Session = Depends(get_session)):
    # Pass templates to AI wizard for context
    workflow_templates = session.exec(select(WorkflowTemplate)).all()
    return get_ai_response(request.message, workflow_templates)

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Auth API ---
@app.post("/api/auth/register", response_model=UserResponse)
async def api_register(data: UserRegister, session: Session = Depends(get_session)):
    user = register_user(
        email=data.email,
        password=data.password,
        display_name=data.display_name,
        company_name=data.company_name,
        session=session
    )
    company_name = user.company.name if user.company else None
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        company_id=user.company_id,
        company_name=company_name
    )

@app.post("/api/auth/login", response_model=Token)
async def api_login(data: UserLogin, session: Session = Depends(get_session)):
    user = authenticate_user(data.email, data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)

@app.get("/api/auth/me", response_model=UserResponse)
async def api_me(user: User = Depends(require_auth)):
    company_name = user.company.name if user.company else None
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        company_id=user.company_id,
        company_name=company_name
    )

# Lightweight health check endpoint for Railway/Render
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Workflow Templates API ---
@app.get("/api/templates")
async def get_templates(session: Session = Depends(get_session)):
    """List all available workflow templates"""
    templates_list = session.exec(select(WorkflowTemplate)).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "required_files": t.required_files,
            "rules": t.rules,
            "is_default": t.is_default
        }
        for t in templates_list
    ]

@app.get("/api/templates/{template_id}")
async def get_template(template_id: int, session: Session = Depends(get_session)):
    """Get a specific workflow template"""
    template = session.get(WorkflowTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "required_files": template.required_files,
        "rules": template.rules
    }


@app.get("/api/settings")
async def get_settings(session: Session = Depends(get_session)):
    policy = session.exec(select(ReimbursementPolicy)).first()
    return policy

@app.post("/api/settings")
async def update_settings(
    policy: ReimbursementPolicy,
    session: Session = Depends(get_session)
):
    db_policy = session.exec(select(ReimbursementPolicy)).first()
    if not db_policy:
        db_policy = ReimbursementPolicy()
        session.add(db_policy)
    
    db_policy.company_name = policy.company_name
    db_policy.overtime_start_time = policy.overtime_start_time
    db_policy.taxi_daily_limit = policy.taxi_daily_limit
    
    session.add(db_policy)
    session.commit()
    session.refresh(db_policy)
    return db_policy

@app.get("/api/settings/ai")
async def get_ai_settings(session: Session = Depends(get_session)):
    settings = session.exec(select(GlobalSettings)).first()
    if not settings:
        settings = GlobalSettings()
        session.add(settings)
        session.commit()
    return settings

@app.post("/api/settings/ai")
async def update_ai_settings(
    settings: GlobalSettings,
    session: Session = Depends(get_session)
):
    db_settings = session.exec(select(GlobalSettings)).first()
    if not db_settings:
        db_settings = GlobalSettings()
        session.add(db_settings)
    
    db_settings.openai_api_key = settings.openai_api_key
    db_settings.openai_base_url = settings.openai_base_url
    db_settings.model_name = settings.model_name
    
    session.add(db_settings)
    session.commit()
    session.refresh(db_settings)
    return db_settings




class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat/intake")
async def chat_intake(
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    try:
        settings = session.exec(select(GlobalSettings)).first()
        templates = session.exec(select(WorkflowTemplate)).all()
        
        # Lazy load if settings not initialized
        if not settings:
            settings = GlobalSettings()
        
        from web_app.ai_wizard import analyze_intake_intent
        response = analyze_intake_intent(request.message, templates, settings)
        return response
    except Exception as e:
        logger.error(f"Error in chat_intake: {e}", exc_info=True)
        return {
            "matched_template_id": None,
            "template_name": None,
            "message": f"抱歉，系统暂时无法处理您的请求。(错误: {str(e)})"
        }

@app.post("/api/process")
async def process_files(
    background_tasks: BackgroundTasks,
    attendance_file: UploadFile = File(...),
    screenshots: List[UploadFile] = File(...),
    invoices: List[UploadFile] = File(default=[]),  # Optional: for paper invoice users
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # Optional auth
):
    # 1. Get Policy
    policy = session.exec(select(ReimbursementPolicy)).first()
    config = {
        "overtime_start": policy.overtime_start_time if policy else "19:00",
        "taxi_limit": policy.taxi_daily_limit if policy else 200.0
    }

    # 2. Setup Temp Directories
    temp_dir = tempfile.mkdtemp()
    base_path = Path(temp_dir)
    
    input_dir = base_path / "input"
    output_dir = base_path / "output"
    
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create structure (Flattened for web upload)
    (input_dir / "打卡和加班截图").mkdir(parents=True, exist_ok=True)
    (input_dir / "打车发票和行程单").mkdir(parents=True, exist_ok=True)

    try:
        # 3. Save Files
        if not attendance_file.filename.endswith('.xlsx'):
             raise HTTPException(status_code=400, detail="打卡记录必须是 xlsx 格式")
        
        with open(input_dir / attendance_file.filename, "wb") as f:
            shutil.copyfileobj(attendance_file.file, f)
            
        for file in screenshots:
            if file.filename:
                with open(input_dir / "打卡和加班截图" / file.filename, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                    
        for file in invoices:
            if file.filename:
                with open(input_dir / "打车发票和行程单" / file.filename, "wb") as f:
                    shutil.copyfileobj(file.file, f)

        # 4. Process with Config
        logger.info(f"Processing in {temp_dir} with config {config}")
        result = get_process_reimbursement()(input_dir, output_dir, config=config)
        
        if result.get("status") == "error":
             shutil.rmtree(temp_dir)
             raise HTTPException(status_code=500, detail=result.get("message"))
        
        # 5. Zip Result to Downloads Folder
        zip_filename = f"reimbursement_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        downloads_dir = Path("web_app/downloads")
        downloads_dir.mkdir(exist_ok=True, parents=True)
        zip_path = downloads_dir / zip_filename
        
        shutil.make_archive(str(zip_path.with_suffix('')), 'zip', output_dir)
        
        # 6. Cleanup Temp Input/Output
        shutil.rmtree(temp_dir)
        
        # 7. Save Record to History (if user is logged in)
        stats = result.get("stats", {})
        record = ReimbursementRecord(
            user_id=current_user.id if current_user else None,
            company_id=current_user.company_id if current_user else None,
            total_amount=stats.get("total_amount", 0.0),
            matched_count=stats.get("matched", 0),
            unmatched_count=stats.get("unmatched", 0),
            download_url=f"/api/download/{zip_filename}",
            template_name="加班打车报销"
        )
        session.add(record)
        session.commit()
        
        # 8. Return JSON
        return {
            "status": "success",
            "download_url": f"/api/download/{zip_filename}",
            "stats": stats,
            "message": "处理成功",
            "record_id": record.id
        }

    except Exception as e:
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        logger.error(f"Error processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = Path("web_app/downloads") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path, 
        media_type='application/zip', 
        filename=filename
    )

# --- History API ---
@app.get("/api/history")
async def get_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get reimbursement history. If logged in, shows user's records. Otherwise, shows all."""
    query = select(ReimbursementRecord).order_by(ReimbursementRecord.created_at.desc())
    
    if current_user:
        query = query.where(ReimbursementRecord.user_id == current_user.id)
    
    records = session.exec(query.offset(offset).limit(limit)).all()
    
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "total_amount": r.total_amount,
            "matched_count": r.matched_count,
            "unmatched_count": r.unmatched_count,
            "download_url": r.download_url,
            "template_name": r.template_name
        }
        for r in records
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
