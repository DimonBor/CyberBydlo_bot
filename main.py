import os
import logging
import hashlib
import random
import setup
import schedule
import sms_module
import call_module
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.emoji import emojize
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup

API_TOKEN = os.getenv('API_TOKEN')

CHAT_IDs = [-1001420903302, 551675002]

commands = {
    'Приветствие': {'\!привет', '\!Привет'},
    'Хуета': {'\!хуета', '\!Хуета', 'Хуета', 'хуета', 'ясно', 'Ясно', 'хуита'},
    'ММММ': {'ммм','мммм','ммммм', 'Ммм','Мммм','Мммм' 'Ммммм','МММ','МММММ','ММММ', 'мммммм','ммммммм','Ммммммм'},
    'ХОЙ': {'Хой','ХОЙ','хой', 'панки', 'Панки', 'ПАНКИ'},
    'СОСАТЬ': {
        '!\ИН', '!\ин', '\!ІН', '\!ін', 'ИН', 'Ин', 'ин', 'ІН', 'ін', 'ИН\-01', 'ин\-01', 'СНАУ', 'Снау', 'снау',
        'Коваль', 'коваль', 'КОВАЛЬ'
    },
    'Пары': {'\!Пары', '\!пары'},
    'Буль': {'!Буль','\!буль'},
    'Шиза': {'\!Шиза', '\!шиза', '\!Диньдон', '\!диньдон'},
    'Завтра': {'завтра', 'Завтра'},
}

logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands=['me'])
async def me_command(message: types.Message):

    if message.chat.id in CHAT_IDs:
        await bot.delete_message(message_id = message.message_id, chat_id = message.chat.id)
        message_str = message.parse_entities(as_html=False)
        message_str = message_str[3:]
        message_str = "<b>" + str(message.from_user.first_name) + message_str + "</b>"
        await message.answer(message_str)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):

    if message.chat.id in CHAT_IDs:
        await message.answer(
            "<b>Справка по командам</b>\n\n"
            "1. <i>!пары [аргумент]</i> - расписание на указаную дату. Можно использовать"
            " <i>завтра</i> или дату в формате 'dd.mm.yyyy'. Пустой аргумент вернет расписание на сегодня.\n"
            "2. <i>/me</i> - привет из сампа. У нас RP сервер.\n"
            "3. <i>/help</i> - вызывает это сообщение.\n"
            "4. <i>/set_group [название группы]</i> - установаить группу.\n"
            "-----------\n"
            "Для админов:\n"
            "/add_url [имя_группы]|[имя_предмета_в_расписании]|[action(лаба/лекция)]|[ссылка] - добавляет ссылку на пару.\n"
            "/delete_url [имя_группы]|[имя_предмета_в_расписании]|[action(лаба/лекция)] - удаляет ссылку на пару.\n"+
            str(emojize("\n P.S. Всё остальное не допилено в силу моей лени :sweat_smile:"))
        )


@dp.message_handler(commands=['set_group'])
async def set_group(message: types.Message):

    if message.chat.id in CHAT_IDs:
        message_str = message.parse_entities(as_html=False)
        message_array = list(map(str, message_str.split()))
        try: group_name = message_array[1]
        except:
            await message.reply("Укажите название группы!")
            return 0

        group_name = group_name[:2]+group_name[3:]

        if group_name not in schedule.groups:
            await message.reply("Укажите название группы!")
            return 0

        if setup.setGroup(message.from_user.id, group_name) == "OK":
             await message.reply(f"Группа <b>{group_name}</b> успешно установлена")
        else:
            await message.reply("Похоже, что я вас почему-то не знаю. @Dimon_Bor, быдло, иди сюда.")


@dp.message_handler(commands=['add_user'])
async def add_user(message: types.Message):

    if message.from_user.id in CHAT_IDs:
        message_str = message.parse_entities(as_html=False)
        message_array = list(map(str, message_str.split()))
        try: user_id = message_array[1]
        except:
            await message.reply("Пиши нормально, быдло.")
            return 0
        try: group_name = message_array[2]
        except:
            await message.reply("Пиши нормально, быдло.")
            return 0

        group_name = group_name[:2]+group_name[3:]

        if setup.addUser(user_id, group_name) == "OK":
             await message.reply(f"Юзер <b>{user_id} | {group_name}</b> успешно добавлен")
        else:
            await message.reply("Он уже есть там, дебил")


@dp.message_handler(commands=['get_users'])
async def get_users(message: types.Message):

    if message.from_user.id in CHAT_IDs:
        users_list = setup.loadUsers()
        output = str()
        for user in users_list:
            output += f"{user[0]} | {user[1]}\n"

        await message.reply(output)


@dp.message_handler(commands=['get_id'])
async def get_id(message: types.Message):

    if message.from_user.id in CHAT_IDs:

        await message.reply(f"User ID is <b>{message.reply_to_message.from_user.id}</b>")


@dp.message_handler(commands=['add_url'])
async def addURL(message: types.Message):

    if message.from_user.id in CHAT_IDs:
        argsStr = message.get_args()
        argsArray = argsStr.split("|")
        groupCode = schedule.groups[argsArray[0]]
        response = setup.addUrl(groupCode, argsArray[1], argsArray[2], argsArray[3])
        if response == "OK": await message.reply("Added Successfully!")
        else: await message.reply(response)
    else:
        await message.reply("Only for Admins!")


@dp.message_handler(commands=['delete_url'])
async def deleteURL(message: types.Message):

    if message.from_user.id in CHAT_IDs:
        argsStr = message.get_args()
        argsArray = argsStr.split("|")
        groupCode = schedule.groups[argsArray[0]]
        response = setup.deleteURL(groupCode, argsArray[1], argsArray[2])
        if response == "OK": await message.reply("Deleted Successfully!")
        else: await message.reply(response)
    else:
        await message.reply("Only for Admins!")


@dp.message_handler(commands=['get_urls'])
async def getURLs(message: types.Message):

    if message.from_user.id in CHAT_IDs:
        urlsList = setup.loadURLs()
        await message.reply(str(urlsList))
    else:
        await message.reply("Only for Admins!")


@dp.message_handler(lambda message: message.chat.id in CHAT_IDs)
async def reply(message: types.Message):

    users_list = setup.loadUsers()
    message_str = message.parse_entities(as_html=False)
    message_array = list(map(str, message_str.split()))
    command = message_array[0]
    arg = str()
    kwarg = str()
    user_id = str(message.from_user.id)
    group_name = str()

    try: kwarg = message_array[2]
    except: pass
    try: arg = message_array[1]
    except: pass

    found = False
    for user in users_list:
        if user[0] == user_id:
            found = True
            group_name = user[1]
    if not found:
        setup.addUser(user_id, "")
        await message.reply("Похоже, что вы новый пользователь. Я запомнил вас, но что-бы смотреть расписание установите группу с помощью /set_group [название].")

    if command in commands['Хуета']:
        if command == "ясно" or command == "Ясно":
            if arg == "хуита" or arg == "хуета":
                await message.reply("И не говори")

        else: await message.reply("И не говори")

    elif command in commands['Приветствие']:
        await message.reply("Привет, я КиберБыдло бот!")

    elif command in commands['Пары']:
        if group_name in schedule.groups:
            await schedule.schedule_func(arg, kwarg, group_name, commands, message)
        else: await message.reply("Установите группу!")
    elif command in commands['Буль']:
        await message.reply(emojize("Буль, буль, буль....:new_moon_with_face:"))
        sms_module.sms_service(arg)

    elif command in commands['Шиза']:
        await message.reply(emojize("Динь-дон....:new_moon_with_face:"))
        call_module.call_service(arg)

    elif command in commands['СОСАТЬ']:
        if len(message_array) == 1: await message.reply("СОСАТЬ!")

    elif command in commands['ХОЙ']:
        await message.reply("ХОООООЙ!")

    elif command in commands['ММММ'] and not arg:
        await message.reply("Хуета")

    else:
        random_number = random.randint(0, 300)
        if random_number == 100:
            await message.reply(emojize("Ты знал, что ты дурачёк?:see_no_evil:"))
        elif random_number == 200:
            await message.reply(emojize("Когда плац подметать?:new_moon_with_face:"))


@dp.message_handler()
async def spam(message: types.Message):
    await message.reply("ПАНКИ ХОЙ, ПОПСУ ДОЛОЙ!")


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    random_number = random.randint(0, 100)
    text = emojize(str(f':new_moon_with_face:{inline_query.from_user.first_name} быдло на {random_number}%:new_moon_with_face:'))
    text_1 = f'<b><i>* {inline_query.from_user.first_name} {inline_query.query}</i></b>'
    result_id: str = hashlib.md5(text.encode()).hexdigest()

    bot_button = InlineKeyboardButton('БыдлоБот', switch_inline_query_current_chat='')
    bot_keyboard = InlineKeyboardMarkup().add(bot_button)

    item_1 = InlineQueryResultArticle(
        id=1,
        title='Памагити(HELP)',
        input_message_content=InputTextMessageContent(emojize(
            "Это инлайн версия @CyberBydlo_bot. Пока вы можете читать это и "
            "радоваться тому, какое вы быдло.\n"
            "Чат-версия бота недоступна простым смертным, а только истинному КиберБыдлу.\n\n"
            "Пы.Сы. Можете ему написать в лс, но ничего интересного там нет.:japanese_goblin:"
        )),
        reply_markup=bot_keyboard,
        thumb_url='https://img.flaticon.com/icons/png/512/682/682055.png?size=1200x630f&pad=10,10,10,10&ext=png&bg=FFFFFFFF'
    )
    item_2 = InlineQueryResultArticle(
        id=2,
        title=emojize('На сколько ты быдло:new_moon_with_face:'),
        input_message_content=InputTextMessageContent(text),
        reply_markup=bot_keyboard,
        thumb_url='https://i.pinimg.com/originals/72/dc/f7/72dcf7e6266ba591e2ed103170bbfa30.jpg'
    )
    item_3 = InlineQueryResultArticle(
        id=3,
        title='/me',
        input_message_content=InputTextMessageContent(text_1),
        thumb_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUM3P2Uddubo9DdDU1QhvFEZ1R0wtm--oPmA&usqp=CAU'
    )


    await bot.answer_inline_query(inline_query.id, results=[item_1, item_2, item_3], cache_time=1)


executor.start_polling(dp, skip_updates=True)
