"""Sample data creation for ESG Reporter."""

from sqlalchemy.orm import Session
from datetime import datetime, date
import random

from app.core.database import get_db, init_db
from app.core.database.models import Company, ESGData


def create_sample_company(db: Session) -> Company:
    """Create a sample company for testing."""
    company = Company(
        name="그린테크 주식회사",
        business_number="123-45-67890",
        industry="제조업",
        size="중소기업",
        address="서울시 강남구 테헤란로 123",
        contact_email="info@greentech.co.kr",
        contact_phone="02-1234-5678",
        description="친환경 기술 솔루션을 제공하는 중소기업"
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company


def create_sample_esg_data(db: Session, company_id: int) -> None:
    """Create sample ESG data for testing."""
    
    # Environmental data
    environmental_data = [
        {
            'category': 'Environmental',
            'subcategory': 'Energy Consumption',
            'metric_name': 'Total Energy Usage',
            'metric_code': 'ENV_ENERGY_TOTAL',
            'value': 125000.0,
            'unit': 'kWh',
            'data_source': 'manual',
            'reporting_year': 2023,
            'notes': '2023년 총 전력 사용량'
        },
        {
            'category': 'Environmental',
            'subcategory': 'Water Usage',
            'metric_name': 'Water Consumption',
            'metric_code': 'ENV_WATER_TOTAL',
            'value': 8500.0,
            'unit': 'm³',
            'data_source': 'excel',
            'reporting_year': 2023,
            'notes': '사무실 및 제조 공정 용수 사용량'
        },
        {
            'category': 'Environmental',
            'subcategory': 'Carbon Emissions',
            'metric_name': 'Scope 1 Emissions',
            'metric_code': 'ENV_CARBON_SCOPE1',
            'value': 45.2,
            'unit': 'tonnes CO2e',
            'data_source': 'manual',
            'reporting_year': 2023,
            'notes': '직접 배출량 (연료 연소 등)'
        },
        {
            'category': 'Environmental',
            'subcategory': 'Waste Management',
            'metric_name': 'Total Waste Generated',
            'metric_code': 'ENV_WASTE_TOTAL',
            'value': 12.8,
            'unit': 'tonnes',
            'data_source': 'excel',
            'reporting_year': 2023,
            'notes': '총 폐기물 발생량'
        }
    ]
    
    # Social data
    social_data = [
        {
            'category': 'Social',
            'subcategory': 'Employee Safety',
            'metric_name': 'Lost Time Injury Rate',
            'metric_code': 'SOC_SAFETY_LTIR',
            'value': 0.85,
            'unit': 'per 100 employees',
            'data_source': 'erp',
            'reporting_year': 2023,
            'notes': '재해율 (100명당)'
        },
        {
            'category': 'Social',
            'subcategory': 'Diversity & Inclusion',
            'metric_name': 'Female Employee Ratio',
            'metric_code': 'SOC_DIVERSITY_FEMALE',
            'value': 42.5,
            'unit': '%',
            'data_source': 'erp',
            'reporting_year': 2023,
            'notes': '전체 직원 중 여성 비율'
        },
        {
            'category': 'Social',
            'subcategory': 'Training & Development',
            'metric_name': 'Training Hours per Employee',
            'metric_code': 'SOC_TRAINING_HOURS',
            'value': 28.5,
            'unit': 'hours',
            'data_source': 'manual',
            'reporting_year': 2023,
            'notes': '직원 1인당 연간 교육시간'
        },
        {
            'category': 'Social',
            'subcategory': 'Community Investment',
            'metric_name': 'Community Investment Amount',
            'metric_code': 'SOC_COMMUNITY_INVEST',
            'value': 15000000,
            'unit': 'KRW',
            'data_source': 'manual',
            'reporting_year': 2023,
            'notes': '지역사회 투자 금액'
        }
    ]
    
    # Governance data
    governance_data = [
        {
            'category': 'Governance',
            'subcategory': 'Board Composition',
            'metric_name': 'Independent Director Ratio',
            'metric_code': 'GOV_BOARD_INDEPENDENT',
            'value': 33.3,
            'unit': '%',
            'data_source': 'manual',
            'reporting_year': 2023,
            'notes': '이사회 내 독립이사 비율'
        },
        {
            'category': 'Governance',
            'subcategory': 'Ethics & Compliance',
            'metric_name': 'Ethics Training Completion Rate',
            'metric_code': 'GOV_ETHICS_TRAINING',
            'value': 98.5,
            'unit': '%',
            'data_source': 'erp',
            'reporting_year': 2023,
            'notes': '윤리교육 이수율'
        },
        {
            'category': 'Governance',
            'subcategory': 'Risk Management',
            'metric_name': 'Risk Assessment Frequency',
            'metric_code': 'GOV_RISK_ASSESSMENT',
            'value': 4,
            'unit': 'times per year',
            'data_source': 'manual',
            'reporting_year': 2023,
            'notes': '연간 리스크 평가 실시 횟수'
        }
    ]
    
    # Combine all data
    all_data = environmental_data + social_data + governance_data
    
    # Create ESG data records
    for data in all_data:
        esg_record = ESGData(
            company_id=company_id,
            category=data['category'],
            subcategory=data['subcategory'],
            metric_name=data['metric_name'],
            metric_code=data['metric_code'],
            value=data['value'],
            unit=data['unit'],
            data_source=data['data_source'],
            reporting_year=data['reporting_year'],
            period_start=date(2023, 1, 1),
            period_end=date(2023, 12, 31),
            notes=data['notes'],
            quality_score=random.uniform(0.7, 1.0),
            raw_data=data
        )
        
        db.add(esg_record)
    
    db.commit()


def create_sample_data():
    """Create all sample data."""
    print("Initializing database...")
    init_db()
    
    db = next(get_db())
    
    try:
        print("Creating sample company...")
        company = create_sample_company(db)
        print(f"Created company: {company.name} (ID: {company.id})")
        
        print("Creating sample ESG data...")
        create_sample_esg_data(db, company.id)
        print("Sample ESG data created successfully!")
        
        print(f"""
Sample data created successfully!

Company: {company.name}
- Environmental metrics: 4
- Social metrics: 4  
- Governance metrics: 3
- Total ESG data points: 11

You can now run the application and explore the data.
        """)
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()