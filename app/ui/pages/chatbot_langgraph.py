"""Chatbot page for ESG AI assistant with structured interface."""

from nicegui import ui
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import asyncio

from .base_page import BasePage
from app.services.chatbot.langgraph.esg_chatbot import ESGReportChatbot

import logging
logger = logging.getLogger(__name__)

class ChatbotPage(BasePage):
    """Structured ESG AI assistant page with guided interface."""
    
    def __init__(self):
        super().__init__()
        self.chatbot = None
        self.session_id = None
        self.messages = []
        self.current_step = "intent"
        self.selected_options = {}
    
    async def render(self, db_session: Session, company_id: Optional[int] = None) -> None:
        """Render structured chatbot page."""
        await super().render(db_session, company_id)
        
        ui.label('ESG AI Assistant').classes('text-h3 font-weight-bold mb-4')
        
        # Initialize chatbot
        self.chatbot = ESGReportChatbot(db_session, company_id)
        if not self.session_id:
            self.session_id = self.chatbot.create_session()
        
        # Main layout
        with ui.row().classes('w-full gap-6'):
            # Left side - Guided Selection
            with ui.card().classes('w-1/3 p-4'):
                ui.label('What would you like to do?').classes('text-h6 font-weight-bold mb-4')
                self._render_intent_selection()
            
            # Right side - Chat Results
            with ui.card().classes('w-2/3 p-4'):
                ui.label('Results').classes('text-h6 font-weight-bold mb-4')
                with ui.scroll_area().classes('h-96 w-full border rounded p-4') as self.results_area:
                    self._show_welcome_message()
    
    def _render_intent_selection(self) -> None:
        """Render intent selection interface."""
        
        # Step 1: Intent Selection
        with ui.expansion('1. Select Action', icon='psychology').classes('w-full mb-4'):
            with ui.column().classes('w-full gap-2'):
                intent_options = {
                    'data_query': '📊 View ESG Data',
                    'analysis_request': '📈 Analyze Trends',
                    'report_generation': '📋 Generate Report',
                    'data_gaps': '🔍 Find Data Gaps',
                    'benchmarking': '⚖️ Compare Performance'
                }
                
                self.intent_select = ui.select(
                    options=intent_options,
                    label='Choose what you want to do',
                    on_change=self._on_intent_change
                ).classes('w-full')
        
        # Step 2: Category Selection (shown based on intent)
        with ui.expansion('2. Select ESG Category', icon='eco').classes('w-full mb-4') as self.category_expansion:
            with ui.column().classes('w-full gap-2'):
                category_options = {
                    'environmental': '🌱 Environmental (E)',
                    'social': '👥 Social (S)', 
                    'governance': '🏢 Governance (G)',
                    'all': '📊 All Categories'
                }
                
                self.category_select = ui.select(
                    options=category_options,
                    label='Choose ESG category',
                    on_change=self._on_category_change
                ).classes('w-full')
        
        # Step 3: Specific Options (shown based on intent + category)
        with ui.expansion('3. Specify Details', icon='tune').classes('w-full mb-4') as self.details_expansion:
            self.details_container = ui.column().classes('w-full gap-2')
        
        # Step 4: Time Period Selection
        with ui.expansion('4. Select Time Period', icon='schedule').classes('w-full mb-4') as self.period_expansion:
            with ui.column().classes('w-full gap-2'):
                period_options = {
                    'current_year': '📅 Current Year (2025)',
                    'last_year': '📅 Last Year (2024)',
                    'last_3_years': '📅 Last 3 Years',
                    'all_time': '📅 All Available Data'
                }
                
                self.period_select = ui.select(
                    options=period_options,
                    label='Choose time period',
                    on_change=self._on_period_change
                ).classes('w-full')
        
        # Execute Button
        with ui.row().classes('w-full justify-center mt-6'):
            self.execute_button = ui.button(
                'Execute Request',
                icon='play_arrow',
                on_click=self._execute_request
            ).props('size=lg color=primary').classes('w-full')
            self.execute_button.disable()
        
        # Quick Actions
        ui.separator().classes('my-6')
        ui.label('Quick Actions').classes('text-subtitle1 font-weight-bold mb-3')
        
        quick_actions = [
            ('📋 Quick Report', 'Generate basic ESG report', self._quick_report),
            ('📊 Current Status', 'Show current ESG status', self._quick_status),
            ('❓ Data Health Check', 'Check data completeness', self._quick_health_check)
        ]
        
        for label, tooltip, action in quick_actions:
            ui.button(label, on_click=action).classes('w-full mb-2').tooltip(tooltip)
    
    def _on_intent_change(self, e) -> None:
        """Handle intent selection change."""
        intent = e.value
        if not intent:
            return
            
        self.selected_options['intent'] = intent
        self.category_expansion.open()
        
        # Update details based on intent
        self._update_details_options()
        self._check_form_completeness()
    
    def _on_category_change(self, e) -> None:
        """Handle category selection change."""
        category = e.value
        if not category:
            return
            
        self.selected_options['category'] = category
        self.details_expansion.open()
        self._update_details_options()
        self._check_form_completeness()
    
    def _on_period_change(self, e) -> None:
        """Handle period selection change."""
        period = e.value
        if not period:
            return
            
        self.selected_options['period'] = period
        self._check_form_completeness()
    
    def _update_details_options(self) -> None:
        """Update detail options based on intent and category."""
        intent = self.selected_options.get('intent')
        category = self.selected_options.get('category')
        
        self.details_container.clear()
        
        if intent == 'report_generation':
            report_types = {
                'summary': '📄 Summary Report',
                'detailed': '📰 Detailed Report',
                'compliance': '✅ Compliance Report',
                'improvement': '🎯 Improvement Plan'
            }
            self.detail_select = ui.select(
                options=report_types,
                label='Select report type',
                on_change=self._on_detail_change
            ).classes('w-full')
            
        elif intent == 'analysis_request':
            analysis_types = {
                'trends': '📈 Trend Analysis',
                'performance': '🎯 Performance Analysis',
                'comparison': '⚖️ Year-over-Year Comparison',
                'correlation': '🔗 Cross-Category Correlation'
            }
            self.detail_select = ui.select(
                options=analysis_types,
                label='Select analysis type',
                on_change=self._on_detail_change
            ).classes('w-full')
            
        elif intent == 'data_query':
            if category != 'all':
                # Show specific metrics for the category
                metrics = self._get_category_metrics(category)
                self.detail_select = ui.select(
                    options=metrics,
                    label='Select specific metrics',
                    multiple=True,
                    on_change=self._on_detail_change
                ).classes('w-full')
        
        self.period_expansion.open()
    
    def _get_category_metrics(self, category: str) -> Dict[str, str]:
        """Get metrics for a specific category."""
        metrics_map = {
            'environmental': {
                'energy_consumption': '⚡ Energy Consumption',
                'ghg_emissions': '🌫️ GHG Emissions',
                'water_usage': '💧 Water Usage',
                'waste_generation': '🗑️ Waste Generation',
                'renewable_energy': '🔋 Renewable Energy'
            },
            'social': {
                'employee_diversity': '👥 Employee Diversity',
                'safety_incidents': '🦺 Safety Incidents',
                'training_hours': '📚 Training Hours',
                'community_investment': '🤝 Community Investment',
                'customer_satisfaction': '😊 Customer Satisfaction'
            },
            'governance': {
                'board_composition': '🏛️ Board Composition',
                'ethics_violations': '⚖️ Ethics Violations',
                'data_privacy': '🔒 Data Privacy',
                'compliance_score': '✅ Compliance Score',
                'transparency_index': '📊 Transparency Index'
            }
        }
        return metrics_map.get(category, {})
    
    def _on_detail_change(self, e) -> None:
        """Handle detail selection change."""
        detail = e.value
        self.selected_options['detail'] = detail
        self._check_form_completeness()
    
    def _check_form_completeness(self) -> None:
        """Check if form is complete and enable/disable execute button."""
        required_fields = ['intent', 'category', 'period']
        
        # Some intents require detail selection
        if self.selected_options.get('intent') in ['report_generation', 'analysis_request']:
            required_fields.append('detail')
        
        is_complete = all(field in self.selected_options for field in required_fields)
        
        if is_complete:
            self.execute_button.enable()
            self.execute_button.props('color=primary')
        else:
            self.execute_button.disable()
            self.execute_button.props('color=grey')
    
    async def _execute_request(self) -> None:
        """Execute the structured request."""
        if not self.selected_options.get('intent'):
            ui.notify('Please select an action first', type='warning')
            return
        
        # Build structured query
        query = self._build_structured_query()
        
        # Show processing message
        with self.results_area:
            ui.separator().classes('my-4')
            with ui.row().classes('items-center gap-2 mb-4'):
                ui.spinner('dots', size='sm', color='primary')
                ui.label('Processing your request...').classes('text-body2')
        
        # Execute with chatbot
        try:
            await self._stream_ai_response(query)
        except Exception as e:
            with self.results_area:
                ui.label(f'Error: {str(e)}').classes('text-negative')
    
    def _build_structured_query(self) -> str:
        """Build structured query from selections."""
        intent = self.selected_options.get('intent')
        category = self.selected_options.get('category', 'all')
        detail = self.selected_options.get('detail')
        period = self.selected_options.get('period', 'current_year')
        
        query_templates = {
            'data_query': f"Show me {category} ESG data for {period}",
            'analysis_request': f"Analyze {category} ESG {detail} trends for {period}",
            'report_generation': f"Generate a {detail} ESG report for {category} covering {period}",
            'data_gaps': f"Identify data gaps in {category} ESG metrics for {period}",
            'benchmarking': f"Compare our {category} ESG performance for {period}"
        }
        
        base_query = query_templates.get(intent, f"Help with {intent}")
        
        if detail and intent in ['data_query']:
            base_query += f" specifically focusing on {detail}"
        
        return base_query
    
    async def _stream_ai_response(self, query: str) -> None:
        """Stream AI response."""
        response_container = ui.column().classes('w-full')
        
        with self.results_area:
            with response_container:
                with ui.row().classes('items-start gap-3 mb-4'):
                    ui.avatar(icon='smart_toy', color='primary')
                    with ui.column():
                        ui.label('AI Assistant').classes('font-weight-bold text-sm')
                        response_label = ui.label('').classes('text-body2')
        
        # Stream response
        full_response = ""
        async for chunk in self.chatbot.stream_response(query, self.session_id):
            full_response += chunk
            response_label.text = full_response
            await asyncio.sleep(0.05)
        
        self.results_area.scroll_to(percent=1)
    
    # Quick action methods
    async def _quick_report(self) -> None:
        """Generate quick report."""
        self.selected_options = {
            'intent': 'report_generation',
            'category': 'all',
            'detail': 'summary',
            'period': 'current_year'
        }
        await self._execute_request()
    
    async def _quick_status(self) -> None:
        """Show quick status."""
        self.selected_options = {
            'intent': 'data_query',
            'category': 'all',
            'period': 'current_year'
        }
        await self._execute_request()
    
    async def _quick_health_check(self) -> None:
        """Perform quick health check."""
        self.selected_options = {
            'intent': 'data_gaps',
            'category': 'all',
            'period': 'current_year'
        }
        await self._execute_request()
    
    def _show_welcome_message(self) -> None:
        """Show welcome message."""
        with ui.row().classes('items-start gap-3 mb-4'):
            ui.avatar(icon='smart_toy', color='primary')
            with ui.column():
                ui.label('AI Assistant').classes('font-weight-bold text-sm')
                ui.label('Welcome! Please use the guided interface on the left to specify exactly what you need. I can help you with ESG data analysis, trend analysis, and report generation.').classes('text-body2')
