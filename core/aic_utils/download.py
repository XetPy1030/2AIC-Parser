import requests

from .config import table_filename, table_url


def download_schedule(filename=table_filename) -> str:
    print('Скачивание...')
    table = requests.get(table_url)
    with open(filename, 'wb') as f:
        f.write(table.content)
    return filename
