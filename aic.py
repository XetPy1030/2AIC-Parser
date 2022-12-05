import requests
import pandas as pd
from datetime import date, timedelta, datetime
import pickle
import parsers_aic
import utils_aic

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


parsers = {
    'standart': parsers_aic.standart_parser,
    'saturday': parsers_aic.saturday_parser
}


def get_day_objs(sheet: list[list], parser = 'standart'):
    return parsers[parser](sheet)
                


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
            break

        if is_table:
            parsed_table.append(item)

    return [[o for o in i] for i in parsed_table]


def run_test():
    # filename = download()
    sheet = parse_table()
    diary = get_day_diary_from_time(sheet, date.today())
    
    # print(len(diary))
    
    with open('list.pickle', 'wb') as f:
        pickle.dump(diary, f)


# run_test()

with open('list.pickle', 'rb') as f:
    objs = pickle.load(f)
    # print(objs)
    ref = get_day_objs(objs)['Веб-дизайн и разработка 1 (гр.215-8-1)']
    print(*ref, sep='\n')
    print(utils_aic.get_now_par(ref))
    print(utils_aic.get_next_par(ref))
