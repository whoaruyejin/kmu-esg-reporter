"""Database models for ESG Reporter."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

"""
2025-09-21 14:00 기준
ESG 분석용 DB 구조 변경 및 리팩토링 요약

1. models.py 주요 변경 사항
---------------------------
- 새로운 모델 클래스:

  1) CmpInfo (CMP_INFO 테이블 매핑)
     - cmp_num: 사업장번호 (PK)
     - cmp_nm: 회사명
     - cmp_industry, cmp_sector: 업종, 산업
     - cmp_extemp: 사외 이사회 수
     - cmp_ethics_yn, cmp_comp_yn: 윤리경영, 컴플라이언스 여부

  2) EmpInfo (EMP_INFO 테이블 매핑)
     - emp_id: 사번 (PK)
     - emp_nm, emp_birth, emp_join: 이름, 생년월일, 입사일
     - emp_acident_cnt: 산재 발생 횟수
     - emp_board_yn, emp_gender: 이사회 여부, 성별

  3) Env (ENV 테이블 매핑)
     - year: 연도 (PK)
     - energy_use, green_use: 에너지 사용량, 온실가스 배출량
     - renewable_yn, renewable_ratio: 재생에너지 사용 여부, 비율

- 호환성 유지:
  - 기존 Report, ChatSession, DataImportLog는 cmp_num FK 사용
  - Company = CmpInfo 별칭으로 하위 호환성 보장

2. data_processor.py 주요 기능
-------------------------------
- 새로운 데이터 처리 메서드:
  - get_company_info(cmp_num: str) -> Dict      # 회사 기본 정보 조회
  - get_employee_data() -> DataFrame            # 직원 데이터 조회
  - get_environmental_data() -> DataFrame       # 환경 데이터 조회

- ESG 지표 계산:
  - calculate_social_metrics(): 성별 다양성, 이사회 구성, 안전 지표, 근속년수
  - calculate_environmental_metrics(): 에너지/온실가스 트렌드, 재생에너지 비율
  - calculate_governance_metrics(): 사외이사 비율, 윤리경영/컴플라이언스 정책

- 통합 분석 기능:
  - generate_comprehensive_report(cmp_num: str) -> Dict  # 종합 ESG 보고서
  - identify_data_gaps(cmp_num: str) -> Dict             # 데이터 갭 분석

3. 계산 지표 예시
-----------------
- Social:
  - 전체 직원 수, 성별 분포, 여성 비율
  - 이사회 구성원 수, 여성 이사 비율
  - 총 산재 발생 수, 산재율, 무재해 직원 수
  - 평균 근속년수, 신입/베테랑 직원 수

- Environmental:
  - 최신 연도 에너지 사용량, 온실가스 배출량
  - 재생에너지 사용 여부 및 비율
  - 최근 3년 트렌드 분석 (증가/감소율)
  - 연도별 에너지 집약도

- Governance:
  - 사외이사 수 및 비율
  - 윤리경영, 컴플라이언스 정책 존재 여부
  - 이사회 다양성 비율
  - 종합 지배구조 점수 및 등급 (A+~D)

4. 하위 호환성
---------------
- 기존 get_company_data(), calculate_category_summaries() 메서드 유지
- 새로운 테이블 데이터를 기존 ESGData 형태로 변환하여 반환
- 새로운 DB 구조 기반으로 더 정확하고 실용적인 ESG 분석 가능
"""


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