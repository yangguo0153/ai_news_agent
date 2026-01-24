from sqlmodel import SQLModel, create_engine, Session, select
from pathlib import Path
import json
from .models import (
    ReimbursementPolicy, 
    WorkflowTemplate, 
    Company, 
    User, 
    ReimbursementRecord,
    GlobalSettings
)

import os

sqlite_file_name = "reimbursement.db"
# Use absolute path to ensure DB is created in the correct directory regardless of runtime CWD
BASE_DIR = Path(__file__).parent.parent
# Default to SQLite
default_db_url = f"sqlite:///{BASE_DIR}/{sqlite_file_name}"

database_url = os.getenv("DATABASE_URL", default_db_url)
# Handle potential Render/Heroku postgresql:// vs postgres:// differences
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}
engine = create_engine(database_url, connect_args=connect_args)


# Default Workflow Templates
DEFAULT_TEMPLATES = [
    {
        "name": "加班打车报销",
        "description": "适用于日常加班后打车回家的报销场景。需上传打卡记录、加班截图和打车发票。",
        "required_files_json": json.dumps(["打卡记录Excel", "打卡/加班截图", "打车发票PDF", "行程单PDF"]),
        "rules_json": json.dumps({
            "overtime_start": "19:00",
            "taxi_daily_limit": 200,
            "match_strategy": "凌晨0-6点匹配前一天加班"
        }),
        "output_format": "excel+word",
        "is_default": True
    },
    {
        "name": "出差报销(规划中)",
        "description": "适用于出差期间的交通、住宿报销。功能开发中...",
        "required_files_json": json.dumps(["出差审批单", "机票/火车票", "酒店发票", "餐饮发票"]),
        "rules_json": json.dumps({
            "per_diem": 100,
            "hotel_limit": 500,
            "transport_class": "经济舱/二等座"
        }),
        "output_format": "excel",
        "is_default": False
    }
]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Init default policy if not exists
        if not session.exec(select(ReimbursementPolicy)).first():
            session.add(ReimbursementPolicy())

        # Init global settings if not exists
        if not session.exec(select(GlobalSettings)).first():
            session.add(GlobalSettings())
        
        # Init default workflow templates
        for tpl_data in DEFAULT_TEMPLATES:
            existing = session.exec(
                select(WorkflowTemplate).where(WorkflowTemplate.name == tpl_data["name"])
            ).first()
            if not existing:
                session.add(WorkflowTemplate(**tpl_data))
        
        session.commit()


def get_session():
    with Session(engine) as session:
        yield session
