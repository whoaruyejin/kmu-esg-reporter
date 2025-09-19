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
        self.current_company_id: Optional[int] = None
        self.current_page = "dashboard"
        self.db_session = None
        
        # Initialize database
        init_db()
        
        # Initialize pages
        self.pages = {
            'dashboard': DashboardPage(),
            'data_input': DataInputPage(),
            'visualization': VisualizationPage(),
            'chatbot': ChatbotPage(),
            'company_management': CompanyManagementPage()
        }
    
    def setup_app(self) -> None:
        """Setup the main application."""
        # Set app configuration
        app.add_static_files('/static', str(Path(__file__).parent.parent.parent / 'static'))
        ui.run_with.fast_reload = settings.app.DEBUG
        
        # Setup main layout
        # self._setup_layout()
        
        # Setup routing
        self._setup_routing()
    
    def _setup_layout(self) -> None:
        """Setup main application layout."""
        # Header
        with ui.header(elevated=True).classes('items-center justify-between'):
            with ui.row().classes('items-center'):
                ui.icon('eco', size='2rem').classes('text-green')
                ui.label('ESG Reporter').classes('text-h5 font-weight-bold')
            
            with ui.row().classes('items-center gap-4'):
                # Company selector
                self.company_select = ui.select(
                    options={},
                    label='Select Company',
                    on_change=self._on_company_change
                ).classes('w-48')
                
                # User menu
                with ui.button(icon='account_circle').props('flat round'):
                    with ui.menu():
                        ui.menu_item('Profile', lambda: ui.notify('Profile clicked'))
                        ui.menu_item('Settings', lambda: ui.notify('Settings clicked'))
                        ui.separator()
                        ui.menu_item('Logout', lambda: ui.notify('Logout clicked'))
        
        # Navigation drawer
        with ui.left_drawer().classes('bg-blue-grey-1') as self.drawer:
            self._setup_navigation()
        
        # Main content area
        self.content_container = ui.column().classes('w-full h-full p-4')
        
        # Footer
        with ui.footer().classes('bg-blue-grey-1'):
            ui.label(f'{settings.app.APP_NAME} v{settings.app.APP_VERSION}').classes('text-caption')
    
    def _setup_navigation(self) -> None:
        """Setup navigation menu."""
        nav_items = [
            {'icon': 'dashboard', 'label': 'Dashboard', 'page': 'dashboard'},
            {'icon': 'input', 'label': 'Data Input', 'page': 'data_input'},
            {'icon': 'analytics', 'label': 'Visualization', 'page': 'visualization'},
            {'icon': 'chat', 'label': 'AI Chatbot', 'page': 'chatbot'},
            {'icon': 'business', 'label': 'Companies', 'page': 'company_management'},
        ]
        
        for item in nav_items:
            with ui.item(on_click=lambda page=item['page']: self._navigate_to(page)):
                with ui.item_section():
                    ui.icon(item['icon'])
                with ui.item_section():
                    ui.item_label(item['label'])
    
    def _setup_routing(self) -> None:
        """Setup page routing."""
        @ui.page('/')
        async def index():
            self._setup_layout()
            await self._load_page('dashboard')
        
        @ui.page('/dashboard')
        async def dashboard():
            await self._load_page('dashboard')
        
        @ui.page('/data-input')
        async def data_input():
            await self._load_page('data_input')
        
        @ui.page('/visualization')
        async def visualization():
            await self._load_page('visualization')
        
        @ui.page('/chatbot')
        async def chatbot():
            await self._load_page('chatbot')
        
        @ui.page('/companies')
        async def companies():
            await self._load_page('company_management')
    
    async def _load_page(self, page_name: str) -> None:
        """Load a specific page."""
        try:
            self.current_page = page_name
            
            # Clear current content
            self.content_container.clear()
            
            # Get database session
            self.db_session = next(get_db())
            
            # Load page content
            page = self.pages.get(page_name)
            if page:
                with self.content_container:
                    await page.render(self.db_session, self.current_company_id)
            else:
                with self.content_container:
                    ui.label(f'Page "{page_name}" not found').classes('text-h4 text-center')
                    
        except Exception as e:
            logger.error(f"Error loading page {page_name}: {str(e)}")
            with self.content_container:
                ui.label(f'Error loading page: {str(e)}').classes('text-negative')
    
    def _navigate_to(self, page_name: str) -> None:
        """Navigate to a specific page."""
        ui.open(f'/{page_name.replace("_", "-")}')
    
    def _on_company_change(self, e) -> None:
        """Handle company selection change."""
        self.current_company_id = e.value
        
        # Refresh current page with new company context
        asyncio.create_task(self._load_page(self.current_page))
    
    async def refresh_company_list(self) -> None:
        """Refresh the company selection dropdown."""
        try:
            from app.core.database.models import Company
            
            db = next(get_db())
            companies = db.query(Company).all()
            
            options = {company.id: company.name for company in companies}
            self.company_select.options = options
            
            if companies and not self.current_company_id:
                self.current_company_id = companies[0].id
                self.company_select.value = self.current_company_id
                
        except Exception as e:
            logger.error(f"Error refreshing company list: {str(e)}")


def create_app() -> None:
    """Create and configure the NiceGUI application."""
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if settings.app.DEBUG else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create app instance
    esg_app = ESGReporterApp()
    esg_app.setup_app()
    
    # Start the application
    ui.run(
        host=settings.app.HOST,
        port=settings.app.PORT,
        title=settings.app.APP_NAME,
        favicon='🌱',
        show=settings.app.DEBUG,
        reload=settings.app.DEBUG
    )