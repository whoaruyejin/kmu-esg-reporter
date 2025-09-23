"""Chatbot page for ESG AI assistant with structured interface."""

import json
from pathlib import Path
from nicegui import ui
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
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
        self._views: dict[int, dict] = {}
        self._state: dict[int, dict] = {}
        self._sessions: dict[int, str] = {}

    def _get_state(self):
        cid = ui.context.client.id
        if cid not in self._state:
            self._state[cid] = {"selected_options": {}}
        return self._state[cid]["selected_options"]

    def _get_view(self):
        return self._views.get(ui.context.client.id)

    def _get_session_id(self):
        cid = ui.context.client.id
        if cid not in self._sessions:
            self._sessions[cid] = self.chatbot.create_session()
        return self._sessions[cid]

    async def render(
        self, db_session: Session, cmp_num: Optional[int] = None
    ) -> None:
        """Render structured chatbot page."""
        await super().render(db_session, cmp_num)
        self.db = db_session
        self.cmp_num = cmp_num or "6182618882"
        cid = ui.context.client.id

        # Initialize chatbot
        self.chatbot = ESGReportChatbot(db_session, cmp_num)

        self._sessions.setdefault(cid, self.chatbot.create_session())
        self._state.setdefault(cid, {"selected_options": {}})
        s = self._state[cid]["selected_options"]

        ui.label("🤖 ESG AI 챗봇").classes("text-4xl font-extrabold mb-6 text-black")

        # Main layout
        with ui.row().classes("w-full gap-6"):
            # Left side - Guided Selection (처음엔 보임)
            with ui.card().classes("w-[30%] min-w-[300px] p-4 transition-all duration-200") as left_panel:
                with ui.row().classes('w-full items-center justify-between mb-2'):
                    ui.label("필터 선택").classes("text-h6 font-weight-bold")
                    ui.button("필터 접기", icon="chevron_left", on_click=self._toggle_filter_panel) \
                        .props("dense flat").classes("ml-auto")
                ui.separator().classes("my-1")
                intent_select, category_select, period_select, execute_button = self._render_intent_selection()

            # Right side - Chat Results
            with ui.card().classes("w-[70%] flex-1 p-4 transition-all duration-200") as right_panel:
                with ui.row().classes("w-full justify-between items-center mb-2"):
                    ui.label("ESG 챗봇").classes("text-h6 font-weight-bold")
                with ui.scroll_area().classes("h-[70vh] w-full border rounded p-4") as results_area:
                    self._show_welcome_message()

                with ui.row().classes('w-full items-center gap-2 mt-3'):
                    chat_input = ui.input(
                        placeholder='메시지를 입력하세요...'
                    ).props('outlined dense clearable').classes('flex-1')
                    send_btn = ui.button('보내기', icon='send',
                                        on_click=lambda: self._send_free_text(chat_input))\
                                .props('color=primary dense')
                    chat_input.on('keydown.enter', lambda: self._send_free_text(chat_input))

        # 필터 토글 FAB (필터가 닫혔을 때만 보이도록)
        filter_fab = ui.button(icon='tune', on_click=self._toggle_filter_panel) \
            .props('round fab color=primary') \
            .style('position: fixed; right: 24px; bottom: 92px; z-index: 1000;') 
        filter_fab.visible = False

        left_panel.style('width: 340px')
        right_panel.style('width: calc(100% - 340px)')

        self._views[cid] = {
            'left': left_panel,
            'right': right_panel,
            'fab': filter_fab,
            'open': True,
            'results': results_area,
            'intent_select': intent_select,
            'category_select': category_select,
            'period_select': period_select,
            'execute_button': execute_button,
            'chat_input': chat_input,
            'send_btn': send_btn,
        }


    def _apply_filter_state(self, view: dict, open_state: bool) -> None:
        """현재 클라이언트(view)에 필터 열림/닫힘 상태 적용"""
        view['open'] = open_state

        if open_state:
            # 열기
            view['left'].style('display: block')
            view['right'].style('width: calc(100% - 340px)')
            view['fab'].visible = False
        else:
            # 닫기
            view['left'].style('display: none')
            view['right'].style('width: 100%')
            view['fab'].visible = True

        # 즉시 반영
        view['left'].update()
        view['right'].update()
        view['fab'].update()

    def _toggle_filter_panel(self) -> None:
        cid = ui.context.client.id
        view = self._views.get(cid)
        if not view:
            return  # 아직 렌더 전이거나 레퍼런스 없음

        self._apply_filter_state(view, not view.get('open', True))

    def _render_intent_selection(self) -> None:
        """Render intent selection interface."""

        # Step 1: Intent Selection
        with ui.row().classes('w-full items-center justify-between'):
            with ui.row().classes('items-center gap-1'):
                ui.icon('psychology').props('size=lg color=primary')
                ui.label('작업 선택').classes('text-subtitle1 font-bold')

        s = self._get_state()
        intent_options = {
            "data_query": "📊 View ESG Data",
            "analysis_request": "📈 Analyze Trends",
            "report_generation": "📋 Generate Report",
            "benchmarking": "⚖️ Compare Performance",
        }

        intent_select = ui.select(
            options=intent_options,
            label="원하는 작업 선택",
            on_change=self._on_intent_change,
            value=s.get('intent'),
        ).props('dense outlined clearable').classes('w-full mb-2')

        ui.separator().classes('my-1')  # 구분선만 넣어주면 깔끔

        # Step 2: Category Selection  ← expansion 제거
        with ui.row().classes('w-full items-center justify-between'):
            with ui.row().classes('items-center gap-1'):
                ui.icon('category').props('size=lg color=primary')
                ui.label('카테고리').classes('text-subtitle1 font-bold')

        category_options = {
            "all": "📊 All Categories",
            "environmental": "🌱 Environmental (E)",
            "social": "👥 Social (S)",
            "governance": "🏢 Governance (G)",
        }

        category_select = ui.select(
            options=category_options,
            label="ESG 카테고리 선택",
            on_change=self._on_category_change,
            value=s.get("category"),
        ).props('dense outlined clearable').classes("w-full mb-2")

        ui.separator().classes("my-1")

        # Step 3: Time Period Selection  ← expansion 제거
        with ui.row().classes('w-full items-center justify-between'):
            with ui.row().classes('items-center gap-1'):
                ui.icon('calendar_today').props('size=lg color=primary')
                ui.label('기간').classes('text-subtitle1 font-bold')

        period_options = {
            "current_year": "📅 Current Year (2025)",
            "last_year": "📅 Previous Year (2024)",
            "last_3_years": "📅 Last 3 Years",
            "all_time": "📅 All Available Data",
        }

        period_select = ui.select(
            options=period_options,
            label="데이터 기간 선택",
            on_change=self._on_period_change,
            value=s.get("period"),
        ).props('dense outlined clearable').classes("w-full mb-2")

        ui.separator().classes("my-1")

        # Execute Button
        with ui.row().classes("w-full justify-center mt-6"):
            execute_button = ui.button(
                    "요청 실행", icon="play_arrow", on_click=self._execute_request
                ).props("size=lg color=primary").classes("w-full")
            execute_button.disable()

        # Quick Actions
        ui.separator().classes("my-6")
        ui.label("빠른 작업").classes("text-h6 font-weight-bold mb-4")

        quick_actions = [
            ("📋 빠른 보고서", "Generate basic ESG report", self._quick_report),
            ("📊 현재 상태", "Show current ESG status", self._quick_status),
            (
                "❓ 데이터 무결성 체크",
                "Check data completeness",
                self._quick_health_check,
            ),
        ]

        for label, tooltip, action in quick_actions:
            ui.button(label, on_click=action).classes("w-full mb-2").tooltip(tooltip)

        return intent_select, category_select, period_select, execute_button

    def _on_intent_change(self, e) -> None:
        s = self._get_state()
        v = self._get_view()
        if not e.value:
            s.pop('intent', None)
        else:
            s['intent'] = e.value
            # 상위 변경 시 하위 리셋
            s.pop('category', None); s.pop('period', None)
            if v:
                v['category_select'].value = None
                v['period_select'].value = None
        self._check_form_completeness()

    def _on_category_change(self, e) -> None:
        s = self._get_state()
        if not e.value: s.pop('category', None)
        else: s['category'] = e.value
        self._check_form_completeness()


    def _on_period_change(self, e) -> None:
        s = self._get_state()
        if not e.value: s.pop('period', None)
        else: s['period'] = e.value
        self._check_form_completeness()
    
    def _check_form_completeness(self) -> None:
        """Check if form is complete and enable/disable execute button."""
        v = self._get_view()
        if not v: return
        s = self._get_state()
        ready = all(k in s for k in ('intent','category','period'))
        btn = v['execute_button']
        if ready:
            btn.enable(); btn.props('color=primary')
        else:
            btn.disable(); btn.props('color=grey')

    def _set_running_ui(self, running: bool):

        v = self._get_view()
        if not v: return
        widgets = [
            v.get('execute_button'),
            v.get('intent_select'),
            v.get('category_select'),
            v.get('period_select'),
        ]
        for w in widgets:
            if not w: continue
            (w.disable() if running else w.enable())

        if v.get('open', True):
            v['left'].style('width: 320px' if running else 'width: 340px')
            v['right'].style('width: calc(100% - 320px)' if running else 'width: calc(100% - 340px)')
        else:
            v['right'].style('width: 100%')

        v['left'].update(); v['right'].update()

    async def _send_free_text(self, chat_input):
        """우측 자유채팅 인풋에서 엔터/버튼으로 전송"""
        text = (chat_input.value or "").strip()
        if not text:
            ui.notify('메시지를 입력하세요', color='warning'); return

        v = self._get_view()
        if not v or 'results' not in v:
            ui.notify('결과 영역을 찾을 수 없습니다.', color='negative'); return
        session_id = self._get_session_id()
        results_area = v['results']

        # 입력 중복 방지
        v.get('send_btn') and v['send_btn'].disable()
        chat_input.disable()

        # 사용자 말풍선 출력
        with results_area:
            with ui.row().classes("w-full justify-end mb-2"):
                with ui.row().classes("max-w-[75%] items-start gap-2"):
                    with ui.column().classes("items-end"):
                        ui.label("You").classes("font-weight-bold text-xs text-gray-500")
                        ui.label(text)\
                        .classes("text-body2 px-3 py-2 rounded-xl bg-primary text-white shadow")
                    ui.avatar(icon="person", color="grey-6")

            # 어시스턴트 말풍선 컨테이너
            with ui.row().classes("w-full items-start gap-2 mb-3"):
                ui.avatar(icon="smart_toy", color="primary")
                with ui.column().classes("max-w-[75%]"):
                    ui.label("AI Assistant").classes("font-weight-bold text-xs text-gray-500")

                    response_container = ui.column()

        # 스트리밍 응답 (일반 텍스트 분기 로직 재사용)
        with response_container:
            pending_row = ui.row(align_items='center')
            with pending_row:
                ui.spinner(color='primary')
                ui.label("응답을 생성하고 있습니다. 잠시만 기다려 주세요...").classes("text-body2")
            response_label = self._bubble_label("").classes("text-body2")

        full_response = ""
        got_first_chunk = False
        try:
            async for chunk in self.chatbot.stream_response(text, session_id):
                if not got_first_chunk:
                    pending_row.delete()
                    got_first_chunk = True
                full_response += chunk
                response_label.text = full_response
                await asyncio.sleep(0.01)
        except Exception as e:
            try: pending_row.delete()
            except: pass
            response_label.text = f"스트리밍 중 오류가 발생했습니다: {e}"
        finally:
            # 입력창 리셋/활성화
            chat_input.value = ""
            chat_input.enable()
            v.get('send_btn') and v['send_btn'].enable()

    async def _execute_request(self) -> None:
        s = self._get_state()
        if 'intent' not in s:
            ui.notify("Please select an action first", type="warning"); return
        query = self._build_structured_query(s)
        self._set_running_ui(True)
        try:
            await self._stream_ai_response(query, context=s)
        finally:
            self._set_running_ui(False)

    def _build_structured_query(self, s: dict) -> str:
        """Build structured query from selections."""
        intent = s.get("intent")
        category = s.get("category", "all")
        period = s.get("period", "current_year")

        query_templates = {
            "data_query": f"Show me {category} ESG data for {period}",
            "analysis_request": f"Analyze {category} ESG trends for {period}",
            "report_generation": f"Generate a ESG report for {category} covering {period}",
            "data_gaps": f"Identify data gaps in {category} ESG metrics for {period}",
            "benchmarking": f"Compare our {category} ESG performance for {period}",
        }

        base_query = query_templates.get(intent, f"Help with {intent}")

        return base_query

    async def _stream_ai_response(self, query: str, context: dict) -> None:
        """AI 응답을 스트리밍하고 보고서 생성을 처리합니다."""

        v = self._get_view()
        if not v or 'results' not in v:
            ui.notify('결과 영역을 찾을 수 없습니다.', color='negative'); return
        session_id = self._get_session_id()
        results_area = v['results']

        s = self._get_state()

        with results_area:
            with ui.row().classes("w-full items-start gap-2 mb-2"):
                ui.avatar(icon="smart_toy", color="primary")
                with ui.column().classes("max-w-[75%]"):
                    ui.label("AI Assistant").classes("font-weight-bold text-xs text-gray-500")

                    response_container = ui.column()

        # 분기: '보고서 생성' 인텐트일 경우와 아닐 경우
        if s.get("intent") == "report_generation":
            with response_container:
                pending_row = ui.row().classes("items-center gap-2")
                with pending_row:
                    ui.spinner(color='primary')
                    ui.label("보고서를 생성하고 있습니다. 잠시만 기다려 주세요...").classes("text-body2")
            await self._handle_report_generation(query, response_container, context)
        else:
            # 일반 텍스트 응답 스트리밍
            with response_container:
                pending_row = ui.row().classes("items-center gap-2")
                with pending_row:
                    ui.spinner(color='primary')
                    ui.label("응답을 생성하고 있습니다. 잠시만 기다려 주세요...").classes("text-body2")
                response_label = self._bubble_label("").classes("hidden")


            full_response = ""
            got_first_chunk = False
            try:
                async for chunk in self.chatbot.stream_response(query, session_id):
                    if not got_first_chunk:
                        # ⬇️ 첫 청크 도착 시 대기 UI 제거
                        try:
                            pending_row.delete()
                        except:
                            pass
                        response_label.classes(remove='hidden')
                        got_first_chunk = True

                    full_response += chunk
                    response_label.text = full_response
                    await asyncio.sleep(0.01)  # UI 스무딩

            except Exception as e:
                try:
                    pending_row.delete()
                except:
                    pass
                response_label.classes(remove='hidden')
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

    # Quick action methods
    async def _quick_report(self) -> None:
        """Generate quick report."""
        s = self._get_state()
        s.update({
            "intent": "report_generation",
            "category": "all",
            "detail": "summary",
            "period": "current_year",
        })
        await self._execute_request()

    async def _quick_status(self) -> None:
        """Show quick status."""
        s = self._get_state()
        s.update({
            "intent": "data_query",
            "category": "all",
            "period": "current_year",
        })
        await self._execute_request()

    async def _quick_health_check(self) -> None:
        """Perform quick health check."""
        s = self._get_state()
        s.update({
            "intent": "data_gaps",
            "category": "all",
            "period": "current_year",
        })
        await self._execute_request()

    def _bubble_label(self, text: str = ""):
        """회색 말풍선 라벨 생성(컨테이너 안에서 호출)."""
        return ui.label(text)\
            .classes("text-body2 px-3 py-2 rounded-xl bg-gray-100 text-gray-900 shadow")\
            .style('white-space: pre-wrap; word-break: break-word')

    def _user_bubble(self, text: str = ""):
        return ui.label(text)\
            .classes("text-body2 px-3 py-2 rounded-xl bg-blue-50 text-gray-900 shadow")\
            .style('white-space: pre-wrap; word-break: break-word')


    def _show_welcome_message(self) -> None:
        """Show welcome message."""
        with ui.row().classes("w-full items-start gap-2 mb-3"):
            ui.avatar(icon="smart_toy", color="primary")
            with ui.column().classes("max-w-[75%]"):
                ui.label("AI Assistant").classes("font-weight-bold text-xs text-gray-500")
                self._bubble_label(
                    "환영합니다!\n왼쪽의 안내 인터페이스를 사용하여 필요한 정보를 정확히 입력해 주세요.\nESG 데이터 분석, 추세 분석 및 보고서 생성을 도와드릴 수 있습니다."
                )