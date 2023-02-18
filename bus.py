from random import randint

import requests
import pandas as pd
from datetime import date, timedelta, datetime
from prettytable import PrettyTable as pt
import textwrap
import threading
import os
import time


table_id = "1zhkVzJlkZpEgMpXKWLyMYno-FxSMbIbd"
table_url = 'https://docs.google.com/spreadsheets/d/'+table_id+'/export?format=xlsx'
table_filename = 'table_bus.xlsx'


class AicBus:
    sheet = None
    old_size = 0
    old_date = None

    def __init__(self) -> None:
        x = threading.Thread(target=self.thread_download, args=(self,), daemon=True)
        x.start()

    def thread_download(_, self):
        while True:
            try:
                self.download()

                new_size = os.path.getsize(table_filename)
                if new_size != self.old_size or self.old_date != date.today():
                    self.old_size = new_size
                    self.old_date = date.today()

                    self.parse_file()

                    print('Обновлено автобусы')
            except Exception as ex:
                print(ex)

            time.sleep(600)


    @staticmethod
    def download(filename=table_filename) -> str:
        print('Скачивание...')
        table = requests.get(table_url)
        with open(filename, 'wb') as f:
            f.write(table.content)
        return filename

    # download()

    def parse_file(self, filename: str = table_filename):
        self.sheet = pd.ExcelFile(filename)

    def get_available_names(self) -> list[str]:
        date_now = date.today()
        allowed_names = []
        
        for name in self.sheet.sheet_names:
            try:
                date_name = datetime.strptime(name, '%d.%m.%Y').date()
                if date_name >= date_now:
                    allowed_names.append(name)
            except Exception as ex:
                continue
        
        return allowed_names

    # parse_file()
    # print(get_available_names(sheet))

    def get_schedule_from_name_day(self, name: str) -> dict[list]:
        table = self.sheet.parse(name)
        table_rows = table.iloc
        table_rows = [[str(o) for o in i] for i in table_rows]
        headers = [i for i in table.columns]

        table_rows = [headers, *table_rows]
        
        schedule = {}
        
        name_bus = ''
        for item in table_rows:
            if isinstance(item[0], str) and item[0].startswith('Автобус'):
                num_bus = 0
                if item[0] in schedule:
                    num_bus += randint(1, 1000)
                name_bus = item[0] + f' {num_bus}'
                schedule[name_bus] = []
            if name_bus:
                schedule[name_bus].append([i for i in item])
        
        return schedule

    # schedule = get_schedule_from_name(sheet, '17.12.2022')
    # middle_schedule = schedule['Автобус №765']
    # print(*middle_schedule, sep='\n')

    @staticmethod
    def schedule_bus_to_table(schedule_bus: list[list]):
        table = pt()
        columns = schedule_bus[2]
        
        for column in columns:
            table.add_column(column, [])
        
        for row in schedule_bus[3:]:
            row = [textwrap.fill(item, 30) for item in row]
            table.add_row(row)

        return table

    # schedule_bus_to_table(middle_schedule)

