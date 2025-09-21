"""Environment management page with database integration."""

from nicegui import ui
from sqlalchemy.orm import Session
from typing import Optional

from .base_page import BasePage
from app.core.database.models import Env


class EnvironmentPage(BasePage):
    async def render(self, db_session: Session, company_num: Optional[str] = None) -> None:
        ui.label('🌱 환경관리').classes('text-2xl font-bold text-blue-600 mb-4')

        # DB에서 환경 데이터 조회
        env_data = []
        if db_session:
            db_envs = db_session.query(Env).order_by(Env.year.desc()).all()
            for env in db_envs:
                env_data.append({
                    '년도': str(env.year),
                    '에너지 사용량': f"{env.energy_use:,.2f}" if env.energy_use else '0.00',
                    '온실가스 배출량': f"{env.green_use:,.2f}" if env.green_use else '0.00',
                    '재생에너지 사용여부': env.renewable_yn or 'N',
                    '재생에너지 비율': f"{(env.renewable_ratio * 100):,.1f}" if env.renewable_ratio else '0.0',
                    'year_pk': env.year,  # PK용
                    'actions': '수정/삭제'  # 액션 컬럼
                })

        # 테이블 컬럼 정의
        columns = [
            {'name': '년도', 'label': '년도', 'field': '년도', 'align': 'center'},
            {'name': '에너지 사용량', 'label': '에너지 사용량(MWh)', 'field': '에너지 사용량', 'align': 'center'},
            {'name': '온실가스 배출량', 'label': '온실가스 배출량(tCO2e)', 'field': '온실가스 배출량', 'align': 'center'},
            {'name': '재생에너지 사용여부', 'label': '재생에너지 사용여부', 'field': '재생에너지 사용여부', 'align': 'center'},
            {'name': '재생에너지 비율', 'label': '재생에너지 비율(%)', 'field': '재생에너지 비율', 'align': 'center'},
            {'name': 'actions', 'label': '수정/삭제', 'field': 'actions', 'align': 'center'},
        ]

        # 테이블 생성
        table = ui.table(columns=columns, rows=env_data, row_key='year_pk').classes(
            'w-full text-center bordered dense flat rounded shadow-sm'
        ).props('table-header-class=bg-blue-200 text-black')

        # 액션 버튼들을 테이블에 추가
        table.add_slot('body-cell-actions', '''
            <q-td key="actions" :props="props">
                <q-btn 
                    @click="$parent.$emit('edit_row', props.row)" 
                    dense 
                    round 
                    flat 
                    color="primary" 
                    icon="edit"
                    size="sm"
                    class="q-mr-xs">
                    <q-tooltip>수정</q-tooltip>
                </q-btn>
                <q-btn 
                    @click="$parent.$emit('delete_row', props.row)" 
                    dense 
                    round 
                    flat 
                    color="negative" 
                    icon="delete"
                    size="sm">
                    <q-tooltip>삭제</q-tooltip>
                </q-btn>
            </q-td>
        ''')

        # =======================
        # 환경 데이터 등록/수정 다이얼로그
        # =======================
        edit_mode = False
        current_env = None

        with ui.dialog() as dialog, ui.card().classes('p-6 w-[500px]'):
            dialog_title = ui.label('📝 신규 환경 데이터 추가').classes('text-lg font-semibold text-gray-700 mb-4')

            inputs = {}

            def setup_dialog(env_data=None):
                nonlocal edit_mode, current_env
                edit_mode = env_data is not None
                current_env = env_data
                
                if edit_mode:
                    dialog_title.text = '📝 환경 데이터 수정'
                    # 기존 데이터로 폼 채우기
                    inputs['년도'].set_value(env_data.get('년도', ''))
                    inputs['에너지 사용량'].set_value(float(env_data.get('에너지 사용량', '0').replace(',', '')))
                    inputs['온실가스 배출량'].set_value(float(env_data.get('온실가스 배출량', '0').replace(',', '')))
                    inputs['재생에너지 사용여부'].set_value(env_data.get('재생에너지 사용여부', 'N'))
                    inputs['재생에너지 비율'].set_value(float(env_data.get('재생에너지 비율', '0')))
                    inputs['년도'].disable()  # 수정 시 년도는 변경 불가
                else:
                    dialog_title.text = '📝 신규 환경 데이터 추가'
                    # 폼 초기화
                    inputs['년도'].set_value('')
                    inputs['에너지 사용량'].set_value(0)
                    inputs['온실가스 배출량'].set_value(0)
                    inputs['재생에너지 사용여부'].set_value('N')
                    inputs['재생에너지 비율'].set_value(0)
                    inputs['년도'].enable()

            def field_input(label, component):
                return component.props('outlined dense').classes('w-full mb-2').props(f'label={label}')

            def field_select(label, component):
                return component.props('outlined dense').classes('w-full mb-2').props(f'label={label}')

            inputs['년도'] = field_input('년도 (YYYY)', ui.number(precision=0, min=2000, max=2100))
            inputs['에너지 사용량'] = field_input('에너지 사용량(MWh)', ui.number(precision=2, min=0))
            inputs['온실가스 배출량'] = field_input('온실가스 배출량(tCO2e)', ui.number(precision=2, min=0))
            inputs['재생에너지 사용여부'] = field_select('재생에너지 사용여부', ui.select(['Y', 'N'], value='N'))
            inputs['재생에너지 비율'] = field_input('재생에너지 비율(%)', ui.number(precision=1, min=0, max=100))

            def save_env():
                try:
                    year = int(inputs['년도'].value)
                    energy_use = float(inputs['에너지 사용량'].value)
                    green_use = float(inputs['온실가스 배출량'].value)
                    renewable_yn = inputs['재생에너지 사용여부'].value
                    renewable_ratio = float(inputs['재생에너지 비율'].value) / 100  # 백분율을 소수로 변환

                    if edit_mode and current_env:
                        # 기존 데이터 수정
                        existing_env = db_session.query(Env).filter_by(year=year).first()
                        if existing_env:
                            existing_env.energy_use = energy_use
                            existing_env.green_use = green_use
                            existing_env.renewable_yn = renewable_yn
                            existing_env.renewable_ratio = renewable_ratio
                            
                            db_session.commit()
                            ui.notify(f"{year}년 환경 데이터가 수정되었습니다 ✅", type='positive')
                        else:
                            ui.notify("수정할 데이터를 찾을 수 없습니다", type='negative')
                    else:
                        # 중복 체크
                        existing = db_session.query(Env).filter_by(year=year).first()
                        if existing:
                            ui.notify(f"{year}년 데이터가 이미 존재합니다", type='negative')
                            return

                        # 신규 데이터 추가
                        new_env = Env(
                            year=year,
                            energy_use=energy_use,
                            green_use=green_use,
                            renewable_yn=renewable_yn,
                            renewable_ratio=renewable_ratio
                        )
                        db_session.add(new_env)
                        db_session.commit()
                        ui.notify(f"{year}년 환경 데이터가 추가되었습니다 ✅", type='positive')

                    dialog.close()
                    ui.navigate.reload()
                except Exception as e:
                    ui.notify(f"저장 중 오류: {str(e)}", type='negative')
                    if db_session:
                        db_session.rollback()

            with ui.row().classes('justify-end mt-4 gap-2'):
                ui.button('저장', on_click=save_env, color='primary').classes('rounded-lg px-6')
                ui.button('취소', on_click=dialog.close, color='negative').classes('rounded-lg px-6')

        # =======================
        # 삭제 확인 다이얼로그
        # =======================
        with ui.dialog() as delete_dialog, ui.card().classes('p-6'):
            ui.label('🗑️ 데이터 삭제').classes('text-lg font-semibold text-red-600 mb-2')
            delete_message = ui.label().classes('text-gray-700 mb-4')
            
            def confirm_delete():
                if current_env:
                    year = current_env['year_pk']
                    env_to_delete = db_session.query(Env).filter_by(year=year).first()
                    if env_to_delete:
                        db_session.delete(env_to_delete)
                        db_session.commit()
                        ui.notify(f"{year}년 환경 데이터가 삭제되었습니다 ✅", type='positive')
                        delete_dialog.close()
                        ui.navigate.reload()
                    else:
                        ui.notify("삭제할 데이터를 찾을 수 없습니다", type='negative')

            with ui.row().classes('justify-end gap-2'):
                ui.button('삭제', on_click=confirm_delete, color='negative').classes('rounded-lg px-6')
                ui.button('취소', on_click=delete_dialog.close, color='primary').classes('rounded-lg px-6')

        # 테이블 이벤트 처리
        def on_edit_row(e):
            row_data = e.args
            if row_data:
                setup_dialog(row_data)
                dialog.open()

        def on_delete_row(e):
            nonlocal current_env
            row_data = e.args
            if row_data:
                current_env = row_data
                delete_message.text = f"{row_data['년도']}년 환경 데이터를 정말 삭제하시겠습니까?"
                delete_dialog.open()

        table.on('edit_row', on_edit_row)
        table.on('delete_row', on_delete_row)

        # 신규등록 버튼
        def open_new_dialog():
            setup_dialog()
            dialog.open()

        ui.button('신규등록', on_click=open_new_dialog, color='blue-200').classes('mt-4 rounded-lg shadow-md')
