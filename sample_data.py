"""Sample data creation for ESG Reporter (new schema: CmpInfo/EmpInfo/Env)."""

from datetime import datetime
from decimal import Decimal
import random

from sqlalchemy.orm import Session

# DB 세션/초기화 유틸 (init_db는 Base.metadata.create_all(...)을 호출해야 함)
from app.core.database import get_db, init_db

# 새 스키마 모델
from app.core.database.models import CmpInfo, EmpInfo, Env, Report, ChatSession


def create_sample_company(db: Session, cmp_num: str = "6182618882") -> CmpInfo:
    """CMP_INFO 샘플 회사 1건 생성."""
    company = CmpInfo(
        cmp_num=cmp_num,
        cmp_nm="그린테크 주식회사",
        cmp_industry="제조업",
        cmp_sector="산업재",
        cmp_addr="서울시 강남구 테헤란로 123",
        cmp_extemp=2,             # 사외 이사회 수
        cmp_ethics_yn="Y",        # 윤리경영 정책 유무
        cmp_comp_yn="Y",          # 컴플라이언스 정책 유무
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def create_sample_employees(db: Session, n: int = 12) -> None:
    """EMP_INFO 샘플 직원 n명 생성.
    (모델에 회사 FK가 없으므로 전사 기준 데이터로 삽입)
    """
    base_id = random.randint(10000, 20000)
    for i in range(n):
        emp = EmpInfo(
            emp_id=base_id + i,
            emp_nm=f"직원{i+1}",
            emp_birth=f"{random.randint(1980, 1998):04d}{random.randint(1,12):02d}{random.randint(1,28):02d}",
            emp_tel=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            emp_email=f"employee{i+1}@greentech.co.kr",
            emp_join=f"{random.randint(2015, 2024):04d}{random.randint(1,12):02d}{random.randint(1,28):02d}",
            emp_acident_cnt=random.choice([0, 0, 0, 1]),  # 대부분 0, 가끔 1
            emp_board_yn="Y" if i < 2 else "N",         # 앞의 2명은 이사회
            emp_gender=random.choice(["M", "F"]),
        )
        db.add(emp)
    db.commit()


def create_sample_env(db: Session, years=(2021, 2022, 2023, 2024)) -> None:
    """ENV 샘플: 연도별 에너지/온실가스/재생에너지 비율."""
    energy = 110000.0
    green = 1200.0
    ratio = Decimal("0.120")
    for y in years:
        # 연도 진행에 따라 약간 변화를 주자
        energy *= random.uniform(0.95, 1.05)
        green *= random.uniform(0.92, 1.08)
        ratio = (ratio + Decimal(str(random.uniform(-0.01, 0.02)))).quantize(Decimal("0.001"))
        # 0~1 범위로 클램프
        ratio = max(Decimal("0.000"), min(Decimal("1.000"), ratio))

        env = Env(
            year=y,
            energy_use=round(energy, 2),
            green_use=round(green, 2),
            renewable_yn="Y" if ratio > Decimal("0.000") else "N",
            renewable_ratio=ratio,  # Numeric(5,3) -> Decimal 권장
        )
        db.add(env)
    db.commit()


def create_sample_report(db: Session, cmp_num: str) -> None:
    """샘플 Report 1건(간단 내용) 생성."""
    rpt = Report(
        company_id=cmp_num,  # FK to cmp_info.cmp_num
        title="그린테크 ESG 샘플 보고서 (자동 생성)",
        report_type="annual",
        content="{'summary': '샘플 ESG 보고서 내용입니다.'}",
        summary="샘플 요약",
        generated_by="script",
        format="json",
        status="draft",
        file_path=None,
        file_size=None,
        created_at=datetime.utcnow(),
    )
    db.add(rpt)
    db.commit()


def create_sample_session(db: Session, cmp_num: str) -> None:
    """샘플 ChatSession 1건 생성(선택)."""
    sess = ChatSession(
        session_id="demo-session-0001",
        company_id=cmp_num,
        user_id="demo-user",
        title="데모 ESG 채팅 세션",
        messages=[],
        context={},
        message_count=0,
        last_activity=datetime.utcnow(),
    )
    db.add(sess)
    db.commit()


def create_sample_data():
    """모든 샘플 데이터 생성."""
    print("Initializing database...")
    init_db()  # Base.metadata.create_all(bind=engine) 수행되어야 함

    db = next(get_db())
    try:
        print("Creating sample company (CmpInfo)...")
        company = create_sample_company(db, cmp_num="6182618882")
        print(f"Created company: {company.cmp_nm} (CMP_NUM: {company.cmp_num})")

        print("Creating sample employees (EmpInfo)...")
        create_sample_employees(db, n=12)

        print("Creating sample environmental data (Env)...")
        create_sample_env(db, years=(2021, 2022, 2023, 2024))

        print("Creating a sample report (Report)...")
        create_sample_report(db, cmp_num=company.cmp_num)

        print("Creating a sample chat session (ChatSession)...")
        create_sample_session(db, cmp_num=company.cmp_num)

        print(
            f"""
Sample data created successfully!

Company: {company.cmp_nm} (CMP_NUM: {company.cmp_num})
- Employees: 12
- Environmental years: 2021~2024
- 1 draft report
- 1 demo chat session

You can now run the application and explore the data.
            """
        )

    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
