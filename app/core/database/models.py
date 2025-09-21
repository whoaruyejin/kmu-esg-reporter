"""Database models for ESG Reporter."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Date
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class Company(Base):
    """Company model for storing company information."""
    
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    business_number = Column(String(50), unique=True, index=True)
    industry = Column(String(100))
    size = Column(String(50))  # small, medium, large
    address = Column(Text)
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    esg_data = relationship("ESGData", back_populates="company")
    reports = relationship("Report", back_populates="company")


class ESGData(Base):
    """ESG data model for storing environmental, social, and governance metrics."""
    
    __tablename__ = "esg_data"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Data categorization
    category = Column(String(50), nullable=False)  # Environmental, Social, Governance
    subcategory = Column(String(100))
    metric_name = Column(String(255), nullable=False)
    metric_code = Column(String(50))
    
    # Data values
    value = Column(Float)
    unit = Column(String(50))
    text_value = Column(Text)  # For qualitative data
    
    # Data source and quality
    data_source = Column(String(100))  # manual, excel, erp, api
    source_file = Column(String(255))  # Original file name if applicable
    quality_score = Column(Float, default=1.0)  # Data quality indicator
    
    # Temporal information
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    reporting_year = Column(Integer, index=True)
    
    # Metadata
    raw_data = Column(JSON)  # Store original raw data
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="esg_data")


class Report(Base):
    """Generated ESG reports."""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    report_type = Column(String(50))  # annual, quarterly, custom
    content = Column(Text)
    summary = Column(Text)
    
    # Report metadata
    generated_by = Column(String(50))  # system, user, chatbot
    format = Column(String(20))  # pdf, html, json
    status = Column(String(20), default="draft")  # draft, published, archived
    
    # File information
    file_path = Column(String(500))
    file_size = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="reports")


class ChatSession(Base):
    """Chat sessions for the ESG chatbot."""
    
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # Session metadata
    user_id = Column(String(255))  # For future user management
    title = Column(String(255))
    
    # Chat history
    messages = Column(JSON)  # Store chat history as JSON
    context = Column(JSON)   # Store conversation context
    
    # Session statistics
    message_count = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")


class CmpInfo(Base):
    """Company information model for company management."""
    
    __tablename__ = "cmp_info"
    
    cmp_num = Column(String(10), primary_key=True)  # 사업장번호 (복합 PK 1)
    cmp_branch = Column(String(10), primary_key=True)  # 지점 (복합 PK 2)
    cmp_nm = Column(String(100), nullable=False)  # 회사명
    cmp_industry = Column(String(20))  # 업종
    cmp_sector = Column(String(20))  # 산업
    cmp_addr = Column(String(200))  # 주소
    cmp_extemp = Column(Integer)  # 사외 이사회 수
    cmp_ethics_yn = Column(String(1))  # 윤리경영 여부
    cmp_comp_yn = Column(String(1))  # 컴플라이언스 정책 여부


class Employee(Base):
    """Employee model for HR management."""
    
    __tablename__ = "emp_info"
    
    EMP_ID = Column(Integer, primary_key=True, index=True)  # 사번 (Primary Key)
    EMP_NM = Column(String(10), nullable=False)  # 이름
    EMP_BIRTH = Column(String(8))  # 생년월일 (YYYYMMDD)
    EMP_TEL = Column(String(20))  # 전화번호
    EMP_EMAIL = Column(String(20))  # 이메일
    EMP_JOIN = Column(String(8))  # 입사년도 (YYYYMMDD)
    EMP_ACIDENT_CNT = Column(Integer, default=0)  # 산재발생횟수
    EMP_BOARD_YN = Column(String(1), default='N')  # 이사회여부
    EMP_GENDER = Column(String(1))  # 성별 (1:남자, 2:여자)
    EMP_ENDYN = Column(String(1), default='Y')  # 재직여부 (Y:재직, N:퇴직)
    EMP_COMP = Column(String(10))  # 사업장
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Environment(Base):
    """환경현황 테이블"""
    
    __tablename__ = "env"
    
    year = Column(Integer, primary_key=True, index=True)  # 년도 (PK, YYYY)
    energy_use = Column(Float)  # 에너지 사용량
    green_use = Column(Float)  # 온실가스 배출량
    renewable_yn = Column(String(1))  # 재생에너지 사용여부 (Y/N)
    renewable_ratio = Column(Float)  # 재생에너지 비율
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataImportLog(Base):
    """Log for data import operations."""
    
    __tablename__ = "data_import_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Import details
    import_type = Column(String(50))  # excel, erp, api, manual
    source_file = Column(String(500))
    status = Column(String(20))  # success, error, partial
    
    # Statistics
    records_processed = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    
    # Error information
    error_log = Column(JSON)
    validation_errors = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")