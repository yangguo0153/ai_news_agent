from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import json


# --- Phase 3: Basic Policy ---
class ReimbursementPolicy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str = Field(default="My Company")
    overtime_start_time: str = Field(default="19:00")
    taxi_daily_limit: float = Field(default=200.0)


# --- Phase 7: AI Settings ---
class GlobalSettings(SQLModel, table=True):
    """Application-wide settings including LLM configuration"""
    id: Optional[int] = Field(default=None, primary_key=True)
    openai_api_key: Optional[str] = None
    openai_base_url: str = Field(default="https://api.openai.com/v1")
    model_name: str = Field(default="gpt-3.5-turbo")



# --- Phase 5A: Workflow Templates ---
class WorkflowTemplate(SQLModel, table=True):
    """Pre-defined reimbursement workflow configurations"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # e.g., "加班打车报销", "出差报销"
    description: str = ""
    required_files_json: str = Field(default="[]")  # JSON array
    rules_json: str = Field(default="{}")  # JSON object
    output_format: str = Field(default="excel+word")
    is_default: bool = Field(default=False)
    
    @property
    def required_files(self) -> list:
        return json.loads(self.required_files_json)
    
    @property
    def rules(self) -> dict:
        return json.loads(self.rules_json)


# --- Phase 5B: Multi-tenant Auth ---
class Company(SQLModel, table=True):
    """Company/Organization for multi-tenancy"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="company")
    records: List["ReimbursementRecord"] = Relationship(back_populates="company")


class User(SQLModel, table=True):
    """User account with company association"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    display_name: str = ""
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Foreign Keys
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    
    # Relationships
    company: Optional[Company] = Relationship(back_populates="users")
    records: List["ReimbursementRecord"] = Relationship(back_populates="user")


# --- Phase 5C: History & Analytics ---
class ReimbursementRecord(SQLModel, table=True):
    """Historical record of each reimbursement processing"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Processing Result
    total_amount: float = Field(default=0.0)
    matched_count: int = Field(default=0)
    unmatched_count: int = Field(default=0)
    download_url: str = ""
    
    # Metadata
    template_name: Optional[str] = None
    notes: str = ""
    
    # Foreign Keys
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="records")
    company: Optional[Company] = Relationship(back_populates="records")
