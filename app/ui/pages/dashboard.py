"""Dashboard page for ESG overview."""

from nicegui import ui
from typing import Optional
from sqlalchemy.orm import Session

from .base_page import BasePage
from app.core.database.models import Company


class DashboardPage(BasePage):
    """Main dashboard page showing ESG overview."""
    
    async def render(self, db_session: Session, company_id: Optional[int] = None) -> None:
        """Render dashboard page."""
        await super().render(db_session, company_id)
        
        ui.label('ESG Dashboard').classes('text-h3 font-weight-bold mb-4')
        
        if not company_id:
            with ui.card().classes('w-full p-6 text-center'):
                ui.icon('business', size='4rem').classes('text-grey-5 mb-4')
                ui.label('No Company Selected').classes('text-h5 mb-2')
                ui.label('Please select a company from the dropdown above.').classes('text-body2 text-grey-7')
            return
        
        # Get company info
        company = db_session.query(Company).filter_by(id=company_id).first()
        if company:
            with ui.card().classes('w-full mb-4'):
                with ui.card_section():
                    ui.label(company.name).classes('text-h5 font-weight-bold')
                    if company.industry:
                        ui.label(f'Industry: {company.industry}').classes('text-body2 text-grey-7')
        
        # Placeholder content
        with ui.row().classes('w-full gap-4 mb-6'):
            for category, icon, color in [
                ('Environmental', 'eco', 'green'),
                ('Social', 'people', 'blue'), 
                ('Governance', 'account_balance', 'purple')
            ]:
                with ui.card().classes('flex-1'):
                    with ui.card_section():
                        ui.icon(icon, size='2rem').classes(f'text-{color} mb-2')
                        ui.label(category).classes('text-h6 font-weight-bold')
                        ui.label('No data available').classes('text-body2 text-grey-7')