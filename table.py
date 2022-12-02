
import time
import requests
from datetime import date, timedelta, datetime
import pandas as pd
from uuid import uuid4
from pandas import DataFrame
import os
import threading


def download(self) -> str:
    myfile = requests.get(self.url)
    filename = f"{uuid4()}.xlsx"
    open(filename, 'wb').write(myfile.content)
    return filename


class Diary:
    api_key = "1_09XtP9nsQpAnL_tRvQ83HVhvLf7rh3jqyDvVSiRNto"
    url = 'https://docs.google.com/spreadsheets/d/'+api_key+'/export?format=xlsx'
    last_update: datetime
    sheet: DataFrame
    diary: list
    is_start = False

    def __init__(self) -> None:
        x = threading.Thread(target=self.thread_download, args=(self,), daemon=True)
        x.start()

    def thread_download(_, self):
        filename = "work_test.xlsx"
        filenamecheck = "work_table.xlsx"
        self.sheet = pd.ExcelFile(filenamecheck).parse('курс 1')
        print("start")
        while True:
            myfile = requests.get(self.url)
            with open(filename, 'wb') as f:
                f.write(myfile.content)
            if os.path.getsize(filename) != os.path.getsize(filenamecheck):
                os.remove(filenamecheck)
                os.rename(filename, filenamecheck)
                self.sheet = pd.ExcelFile(filenamecheck).parse('курс 1')
                print("yes")
            time.sleep(600)

    def download(self) -> str:
        self.last_update = datetime.now()
        myfile = requests.get(self.url)
        filename = "work_table.xlsx"
        open(filename, 'wb').write(myfile.content)
        self.sheet = pd.ExcelFile(filename).parse('курс 1')

    def get_day_diary_from_time(self, date_parse: date):
        date_parse_future = (date_parse + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        date_parse = date_parse.strftime("%Y-%m-%d 00:00:00")
        
        parsed_table = []
        is_seted = False
        for number, item in enumerate(self.sheet.iloc):
            set_item = str(item[0])
            if set_item == date_parse:
                is_seted = True
                parsed_table.append(self.sheet.iloc[number-1])
            elif set_item == date_parse_future:
                parsed_table.pop(-1)
                is_seted = False
            
            if is_seted:
                parsed_table.append(item)
        return [[o for o in i] for i in parsed_table]

    def get_diary_by_object(self, diary: list, object: str) -> list:
        index_obj = diary[0].index(object)
        diary_obj = []
        for y in range(len(diary)):
            x_stroka = []
            stroka = diary[y]
            x_stroka.append(stroka[0] if not isinstance(stroka[0], datetime) else stroka[0].strftime("%Y-%m-%d"))
            x_stroka.append(stroka[index_obj])
            x_stroka.append(stroka[index_obj+1])
            diary_obj.append(x_stroka)
        return diary_obj

    def format_diary(self, diary: list):
        text = ''
        fmt = '{:12}| {:20} | {}'
        for num1, i in enumerate(diary):
            for num2, o in enumerate(i):
                if str(o) == str(float('nan')):
                    diary[num1][num2] = ''
            text += fmt.format(*i) + '\n'
        return text

    def get_diary(self, dt: datetime, object: str) -> str:
        self.update()

        diary = self.get_day_diary_from_time(date_parse=dt)
        diary_by_object = self.get_diary_by_object(diary=diary, object=object)
        return self.format_diary(diary=diary_by_object)

    def get_objects(self, dt: datetime, sep=", ") -> str:
        self.update()
        
        diary = self.get_day_diary_from_time(date_parse=dt)
        return [i if str(i)!="nan" else '' for i in diary[0]]

    def update(self):
        return
        if (datetime.now()-self.last_update)>timedelta(hours=1):
            self.download()
