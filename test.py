
import pandas as pd
from datetime import datetime, timedelta
from pprint import pprint
import json


def get_table():
    data = pd.read_excel(r'work_table.xlsx')

    date_now = datetime.now()
    open("table.csv", "w").write(data.replace("\n", "").to_csv())
    return
    # open("table.txt", "w").write(data.to_string())
    read = False
    text = ""
    spl = data.to_csv(quoting=csv.QUOTE_NONE).split("\n")
    spl_str = data.to_string().split("\n")
    for i in spl_str:
        try:
            if (date_now).strftime("%Y-%m-%d 00:00:00") in i:
                read = True
            if read:
                if (date_now+timedelta(1)).strftime("%Y-%m-%d 00:00:00") in i:
                    return text
                text += i+'\n'
        except:
            pass
    return text


def recompile_par(filename: str) -> list[str]:
    data = pd.ExcelFile(r'work_table.xlsx').parse('курс 1')
    date_now = datetime.now()+timedelta(days=1)
    datakey = data[data.keys()[0]]
    text = []
    for o in range(len(datakey)):
        i = datakey[o]
        if str(i) == (date_now).strftime("%Y-%m-%d 00:00:00"):
            for p in data.keys():
                # print(data[p][0], type(data[p][0]), dir(data[p][0]))
                # return
                # print(data[p][o-1:])
                datajson = json.loads(data[p][o-1:].to_json())
                text.append([datajson[i] for i in datajson.keys()])
                # print(data[p][o-1:].to_json())
                data[p] = data[p][o-1:]
                # print(data[p][o-1:], type(data[p][o-1:]), dir(data[p][o-1:]), data[p][o-1:].index(Index()))
        if str(i) == (date_now+timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"):
            break
    # pprint(text)
    return text
    data.to_excel("new.xlsx")

def other_view(my_list):
    width = len(my_list)
    height = len(my_list[0])
    print(height)
    
    new_list = [[] for i in range(height)]
    print(new_list)
    for i in range(width):
        for o in range(height):
            item = my_list[i][o]
            print(item, o)
            new_list[o].append(item)
    return my_list
            

ttt = recompile_par("")
print(ttt[0])

# солнце звездыыы ясны 