from pprint import pprint

import pandas as pd
from datetime import date, datetime, timedelta
from prettytable import PrettyTable as pt
import textwrap
import threading

from bus_utils.config import table_filename
from bus_utils.utils_bus import download_bus, thread_download, check_time_format


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

    def parse_file(self, filename: str = table_filename) -> None:
        self.sheet = pd.ExcelFile(filename)
        self.last_update = datetime.now()

    @property
    def available_days(self) -> list[str]:
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

    def get_file_schedule(self, name: str) -> list[dict]:
        table = self.sheet.parse(name)

        table_rows = table.iloc
        table_rows = [[str(o) if str(o) != 'nan' else None for o in i] for i in table_rows]

        # в header'ах могут начинаться названия автобусов, поэтому их добавляем в строки основной таблицы
        headers = [i if not str(i).startswith("Unnamed") else None for i in table.columns]
        table_rows = [headers, *table_rows]

        schedule = []

        item_number = 0
        while item_number < len(table_rows):
            item = table_rows[item_number]
            if isinstance(item[0], str) and item[0].startswith('Автобус'):
                schedule.append({
                    'name': item[0],
                    'route': table_rows[item_number + 1][0],
                    'schedule': []
                })
                item_number += 3
                continue

            if isinstance(item[0], str) and \
                    (check_time_format(item[0], '%H:%M:%S') or check_time_format(item[0], '%H:%M')):
                if check_time_format(item[0], '%H:%M:%S'):
                    item[0] = datetime.strptime(item[0], '%H:%M:%S').time()
                else:
                    item[0] = datetime.strptime(item[0], '%H:%M').time()

                optional = {}
                if len(item) > 4:
                    optional = {
                        'quantity': int(item[3]),
                        'comments': item[4]
                    }
                else:
                    optional = {
                        'quantity': None,
                        'comments': item[3]
                    }

                schedule[-1]['schedule'].append({
                    'time': item[0],
                    'places': item[1],
                    'groups': [i.strip() for i in item[2].split(',') if i is not None],
                    **optional
                })
                item_number += 1
                continue

            item_number += 1

        return schedule

    def get_schedule(self, f_schedule: list[dict]) -> list[dict]:
        official_buses = []
        not_official_buses = []
        wrong_buses = []

        for bus_dict in f_schedule:
            routes_list = []
            bus_schedule_number = 0
            while bus_schedule_number < len(bus_dict['schedule']):
                bus_schedule = bus_dict['schedule'][bus_schedule_number]

                places = bus_schedule['places']

                if '-' in places:
                    name_bus = bus_dict['name']
                    start_time = bus_schedule['time']
                    end_time = None
                    groups = bus_schedule['groups']
                    start_place = places.split('-')[0].strip()
                    end_place = places.split('-')[1].strip()
                    comments = bus_schedule['comments']
                    quantity = bus_schedule['quantity']

                    routes_list.append({
                        'name_bus': name_bus,
                        'start_time': start_time,
                        'end_time': end_time,
                        'groups': groups,
                        'start_place': start_place,
                        'end_place': end_place,
                        'comments': comments,
                        'quantity': quantity,
                        'is_official': True
                    })

                    if bus_schedule_number + 1 < len(bus_dict['schedule']):
                        name_bus = bus_dict['name']
                        start_time = None
                        start_time_the_beginning_of_the_beginning = bus_schedule['time']
                        start_place_the_beginning_of_the_beginning = places.split('-')[0].strip()
                        end_time = bus_dict['schedule'][bus_schedule_number + 1]['time']
                        groups = None
                        start_place = places.split('-')[1].strip()

                        if '-' in bus_dict['schedule'][bus_schedule_number + 1]['places']:
                            end_place = bus_dict['schedule'][bus_schedule_number + 1]['places'].split('-')[0].strip()
                        else:
                            end_place = bus_dict['schedule'][bus_schedule_number + 1]['places']

                        comments = None
                        quantity = None

                        routes_list.append({
                            'name_bus': name_bus,
                            'start_time': start_time,
                            'start_time_the_beginning_of_the_beginning': start_time_the_beginning_of_the_beginning,
                            'end_time': end_time,
                            'groups': groups,
                            'start_place': start_place,
                            'start_place_the_beginning_of_the_beginning': start_place_the_beginning_of_the_beginning,
                            'end_place': end_place,
                            'comments': comments,
                            'quantity': quantity,
                            'is_official': False
                        })
                else:
                    if bus_schedule_number + 1 >= len(bus_dict['schedule']):
                        bus_schedule_number += 1
                        continue

                    name_bus = bus_dict['name']
                    start_time = bus_schedule['time']
                    end_time = bus_dict['schedule'][bus_schedule_number + 1]['time']
                    groups = bus_schedule['groups']
                    start_place = places

                    if '-' in bus_dict['schedule'][bus_schedule_number + 1]['places']:
                        end_place = bus_dict['schedule'][bus_schedule_number + 1]['places'].split('-')[0].strip()
                    else:
                        end_place = bus_dict['schedule'][bus_schedule_number + 1]['places']

                    comments = bus_schedule['comments']
                    quantity = bus_schedule['quantity']

                    routes_list.append({
                        'name_bus': name_bus,
                        'start_time': start_time,
                        'end_time': end_time,
                        'groups': groups,
                        'start_place': start_place,
                        'end_place': end_place,
                        'comments': comments,
                        'quantity': quantity,
                        'is_official': True
                    })

                bus_schedule_number += 1

            pprint(routes_list)

            # обработать routes_list в official_buses, not_official_buses, wrong_buses
            for route in routes_list:
                if route['is_official']:
                    if route['end_time'] is None:
                        official_buses.append(route)
                    else:
                        if route['end_time'] - route['start_time'] > timedelta(hours=1):
                            wrong_buses.append(route)
                        else:
                            official_buses.append(route)
                else:
                    if route['end_time'] - route['start_time_the_beginning_of_the_beginning'] > timedelta(hours=1):
                        wrong_buses.append(route)
                    else:
                        not_official_buses.append(route)

            # TODO, имена автобусов могут быть одинаковыми, добавить маршрут, если 2 автобуса с одинаковым именем

        return f_schedule

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
    # bus.download()
    bus.parse_file()
    available_days = bus.available_days
    file_schedule = bus.get_file_schedule(available_days[0])
    # pprint(file_schedule)
    schedule = bus.get_schedule(file_schedule)
    # pprint(schedule)
