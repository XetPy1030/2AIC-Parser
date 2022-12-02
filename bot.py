
import logging
from time import time

from aiogram import Bot, Dispatcher, executor, types

from uuid import uuid4
import os
import table
import db
from datetime import datetime, timedelta
import difflib
from PIL import Image, ImageDraw, ImageFont
from aiogram.types.bot_command import BotCommand
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '5789559260:AAH4EohMvS4-S0GiS1mrF9b48rEz7jFDzXE'

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

diary = table.Diary()


def to_img(text: str):
    im = Image.new('RGB', (500, 300), color=('#FAACAC'))
    # Создаем объект со шрифтом
    font = ImageFont.truetype('Anonymous_Pro.ttf', size=12, encoding='UTF-8')
    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (10, 10),
        text,
        # Добавляем шрифт к изображению
        font=font,
        fill='#1C0606')
    filename = f'./imgs/{str(uuid4())}.png'
    im.save(filename, 'PNG')
    return filename


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Иди нахуй")


def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def search_object(obj: str, dt):
    objs = [[i, similarity(i, obj)] for i in diary.get_objects(dt)]
    return sorted(objs, key=lambda x: x[1])[-1][0]

marks_menu = InlineKeyboardMarkup()
marks_menu.insert(InlineKeyboardButton('сегодня', callback_data='par_show_today'))
marks_menu.insert(InlineKeyboardButton('завтра', callback_data='par_show_tomorrow'))


@dp.message_handler(commands=['par'])
async def send_welcome(message: types.Message):
    await message.reply('пары', reply_markup=marks_menu)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('par_show'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    dt = datetime.now() if callback_query.data == 'par_show_today' else datetime.now()+timedelta(1)
    txtdata = dt.strftime("%Y-%m-%d")
    marks = InlineKeyboardMarkup(row_width=1)
    for num, i in enumerate(diary.get_objects(dt)):
        if not i:
            continue
        marks.insert(InlineKeyboardButton(i, callback_data=f'par_get_{txtdata}|{num}'))
    await callback_query.message.edit_text('пары: '+dt.strftime("%Y-%m-%d"))
    await callback_query.message.edit_reply_markup(marks)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('par_get'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    dt, num = callback_query.data.split('_')[-1].split('|')
    dt = datetime.strptime(dt, "%Y-%m-%d")
    object = diary.get_objects(dt)[int(num)]
    db.set_last_object(callback_query.from_user.id, object)
    db.save()
    text = diary.get_diary(dt, object)
    fi = to_img(text)
    await callback_query.message.reply_photo(open(fi, 'rb'))
    os.remove(fi)


@dp.message_handler(commands=['par_today'])
async def send_welcome(message: types.Message):
    if not db.is_user_in_db(message.from_user.id):
        await message.reply('Тебя нет в бд')
        return
    dt = datetime.now()
    object = db.get_last_object(message.from_user.id)
    text = diary.get_diary(dt, object)
    fi = to_img(text)
    await message.reply_photo(open(fi, 'rb'))
    os.remove(fi)


@dp.message_handler(commands=['par_tomorrow'])
async def send_welcome(message: types.Message):
    if not db.is_user_in_db(message.from_user.id):
        await message.reply('Тебя нет в бд')
        return
    dt = datetime.now()+timedelta(days=1)
    object = db.get_last_object(message.from_user.id)
    text = diary.get_diary(dt, object)
    fi = to_img(text)
    await message.reply_photo(open(fi, 'rb'))
    os.remove(fi)


@dp.message_handler(commands=['db'])
async def send_welcome(message: types.Message):
    print(db.users)


@dp.message_handler(commands=['schedule_bus'])
async def send_welcome(message: types.Message):
    filename = table.download("1zhkVzJlkZpEgMpXKWLyMYno-FxSMbIbd")
    await message.reply_document(open(filename, "rb"))
    os.remove(filename)


@dp.message_handler(commands=['tournaments'])
async def send_welcome(message: types.Message):
    filename = table.download("1pogIUBApsCn_MtkUopfIrrRUXG_x64O6cEomLJ5nitM")
    await message.reply_document(open(filename, "rb"))
    os.remove(filename)


@dp.message_handler(commands=['important'])
async def send_welcome(message: types.Message):
    await message.reply("""Вопросы по пропускам на территорию ОЭЗ (разовый пропуск можно получить не чаще 1 раза в неделю) - Администратор Международной Школы Эльвина
8 (85557) 5-34-05

Вопросы по заключению договоров - Хамидуллина Юлия
8 (85557) 5-34-08 (221).

Вопросы по учебной части -
Доценко Дмитрий
8 (937) 641-31-67

Бытовые вопросы по жилью - Администратор 
8 (927) 480-00-08

По вопросам пропускного режима и Face ID (Ассессмент-центр, Хостелы, Пешее КПП) - Светлана Ахметова +7 (937) 299-34-60""")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
