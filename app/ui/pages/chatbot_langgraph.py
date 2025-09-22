"""Chatbot page for ESG AI assistant with structured interface."""

import json
from pathlib import Path
from nicegui import ui
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import asyncio

from .base_page import BasePage
from app.services.chatbot.langgraph.esg_chatbot import ESGReportChatbot
from app.ui.actions.report_download import generate_esg_pdf

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

    async def render(
        self, db_session: Session, cmp_num: Optional[int] = None
    ) -> None:
        """Render structured chatbot page."""
        await super().render(db_session, cmp_num)
        self.db = db_session
        self.cmp_num = cmp_num or "6182618882"

        ui.label("🤖 ESG AI 챗봇").classes("text-4xl font-extrabold mb-6 text-black")


        # Initialize chatbot
        self.chatbot = ESGReportChatbot(db_session, cmp_num)
        if not self.session_id:
            self.session_id = self.chatbot.create_session()

        # Main layout
        with ui.row().classes("w-full gap-6"):
            # Left side - Guided Selection
            with ui.card().classes("w-1/2 p-4"):
                ui.label("어떤 작업을 도와드릴까요?").classes(
                    "text-h6 font-weight-bold mb-4"
                )
                self._render_intent_selection()

            # Right side - Chat Results
            with ui.card().classes("w-1/2 p-4"):
                ui.label("Results").classes("text-h6 font-weight-bold mb-4")
                with ui.scroll_area().classes(
                    "h-96 w-full border rounded p-4"
                ) as self.results_area:
                    self._show_welcome_message()

    def _render_intent_selection(self) -> None:
        """Render intent selection interface."""

        # Step 1: Intent Selection
        with ui.expansion("1. Select Action", icon="psychology").classes("w-full mb-4"):
            with ui.column().classes("w-full gap-2"):
                intent_options = {
                    "data_query": "📊 View ESG Data",
                    "analysis_request": "📈 Analyze Trends",
                    "report_generation": "📋 Generate Report",
                    "data_gaps": "🔍 Find Data Gaps",
                    "benchmarking": "⚖️ Compare Performance",
                }

                self.intent_select = ui.select(
                    options=intent_options,
                    label="Choose what you want to do",
                    on_change=self._on_intent_change,
                ).classes("w-full")

        # Step 2: Category Selection (shown based on intent)
        with ui.expansion("2. Select ESG Category", icon="eco").classes(
            "w-full mb-4"
        ) as self.category_expansion:
            with ui.column().classes("w-full gap-2"):
                category_options = {
                    "all": "📊 All Categories",
                    "environmental": "🌱 Environmental (E)",
                    "social": "👥 Social (S)",
                    "governance": "🏢 Governance (G)",
                }

                self.category_select = ui.select(
                    options=category_options,
                    label="ESG 카테고리 선택",
                    on_change=self._on_category_change,
                ).classes("w-full")

        # Step 3: Time Period Selection
        with ui.expansion("3. Select Time Period", icon="schedule").classes(
            "w-full mb-4"
        ) as self.period_expansion:
            with ui.column().classes("w-full gap-2"):
                period_options = {
                    "current_year": "📅 Current Year (2025)",
                    "last_year": "📅 Previous Year (2024)",
                    "last_3_years": "📅 Last 3 Years",
                    "all_time": "📅 All Available Data",
                }

                self.period_select = ui.select(
                    options=period_options,
                    label="Choose time period",
                    on_change=self._on_period_change,
                ).classes("w-full")

        # Execute Button
        with ui.row().classes("w-full justify-center mt-6"):
            self.execute_button = (
                ui.button(
                    "Execute Request", icon="play_arrow", on_click=self._execute_request
                )
                .props("size=lg color=primary")
                .classes("w-full")
            )
            self.execute_button.disable()

        # Quick Actions
        ui.separator().classes("my-6")
        ui.label("Quick Actions").classes("text-subtitle1 font-weight-bold mb-3")

        quick_actions = [
            ("📋 Quick Report", "Generate basic ESG report", self._quick_report),
            ("📊 Current Status", "Show current ESG status", self._quick_status),
            (
                "❓ Data Health Check",
                "Check data completeness",
                self._quick_health_check,
            ),
        ]

        for label, tooltip, action in quick_actions:
            ui.button(label, on_click=action).classes("w-full mb-2").tooltip(tooltip)

    def _on_intent_change(self, e) -> None:
        """Handle intent selection change."""
        intent = e.value
        if not intent:
            return

        self.selected_options["intent"] = intent
        self.category_expansion.open()

        # Update details based on intent
        self._update_details_options()
        self._check_form_completeness()

    def _on_category_change(self, e) -> None:
        """Handle category selection change."""
        category = e.value
        if not category:
            return

        self.selected_options["category"] = category
        # self.details_expansion.open()
        self._update_details_options()
        self._check_form_completeness()

    def _on_period_change(self, e) -> None:
        """Handle period selection change."""
        period = e.value
        if not period:
            return

        self.selected_options["period"] = period
        self._check_form_completeness()

    def _update_details_options(self) -> None:
        """Update detail options based on intent and category."""
        intent = self.selected_options.get("intent")
        category = self.selected_options.get("category")

        # self.details_container.clear()

        # if intent == "report_generation":
        #     report_types = {
        #         "summary": "📄 Summary Report",
        #         "detailed": "📰 Detailed Report",
        #         "compliance": "✅ Compliance Report",
        #         "improvement": "🎯 Improvement Plan",
        #     }
        #     self.detail_select = ui.select(
        #         options=report_types,
        #         label="Select report type",
        #         on_change=self._on_detail_change,
        #     ).classes("w-full")

        # elif intent == "analysis_request":
        #     analysis_types = {
        #         "trends": "📈 Trend Analysis",
        #         "performance": "🎯 Performance Analysis",
        #         "comparison": "⚖️ Year-over-Year Comparison",
        #         "correlation": "🔗 Cross-Category Correlation",
        #     }
        #     self.detail_select = ui.select(
        #         options=analysis_types,
        #         label="Select analysis type",
        #         on_change=self._on_detail_change,
        #     ).classes("w-full")

        # elif intent == "data_query":
        #     if category != "all":
        #         # Show specific metrics for the category
        #         metrics = self._get_category_metrics(category)
        #         self.detail_select = ui.select(
        #             options=metrics,
        #             label="Select specific metrics",
        #             multiple=True,
        #             on_change=self._on_detail_change,
        #         ).classes("w-full")

        self.period_expansion.open()

    def _get_category_metrics(self, category: str) -> Dict[str, str]:
        """Get metrics for a specific category."""
        metrics_map = {
            "environmental": {
                "energy_consumption": "⚡ Energy Consumption",
                "ghg_emissions": "🌫️ GHG Emissions",
                "water_usage": "💧 Water Usage",
                "waste_generation": "🗑️ Waste Generation",
                "renewable_energy": "🔋 Renewable Energy",
            },
            "social": {
                "employee_diversity": "👥 Employee Diversity",
                "safety_incidents": "🦺 Safety Incidents",
                "training_hours": "📚 Training Hours",
                "community_investment": "🤝 Community Investment",
                "customer_satisfaction": "😊 Customer Satisfaction",
            },
            "governance": {
                "board_composition": "🏛️ Board Composition",
                "ethics_violations": "⚖️ Ethics Violations",
                "data_privacy": "🔒 Data Privacy",
                "compliance_score": "✅ Compliance Score",
                "transparency_index": "📊 Transparency Index",
            },
        }
        return metrics_map.get(category, {})

    def _on_detail_change(self, e) -> None:
        """Handle detail selection change."""
        detail = e.value
        self.selected_options["detail"] = detail
        self._check_form_completeness()

    def _check_form_completeness(self) -> None:
        """Check if form is complete and enable/disable execute button."""
        required_fields = ["intent", "category", "period"]

        # # Some intents require detail selection
        # if self.selected_options.get("intent") in [
        #     "report_generation",
        #     "analysis_request",
        # ]:
        #     required_fields.append("detail")

        is_complete = all(field in self.selected_options for field in required_fields)
        
        # print("Current selected_options:", self.selected_options)

        if is_complete:
            self.execute_button.enable()
            self.execute_button.props("color=primary")
        else:
            self.execute_button.disable()
            self.execute_button.props("color=grey")

    async def _execute_request(self) -> None:
        """Execute the structured request."""
        if not self.selected_options.get("intent"):
            ui.notify("Please select an action first", type="warning")
            return

        # Build structured query
        query = self._build_structured_query()

        # Show processing message
        # with self.results_area:
        #     ui.separator().classes("my-4")
        #     with ui.row().classes("items-center gap-2 mb-4"):
        #         ui.spinner("dots", size="sm", color="primary")
        #         ui.label("Processing your request...").classes("text-body2")

        # Execute with chatbot
        try:
            await self._stream_ai_response(query, context=self.selected_options)
        except Exception as e:
            with self.results_area:
                ui.label(f"Error: {str(e)}").classes("text-negative")

    def _build_structured_query(self) -> str:
        """Build structured query from selections."""
        intent = self.selected_options.get("intent")
        category = self.selected_options.get("category", "all")
        # detail = self.selected_options.get("detail")
        period = self.selected_options.get("period", "current_year")

        query_templates = {
            "data_query": f"Show me {category} ESG data for {period}",
            "analysis_request": f"Analyze {category} ESG trends for {period}",
            "report_generation": f"Generate a ESG report for {category} covering {period}",
            "data_gaps": f"Identify data gaps in {category} ESG metrics for {period}",
            "benchmarking": f"Compare our {category} ESG performance for {period}",
        }

        base_query = query_templates.get(intent, f"Help with {intent}")

        # if detail and intent in ["data_query"]:
        #     base_query += f" specifically focusing on {detail}"

        return base_query

    async def _stream_ai_response(self, query: str, context: dict) -> None:
        """AI 응답을 스트리밍하고 보고서 생성을 처리합니다."""
        # 공통: AI 응답을 표시할 UI 컨테이너 구성
        with self.results_area:
            ui.separator().classes("my-2")
            with ui.row().classes("items-start gap-3 mb-2"):
                ui.avatar(icon="smart_toy", color="primary")
                with ui.column():
                    ui.label("AI Assistant").classes("font-weight-bold text-sm")
                    # 이 컨테이너는 보고서 생성 결과 또는 스트리밍 텍스트를 담습니다.
                    response_container = ui.column()

        # 분기: '보고서 생성' 인텐트일 경우와 아닐 경우
        if self.selected_options.get("intent") == "report_generation":
            # 별도의 비동기 함수를 호출하여 보고서 생성 처리
            with response_container:
                with ui.row(align_items='center'):
                    ui.spinner(color='primary')
                    ui.label("보고서를 생성하고 있습니다. 잠시만 기다려 주세요...").classes("text-body2")
            await self._handle_report_generation(query, response_container, context)
        else:
            # 일반 텍스트 응답 스트리밍
            with response_container:
                response_label = ui.label("").classes("text-body2")
            
            full_response = ""
            try:
                # 챗봇의 스트리밍 응답을 받아 UI에 표시
                async for chunk in self.chatbot.stream_response(query, self.session_id):
                    full_response += chunk
                    response_label.text = full_response
                    await asyncio.sleep(0.01) # UI 업데이트를 위한 짧은 대기
            except Exception as e:
                response_label.text = f"스트리밍 중 오류가 발생했습니다: {e}"

    async def _handle_report_generation(self, query: str, container: ui.column, context: dict) -> None:
        try:
            # 1) 보고서 직접 생성(LLM 스트리밍 우회): 도구를 dict로 호출
            report_type = "comprehensive" if context.get("category") in (None, "all") else "category_specific"
            gen_res_raw = await self.chatbot.tools[3].arun({"cmp_num": self.cmp_num, "report_type": report_type})
            gen_res = json.loads(gen_res_raw)

            if gen_res.get("status") != "success":
                raise RuntimeError(f"보고서 생성 실패: {gen_res.get('message')}")

            report_id = gen_res.get("report_id")
            if not report_id:
                raise RuntimeError("보고서 ID를 받지 못했습니다.")

            # 2) 받은 report_id로 바로 PDF 내보내기
            pdf_path = self.chatbot.export_report_to_pdf(report_id=report_id)

            container.clear()
            with container:
                if pdf_path:
                    self._last_report_path = pdf_path
                    report_title = Path(pdf_path).name.replace(".pdf", "").replace("_", " ")
                    ui.label("✅ 보고서 생성이 완료되었습니다.").classes("text-body2 text-positive")
                    ui.label(f"보고서명: {report_title}").classes("text-caption text-grey")
                    ui.button("⬇️ PDF 다운로드", on_click=self._download_pdf).props("color=primary")
                else:
                    ui.label("⚠️ 보고서를 생성했지만 PDF 파일 경로를 얻지 못했습니다.").classes("text-warning")
        except Exception as e:
            logger.error(f"보고서 생성 실패: {e}", exc_info=True)
            container.clear()
            with container:
                ui.label(f"❌ 보고서 생성에 실패했습니다: {e}").classes("text-negative")

    def _download_pdf(self) -> None:
        """생성된 PDF 파일을 다운로드합니다."""
        if self._last_report_path and Path(self._last_report_path).exists():
            ui.download(self._last_report_path)
        else:
            ui.notify("다운로드할 보고서 파일을 찾을 수 없습니다.", color="negative")

    # async def _stream_ai_response(self, query: str) -> None:
    #     """Stream AI response."""
    #     # 공통: results_area 안에 'AI Assistant' 말풍선 컨테이너 구성
    #     with self.results_area:
    #         container = ui.column().classes("w-full")
    #         with container:
    #             ui.separator().classes("my-2")
    #             with ui.row().classes("items-start gap-3 mb-2"):
    #                 ui.avatar(icon="smart_toy", color="primary")
    #                 with ui.column():
    #                     ui.label("AI Assistant").classes("font-weight-bold text-sm")
    #                     # 스트리밍일 때만 활용되는 라벨(보고서 생성일 때는 별도 메시지 사용)
    #                     response_label = ui.label("").classes("text-body2")

    #     # 분기: 보고서 생성 vs 일반 답변
    #     if self.selected_options.get("intent") == "report_generation":
    #         # 예: 보고서 생성 로직 (동기/비동기 여부에 맞게 호출)
    #         # 반환값은 예시 — 실제 너의 구현에 맞게 바꿔줘
    #         try:
    #             # 실제 보고서 생성 (예: self.chatbot.generate_report(...) 또는 내부 함수)
    #             # report_info = await self.chatbot.generate_report(query, self.session_id)
    #             # self._last_report_path = report_info.file_path
    #             # self._last_report_summary = report_info.summary

    #             # 데모용: 생성 완료 메시지
    #             self._last_report_path = "/tmp/report.pdf"  # _download_pdf에서 사용
    #             self._last_report_summary = "ESG Report for 2024 (HQ)"

    #             with self.results_area:
    #                 ui.label("Report ready. You can download a PDF version.").classes("text-body2")
    #                 ui.label(self._last_report_summary).classes("text-caption text-grey")
    #                 ui.button("⬇️ Download PDF", on_click=self._download_pdf).props("color=primary")
    #         except Exception as e:
    #             with self.results_area:
    #                 ui.separator().classes("my-2")
    #                 ui.label(f"Report generation failed: {e}").classes("text-negative")
    #     else:
    #         # 일반 답변 스트리밍
    #         full_response = ""
    #         try:
    #             async for chunk in self.chatbot.stream_response(query, self.session_id):
    #                 full_response += chunk
    #                 response_label.text = full_response
    #                 await asyncio.sleep(0.02)
    #         except Exception as e:
    #             response_label.text = f"(stream error) {e}"

    #     # 끝으로 스크롤 다운
    #     self.results_area.scroll_to(percent=1)

    # async def _download_pdf(self) -> None:
    #     try:
    #         # PDF 생성 (서비스 호출)
    #         pdf_path = await generate_esg_pdf(self.db, cmp_num=self.cmp_num, options=self.selected_options)
    #         # NiceGUI 다운로드
    #         ui.download(pdf_path)
    #     except Exception as e:
    #         ui.notify(f"PDF 생성 중 오류: {e}", type='negative')



    # Quick action methods
    async def _quick_report(self) -> None:
        """Generate quick report."""
        self.selected_options = {
            "intent": "report_generation",
            "category": "all",
            "detail": "summary",
            "period": "current_year",
        }
        await self._execute_request()

    async def _quick_status(self) -> None:
        """Show quick status."""
        self.selected_options = {
            "intent": "data_query",
            "category": "all",
            "period": "current_year",
        }
        await self._execute_request()

    async def _quick_health_check(self) -> None:
        """Perform quick health check."""
        self.selected_options = {
            "intent": "data_gaps",
            "category": "all",
            "period": "current_year",
        }
        await self._execute_request()

    def _show_welcome_message(self) -> None:
        """Show welcome message."""
        with ui.row().classes("items-start gap-3 mb-4"):
            ui.avatar(icon="smart_toy", color="primary")
            with ui.column():
                ui.label("AI Assistant").classes("font-weight-bold text-sm")
                ui.label(
                    "Welcome! Please use the guided interface on the left to specify exactly what you need. I can help you with ESG data analysis, trend analysis, and report generation."
                ).classes("text-body2")
