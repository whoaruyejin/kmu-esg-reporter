"""Company management page with table and add dialog."""

from nicegui import ui
from sqlalchemy.orm import Session
from typing import Optional
import datetime

from .base_page import BasePage
from app.core.database.models import CmpInfo


class CompanyManagementPage(BasePage):
    async def render(self, db_session: Session, company_num: Optional[str] = None) -> None:
        ui.label('🏢 회사관리').classes('text-2xl font-bold text-blue-600 mb-4')

        companies = []
        if db_session:
            db_companies = db_session.query(CmpInfo).all()
            for c in db_companies:
                companies.append({
                    '사업장번호': c.cmp_num or '',
                    '지점': c.cmp_branch or '',
                    '회사명': c.cmp_nm,
                    '업종': c.cmp_industry or '',
                    '산업': c.cmp_sector or '',
                    '주소': c.cmp_addr or '',
                    '사외 이사회 수': c.cmp_extemp or 0,
                    '윤리경영 여부': c.cmp_ethics_yn,
                    '컴플라이언스 정책 여부': c.cmp_comp_yn,
                    'unique_key': f"{c.cmp_num}_{c.cmp_branch}",  # 복합키용 유니크 키
                    'actions': '수정'  # 액션 컬럼 추가
                })

        # =======================
        # 테이블 정의
        # =======================
        columns = [
            {'name': '사업장번호', 'label': '사업장번호', 'field': '사업장번호', 'align': 'center'},
            {'name': '회사명', 'label': '회사명', 'field': '회사명', 'align': 'center'},
            {'name': '지점', 'label': '지점', 'field': '지점', 'align': 'center'},
            {'name': '업종', 'label': '업종', 'field': '업종', 'align': 'center'},
            {'name': '산업', 'label': '산업', 'field': '산업', 'align': 'center'},
            {'name': '주소', 'label': '주소', 'field': '주소', 'align': 'center'},
            {'name': '사외 이사회 수', 'label': '사외 이사회 수', 'field': '사외 이사회 수', 'align': 'center'},
            {'name': '윤리경영 여부', 'label': '윤리경영 여부', 'field': '윤리경영 여부', 'align': 'center'},
            {'name': '컴플라이언스 정책 여부', 'label': '컴플라이언스 정책 여부', 'field': '컴플라이언스 정책 여부', 'align': 'center'},
            {'name': 'actions', 'label': '수정', 'field': 'actions', 'align': 'center'},
        ]

        # =======================
        # 회사 등록/수정 다이얼로그
        # =======================
        edit_mode = False
        current_company = None
        dialog_title = ui.label()

        with ui.dialog() as dialog, ui.card().classes('p-6 w-[600px]'):
            inputs = {}

            def setup_dialog(company_data=None):
                nonlocal edit_mode, current_company
                edit_mode = company_data is not None
                current_company = company_data
                
                if edit_mode:
                    dialog_title.text = '📝 회사 등록'
                    dialog_title.classes('text-xl font-bold text-blue-600 mb-4')

                # 기존 데이터로 폼 채우기
                if company_data:
                    inputs['cmp_num'].set_value(company_data.get('사업장번호', '6182618882'))
                    inputs['cmp_nm'].set_value(company_data.get('회사명', '국민AI 주식회사'))
                    inputs['cmp_branch'].set_value(company_data.get('지점', ''))
                    inputs['cmp_industry'].set_value(company_data.get('업종', ''))
                    inputs['cmp_sector'].set_value(company_data.get('산업', ''))
                    inputs['cmp_addr'].set_value(company_data.get('주소', ''))
                    inputs['cmp_extemp'].set_value(company_data.get('사외 이사회 수', 0))
                    inputs['cmp_ethics_yn'].set_value(company_data.get('윤리경영 여부', 'N'))
                    inputs['cmp_comp_yn'].set_value(company_data.get('컴플라이언스 정책 여부', 'N'))
                else:
                    # 신규 등록 시 기본값 설정
                    inputs['cmp_num'].set_value('6182618882')
                    inputs['cmp_nm'].set_value('국민AI 주식회사')
                    inputs['cmp_branch'].set_value('')
                    inputs['cmp_industry'].set_value('')
                    inputs['cmp_sector'].set_value('')
                    inputs['cmp_addr'].set_value('')
                    inputs['cmp_extemp'].set_value(0)
                    inputs['cmp_ethics_yn'].set_value('N')
                    inputs['cmp_comp_yn'].set_value('N')

            # 입력 필드 - 사업장번호와 회사명은 숨김 처리
            # 사업장번호는 고정값으로 설정 (6182618882)
            inputs['cmp_num'] = ui.input(value='6182618882').style('display: none')  # 숨김 처리
            # 회사명은 고정값으로 설정 (국민AI 주식회사)
            inputs['cmp_nm'] = ui.input(value='국민AI 주식회사').style('display: none')  # 숨김 처리
            inputs['cmp_branch'] = ui.input(label='지점', placeholder='지점명 입력 (예: 서울본사, 부산지사)').props('outlined dense').classes('w-full mb-3')
            inputs['cmp_industry'] = ui.input(label='업종', placeholder='업종 입력').props('outlined dense').classes('w-full mb-3')
            inputs['cmp_sector'] = ui.input(label='산업', placeholder='산업 입력').props('outlined dense').classes('w-full mb-3')
            inputs['cmp_addr'] = ui.input(label='주소', placeholder='주소 입력').props('outlined dense').classes('w-full mb-3')
            inputs['cmp_extemp'] = ui.number(label='사외 이사회 수', placeholder='숫자 입력', min=0).props('outlined dense').classes('w-full mb-3')

            # 토글 스위치
            with ui.row().classes('items-center gap-4 w-full mb-3'):
                ui.label('윤리경영 여부').classes('text-sm font-medium text-gray-700')
                inputs['cmp_ethics_yn'] = ui.toggle(['Y', 'N'], value='N').classes('ml-auto')

            with ui.row().classes('items-center gap-4 w-full mb-3'):
                ui.label('컴플라이언스 정책 여부').classes('text-sm font-medium text-gray-700')
                inputs['cmp_comp_yn'] = ui.toggle(['Y', 'N'], value='N').classes('ml-auto')

            # 저장/수정 로직
            def save_company():
                try:
                    if edit_mode and current_company:
                        # 기존 회사 정보 수정
                        cmp_num = current_company.get('사업장번호')
                        cmp_branch = current_company.get('지점')
                        
                        existing_company = db_session.query(CmpInfo).filter_by(
                            cmp_num=cmp_num, 
                            cmp_branch=cmp_branch
                        ).first()
                        
                        if existing_company:
                            existing_company.cmp_nm = inputs['cmp_nm'].value
                            existing_company.cmp_industry = inputs['cmp_industry'].value
                            existing_company.cmp_sector = inputs['cmp_sector'].value
                            existing_company.cmp_addr = inputs['cmp_addr'].value
                            existing_company.cmp_extemp = int(inputs['cmp_extemp'].value or 0)
                            existing_company.cmp_ethics_yn = inputs['cmp_ethics_yn'].value
                            existing_company.cmp_comp_yn = inputs['cmp_comp_yn'].value
                            
                            db_session.commit()
                            ui.notify(f"{existing_company.cmp_nm} 회사 정보가 수정되었습니다 ✅", type='positive')
                        else:
                            ui.notify("수정할 회사를 찾을 수 없습니다", type='negative')
                    else:
                        # 신규 회사 등록
                        new_company = CmpInfo(
                            cmp_num=inputs['cmp_num'].value,
                            cmp_branch=inputs['cmp_branch'].value,
                            cmp_nm=inputs['cmp_nm'].value,
                            cmp_industry=inputs['cmp_industry'].value,
                            cmp_sector=inputs['cmp_sector'].value,
                            cmp_addr=inputs['cmp_addr'].value,
                            cmp_extemp=int(inputs['cmp_extemp'].value or 0),
                            cmp_ethics_yn=inputs['cmp_ethics_yn'].value,
                            cmp_comp_yn=inputs['cmp_comp_yn'].value
                        )
                        db_session.add(new_company)
                        db_session.commit()
                        ui.notify(f"{new_company.cmp_nm} 회사가 등록되었습니다 ✅", type='positive')
                    
                    dialog.close()
                    ui.navigate.reload()
                except Exception as e:
                    ui.notify(f"저장 중 오류: {str(e)}", type='negative')
                    if db_session:
                        db_session.rollback()

            # 버튼들
            with ui.row().classes('justify-end mt-4 gap-3'):
                ui.button('저장', on_click=save_company).props('color=primary text-color=white').classes('px-6 py-2 rounded-lg')
                ui.button('취소', on_click=dialog.close).props('color=negative text-color=white').classes('px-6 py-2 rounded-lg')

        # 테이블 생성
        table = ui.table(columns=columns, rows=companies, row_key='unique_key').classes(
            'w-full text-center bordered dense flat rounded shadow-sm'
        ).props('table-header-class=bg-blue-200 text-black')
        
        # 각 행의 액션 컬럼에 수정 버튼 추가
        table.add_slot('body-cell-actions', '''
            <q-td key="actions" :props="props">
                <q-btn 
                    @click="$parent.$emit('edit_row', props.row)" 
                    dense 
                    round 
                    flat 
                    color="primary" 
                    icon="edit"
                    size="sm">
                    <q-tooltip>수정</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        
        # 수정 버튼 클릭 이벤트 처리
        def on_edit_row(e):
            row_data = e.args
            if row_data:
                setup_dialog(row_data)
                dialog.open()
        
        table.on('edit_row', on_edit_row)

        # =======================
        # 신규등록 버튼
        # =======================
        def open_new_dialog():
            setup_dialog()  # 신규 등록 모드로 다이얼로그 설정
            dialog.open()

        # =======================
        # 신규등록 버튼
        # =======================
        def open_new_dialog():
            setup_dialog()  # 신규 등록 모드로 다이얼로그 설정
            dialog.open()

        ui.button('신규등록', on_click=open_new_dialog) \
            .props('color=blue-200 text-color=black').classes('mt-4 rounded-lg shadow-md')
