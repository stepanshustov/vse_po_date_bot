import datetime

from addutions import *

sql = Sql()
f = open("chat_admin.txt", "r", encoding='utf-8')
admin_chat_id = int(f.read().strip())
f.close()

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def select_analysis(c: CallbackQuery, state: FSMContext, type_):
    mas = sql.get_user_data(c.from_user.id)
    async with state.proxy() as data:
        data['type'] = type_
    if not mas or len(mas) == 0:
        await bot.send_message(chat_id=c.from_user.id, text="""введите имя""")
        await Fsm.name.set()
    else:
        if type_ == "career":
            await bot.send_message(chat_id=c.from_user.id, text=career_txt, parse_mode='html')
        elif type_ == "plan_week":
            await bot.send_message(chat_id=c.from_user.id, text=plan_week_text, parse_mode='html')

        kb = InlineKeyboardMarkup()
        for k, el in enumerate(mas):
            kb.add(InlineKeyboardButton(el[0], callback_data=f'_name_num{k}'))
        kb.add(InlineKeyboardButton("+ добавить", callback_data="new_name"))
        await Fsm.chose_name.set()
        if type_ == "consultation":
            await bot.send_message(chat_id=c.from_user.id, text="""Выберите для кого""", reply_markup=kb)
        else:
            await bot.send_message(chat_id=c.from_user.id, text="""Выберите для кого сделать расчёт""", reply_markup=kb)


async def select_human(user_id, state, tp):
    await Fsm.pass_.set()
    if tp == 'year_analysis':
        await Fsm.year_analysis.set()
        await bot.send_message(chat_id=user_id, text="""Каждый год именно для вас становится важной одна из сторон жизни, у вашего личного года есть тема.
Какой она будет именно для вас, на чем держать фокус в течение года?
<strong>Введите год для составления прогноза и получите подсказку!</strong>""", parse_mode='html')
        return
    if tp == "consultation":
        numb = sql.get_user_number(user_id)
        await Fsm.number.set()
        if f'{numb}' == "-1":
            await bot.send_message(chat_id=user_id,
                                   text="Введите номер телефона, по которому можно будет с вами связаться")
        else:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            first_button = KeyboardButton(f'{numb}')
            markup.add(first_button)
            await bot.send_message(chat_id=user_id,
                                   text="Введите номер телефона, по которому можно будет с вами связаться",
                                   reply_markup=markup)
        return
    if tp == 'plan_week':
        await bot.send_message(chat_id=user_id,
                               text="""Введите для расчета плана на неделю дату первого дня в формате дд.мм.гггг""")
        await Fsm.select_date_plan_week.set()
        return
    if tp == "financial_code":
        async with state.proxy() as data:
            dat_ = data["date"]
            d, m, y = dat_
            await bot.send_message(chat_id=user_id,
                                   text=get_financial_code(d, m, y, data['name']), parse_mode='html',
                                   reply_markup=ikb_tarif)
        return
    if tp == "career":
        async with state.proxy() as data:
            dat_ = data["date"]
            d, m, y = dat_
            await bot.send_message(chat_id=user_id, text=get_career(d, m, y, data['name']), parse_mode='html',
                                   reply_markup=ikb_tarif)
        return
    if tp == "pythagoras":
        async with state.proxy() as data:
            d, m, y = data["date"]
            filename = get_pythagoras(d, m, y)
            photo = InputFile(filename)
            await bot.send_photo(chat_id=user_id, photo=photo, reply_markup=main_board)


async def menu_main(user_id):
    await Fsm.menu_chose.set()
    await bot.send_message(chat_id=user_id, text="Меню", reply_markup=main_board)


@dp.message_handler(commands=['start'], state='*')
async def start(m: Message):
    await m.answer(text=convert_html(hello_text.format(m.from_user.full_name)), reply_markup=main_board,
                   parse_mode='HTML', disable_web_page_preview=True)
    #     ikb_ = InlineKeyboardMarkup()
    #     ikb_.add(InlineKeyboardButton(text="Проверить подписку", callback_data="check_describe_of_canal"))
    #     await m.answer("""Подпишись на наш канал
    # @test_shustov""", reply_markup=ikb_)
    sql.add_user(m.from_user.id)
    await Fsm.pass_.set()


@dp.message_handler(commands=['set_this_chat'], state='*')
async def start(m: Message):
    await m.answer("Введите пароль для того, чтобы выполнить команду")
    await Fsm.admin_key.set()


@dp.message_handler(state=Fsm.admin_key)
async def fun(m: Message, state: FSMContext):
    global admin_chat_id
    if m.text.strip() == admin_key_for_set_chat:
        with open("chat_admin.txt", "w", encoding='utf-8') as fl:
            admin_chat_id = m.from_user.id
            print(admin_chat_id, file=fl)
            await m.answer("Удачно", reply_markup=main_board)
            return
    await m.answer("Неудачно")


@dp.callback_query_handler(state='*', text='menu')
async def funss(c: CallbackQuery, state: FSMContext):
    await menu_main(c.from_user.id)


@dp.callback_query_handler(state=Fsm.chose_name)
async def fun(c: CallbackQuery, state: FSMContext):
    if c.data == 'new_name':
        await bot.send_message(chat_id=c.from_user.id, text="""введите имя""")
        await Fsm.name.set()
        return
    if c.data[:9] == "_name_num":
        k = int(c.data[9:])
        name_, date_ = sql.get_user_data(c.from_user.id)[k]
        date_ = (date_ % 100, date_ // 100 % 100, date_ // 10000)
        async with state.proxy() as data:
            data['name'] = name_
            data['date'] = date_
            tp = data['type']
        await select_human(c.from_user.id, state, tp)


@dp.callback_query_handler(state='*')
async def fun(c: CallbackQuery, state: FSMContext):
    k = c.data.split(':')
    if len(k) == 2:
        if k[0] == 'analysis':
            await select_analysis(c, state, k[1])


@dp.message_handler(state=Fsm.name)
async def get_name(m: Message, state: FSMContext):
    text = m.text.strip().split()
    nm = ""
    for el in text:
        nm += el.capitalize() + ' '
    nm.strip()
    async with state.proxy() as data:
        data['name'] = nm
    await m.answer('''Введите дату рождения
    в формате дд.мм.гггг''')
    await Fsm.date.set()


@dp.message_handler(state=Fsm.date)
async def get_date(m: Message, state: FSMContext):
    try:
        dy, mh, yr = map(int, m.text.strip().replace('.', ' ').replace(',', ' ').split())

    except Exception:
        await m.answer("""Неверный формат ввода""")
        return
    try:
        dt = datetime.date(day=dy, month=mh, year=yr)
        if dt < datetime.date(day=1, month=1, year=1900):
            await m.answer("Пожалуйста вводите дату позже 1900 года")
            return
    except Exception as exp:
        await m.answer("""некорректная дата""")
        return

    async with state.proxy() as data:
        data['date'] = (dy, mh, yr)
        sql.add_new_human(m.from_user.id, data['name'], data['date'])
    #
    async with state.proxy() as data:
        tp = data['type']
    await select_human(m.from_user.id, state, tp)


@dp.message_handler(state=Fsm.select_date_plan_week)
async def fum_sel_dt(m: Message, state: FSMContext):
    try:
        dy, mh, yr = map(int, m.text.strip().replace('.', ' ').replace(',', ' ').split())
    except Exception:
        await m.answer("""Неверный формат ввода""")
        return
    try:
        dt = datetime.date(day=dy, month=mh, year=yr)
        if dt < datetime.date(day=1, month=1, year=1900):
            await m.answer("Пожалуйста вводите дату позже 1900 года")
            return
    except Exception:
        await m.answer("""некорректная дата""")
        return
    mas = [dt]
    for i in range(6):
        mas.append(mas[-1] + datetime.timedelta(days=1))
    async with state.proxy() as data:
        d, mon, y = data['date']
        ans_ = f"<strong>{data['name']} {d:02}.{mon:02}.{y:02}\n\nВаш план на 7 дней:</strong>\n\n"
    for el in mas:
        ans_ += get_plan_week_day(el, d, mon) + '\n\n'
    await m.answer(text=ans_, parse_mode='html', reply_markup=ikb_tarif)


@dp.message_handler(state=Fsm.number)
async def fun(m: Message, state: FSMContext):
    num = m.text.strip()
    num = num.replace(' ', '').replace('(', '').replace(')', '')
    num = num.replace('-', '').replace('\t', '')
    cnt = num.count('+')
    if (cnt == 1 and num[0] == '+' and num[1:].isdigit()) or (cnt == 0 and num.isdigit()):
        async with state.proxy() as data:
            data['number'] = num
        await m.answer("Основной запрос (отношения, карьера, финансы, и т.д)")
        await Fsm.zapros_.set()
        return
    await m.answer("Некорректный номер телефона")


@dp.message_handler(state=Fsm.zapros_)
async def fun(m: Message, state: FSMContext):
    if len(m.text.split()) > 150:
        await m.answer("Пожалуйста вводите менее 150 слов")
        return
    async with state.proxy() as data:
        data['zapros'] = m.text
    await Fsm.kratko_po_zaprosu.set()
    await m.answer(
        "Опишите кратко по запросу свою ситуацию, возникающие трудности и какой цели хотите достичь")


@dp.message_handler(state=Fsm.kratko_po_zaprosu)
async def fun(m: Message, state: FSMContext):
    if len(m.text.split()) > 150:
        await m.answer("Пожалуйста вводите менее 150 слов")
        return
    async with state.proxy() as data:
        data['kratko'] = m.text
    async with state.proxy() as data:
        kratko = data['kratko'].strip()
        zapros = data['zapros'].strip()
        number = data['number'].strip()
        name = data['name'].strip()
        date = f'{data["date"][0]:02}.{data["date"][1]:02}.{data["date"][2]}'
    sql.add_number(m.from_user.id, number)
    login = "отсутсвует"
    if m.from_user.username:
        login = f'@{m.from_user.username}'
    st = f"""
    Поступила новая заявка!
    Имя: {name}
    Дата рождения: {date}
    username: {login}
    id telegram: {m.from_user.id}
    номер телефона: {number}
    -----------
    Основной запрос:
    {zapros}
    -----------
    Кратко по запросу:
    {kratko}
    -----------
    """
    await bot.send_message(chat_id=admin_chat_id, text=st)
    await m.answer("""Ваша заявка принята!
Для согласования формата консультации, назначения даты и времени с вами скоро свяжутся.""",
                   reply_markup=main_board)
    await Fsm.pass_.set()


@dp.message_handler(state=Fsm.year_analysis)
async def get_year(m: Message, state: FSMContext):
    a = m.text.strip()
    if not a.isdigit():
        await m.answer("Пожалуйста введите число")
        return
    if not (1900 < int(a) < 2100):
        await m.answer("год должен быть не более 2100 и не менее 1900")
        return

    async with state.proxy() as data:
        data['year'] = int(a)
    res = 0
    async with state.proxy() as data:
        res = f'{data["date"][0]}{data["date"][1]}{data["year"]}'
        res = int(res) % 9
    if res == 0:
        res = 9
    await m.answer(convert_html(year_list[res - 1].format(a)),
                   parse_mode='HTML')
    await m.answer(
        text="""Обратите внимание что это короткая подсказка, определяющая вектор развития года.
📌 На <strong>личной консультации</strong> разберем любой запрос с учетом особенностей вашей  психоматрицы.
Вы получите: 
🔹 готовый план на весь год в виде детальной расшифровки каждого месяца: когда активно действовать, когда отдыхать и восстанавливать силы, когда начинать проекты, когда держать фокус на развитии или обратить внимание на здоровье
🔹 аудит событий прошедшего года
🔹 расчет нумерологических биоритмов для построения планов действий на любой период года
🔹 детальная расшифровка конкретных месяцев с учетом предполагаемых событий
 💠 <strong>БОНУС</strong> - инструкция по личному году в печатном или электронном виде""",
        reply_markup=full_analysis, parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
