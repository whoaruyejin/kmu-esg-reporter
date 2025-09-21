from nicegui import ui
import datetime

class HRPage:
    async def render(self, db_session=None, company_id=None):
        ui.label('👨‍💼 직원관리').classes('text-2xl font-bold text-green-600 mb-4')

        hr_data = [
            {
                '사업장': '서울공장',
                '사번': '1001',
                '이름': '김철수',
                '생년월일': '1990-01-15',
                '전화번호': '010-1234-5678',
                '이메일': 'chulsoo@example.com',
                '입사년도': '2015',
                '산재발생횟수': 0,
                '이사회여부': 'N',
                '성별': '여자',
                '재직여부': 'Y'
            }
        ]

        # 테이블
        columns = [
            {'name': '사업장', 'label': '사업장', 'field': '사업장', 'align': 'center'},
            {'name': '사번', 'label': '사번', 'field': '사번', 'align': 'center'},
            {'name': '이름', 'label': '이름', 'field': '이름', 'align': 'center'},
            {'name': '생년월일', 'label': '생년월일', 'field': '생년월일', 'align': 'center'},
            {'name': '전화번호', 'label': '전화번호', 'field': '전화번호', 'align': 'center'},
            {'name': '이메일', 'label': '이메일', 'field': '이메일', 'align': 'center'},
            {'name': '입사년도', 'label': '입사년도', 'field': '입사년도', 'align': 'center'},
            {'name': '산재발생횟수', 'label': '산재발생횟수', 'field': '산재발생횟수', 'align': 'center'},
            {'name': '이사회여부', 'label': '이사회여부', 'field': '이사회여부', 'align': 'center'},
            {'name': '성별', 'label': '성별', 'field': '성별', 'align': 'center'},
            {'name': '재직여부', 'label': '재직여부', 'field': '재직여부', 'align': 'center'},
        ]

        table = ui.table(columns=columns, rows=hr_data, row_key='사번').classes(
            'w-full text-center bordered dense flat rounded shadow-sm'
        ).props(
             'table-header-class=bg-green-200 text-white'
        )

        # 다이얼로그
        with ui.dialog() as dialog, ui.card().classes('p-6 w-[500px]'):
            ui.label('📝 신규 직원 추가').classes('text-lg font-semibold text-gray-700 mb-4')

            inputs = {}

            # helper (라벨 위, 간격 좁게)
            def field(label, component):
                return component.props('outlined dense').classes('w-full mb-2').props(f'label={label}')

            inputs['사번'] = field('사번', ui.input())
            inputs['이름'] = field('이름', ui.input())

            # 생년월일 (한 줄, 라벨 위)
            years = [str(y) for y in range(1950, datetime.date.today().year + 1)]
            months = [str(m).zfill(2) for m in range(1, 13)]
            days = [str(d).zfill(2) for d in range(1, 32)]
            with ui.column().classes('w-full mb-2'):
                ui.label('생년월일').classes('text-sm font-medium text-gray-700')
                with ui.row().classes('gap-2 w-full'):
                    year = ui.select(years, value='1990').props('outlined dense').classes('w-28')
                    month = ui.select(months, value='01').props('outlined dense').classes('w-20')
                    day = ui.select(days, value='01').props('outlined dense').classes('w-20')
            inputs['생년'] = year
            inputs['생월'] = month
            inputs['생일'] = day

            inputs['전화번호'] = field('전화번호', ui.input())
            inputs['이메일'] = field('이메일', ui.input())
            inputs['입사년도'] = field('입사년도', ui.input())
            inputs['산재발생횟수'] = field('산재발생횟수', ui.input().props('type=number'))
            inputs['이사회여부'] = field('이사회여부', ui.select(['Y', 'N']))
            inputs['성별'] = field('성별', ui.select(['남자', '여자']))
            inputs['재직여부'] = field('재직여부', ui.select(['Y', 'N']))

            # 저장 로직
            def add_row():
                new_row = {k: v.value for k, v in inputs.items()}
                new_row['생년월일'] = f"{new_row.pop('생년')}-{new_row.pop('생월')}-{new_row.pop('생일')}"
                new_row['사업장'] = company_id if company_id else '서울공장'
                hr_data.append(new_row)
                table.update()
                dialog.close() 
                ui.notify(f"{new_row['이름']} 님 추가 완료 ✅", type='positive')

            with ui.row().classes('justify-end mt-4 gap-2'):
                ui.button('추가', on_click=add_row, color='green').classes('rounded-lg px-6')
                ui.button('취소', on_click=dialog.close, color='red').classes('rounded-lg px-6')

        ui.button('신규등록', on_click=dialog.open, color='green-200').classes('mt-4 rounded-lg shadow-md')
