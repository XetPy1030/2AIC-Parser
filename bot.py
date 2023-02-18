
import logging

from aiogram import Bot, Dispatcher, executor, types

from uuid import uuid4
import os
import db
from datetime import datetime, timedelta
import difflib
from PIL import Image, ImageDraw, ImageFont
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
import aic
import bus

from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

diary = aic.Aic()
diary_bus = bus.AicBus()


def to_img(text: str):
    height = len(text.split('\n'))//4
    im = Image.new('RGB', (500, height*60), color=('#FAACAC'))
    font = ImageFont.truetype('Anonymous_Pro.ttf', size=12, encoding='UTF-8')
    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (10, 10),
        text,
        font=font,
        fill='#1C0606')
    filename = f'./imgs/{str(uuid4())}.png'
    im.save(filename, 'PNG')
    return filename


def to_img_bus(text: str):
    height = len(text.split('\n'))//4
    im = Image.new('RGB', (600, 80+height*60), color=('#FAACAC'))
    font = ImageFont.truetype('Anonymous_Pro.ttf', size=12, encoding='UTF-8')
    draw_text = ImageDraw.Draw(im)
    draw_text.text(
        (10, 10),
        text,
        font=font,
        fill='#1C0606')
    filename = f'./imgs/{str(uuid4())}.png'
    im.save(filename, 'PNG')
    return filename


def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def search_object(obj: str, dt):
    objs = [[i, similarity(i, obj)] for i in diary.get_allowed_objects(dt)]
    return sorted(objs, key=lambda x: x[1])[-1][0]

marks_menu = InlineKeyboardMarkup()
marks_menu.insert(InlineKeyboardButton('сегодня', callback_data='par_show_today'))
marks_menu.insert(InlineKeyboardButton('завтра', callback_data='par_show_tomorrow'))


@dp.message_handler(commands=['par'])
async def send_welcome(message: types.Message):
    await message.reply('пары', reply_markup=marks_menu)


@dp.message_handler(commands=['buses'])
async def send_welcome(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in diary_bus.get_available_names():
        markup.add(types.InlineKeyboardButton(
            i,
            callback_data=f'bus:{i}'
        ))
    await message.reply('Автобусы', reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('bus'))
async def awdwad(callback_query: types.CallbackQuery):
    name = callback_query.data.split(':')[1]
    schedule = diary_bus.get_schedule_from_name_day(name)
    tables = [f'{i}\n{schedule[i][1][0]}\n{diary_bus.schedule_bus_to_table(schedule[i])}' for i in schedule.keys()]
    
    for i in tables:
        text = i if i else 'Нет расписания'
        fi = to_img_bus(text)
        await callback_query.message.answer_photo(open(fi, 'rb'))
        os.remove(fi)
        # await callback_query.message.answer(i)


async def send_schedule(dt, message: types.Message, object):
    schedule = diary.get_diary(dt, object) if object in diary.get_allowed_objects(dt) else None
    text = diary.toText(schedule) if schedule is not None else 'Нет расписания\n\n\n'
    fi = to_img(text)
    await message.reply_photo(open(fi, 'rb'))
    os.remove(fi)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('par_show'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    dt = datetime.now() if callback_query.data == 'par_show_today' else datetime.now()+timedelta(days=1)
    txtdata = callback_query.data.split('_')[-1]
    dt = dt.date()
    marks = InlineKeyboardMarkup(row_width=1)
    objs = diary.get_allowed_objects(dt)
    if not len(objs):
        marks.insert(
            InlineKeyboardButton(
                'Нет пар',
                callback_data='no'
            )
        )
    for num, i in enumerate(objs):
        if not i:
            continue
        marks.insert(InlineKeyboardButton(i, callback_data=f'par_get_{txtdata}|{num}'))
    await callback_query.message.edit_text('пары: '+dt.strftime("%Y-%m-%d"))
    await callback_query.message.edit_reply_markup(marks)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('par_get'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    dt, num = callback_query.data.split('_')[-1].split('|')
    dt = datetime.now() if dt == 'today' else datetime.now()+timedelta(days=1)
    dt = dt.date()
    object = diary.get_allowed_objects(dt)[int(num)]
    db.set_last_object(callback_query.from_user.id, object)
    db.save()
    await send_schedule(dt, callback_query.message, object)


@dp.message_handler(commands=['par_today'])
async def send_welcome(message: types.Message):
    if not db.is_user_in_db(message.from_user.id):
        await message.reply('Тебя нет в бд')
        return
    dt = datetime.now()
    dt = dt.date()
    object = db.get_last_object(message.from_user.id)
    await send_schedule(dt, message, object)


@dp.message_handler(commands=['par_tomorrow'])
async def send_welcome(message: types.Message):
    if not db.is_user_in_db(message.from_user.id):
        await message.reply('Тебя нет в бд')
        return
    dt = datetime.now()+timedelta(days=1)
    dt = dt.date()
    object = db.get_last_object(message.from_user.id)
    await send_schedule(dt, message, object)


@dp.message_handler(commands=['db'])
async def send_welcome(message: types.Message):
    await message.answer(db.users)


@dp.message_handler(commands=['num'])
async def send_welcome(message: types.Message):
    await message.answer(f'Всего пользователей: {len(db.users)}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
