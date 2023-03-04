import os
import time
from datetime import date, datetime

import requests

from .config import table_filename, table_url


def download_bus(filename=table_filename) -> str:
    print('Скачивание...')
    table = requests.get(table_url)
    with open(filename, 'wb') as f:
        f.write(table.content)
    return filename


def thread_download(bus):
    while True:
        try:
            download_bus()

            new_size = os.path.getsize(table_filename)
            if new_size != bus.old_size or bus.old_date != date.today():
                bus.old_size = new_size
                bus.old_date = date.today()

                bus.parse_file()

                print('Обновлено автобусы')
        except Exception as ex:
            print(ex)

        time.sleep(600)


def check_time_format(text: str, format_time: str) -> bool:
    try:
        datetime.strptime(text, format_time)
        return True
    except ValueError:
        return False
