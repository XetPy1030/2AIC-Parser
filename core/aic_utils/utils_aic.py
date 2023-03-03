import os
import time
from datetime import datetime, timedelta, date

from .config import table_filename


def get_now_par(schedule: list[dict], dt: datetime = None) -> int:
    d_now = datetime.now() if dt is None else dt
    for num, item in enumerate(schedule):
        if item['start_hour'] == d_now.hour:  # add >
            if item['start_min'] >= d_now.minute:
                pass
            else:
                continue
        if item['end_hour'] == d_now.hour:
            if item['end_min'] <= d_now.minute:
                pass
            else:
                continue
        if d_now.hour >= item['start_hour'] and d_now.hour <= item['end_hour']:
            # print(item)
            return num

    return None


def get_next_par(schedule: list[dict], dt: datetime = None) -> int:
    d_now = datetime.now() if dt is None else dt
    for num, item in enumerate(schedule):
        if item['start_hour'] == d_now.hour:  # add >
            if item['start_min'] <= d_now.minute:
                return num
            else:
                continue
        if d_now.hour <= item['start_hour']:
            return num

    return None


def get_remaining_time(schedules: list[dict], dt: datetime = None) -> timedelta:
    schedule = get_now_par(schedules, dt)
    dt = datetime.now() if dt is None else dt
    dt_para = datetime(dt.year, dt.month, dt.day, schedule.end_hour, schedule.end_min)
    return dt_para - dt


def get_next_para_time(schedules: list[dict], dt: datetime = None) -> timedelta:
    schedule = get_now_par(schedules, dt)
    dt = datetime.now() if dt is None else dt
    dt_para = datetime(dt.year, dt.month, dt.day, schedule.end_hour, schedule.end_min)
    return dt_para - dt


def to_text(schedule: list[dict]):
    text = ''
    for num, i in enumerate(schedule):
        list_text = [
            f"{num + 1}. {i['name']}",
            f"{i['cabinet']}",
            f"{i['start_hour']}:{i['start_min']}-{i['end_hour']}:{i['end_min']}"
        ]
        text += '\n'.join(list_text)
        text += '\n\n'
    return text if text.strip() else 'Нет расписания\n\n\n'


def thread_download(aic):
    while True:
        try:
            aic.download_bus()

            new_size = os.path.getsize(table_filename)
            if new_size != aic.old_size or aic.old_date != date.today():
                aic.old_size = new_size
                aic.old_date = date.today()

                aic.parse_table()

                print('Обновлено')
        except Exception as ex:
            print(ex)

        time.sleep(600)
