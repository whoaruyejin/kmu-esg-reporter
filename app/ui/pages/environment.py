"""Environment management page with database integration."""

from nicegui import ui
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
import io

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

        # 신규등록 버튼과 엑셀 일괄등록 버튼
        def open_new_dialog():
            setup_dialog()
            dialog.open()

        def open_excel_dialog():
            excel_dialog.open()

        # 버튼들을 가로로 배치
        with ui.row().classes('mt-4 gap-3'):
            ui.button('신규등록', on_click=open_new_dialog) \
                .props('color=blue-200 text-color=black').classes('rounded-lg shadow-md')
            
            ui.button('엑셀 일괄등록', on_click=open_excel_dialog) \
                .props('color=green-200 text-color=black').classes('rounded-lg shadow-md')

        # =======================
        # 엑셀 일괄등록 다이얼로그
        # =======================
        with ui.dialog() as excel_dialog, ui.card().classes('p-6 w-[700px]'):
            ui.label('📄 환경 데이터 엑셀 일괄등록').classes('text-xl font-bold text-green-600 mb-4')
            
            # 엑셀 템플릿 안내
            with ui.card().classes('p-4 mb-4 bg-blue-50'):
                ui.label('📝 엑셀 파일 형식 안내').classes('text-lg font-bold text-blue-600')
                
                ui.label('⚠️ 재생에너지 사용여부는 Y 또는 N으로 입력해주세요.').classes('text-sm text-orange-600 mt-2')
                ui.label('⚠️ 재생에너지 비율은 0~100 사이의 숫자로 입력해주세요.').classes('text-sm text-orange-600')
                ui.label('⚠️ 에너지 사용량과 온실가스 배출량은 숫자로 입력해주세요.').classes('text-sm text-orange-600')
                ui.label('💡 열 이름에 공백이 있어도 자동으로 처리됩니다.').classes('text-sm text-blue-600 mt-1')
            
            # 엑셀 양식 다운로드 버튼
            def download_template():
                try:
                    # 엑셀 양식 데이터 생성
                    template_data = {
                        '년도': [2023, 2024],
                        '에너지 사용량': [1500.50, 1600.75],
                        '온실가스 배출량': [500.25, 520.80],
                        '재생에너지 사용여부': ['Y', 'N'],
                        '재생에너지 비율': [15.5, 12.3]
                    }
                    
                    # DataFrame 생성
                    template_df = pd.DataFrame(template_data)
                    
                    # 메모리에 엑셀 파일 생성
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        template_df.to_excel(writer, sheet_name='환경데이터양식', index=False)
                    
                    # 파일 다운로드
                    output.seek(0)
                    ui.download(output.getvalue(), filename='환경데이터_업로드양식.xlsx')
                    ui.notify('✅ 엑셀 양식이 다운로드되었습니다', type='positive')
                    
                except Exception as e:
                    ui.notify(f'❌ 양식 다운로드 오류: {str(e)}', type='negative')
            
            with ui.row().classes('w-full justify-center mb-4'):
                ui.button('📥 엑셀 양식 다운로드', on_click=download_template) \
                    .props('color=blue-200 text-color=black').classes('rounded-lg shadow-md px-4 py-2')
            
            # 파일 업로드
            upload_result = ui.label()
            preview_data = []
            preview_table = None
            
            def handle_upload(e):
                nonlocal preview_data, preview_table
                try:
                    upload_result.text = '파일 처리 중...'
                    upload_result.classes('text-blue-600')
                    
                    # 업로드된 파일 읽기
                    content = e.content.read()
                    
                    # 엑셀 파일 파싱
                    try:
                        # 엑셀 파일 읽기 (첫 번째 시트)
                        df = pd.read_excel(io.BytesIO(content), sheet_name=0)
                        
                        # 열 이름 정리 (모든 공백 제거)
                        df.columns = df.columns.str.replace(' ', '').str.strip()
                        
                        # 필수 열 확인 (공백 제거된 버전)
                        required_cols = ['년도', '에너지사용량', '온실가스배출량', '재생에너지사용여부', '재생에너지비율']
                        missing_cols = [col for col in required_cols if col not in df.columns]
                        
                        if missing_cols:
                            upload_result.text = f'❌ 누락된 열: {", ".join(missing_cols)}'
                            upload_result.classes('text-red-600')
                            return
                        
                        # 데이터 검증 및 임시 저장
                        preview_data = []
                        valid_count = 0
                        error_count = 0
                        error_messages = []
                        
                        for idx, row in df.iterrows():
                            try:
                                # 년도 검증
                                year = int(float(row['년도'])) if pd.notna(row['년도']) else None
                                if not year or year < 2000 or year > 2100:
                                    error_messages.append(f'행 {idx + 2}: 잘못된 년도 ({year})')
                                    error_count += 1
                                    continue
                                
                                # 에너지 사용량 검증
                                try:
                                    energy_use = float(row['에너지사용량']) if pd.notna(row['에너지사용량']) else 0.0
                                    if energy_use < 0:
                                        energy_use = 0.0
                                except (ValueError, TypeError):
                                    error_messages.append(f'행 {idx + 2}: 잘못된 에너지 사용량')
                                    error_count += 1
                                    continue
                                
                                # 온실가스 배출량 검증
                                try:
                                    green_use = float(row['온실가스배출량']) if pd.notna(row['온실가스배출량']) else 0.0
                                    if green_use < 0:
                                        green_use = 0.0
                                except (ValueError, TypeError):
                                    error_messages.append(f'행 {idx + 2}: 잘못된 온실가스 배출량')
                                    error_count += 1
                                    continue
                                
                                # 재생에너지 사용여부 검증
                                renewable_yn = str(row['재생에너지사용여부']).strip().upper() if pd.notna(row['재생에너지사용여부']) else 'N'
                                if renewable_yn not in ['Y', 'N']:
                                    error_messages.append(f'행 {idx + 2}: 재생에너지 사용여부는 Y 또는 N만 가능')
                                    error_count += 1
                                    continue
                                
                                # 재생에너지 비율 검증
                                try:
                                    renewable_ratio = float(row['재생에너지비율']) if pd.notna(row['재생에너지비율']) else 0.0
                                    if renewable_ratio < 0 or renewable_ratio > 100:
                                        error_messages.append(f'행 {idx + 2}: 재생에너지 비율은 0~100 사이여야 함')
                                        error_count += 1
                                        continue
                                except (ValueError, TypeError):
                                    error_messages.append(f'행 {idx + 2}: 잘못된 재생에너지 비율')
                                    error_count += 1
                                    continue
                                
                                # 유효한 데이터를 임시 저장
                                preview_data.append({
                                    '년도': str(year),
                                    '에너지 사용량': f"{energy_use:,.2f}",
                                    '온실가스 배출량': f"{green_use:,.2f}",
                                    '재생에너지 사용여부': renewable_yn,
                                    '재생에너지 비율': f"{renewable_ratio:.1f}",
                                    '상태': '업로드 대기',
                                    # DB 저장용 원본 값들
                                    '_year': year,
                                    '_energy_use': energy_use,
                                    '_green_use': green_use,
                                    '_renewable_yn': renewable_yn,
                                    '_renewable_ratio': renewable_ratio / 100  # 백분율을 소수로 변환
                                })
                                valid_count += 1
                                
                            except Exception as row_error:
                                error_count += 1
                                error_messages.append(f'행 {idx + 2}: {str(row_error)}')
                        
                        # 결과 메시지
                        if error_count == 0:
                            upload_result.text = f'✅ 검증 완료: {valid_count}건의 유효한 데이터가 준비되었습니다.'
                            upload_result.classes('text-green-600')
                        else:
                            upload_result.text = f'⚠️ 부분 성공: {valid_count}건 유효, {error_count}건 오류\n오류: {"; ".join(error_messages[:3])}'
                            upload_result.classes('text-orange-600')
                        
                        # 미리보기 테이블 업데이트
                        if preview_data:
                            if preview_table:
                                preview_table.rows = preview_data
                                preview_table.update()
                            else:
                                # 미리보기 테이블 생성
                                preview_columns = [
                                    {'name': '년도', 'label': '년도', 'field': '년도', 'align': 'center'},
                                    {'name': '에너지 사용량', 'label': '에너지 사용량(MWh)', 'field': '에너지 사용량', 'align': 'center'},
                                    {'name': '온실가스 배출량', 'label': '온실가스 배출량(tCO2e)', 'field': '온실가스 배출량', 'align': 'center'},
                                    {'name': '재생에너지 사용여부', 'label': '재생에너지 사용여부', 'field': '재생에너지 사용여부', 'align': 'center'},
                                    {'name': '재생에너지 비율', 'label': '재생에너지 비율(%)', 'field': '재생에너지 비율', 'align': 'center'},
                                    {'name': '상태', 'label': '상태', 'field': '상태', 'align': 'center'}
                                ]
                                
                                ui.label('🔍 업로드 데이터 미리보기').classes('text-lg font-bold text-blue-600 mt-4 mb-2')
                                preview_table = ui.table(
                                    columns=preview_columns, 
                                    rows=preview_data,
                                    row_key='년도'
                                ).classes('w-full text-center bordered dense flat rounded shadow-sm max-h-60')
                        
                    except Exception as excel_error:
                        upload_result.text = f'❌ 엑셀 파일 처리 오류: {str(excel_error)}'
                        upload_result.classes('text-red-600')
                        
                except Exception as e:
                    upload_result.text = f'❌ 파일 업로드 오류: {str(e)}'
                    upload_result.classes('text-red-600')
            
            # 파일 업로드 컴포넌트
            ui.upload(
                label='엑셀 파일 선택 (.xlsx, .xls)',
                auto_upload=True,
                on_upload=handle_upload,
                multiple=False
            ).props('accept=".xlsx,.xls"').classes('w-full mb-4')
            
            # 일괄 저장 버튼
            def save_all_data():
                if not preview_data:
                    ui.notify('❌ 저장할 데이터가 없습니다', type='warning')
                    return
                
                if not db_session:
                    ui.notify('❌ 데이터베이스 연결이 없습니다', type='negative')
                    return
                
                try:
                    saved_count = 0
                    updated_count = 0
                    errors = []
                    
                    for env_data in preview_data:
                        try:
                            year = env_data['_year']
                            
                            # 기존 환경 데이터 확인
                            existing_env = db_session.query(Env).filter_by(year=year).first()
                            
                            if existing_env:
                                # 기존 데이터 업데이트
                                existing_env.energy_use = env_data['_energy_use']
                                existing_env.green_use = env_data['_green_use']
                                existing_env.renewable_yn = env_data['_renewable_yn']
                                existing_env.renewable_ratio = env_data['_renewable_ratio']
                                updated_count += 1
                            else:
                                # 신규 환경 데이터 추가
                                new_env = Env(
                                    year=year,
                                    energy_use=env_data['_energy_use'],
                                    green_use=env_data['_green_use'],
                                    renewable_yn=env_data['_renewable_yn'],
                                    renewable_ratio=env_data['_renewable_ratio']
                                )
                                db_session.add(new_env)
                                saved_count += 1
                                
                        except Exception as e:
                            errors.append(f"년도 {env_data['년도']}: {str(e)}")
                    
                    if errors:
                        error_msg = f"❌ 일부 데이터 저장 실패:\n" + "\n".join(errors[:5])
                        if len(errors) > 5:
                            error_msg += f"\n... 외 {len(errors) - 5}개"
                        ui.notify(error_msg, type='negative')
                        db_session.rollback()
                        return
                    
                    # 데이터베이스 커밋
                    db_session.commit()
                    
                    # 메인 테이블 새로고침
                    refresh_table_data()
                    
                    # 다이얼로그 닫기 및 초기화
                    excel_dialog.close()
                    preview_data.clear()
                    if preview_table:
                        preview_table.rows = []
                        preview_table.update()
                    upload_result.text = ''
                    
                    ui.notify(f'✅ 저장 완료: 신규 {saved_count}건, 수정 {updated_count}건', type='positive')
                    
                except Exception as e:
                    ui.notify(f'❌ 저장 중 오류 발생: {str(e)}', type='negative')
                    if db_session:
                        db_session.rollback()
            
            # 다이얼로그 하단 버튼들
            with ui.row().classes('justify-end mt-4 gap-3'):
                ui.button('저장', on_click=save_all_data).props('color=primary text-color=white').classes('px-6 py-2 rounded-lg')
                ui.button('취소', on_click=excel_dialog.close).props('color=negative text-color=white').classes('px-6 py-2 rounded-lg')

        # 테이블 새로고침 함수 (엑셀 저장 후 사용)
        def refresh_table_data():
            """테이블 데이터만 새로고침"""
            updated_env_data = []
            if db_session:
                try:
                    db_envs = db_session.query(Env).order_by(Env.year.desc()).all()
                    for env in db_envs:
                        updated_env_data.append({
                            '년도': str(env.year),
                            '에너지 사용량': f"{env.energy_use:,.2f}" if env.energy_use else '0.00',
                            '온실가스 배출량': f"{env.green_use:,.2f}" if env.green_use else '0.00',
                            '재생에너지 사용여부': env.renewable_yn or 'N',
                            '재생에너지 비율': f"{(env.renewable_ratio * 100):,.1f}" if env.renewable_ratio else '0.0',
                            'year_pk': env.year,
                            'actions': '수정/삭제'
                        })
                except Exception as e:
                    print(f"테이블 새로고침 오류: {str(e)}")
            
            # 전역 env_data 업데이트
            env_data.clear()
            env_data.extend(updated_env_data)
            table.rows = env_data
            table.update()
