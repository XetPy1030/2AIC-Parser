import requests
import pandas as pd
from datetime import date, timedelta, datetime
import pickle

table_id = "1_09XtP9nsQpAnL_tRvQ83HVhvLf7rh3jqyDvVSiRNto"
table_url = 'https://docs.google.com/spreadsheets/d/'+table_id+'/export?format=xlsx'
table_filename = 'table.xlsx'

def download(filename=table_filename) -> str:
    table = requests.get(table_url)
    with open(filename, 'wb') as f:
        f.write(table.content)
    return filename


def parse_table(filename: str = table_filename):
    sheet = pd.ExcelFile(filename).parse('курс 1')
    return sheet


def get_day_objs(sheet: list[list], parser: str['standart', 'saturday'] = 'standart'):
    objs = {}
    for x in range(len(sheet[0])//2):
        cur_x = x*2+1
        name_obj = sheet[0][cur_x]
        objs[name_obj] = objs.get(name_obj, [])
        for y in range((len(sheet)-2)//2):
            cur_y = y*2 + 2
            obj_time = sheet[cur_y][0]
            obj_name = sheet[cur_y][cur_x]
            obj_cab = sheet[cur_y][cur_x+1]
            obj_teacher = sheet[cur_y+1][cur_x]
            
            if isinstance(obj_time, float):
                continue


            start_time, end_time = obj_time.split('-')
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            
            data = {
                'name': obj_name,
                'cabinet': obj_cab,
                'teacher': obj_teacher,
                'start_hour': start_hour,
                'start_min': start_min,
                'end_hour': end_hour,
                'end_min': end_min,
            }

            objs[name_obj].append(data)

    return objs
                


def get_day_diary_from_time(sheet, date_parse: date):
    date_parse_future = date_parse + timedelta(days=1)
    date_parse = date_parse
    
    parsed_table = []
    is_table = False
    for number, item in enumerate(sheet.iloc):
        try:
            set_item = datetime.strptime(str(item[0]), '%Y-%m-%d 00:00:00').date()
        except:
            if is_table:
                pass
            else:
                continue
        if set_item == date_parse and not is_table:
            is_table = True
            parsed_table.append(sheet.iloc[number-1])
        elif set_item >= date_parse_future:
            parsed_table.pop(-1)
            is_table = False

        if is_table:
            parsed_table.append(item)

    return [[o for o in i] for i in parsed_table]


def run_test():
    # filename = download()
    sheet = parse_table()
    diary = get_day_diary_from_time(sheet, date.today())
    
    with open('list.pickle', 'wb') as f:
        pickle.dump(diary, f)


# run_test()

with open('list.pickle', 'rb') as f:
    objs = pickle.load(f)
    # print(objs)
    ref = get_day_objs(objs)['Веб-дизайн и разработка 1 (гр.215-8-1)']
    print(ref)
