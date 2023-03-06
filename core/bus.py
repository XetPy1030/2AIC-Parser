from pprint import pprint

import pandas as pd
from datetime import date, datetime, timedelta
import threading
from uuid import uuid4, UUID

from bus_utils.config import table_filename
from bus_utils.utils_bus import download_bus, thread_download, check_time_format
from bus_utils.schedule import Schedule
from bus_utils.data import BusesSchedules, BusSchedule


class AicBus:
    sheet = None
    old_size = 0
    old_date = None
    last_update = None

    def __init__(self, is_thread_download=False) -> None:
        if is_thread_download:
            x = threading.Thread(target=thread_download, args=(self,), daemon=True)
            x.start()

    @staticmethod
    def download():
        download_bus()

    def parse_file(self, filename: str = table_filename) -> None:
        self.sheet = pd.ExcelFile(filename)
        self.last_update = datetime.now()

    @property
    def available_days(self) -> list[str]:
        date_now = date.today()-timedelta(days=2)
        allowed_names = []

        for name in self.sheet.sheet_names:
            try:
                date_name = datetime.strptime(name, '%d.%m.%Y').date()
                if date_name >= date_now:
                    allowed_names.append(name)
            except Exception as ex:
                continue

        return allowed_names

    def get_file_schedule(self, name: str) -> list[BusesSchedules]:
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
                schedule.append(BusesSchedules(
                    name=item[0].removeprefix('Автобус').replace('№', '').strip(),
                    route=table_rows[item_number + 1][0],
                    schedule=[]
                ))
                item_number += 3
                continue

            if isinstance(item[0], str) and \
                    (check_time_format(item[0], '%H:%M:%S') or check_time_format(item[0], '%H:%M')):
                if check_time_format(item[0], '%H:%M:%S'):
                    item[0] = datetime.strptime(item[0], '%H:%M:%S').time()
                else:
                    item[0] = datetime.strptime(item[0], '%H:%M').time()

                if len(item) > 4:
                    optional = {
                        'quantity': int(item[3]),
                        'comment': item[4].strip() if item[4] is not None else None
                    }
                else:
                    optional = {
                        'quantity': None,
                        'comment': item[3].strip() if item[3] is not None else None
                    }

                schedule[-1].schedule.append(BusSchedule(
                    time=item[0],
                    places=item[1],
                    groups=[i.strip() for i in item[2].split(',') if i is not None],
                    **optional
                ))
                item_number += 1
                continue

            item_number += 1

        return schedule

    def bus_distribution(self, routes_list: list[dict], official_buses: list[dict], not_official_buses: list[dict], wrong_buses: list[dict]) -> None:
        for route in routes_list:
            if route['start_time'] is not None:
                route['start_time'] = datetime.combine(date.today(), route['start_time'])
            if route['end_time'] is not None:
                route['end_time'] = datetime.combine(date.today(), route['end_time'])
            if route['start_time_the_beginning_of_the_beginning'] is not None:
                route['start_time_the_beginning_of_the_beginning'] = datetime.combine(
                    date.today(),
                    route['start_time_the_beginning_of_the_beginning']
                )

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

        # преобразовать время в datetime.time, чтобы не было проблем с сравнением и лишних данных
        for route in routes_list:
            if route['start_time'] is not None:
                route['start_time'] = route['start_time'].time()
            if route['end_time'] is not None:
                route['end_time'] = route['end_time'].time()
            if route['start_time_the_beginning_of_the_beginning'] is not None:
                route['start_time_the_beginning_of_the_beginning'] = route[
                    'start_time_the_beginning_of_the_beginning'].time()

    def patch_for_identical(self, routes_list: list[dict]) -> None:
        for route in routes_list:
            if route['start_place'] == route['end_place']:
                next_route = self.get_route(routes_list, route['next_route'])
                previous_route = self.get_route(routes_list, route['previous_route'])
                next_route['previous_route'] = previous_route['this_route']
                previous_route['next_route'] = next_route['this_route']
                routes_list.remove(route)

    def path_for_next_route(self, routes_list: list[dict]) -> None:
        for route in routes_list:
            if 'previous_route' in route.keys():
                if route['previous_route'] is not None:
                    route_find = self.get_route(routes_list, route['previous_route'])
                    route_find['next_route'] = route['this_route']

    def get_route(self, routes_list: list[dict], uuid: UUID) -> dict:
        for route in routes_list:
            if route['this_route'] == uuid:
                return route

    def get_schedule(self, f_schedule: list[BusesSchedules]) -> Schedule:
        official_buses = []
        not_official_buses = []
        wrong_buses = []

        for bus_dict in f_schedule:
            routes_list = []
            bus_schedule_number = 0
            while bus_schedule_number < len(bus_dict.schedule):
                bus_schedule = bus_dict.schedule[bus_schedule_number]

                places = bus_schedule.places

                if bus_schedule_number == 0:
                    previous_route = None
                else:
                    previous_route = routes_list[-1]['this_route']

                all_official = {
                    'name_bus': bus_dict.name,
                    'start_time': bus_schedule.time,
                    'start_time_the_beginning_of_the_beginning': None,
                    'groups': bus_schedule.groups,
                    'start_place_the_beginning_of_the_beginning': None,
                    'comments': bus_schedule.comment,
                    'quantity': bus_schedule.quantity,
                    'is_official': True,
                    'this_route': uuid4(),
                    'previous_route': previous_route
                }

                if ' - ' in places:
                    routes_list.append({
                        'end_time': None,
                        'start_place': places.split(' - ')[0].strip(),
                        'end_place': places.split(' - ')[1].strip(),
                        **all_official
                    })

                    if bus_schedule_number + 1 < len(bus_dict.schedule):
                        if ' - ' in bus_dict.schedule[bus_schedule_number + 1].places:
                            end_place = bus_dict.schedule[bus_schedule_number + 1].places.split(' - ')[0].strip()
                        else:
                            end_place = bus_dict.schedule[bus_schedule_number + 1].places

                        routes_list.append({
                            **all_official,
                            'start_time': None,
                            'start_time_the_beginning_of_the_beginning': bus_schedule.time,
                            'end_time': bus_dict.schedule[bus_schedule_number + 1].time,
                            'groups': None,
                            'start_place': places.split(' - ')[1].strip(),
                            'start_place_the_beginning_of_the_beginning': places.split(' - ')[0].strip(),
                            'end_place': end_place,
                            'comments': None,
                            'quantity': None,
                            'is_official': False,
                            'this_route': uuid4(),
                            'previous_route': routes_list[-1]['this_route']
                        })
                else:
                    if bus_schedule_number + 1 >= len(bus_dict.schedule):
                        bus_schedule_number += 1
                        continue

                    if ' - ' in bus_dict.schedule[bus_schedule_number + 1].places:
                        end_place = bus_dict.schedule[bus_schedule_number + 1].places.split(' - ')[0].strip()
                    else:
                        end_place = bus_dict.schedule[bus_schedule_number + 1].places

                    routes_list.append({
                        'end_time': bus_dict.schedule[bus_schedule_number + 1].time,
                        'start_place': places,
                        'end_place': end_place,
                        **all_official
                    })

                bus_schedule_number += 1

            self.path_for_next_route(routes_list)

            self.patch_for_identical(routes_list)

            self.bus_distribution(routes_list, official_buses, not_official_buses, wrong_buses)

        return Schedule(official_buses, not_official_buses, wrong_buses)


if __name__ == '__main__':
    bus = AicBus()
    # bus.download()
    bus.parse_file()
    available_days = bus.available_days
    file_schedule = bus.get_file_schedule(available_days[0])
    # pprint(file_schedule)
    schedule = bus.get_schedule(file_schedule)
    pprint(schedule.buses)
