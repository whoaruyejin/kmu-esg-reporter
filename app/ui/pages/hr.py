from nicegui import ui
import datetime
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database.models import EmpInfo, CmpInfo

class HRPage:
    async def render(self, db_session: Session, cmp_num: Optional[str] = None):
        ui.label('👨‍💼 직원관리').classes('text-2xl font-bold text-blue-600 mb-4')

        # 현재 회사의 직원 데이터 조회
        employees = []
        current_company = None
        available_branches = ['서울지사']  # 기본값
        
        if db_session:
            try:
                # 회사 정보 조회 (표시용)
                if cmp_num:
                    current_company = db_session.query(CmpInfo).filter(CmpInfo.cmp_num == cmp_num).first()
                else:
                    # 기본적으로 첫 번째 회사 조회
                    current_company = db_session.query(CmpInfo).first()
                
                # CmpInfo에서 사용 가능한 지점 목록 조회
                branch_records = db_session.query(CmpInfo.cmp_branch).distinct().all()
                if branch_records:
                    available_branches = [branch[0] for branch in branch_records if branch[0]]
                if not available_branches:  # 빈 리스트인 경우 기본값 추가
                    available_branches = ['서울지사']
                
                # 모든 직원 조회 (새 스키마에는 company_id가 없음)
                db_employees = db_session.query(EmpInfo).all()
                
                # DB 데이터를 테이블 형식으로 변환
                for emp in db_employees:
                        # 생년월일 포맷 변환 (YYYYMMDD -> YYYY-MM-DD)
                        birth_formatted = ''
                        if emp.EMP_BIRTH and len(emp.EMP_BIRTH) == 8:
                            birth_formatted = f"{emp.EMP_BIRTH[:4]}-{emp.EMP_BIRTH[4:6]}-{emp.EMP_BIRTH[6:8]}"
                        
                        # 입사일 포맷 변환 (YYYYMMDD -> YYYY-MM-DD)
                        join_formatted = ''
                        if emp.EMP_JOIN and len(emp.EMP_JOIN) == 8:
                            join_formatted = f"{emp.EMP_JOIN[:4]}-{emp.EMP_JOIN[4:6]}-{emp.EMP_JOIN[6:8]}"
                        
                        # 성별 변환 (1->남자, 2->여자)
                        gender_text = ''
                        if emp.EMP_GENDER == '1':
                            gender_text = '남자'
                        elif emp.EMP_GENDER == '2':
                            gender_text = '여자'
                        
                        employees.append({
                            '지점': emp.EMP_COMP or '서울지사',
                            '사번': str(emp.EMP_ID),
                            '이름': emp.EMP_NM,
                            '생년월일': birth_formatted,
                            '전화번호': emp.EMP_TEL or '',
                            '이메일': emp.EMP_EMAIL or '',
                            '입사년도': emp.EMP_JOIN[:4] if emp.EMP_JOIN and len(emp.EMP_JOIN) >= 4 else '',
                            '입사일': join_formatted,
                            '산재발생횟수': emp.EMP_ACIDENT_CNT or 0,
                            '이사회여부': emp.EMP_BOARD_YN or 'N',
                            '성별': gender_text,
                            '재직여부': emp.EMP_ENDYN or 'Y',
                            'db_id': emp.EMP_ID,  # 사번을 DB ID로 사용
                            'actions': '수정'  # 액션 컬럼 추가
                        })
            except Exception as e:
                # 테이블이 존재하지 않거나 다른 DB 오류 시 샘플 데이터 사용
                print(f"DB 오류로 샘플 데이터 사용: {str(e)}")
                current_company = None
                available_branches = ['서울지사']  # 기본값 설정
                employees = [
                    {
                        '지점': '서울지사',
                        '사번': '1001',
                        '이름': '김철수',
                        '생년월일': '1990-01-15',
                        '전화번호': '010-1234-5678',
                        '이메일': 'chulsoo@example.com',
                        '입사년도': '2015',
                        '입사일': '2015-03-01',
                        '산재발생횟수': 0,
                        '이사회여부': 'N',
                        '성별': '남자',
                        '재직여부': 'Y',
                        'db_id': None,
                        'actions': '수정'
                    }
                ]
        
       
        # # 현재 상태 표시
        # with ui.row().classes('w-full justify-between items-center mb-4'):
        #     if current_company:
        #         ui.label(f"📊 {current_company.cmp_nm} - 총 직원 수: {len(employees)}명").classes('text-lg font-medium text-gray-700')
        #         ui.label(f"✅ 자동 조회 완료").classes('text-sm text-green-600')
        #     else:
        #         ui.label(f"📊 샘플 데이터 - 총 {len(employees)}명").classes('text-lg font-medium text-gray-700')
        #         ui.label(f"⚠️ DB 연결 없음").classes('text-sm text-orange-600')

        # 테이블 컬럼 정의
        columns = [
            {'name': '지점', 'label': '지점', 'field': '지점', 'align': 'center'},
            {'name': '사번', 'label': '사번', 'field': '사번', 'align': 'center'},
            {'name': '이름', 'label': '이름', 'field': '이름', 'align': 'center'},
            {'name': '생년월일', 'label': '생년월일', 'field': '생년월일', 'align': 'center'},
            {'name': '전화번호', 'label': '전화번호', 'field': '전화번호', 'align': 'center'},
            {'name': '이메일', 'label': '이메일', 'field': '이메일', 'align': 'center'},
            {'name': '입사년도', 'label': '입사년도', 'field': '입사년도', 'align': 'center'},
            {'name': '입사일', 'label': '입사일', 'field': '입사일', 'align': 'center'},
            {'name': '산재발생횟수', 'label': '산재발생횟수', 'field': '산재발생횟수', 'align': 'center'},
            {'name': '이사회여부', 'label': '이사회여부', 'field': '이사회여부', 'align': 'center'},
            {'name': '성별', 'label': '성별', 'field': '성별', 'align': 'center'},
            {'name': '재직여부', 'label': '재직여부', 'field': '재직여부', 'align': 'center'},
            {'name': 'actions', 'label': '수정', 'field': 'actions', 'align': 'center'},
        ]

        table = ui.table(columns=columns, rows=employees, row_key='사번').classes(
            'w-full text-center bordered dense flat rounded shadow-sm'
        ).props(
             'table-header-class=bg-blue-200 text-white'
        )

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

        # 직원 등록/수정 다이얼로그
        edit_mode = False
        current_employee = None
        dialog_title = ui.label()
        with ui.dialog() as dialog, ui.card().classes('p-4 w-[450px] max-h-[85vh] overflow-y-auto'):
            inputs = {}

            def setup_dialog(employee_data=None):
                nonlocal edit_mode, current_employee
                edit_mode = employee_data is not None
                current_employee = employee_data
               
                # 기존 데이터로 폼 채우기
                if employee_data:
                    # 날짜 파싱
                    birth_parts = employee_data.get('생년월일', '1990-01-01').split('-')
                    hire_parts = employee_data.get('입사일', '2025-01-01').split('-')
                    
                    # 기존 직원의 지점 값을 유지, 하지만 수정 시에는 사용자 기본값(서울지사) 우선
                    user_default_branch = "서울지사"  # 사용자 기본 지점
                    
                    # available_branches에 서울지사가 있으면 서울지사를 기본값으로 사용
                    if user_default_branch in available_branches:
                        branch_value = user_default_branch
                    else:
                        # 서울지사가 없으면 available_branches의 첫 번째 값 사용
                        branch_value = available_branches[0] if available_branches else '서울지사'
                    
                    inputs['지점'].set_value(branch_value)
                    inputs['사번'].set_value(employee_data.get('사번', ''))
                    inputs['이름'].set_value(employee_data.get('이름', ''))
                    inputs['생년'].set_value(birth_parts[0] if len(birth_parts) > 0 else '1990')
                    inputs['생월'].set_value(birth_parts[1] if len(birth_parts) > 1 else '01')
                    inputs['생일'].set_value(birth_parts[2] if len(birth_parts) > 2 else '01')
                    inputs['전화번호'].set_value(employee_data.get('전화번호', ''))
                    inputs['이메일'].set_value(employee_data.get('이메일', ''))
                    inputs['입사년'].set_value(hire_parts[0] if len(hire_parts) > 0 else str(datetime.datetime.now().year))
                    inputs['입사월'].set_value(hire_parts[1] if len(hire_parts) > 1 else '01')
                    inputs['입사일'].set_value(hire_parts[2] if len(hire_parts) > 2 else '01')
                    inputs['산재발생횟수'].set_value(str(employee_data.get('산재발생횟수', 0)))
                    inputs['이사회여부'].set_value(employee_data.get('이사회여부', 'N'))
                    inputs['성별'].set_value(employee_data.get('성별', '남자'))
                    inputs['재직여부'].set_value(employee_data.get('재직여부', 'Y'))
                    
                    # 수정 모드에서는 사번 비활성화 (읽기 전용)
                    inputs['사번'].props('readonly disabled')
                else:
                    # 신규 등록 시 기본값 설정 - 서울지사 우선
                    user_default_branch = "서울지사"
                    if user_default_branch in available_branches:
                        default_branch = user_default_branch
                    else:
                        default_branch = available_branches[0] if available_branches else '서울지사'
                    
                    inputs['지점'].set_value(default_branch)
                    inputs['사번'].set_value('')
                    inputs['이름'].set_value('')
                    inputs['생년'].set_value('1990')
                    inputs['생월'].set_value('01')
                    inputs['생일'].set_value('01')
                    inputs['전화번호'].set_value('')
                    inputs['이메일'].set_value('')
                    inputs['입사년'].set_value(str(datetime.datetime.now().year))
                    inputs['입사월'].set_value('01')
                    inputs['입사일'].set_value('01')
                    inputs['산재발생횟수'].set_value('0')
                    inputs['이사회여부'].set_value('N')
                    inputs['성별'].set_value('남자')
                    inputs['재직여부'].set_value('Y')
                    
                    # 신규 등록 시 사번 활성화 (편집 가능)
                    inputs['사번'].props(remove='readonly disabled')

            inputs = {}

            # helper 함수
            def field(label, component):
                return component.props('outlined dense').classes('w-full mb-1').props(f'label={label}')

            # 지점 선택 (CmpInfo의 cmp_branch 값들을 사용)
            inputs['지점'] = ui.select(
                options=available_branches, 
                value=available_branches[0] if available_branches else '서울지사',
                label='지점'
            ).props('outlined dense').classes('w-full mb-1')
            inputs['사번'] = field('사번', ui.input())
            inputs['이름'] = field('이름', ui.input())

            # 생년월일 선택
            years = [str(y) for y in range(1950, datetime.date.today().year + 1)]
            months = [str(m).zfill(2) for m in range(1, 13)]
            days = [str(d).zfill(2) for d in range(1, 32)]
            with ui.column().classes('w-full mb-1'):
                ui.label('생년월일').classes('text-xs font-medium text-gray-700')
                with ui.row().classes('gap-1 w-full'):
                    year = ui.select(years, value='1990').props('outlined dense').classes('w-24')
                    month = ui.select(months, value='01').props('outlined dense').classes('w-16')
                    day = ui.select(days, value='01').props('outlined dense').classes('w-16')
            inputs['생년'] = year
            inputs['생월'] = month
            inputs['생일'] = day

            # 전화번호 입력 (마스크 사용)
            phone_input = ui.input(
                label='전화번호',
                placeholder='010-0000-0000'
            ).props('outlined dense mask="###-####-####" fill-mask').classes('w-full mb-1')
            
            inputs['전화번호'] = phone_input
            inputs['이메일'] = field('이메일', ui.input())
            
            # 입사일 선택 (년월일)
            hire_years = [str(y) for y in range(1980, datetime.date.today().year + 1)]
            hire_months = [str(m).zfill(2) for m in range(1, 13)]
            hire_days = [str(d).zfill(2) for d in range(1, 32)]
            with ui.column().classes('w-full mb-1'):
                ui.label('입사일').classes('text-xs font-medium text-gray-700')
                with ui.row().classes('gap-1 w-full'):
                    hire_year = ui.select(hire_years, value=str(datetime.date.today().year)).props('outlined dense').classes('w-24')
                    hire_month = ui.select(hire_months, value='01').props('outlined dense').classes('w-16')
                    hire_day = ui.select(hire_days, value='01').props('outlined dense').classes('w-16')
            inputs['입사년'] = hire_year
            inputs['입사월'] = hire_month
            inputs['입사일'] = hire_day
            
            inputs['산재발생횟수'] = field('산재발생횟수', ui.input().props('type=number'))
            inputs['이사회여부'] = field('이사회여부', ui.select(['Y', 'N'], value='N'))
            inputs['성별'] = field('성별', ui.select(['남자', '여자'], value='남자'))
            inputs['재직여부'] = field('재직여부', ui.select(['Y', 'N'], value='Y'))

            # 저장/수정 로직
            def add_employee():
                try:
                    # 필수 입력값 검증
                    if not inputs['사번'].value or not inputs['이름'].value:
                        ui.notify('사번과 이름은 필수 입력 항목입니다', type='warning')
                        return
                    
                    # 사번 중복 확인 (신규 등록 시에만)
                    emp_id = inputs['사번'].value
                    if not edit_mode and any(emp['사번'] == emp_id for emp in employees):
                        ui.notify('이미 존재하는 사번입니다', type='warning')
                        return
                    
                    # 입력값 검증 및 수집
                    workplace_value = inputs['지점'].value or '서울지사'  # 기본값 보장
                    birth_date_str = f"{inputs['생년'].value}-{inputs['생월'].value}-{inputs['생일'].value}"
                    
                    try:
                        birth_date = datetime.datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        ui.notify('올바른 생년월일을 입력해주세요', type='warning')
                        return
                    
                    # 입사일 처리
                    hire_date_str = f"{inputs['입사년'].value}-{inputs['입사월'].value}-{inputs['입사일'].value}"
                    try:
                        hire_date = datetime.datetime.strptime(hire_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        ui.notify('올바른 입사일을 입력해주세요', type='warning')
                        return
                    
                    try:
                        # 산재발생횟수 검증
                        accident_count = int(inputs['산재발생횟수'].value or 0)
                        if accident_count < 0:
                            ui.notify('산재발생횟수는 0 이상이어야 합니다', type='warning')
                            return
                    except ValueError:
                        ui.notify('산재발생횟수는 숫자만 입력 가능합니다', type='warning')
                        return
                    
                    # 데이터 포맷 변환
                    birth_date_formatted = f"{inputs['생년'].value}{inputs['생월'].value}{inputs['생일'].value}"  # YYYYMMDD
                    hire_date_formatted = f"{inputs['입사년'].value}{inputs['입사월'].value}{inputs['입사일'].value}"  # YYYYMMDD
                    
                    # 성별 변환 (남자->1, 여자->2)
                    gender_code = '1' if inputs['성별'].value == '남자' else '2'
                    
                    new_row = {
                        '지점': workplace_value,
                        '사번': inputs['사번'].value,
                        '이름': inputs['이름'].value,
                        '생년월일': birth_date_str,
                        '전화번호': inputs['전화번호'].value or '',
                        '이메일': inputs['이메일'].value or '',
                        '입사년도': inputs['입사년'].value,  # 테이블 표시용으로는 년도만
                        '입사일': hire_date_str,  # 전체 입사일
                        '산재발생횟수': accident_count,
                        '이사회여부': inputs['이사회여부'].value,
                        '성별': inputs['성별'].value,
                        '재직여부': inputs['재직여부'].value,
                        'db_id': None
                    }
                    
                    # 데이터베이스에 저장 (새로운 스키마)
                    if db_session:
                        try:
                            if edit_mode and current_employee:
                                # 기존 직원 정보 수정
                                existing_employee = db_session.query(EmpInfo).filter_by(
                                    EMP_ID=int(current_employee.get('사번'))
                                ).first()
                                
                                if existing_employee:
                                    existing_employee.EMP_NM = inputs['이름'].value
                                    existing_employee.EMP_BIRTH = birth_date_formatted
                                    existing_employee.EMP_TEL = inputs['전화번호'].value or ''
                                    existing_employee.EMP_EMAIL = inputs['이메일'].value or ''
                                    existing_employee.EMP_JOIN = hire_date_formatted
                                    existing_employee.EMP_ACIDENT_CNT = accident_count
                                    existing_employee.EMP_BOARD_YN = inputs['이사회여부'].value
                                    existing_employee.EMP_GENDER = gender_code
                                    existing_employee.EMP_ENDYN = inputs['재직여부'].value
                                    existing_employee.EMP_COMP = workplace_value
                                    
                                    db_session.commit()
                                    
                                    # 테이블에서 해당 직원 데이터 업데이트
                                    for i, emp in enumerate(employees):
                                        if emp['사번'] == current_employee.get('사번'):
                                            employees[i] = new_row
                                            break
                                    
                                    ui.notify(f"{existing_employee.EMP_NM} 님의 정보가 수정되었습니다 ✅", type='positive')
                                else:
                                    ui.notify("수정할 직원을 찾을 수 없습니다", type='negative')
                                    return
                            else:
                                # 신규 직원 등록
                                new_employee = EmpInfo(
                                    EMP_ID=int(inputs['사번'].value),
                                    EMP_NM=inputs['이름'].value,
                                    EMP_BIRTH=birth_date_formatted,
                                    EMP_TEL=inputs['전화번호'].value or '',
                                    EMP_EMAIL=inputs['이메일'].value or '',
                                    EMP_JOIN=hire_date_formatted,
                                    EMP_ACIDENT_CNT=accident_count,
                                    EMP_BOARD_YN=inputs['이사회여부'].value,
                                    EMP_GENDER=gender_code,
                                    EMP_ENDYN=inputs['재직여부'].value,
                                    EMP_COMP=workplace_value
                                )
                                
                                db_session.add(new_employee)
                                db_session.commit()
                                new_row['db_id'] = new_employee.EMP_ID
                                
                                # 테이블에 새 직원 추가
                                employees.append(new_row)
                                
                                ui.notify(f"{new_row['이름']} 님이 데이터베이스에 저장되었습니다 ✅", type='positive')
                            
                            table.update()
                            dialog.close()
                            
                            # 폼 초기화
                            for key, input_field in inputs.items():
                                if hasattr(input_field, 'set_value'):
                                    if key == '지점':
                                        input_field.set_value('서울지사')
                                    elif key in ['이사회여부', '재직여부']:
                                        input_field.set_value('N' if key == '이사회여부' else 'Y')
                                    elif key == '성별':
                                        input_field.set_value('남자')
                                    elif key in ['생년', '입사년']:
                                        input_field.set_value('1990' if key == '생년' else str(datetime.datetime.now().year))
                                    elif key in ['생월', '생일', '입사월', '입사일']:
                                        input_field.set_value('01')
                                    else:
                                        input_field.set_value('')
                            
                        except Exception as db_error:
                            print(f"DB 저장 오류: {str(db_error)}")
                            ui.notify(f"데이터베이스 저장 중 오류 발생: {str(db_error)}", type='negative')
                            if db_session:
                                db_session.rollback()
                            return
                        
                    else:
                        ui.notify(f"{new_row['이름']} 님이 추가되었습니다 (임시) ⚠️", type='warning')
                        # 테이블 업데이트
                        employees.append(new_row)
                        table.update()
                        dialog.close()
                    
                except Exception as e:
                    ui.notify(f"저장 중 오류가 발생했습니다: {str(e)}", type='negative')
                    if db_session:
                        db_session.rollback()

            with ui.row().classes('justify-end mt-3 gap-2'):
                ui.button('저장', on_click=add_employee, color='blue').classes('rounded-lg px-4 py-1')
                ui.button('취소', on_click=dialog.close, color='red').classes('rounded-lg px-4 py-1')

        # 수정 버튼 클릭 이벤트 처리
        def on_edit_row(e):
            row_data = e.args
            if row_data:
                setup_dialog(row_data)
                dialog.open()
        
        table.on('edit_row', on_edit_row)

        # 신규등록 버튼
        def open_new_dialog():
            setup_dialog()  # 신규 등록 모드로 다이얼로그 설정
            dialog.open()

        ui.button('신규등록', on_click=open_new_dialog, color='blue-200').classes('mt-3 rounded-lg shadow-md px-4 py-2')
        
       