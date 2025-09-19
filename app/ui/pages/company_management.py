"""Company management page."""

from nicegui import ui
from typing import Optional
from sqlalchemy.orm import Session

from .base_page import BasePage
from app.core.database.models import Company


class CompanyManagementPage(BasePage):
    """Company management page."""
    
    async def render(self, db_session: Session, company_id: Optional[int] = None) -> None:
        """Render company management page."""
        await super().render(db_session, company_id)
        
        ui.label('Company Management').classes('text-h3 font-weight-bold mb-4')
        
        # Add company button
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label('Manage your companies and their ESG data').classes('text-body1 text-grey-7')
            ui.button('Add Company', icon='add').props('color=primary')
        
        # Companies list
        companies = db_session.query(Company).all()
        
        if not companies:
            with ui.card().classes('w-full p-6 text-center'):
                ui.icon('business', size='4rem').classes('text-grey-5 mb-4')
                ui.label('No Companies Yet').classes('text-h5 mb-2')
                ui.label('Create your first company to start ESG reporting').classes('text-body2 text-grey-7 mb-4')
                ui.button('Create Company', icon='add').props('color=primary')
        else:
            # Companies grid
            with ui.grid(columns=3).classes('w-full gap-4'):
                for company in companies:
                    with ui.card().classes('w-full'):
                        with ui.card_section():
                            ui.label(company.name).classes('text-h6 font-weight-bold mb-2')
                            if company.industry:
                                ui.label(f'Industry: {company.industry}').classes('text-body2 text-grey-7')
                            if company.size:
                                ui.label(f'Size: {company.size}').classes('text-body2 text-grey-7')
                            
                            with ui.row().classes('mt-4 gap-2'):
                                ui.button('View', icon='visibility').props('size=sm outline')
                                ui.button('Edit', icon='edit').props('size=sm outline')
                                ui.button('Delete', icon='delete').props('size=sm outline color=negative')