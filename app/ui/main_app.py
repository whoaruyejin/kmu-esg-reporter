"""Main NiceGUI application for ESG Reporter."""

from nicegui import ui, app
from typing import Dict, Any, Optional
import asyncio
import logging
from pathlib import Path

from config.settings import settings
from app.core.database import init_db, get_db

# Import pages with error handling
try:
    from app.ui.pages import (
        DashboardPage, 
        DataInputPage, 
        VisualizationPage, 
        ChatbotPage,
        CompanyManagementPage
    )
except ImportError as e:
    logging.error(f"Error importing pages: {e}")
    # Create dummy pages for development
    class DummyPage:
        async def render(self, db_session, company_id=None):
            ui.label('Page not implemented yet')
    
    DashboardPage = DummyPage
    DataInputPage = DummyPage
    VisualizationPage = DummyPage
    ChatbotPage = DummyPage
    CompanyManagementPage = DummyPage

logger = logging.getLogger(__name__)


class ESGReporterApp:
    """Main ESG Reporter Application class."""
    def __init__(self):
        self.erp_open = True  # ERP 메뉴 항상 열림 상태
        self.current_company_id: Optional[int] = None
        self.current_page = "dashboard"
        self.db_session = None

        # Initialize database
        init_db()


        # Initialize pages
        from app.ui.pages import HRPage, EnvironmentPage
        self.pages = {
            'dashboard': DashboardPage(),
            'data_input': DataInputPage(),
            # 'visualization': VisualizationPage(),
            'chatbot': ChatbotPage(),
            'company_management': CompanyManagementPage(),
            'hr': HRPage(),
            'environment': EnvironmentPage(),
        }
    
    def setup_app(self) -> None:
        ui.label('ESG Reporter').classes('text-h5 font-weight-bold')
            
        with ui.row().classes('items-center gap-4'):
            # User menu
            with ui.button(icon='account_circle').props('flat round'):
                with ui.menu():
                    """Setup navigation menu."""
            nav_items = [
                {'icon': 'dashboard', 'label': 'Dashboard', 'page': 'dashboard'},
                    # ERP 확장 메뉴는 별도 처리
                {'icon': 'chat', 'label': 'AI Chatbot', 'page': 'chatbot'},
                ]

        # Dashboard
        with ui.item(on_click=lambda: self._navigate_to('dashboard')):
                with ui.item_section():
                    ui.icon('dashboard')
                with ui.item_section():
                    ui.item_label('Dashboard')

        # ERP 확장(expansion) 메뉴 (회사관리, HR, 환경관리 세로 표기, 항상 열림)
        with ui.expansion('ERP', icon='input', value=self.erp_open, on_value_change=lambda e: setattr(self, 'erp_open', e.value)).classes('q-pa-none') as erp_expansion:
            with ui.list().classes('q-pa-none'):
                with ui.item(on_click=lambda: (self._navigate_to('company_management'), setattr(self, 'erp_open', True))):
                    with ui.item_section():
                        ui.icon('business')
                    with ui.item_section():
                        ui.item_label('회사관리').classes('whitespace-nowrap')
                with ui.item(on_click=lambda: (self._navigate_to('hr'), setattr(self, 'erp_open', True))):
                    with ui.item_section():
                        ui.icon('people')
                    with ui.item_section():
                        ui.item_label('HR')
                with ui.item(on_click=lambda: (self._navigate_to('environment'), setattr(self, 'erp_open', True))):
                    with ui.item_section():
                        ui.icon('eco')
                    with ui.item_section():
                        ui.item_label('환경관리').classes('whitespace-nowrap')

        # 나머지 메뉴
        for item in nav_items:
            if item['label'] not in ['Dashboard']:
                with ui.item(on_click=lambda page=item['page']: self._navigate_to(page)):
                    with ui.item_section():
                        ui.icon(item['icon'])
                    with ui.item_section():
                        if item['label'] == 'AI Chatbot':
                            ui.item_label(item['label']).classes('whitespace-nowrap')
                        else:
                            ui.item_label(item['label'])
    
    def _setup_routing(self) -> None:
        """Setup page routing."""
        async def visualization():
            self._setup_layout()
            await self._load_page('visualization')
        

        @ui.page('/chatbot')
        async def chatbot():
            self._setup_layout()
            await self._load_page('chatbot')
        
        # @ui.page('/companies')
        # async def companies():
        #     self._setup_layout()
        #     await self._load_page('company_management')

        @ui.page('/hr')
        async def hr():
            self._setup_layout()
            await self._load_page('hr')

        @ui.page('/environment')
        async def environment():
            self._setup_layout()
            await self._load_page('environment')

        @ui.page('/company-management')
        async def company_management():
            self._setup_layout()
            await self._load_page('company_management')