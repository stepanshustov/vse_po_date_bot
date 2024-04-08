import math
from texts import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import *
from aiogram.dispatcher import *
import datetime
import sqlite3
from PIL import Image, ImageDraw, ImageFont

TOKEN = "6752555373:AAGLrj8B_jcKy0VhDE7P5qsT-xWCdexz4Lk"

CANAL_ID = -1002030907197

admin_key_for_set_chat = "O0D_oc81L6"


def get_pythagoras(d, m, ye):
    text = [['Характер', 'Здоровье', 'Удача', 'Цель'],

            ['Энергия', 'Логика', 'Долг', 'Семья'],

            ['Интерес', 'Труд', 'Память', 'Привычки']]
    dc = {'Характер': '1',
          'Энергия': '2',
          'Интерес': '3',
          'Здоровье': '4',
          'Логика': '5',
          'Труд': '6',
          'Удача': '7',
          'Долг': '8',
          'Память': '9',
          }
    f = 20
    cs = 200
    a = d % 10 + d // 10 + m % 10 + m // 10 + ye % 10 + ye // 10 % 10 + ye // 100 % 10 + ye // 1000
    b = a % 10 + a // 10
    c = a - int(str(d)[0]) * 2
    k = c // 10 + c % 10
    st = f'{d}{m}{ye}{a}{b}{c}{k}'
    mas = [[0, 0, 0, 0] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            mas[i][j] = st.count(dc[text[i][j]])
    mas[0][3] = sum(mas[0])
    mas[1][3] = sum(mas[1])
    mas[2][3] = sum(mas[2])
    temp = f'{mas[0][2] + mas[1][1] + mas[2][0]}'
    if temp == '0':
        temp = '   — '
    bt = f'{mas[0][1] + mas[1][1] + mas[2][1]}'
    if bt == '0':
        bt = '   — '

    width, height = 840, 1050
    im = Image.new("RGB", (width, height), color='#ffffff')
    draw = ImageDraw.Draw(im)

    font = ImageFont.truetype("arial.ttf", 26, encoding='UTF-8')
    font2 = ImageFont.truetype("arial.ttf", 32, encoding='UTF-8')
    for i in range(3):
        for j in range(3):
            x, y = f + cs * j, f + cs * (i + 1)
            draw.rectangle(((x, y), (x + 190, y + 190)), '#D4E3FF')

            draw.text((x + 15, y + 10), text[i][j], font=font, fill='black')
            txt_ = f'{mas[i][j]}'
            if i < 3 and j < 3:
                txt_ = f'{mas[i][j] * dc[text[i][j]]}'
            if mas[i][j] == 0:
                txt_ = '   — '
            draw.text((x + 30, y + cs // 2.5), txt_, font=font2,
                      fill='red')
    j = 3
    for i in range(3):
        x, y = f + cs * j, f + cs * (i + 1)
        draw.rectangle(((x, y), (x + 190, y + 190)), '#FCF6E6')

        draw.text((x + 15, y + 10), text[i][j], font=font, fill='black')
        txt_ = f'{mas[i][j]}'
        if i < 3 and j < 3:
            txt_ = f'{mas[i][j] * dc[text[i][j]]}'
        if mas[i][j] == 0:
            txt_ = '   — '
        draw.text((x + 30, y + cs // 2.5), txt_, font=font2,
                  fill='red')
    draw.rectangle(((f + cs * 3, f), (f + cs * 3 + 190, f + 190)), '#FCF6E6')
    draw.text((13 + f + cs * 3, 10 + f), "Темперамент", font=font, fill='black')
    draw.text((30 + f + cs * 3, f + cs // 2.5), temp, font=font2, fill='red')
    draw.rectangle(((f + cs, f + cs * 4), (f + cs + 190, f + cs * 4 + 190)), '#FCF6E6')
    draw.text((15 + f + cs, 10 + f + cs * 4), "Быт", font=font, fill='black')
    draw.text((30 + f + cs, f + cs * 4 + cs // 2.5), bt, font=font2, fill='red')

    font3 = ImageFont.truetype("arial.ttf", 50, encoding='UTF-8')
    draw.text((50, 50), f'{d:02}.{m:02}.{ye}', fill='blue', font=font3)

    im.save("ff.jpg")
    return 'ff.jpg'


def rec_career(n: int):
    if n < 12:
        if n == 10:
            return 0
        if n == 11:
            return 9
        return n - 1
    k = 0
    while n:
        k += n % 10
        n //= 10
    return rec_career(k)


def get_career(d: int, m: int, y: int, name: str):
    c = d // 10 + d % 10 + m // 10 + m % 10
    c += y % 10 + y // 10 % 10 + y // 100 % 10 + y // 1000
    i = rec_career(c)
    return convert_html(f"""<strong>{name}</strong> <strong>{d:02}.{m:02}.{y}</strong>

{career_list_txt[i]}
- - - - - - - - - - - - - - &gt;&gt;&gt;
{career_end_txt}""")


def get_financial_code(d, m, y, name):
    return convert_html(f"""<strong>{name} {d:02}.{m:02}.{y}\n

Ваш финансовый код - {sum_help(d)}{sum_help(m)}{sum_help(y)}{sum_help(d, m, y)}</strong>

{financial_code_text}""")


def sum_help(*args, f=True):
    res = 0
    for el in args:
        res += el
    res %= 9
    if f and not res:
        res = 9
    return res


def get_plan_week_day(dt: datetime.datetime, day: int, month: int):
    d, m, y = dt.day, dt.month, dt.year
    return f"<strong>{d:02}.{m:02}.{y}</strong> - {list_plan_week[sum_help(d, m, y, month, day, f=False)]}"


def convert_html(st: str):
    st = st.replace('<p>', '').replace('</p>', '\n')
    st = st.replace('<br />', '\n')
    st = st.replace('&nbsp;', ' ')
    st = st.replace(' &ndash;', ' ')
    st = st.replace('\n\n', '\n')
    st = st.replace('&bull;', '•')
    st = st.replace('&laquo;', '«')
    st = st.replace('&raquo;', '»')
    return st


main_board = InlineKeyboardMarkup()
main_board.add(InlineKeyboardButton(text="РАСЧЁТ МАТРИЦЫ".capitalize(), callback_data="analysis:pythagoras"))
main_board.add(InlineKeyboardButton(text="КОНСУЛЬТАЦИЯ", callback_data="analysis:consultation"))
main_board.add(InlineKeyboardButton(text="ПРИЗВАНИЕ/ПРОФЕССИЯ".capitalize(), callback_data="analysis:career"))
main_board.add(InlineKeyboardButton(text="ФИНАНСОВЫЙ КОД".capitalize(), callback_data="analysis:financial_code"))
main_board.add(InlineKeyboardButton(text="ПЛАН НА НЕДЕЛЮ".capitalize(), callback_data="analysis:plan_week"))
main_board.add(InlineKeyboardButton(text="ПРОГНОЗ НА ГОД".capitalize(), callback_data="analysis:year_analysis"))

full_analysis = main_board

ikb_tarif = main_board


class Fsm(StatesGroup):
    menu_chose = State()
    name = State()
    date = State()
    year_analysis = State()
    pass_ = State()
    admin_key = State()
    chose_name = State()
    tariff_karusel = State()
    number = State()
    zapros_ = State()
    kratko_po_zaprosu = State()
    vaznue_sobutiy = State()
    select_date_plan_week = State()


async def date_to_int(date):
    return date[2] * 10000 + date[1] * 100 + date[0]


class Sql:
    def __init__(self, bd="users.db"):
        self.con = sqlite3.Connection(bd)
        self.cur = self.con.cursor()

    def check_user(self, user_id: int):
        mas = self.cur.execute(f"""SELECT id FROM users WHERE id = {user_id}""").fetchall()

        return len(mas) == 1

    def get_user_data(self, user_id: int):
        if not self.check_user(user_id):
            return False
        return self.cur.execute(f"SELECT * FROM user_{user_id}").fetchall()

    def get_user_number(self, user_id: int):
        return self.cur.execute(f"SELECT number FROM users WHERE id = {user_id}").fetchall()[0][0]

    def add_user(self, user_id):
        if self.check_user(user_id):
            return False
        self.cur.execute(
            f"""INSERT INTO users(id, number) VALUES('{user_id}', '-1')""")
        self.cur.execute(f"""
                    CREATE TABLE user_{user_id} (

                    name TEXT,

                    date INTEGER)""")
        self.con.commit()

    def add_new_human(self, user_id: int, name: str, date):
        if self.check_user(user_id):
            self.cur.execute(
                f"""INSERT INTO user_{user_id}(name, date) VALUES('{name}', {date[2] * 10000 + date[1] * 100 + date[0]})
                            """)
            self.con.commit()
            return True
        return False

    def add_number(self, user_id: int, number):
        self.cur.execute(f"""UPDATE users
                             SET number = '{number}'
                             WHERE id = {user_id}""")
        self.con.commit()


if __name__ == '__main__':
    get_pythagoras(22, 12, 2022)
