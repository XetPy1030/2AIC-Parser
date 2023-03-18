from pprint import pprint

import pandas as pd
from datetime import date, datetime, timedelta
import threading
from uuid import uuid4, UUID
import re

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
        date_now = date.today()-timedelta(days=5)  # TODO: щелчок Таноса потом
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

        for route in routes_list:
            if 'status' in route.keys():
                if route['status'] == 'official':
                    official_buses.append(route)
                    continue
                elif route['status'] == 'not_official':
                    not_official_buses.append(route)
                    continue
                elif route['status'] == 'wrong':
                    wrong_buses.append(route)
                    continue

            if route['is_official']:
                if route['end_time'] is None:
                    official_buses.append(route)
                else:
                    if route['end_time'] - route['start_time'] > timedelta(hours=1):
                        wrong_buses.append(route)
                    else:
                        official_buses.append(route)
            else:
                next_route = self.get_route(routes_list, route['next_route'])

                print(route, next_route, sep='\n', end='\n\n')

                if route['end_time'] - next_route['start_time'] > timedelta(hours=1):
                    wrong_buses.append(route)
                else:
                    not_official_buses.append(route)

        for route in routes_list:
            if route['start_time'] is not None:
                route['start_time'] = route['start_time'].time()
            if route['end_time'] is not None:
                route['end_time'] = route['end_time'].time()

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

    def path_divide_hostels(self, routes_list: list[dict]):
        params = {
            # 'status': 'official'  # статус автобуса, точный, для bus_distribution
        }
        test = 0

        route_num = 0
        while route_num < len(routes_list):
            route = routes_list[route_num]

            re_hostel = re.compile(r'Хостел \d-\d')

            if re_hostel.match(route['start_place']):
                test += 1
                print(route, route_num)
                hostel_num_1 = re_hostel.match(route['start_place']).group(0)[7]
                hostel_num_2 = re_hostel.match(route['start_place']).group(0)[9]
                next_next_route = self.get_route(routes_list, route['next_route'])

                next_route_add = {
                    'name_bus': route['name_bus'],
                    'start_time': None,
                    'end_time': route['end_time'],
                    'start_place': 'Хостел ' + hostel_num_2,
                    'end_place': route['end_place'],
                    'groups': route['groups'],
                    'is_official': route['is_official'],
                    'comments': route['comments'],
                    'quantity': route['quantity'],
                    'this_route': uuid4(),
                    'next_route': route['next_route'],
                    'previous_route': route['this_route']
                }

                next_next_route['previous_route'] = next_route_add['this_route']

                route['start_place'] = 'Хостел ' + hostel_num_1
                route['end_place'] = 'Хостел ' + hostel_num_2
                route['end_time'] = None
                route['next_route'] = next_route_add['this_route']
                route.update(params)

                print(route)
                print()

                routes_list.insert(route_num + 1, next_route_add)
                route_num += 1

            if re_hostel.match(route['end_place']):
                # test += 1
                hostel_num_1 = re_hostel.match(route['end_place']).group(0)[7]
                hostel_num_2 = re_hostel.match(route['end_place']).group(0)[9]
                previous_previous_route = self.get_route(routes_list, route['previous_route'])

                # TODO: ЧЕКНУТЬ ПРАВИЛЬНОСТЬ

                previous_route_add = {
                    'name_bus': route['name_bus'],
                    'start_time': route['start_time'],
                    'end_time': None,
                    'start_place': route['start_place'],
                    'end_place': 'Хостел ' + hostel_num_1,
                    'groups': route['groups'],
                    'is_official': route['is_official'],
                    'comments': route['comments'],
                    'quantity': route['quantity'],
                    'this_route': uuid4(),
                    'next_route': route['this_route'],
                    'previous_route': route['previous_route']
                }

                previous_previous_route['next_route'] = previous_route_add['this_route']

                route['start_place'] = 'Хостел ' + hostel_num_1
                route['end_place'] = 'Хостел ' + hostel_num_2
                route['start_time'] = None
                route['previous_route'] = previous_route_add['this_route']
                route.update(params)

                routes_list.insert(route_num, previous_route_add)
                route_num += 1

            route_num += 1

        print(test)

    def get_schedule(self, f_schedule: list[BusesSchedules]) -> Schedule:
        official_buses = []
        not_official_buses = []
        wrong_buses = []

        for bus_dict in f_schedule[4:len(f_schedule)]:
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
                    'groups': bus_schedule.groups,
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

            self.path_divide_hostels(routes_list)

            # self.bus_distribution(routes_list, official_buses, not_official_buses, wrong_buses)

            print(*[[i['start_place'], i['end_place']] for i in routes_list], sep='\n')

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
