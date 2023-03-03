from pprint import pprint

import pandas as pd
import threading
from datetime import date, timedelta, datetime

from aic_utils import utils_aic
from aic_utils.config import table_filename, parsers
from aic_utils.download import download_schedule
from aic_utils.utils_aic import thread_download


class Aic:
    old_size = 0
    old_date = None
    sheet = None
    schedule_today = None
    schedule_tomorrow = None

    download = lambda self: download_schedule()

    def __init__(self, download_thread=False) -> None:
        if download_thread:
            x = threading.Thread(target=thread_download, args=(self,), daemon=True)
            x.start()

    def parse_table(self, filename: str = table_filename):
        self.sheet = pd.ExcelFile(filename).parse('курс 1')
        try:
            self.schedule_today = self.get_day_diary_from_time(date.today())
        except:
            pass
        try:
            self.schedule_tomorrow = self.get_day_diary_from_time(date.today() + timedelta(days=1))
        except:
            pass
        return self.sheet

    def get_day_objs(self, dt: date = None, parser: str = None):
        dt = date.today() if dt is None else dt

        get_parser = lambda dt: 'saturday' if dt.weekday() == 5 else 'standart'
        parser = parser if parser is not None else get_parser(dt)

        diary = None
        today = dt.today()
        tomorrow = today + timedelta(days=1)
        if dt == today:
            diary = self.schedule_today
        if dt == tomorrow:
            diary = self.schedule_tomorrow
        if diary is None:
            diary = self.get_day_diary_from_time(dt)

        try:
            objs = parsers[parser](diary)
        except Exception as ex:
            objs = {}

        return objs

    def get_day_diary_from_time(self, date_parse: date):
        date_parse_future = date_parse + timedelta(days=1)
        date_parse = date_parse

        parsed_table = []
        is_table = False
        for number, item in enumerate(self.sheet.iloc):
            try:
                set_item = datetime.strptime(str(item[0]), '%Y-%m-%d 00:00:00').date()
            except:
                if is_table:
                    pass
                else:
                    continue
            if set_item == date_parse and not is_table:
                is_table = True
                parsed_table.append(self.sheet.iloc[number - 1])
            elif set_item >= date_parse_future:
                parsed_table.pop(-1) if len(parsed_table) else 0
                is_table = False
                break

            if is_table:
                parsed_table.append(item)

        return [[o for o in i] for i in parsed_table]

    def get_allowed_objects(self, dt: date) -> list[str]:
        diary = self.get_day_objs(dt)
        return [i for i in diary.keys()]

    def get_diary(self, dt: date, object: str):
        try:
            return self.get_day_objs(dt)[object]
        except KeyError:
            return []

    def get_remain_diary(self, dt: datetime, object: str):
        diary = self.get_diary(dt.date(), object)
        now_par = utils_aic.get_now_par(diary, dt)
        if now_par is not None:
            return diary[now_par:len(diary)]
        next_par = utils_aic.get_next_par(diary, dt)
        if next_par is not None:
            return diary[next_par:len(diary)]
        return []


if __name__ == '__main__':
    aic = Aic()
    aic.download()
    aic.parse_table()
    awd = aic.get_day_objs(date.today())
    pprint(awd)
