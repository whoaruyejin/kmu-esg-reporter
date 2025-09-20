from nicegui import ui

class EnvironmentPage:
    async def render(self, db_session=None, company_id=None):
        ui.label('🌱 환경관리').classes('text-2xl font-bold text-green-600 mb-4')

        # 샘플 데이터 (표시할 때는 문자열 포맷)
        env_data = [
            {
                '년도': '2024',
                '에너지 사용량': f"{12000:,}",
                '온실가스 배출량': f"{4500:,}",
                '재생에너지 사용여부': 'Y',
                '재생에너지 비율': f"{35:,}"
            }
        ]

        # 테이블 컬럼 정의
        columns = [
            {'name': '년도', 'label': '년도', 'field': '년도', 'align': 'center'},
            {'name': '에너지 사용량', 'label': '에너지 사용량(MWh)', 'field': '에너지 사용량', 'align': 'center'},
            {'name': '온실가스 배출량', 'label': '온실가스 배출량(tCO2e)', 'field': '온실가스 배출량', 'align': 'center'},
            {'name': '재생에너지 사용여부', 'label': '재생에너지 사용여부', 'field': '재생에너지 사용여부', 'align': 'center'},
            {'name': '재생에너지 비율', 'label': '재생에너지 비율(%)', 'field': '재생에너지 비율', 'align': 'center'},
        ]

        table = ui.table(columns=columns, rows=env_data, row_key='년도').classes(
            'w-full text-center bordered dense flat rounded shadow-sm'
        ).props(
            'table-header-class=bg-green-200 text-white'
        )


        # 다이얼로그 (신규등록)
        with ui.dialog() as dialog, ui.card().classes('p-6 w-[500px]'):
            ui.label('📝 신규 데이터 추가').classes('text-lg font-semibold text-gray-700 mb-4')

            inputs = {}
            def field(label, component):
                return component.props('outlined dense').classes('w-full mb-2').props(f'label={label}')

            inputs['년도'] = field('년도', ui.input())
            inputs['에너지 사용량'] = field('에너지 사용량(MWh)', ui.input().props('type=number'))
            inputs['온실가스 배출량'] = field('온실가스 배출량(tCO2e)', ui.input().props('type=number'))
            inputs['재생에너지 사용여부'] = field('재생에너지 사용여부', ui.select(['Y', 'N']))
            inputs['재생에너지 비율'] = field('재생에너지 비율(%)', ui.input().props('type=number'))

            def add_row():
                new_row = {k: v.value for k, v in inputs.items()}
                # 숫자 필드는 천 단위 구분 기호 적용
                for key in ['에너지 사용량', '온실가스 배출량', '재생에너지 비율']:
                    if new_row[key]:
                        new_row[key] = f"{int(new_row[key]):,}"
                env_data.append(new_row)
                table.update()
                dialog.close()
                ui.notify(f"{new_row['년도']}년 데이터 추가 완료 ✅", type='positive')

            with ui.row().classes('justify-end mt-4 gap-2'):
                ui.button('추가', on_click=add_row, color='green').classes('rounded-lg px-6')
                ui.button('취소', on_click=dialog.close, color='red').classes('rounded-lg px-6')

        ui.button('신규등록', on_click=dialog.open, color='green-200').classes('mt-4 rounded-lg shadow-md')
