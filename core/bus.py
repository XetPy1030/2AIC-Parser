from random import randint

import pandas as pd
from datetime import date, datetime
from prettytable import PrettyTable as pt
import textwrap
import threading

from bus_utils.config import table_filename
from bus_utils.utils_bus import download_bus, thread_download


class AicBus:
    sheet = None
    old_size = 0
    old_date = None
    last_update = None

    def __init__(self, is_thread_download=False) -> None:
        if is_thread_download:
            x = threading.Thread(target=thread_download, args=(self,), daemon=True)
            x.start()

    download = lambda self: download_bus()

    def parse_file(self, filename: str = table_filename):
        self.sheet = pd.ExcelFile(filename)
        self.last_update = datetime.now()

    def get_available_names_of_days_schedule_of_buses(self) -> list[str]:
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

    def get_schedule_of_buses_from_name_of_day(self, name: str) -> dict[list]:
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


if __name__ == '__main__':
    bus = AicBus()
    bus.download()
    bus.parse_file()
    names_of_days = bus.get_available_names_of_days_schedule_of_buses()
    names = bus.get_schedule_of_buses_from_name_of_day(names_of_days[0])
    print(names)
