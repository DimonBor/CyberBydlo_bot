import asyncio
import os
import logging
import hashlib
import random
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardButton, \
    InlineKeyboardMarkup

from bot import setup, schedule, sms_module, call_module

API_TOKEN = os.getenv('API_TOKEN')

CHAT_IDs = [-1001420903302, 551675002]

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

commands = {
    'Привітання': {'!привет', '!Привет', '!привіт', '!Привіт'},
    'Хуета': {'!хуета', '!Хуета', 'Хуета', 'хуета', 'ясно', 'Ясно', 'хуита'},
    'ММММ': {'ммм', 'мммм', 'ммммм', 'Ммм', 'Мммм', 'Мммм' 'Ммммм', 'МММ', 'МММММ', 'ММММ', 'мммммм', 'ммммммм',
             'Ммммммм'},
    'СОСАТЬ': {
        '!ИН', '!ин', '!ІН', '!ін', 'ИН', 'Ин', 'ин', 'ІН', 'ін', 'ИН-01', 'ин-01', 'СНАУ', 'Снау', 'снау',
    },
    'Пары': {'!Пары', '!пары', '!пари', '!Пари'},
    'Буль': {'!Буль', '!буль'},
    'Шиза': {'!Шиза', '!шиза', '!Диньдон', '!диньдон'},
    'Завтра': {'завтра', 'Завтра'},
}


@dp.message(Command('me'))
async def me_command(message: types.Message):
    if message.chat.id in CHAT_IDs:
        await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
        message_str = message.text
        message_str = message_str[3:]
        message_str = "<b>" + str(message.from_user.first_name) + message_str + "</b>"
        await message.answer(message_str)


@dp.message(Command('help'))
async def help_command(message: types.Message):
    if message.chat.id in CHAT_IDs:
        await message.answer(
            "<b>Справка по командах</b>\n\n" +
            "1. <i>!пари [аргумент]</i> - розклад на вкану дату. Можна використовувати" +
            " <i>завтра</i> або дату в форматі 'dd.mm.yyyy'. Пустий аргумент поверне розклад на сьогодні.\n" +
            "2. <i>/me</i> - У нас RP сервер.\n" +
            "3. <i>/help</i> - викликає це повідомлення.\n" +
            "4. <i>/set_group [назва групи]</i> - встановити групу.\n" +
            "-----------\n" +
            "Для мене справка, бо забуваю як воно працює:\n" +
            "/add_user [ID] [назва групи] - додати або перезаписати користувача.\n" +
            "/get_users - отримати список усіх користувачів.\n" +
            "/get_id - отримати ID юзера.\n" +
            "/add_url [назва групи]|[назва предмету в розкладі]|[action(лаба/лекція)]|[посилання] - додає посилання на пару.\n" +
            "/delete_url [назва групи]|[назва предмету в розкладі]|[action(лаба/лекція)]|[посилання] - видаляє посилання на пару.\n" +
            "/get_urls - повернути JSON з посиланнями.\n" +
            "\n P.S. Все що недопилене, таким і залишиться в пам'ятник тому, яку діч я ліпив на першому курсі. ☺️"
        )


@dp.message(Command('set_group'))
async def set_group(message: types.Message):
    if message.chat.id in CHAT_IDs:
        message_str = message.text
        message_array = list(map(str, message_str.split()))
        try:
            group_name = message_array[1]
        except:
            await message.reply("Вкажіть назву групи!")
            return 0

        if group_name not in schedule.groups:
            await message.reply("Вкажіть назву групи!")
            return 0

        if setup.setGroup(message.from_user.id, group_name) == "OK":
            await message.reply(f"Група <b>{group_name}</b> успішно встановлена.")
        else:
            await message.reply("Схоже, що я вас чомусь не знаю.")


@dp.message(Command('add_user'))
async def add_user(message: types.Message):
    if message.from_user.id in CHAT_IDs:
        message_str = message.text
        message_array = list(map(str, message_str.split()))
        try:
            user_id = message_array[1]
        except:
            await message.reply("Пиши нормально, бидло.")
            return 0
        try:
            group_name = message_array[2]
        except:
            await message.reply("Пиши нормально, бидло.")
            return 0

        group_name = group_name[:2] + group_name[3:]

        if setup.addUser(user_id, group_name) == "OK":
            await message.reply(f"Юзер <b>{user_id} | {group_name}</b> доданий успішно")
        else:
            await message.reply("Він там уже є, бидло!")


@dp.message(Command('get_users'))
async def get_users(message: types.Message):
    if message.from_user.id in CHAT_IDs:
        users_list = setup.loadUsers()
        output = str()
        for user in users_list:
            output += f"{user[0]} | {user[1]}\n"

        await message.reply(output)


@dp.message(Command('get_id'))
async def get_id(message: types.Message):
    if message.from_user.id in CHAT_IDs:
        await message.reply(f"User ID is <b>{message.reply_to_message.from_user.id}</b>")


@dp.message(Command('add_url'))
async def addURL(message: types.Message):
    if message.from_user.id in CHAT_IDs:
        argsStr = message.get_args()
        argsArray = argsStr.split("|")
        groupCode = schedule.groups[argsArray[0]]
        response = setup.addUrl(groupCode, argsArray[1], argsArray[2], argsArray[3])
        if response == "OK":
            await message.reply("Added Successfully!")
        else:
            await message.reply(response)
    else:
        await message.reply("Only for Admins!")


@dp.message(Command('delete_url'))
async def deleteURL(message: types.Message):
    if message.from_user.id in CHAT_IDs:
        argsStr = message.get_args()
        argsArray = argsStr.split("|")
        groupCode = schedule.groups[argsArray[0]]
        response = setup.deleteURL(groupCode, argsArray[1], argsArray[2])
        if response == "OK":
            await message.reply("Deleted Successfully!")
        else:
            await message.reply(response)
    else:
        await message.reply("Only for Admins!")


@dp.message(Command('get_urls'))
async def getURLs(message: types.Message):
    if message.from_user.id in CHAT_IDs:
        urlsList = setup.loadURLs()
        await message.reply(str(urlsList))
    else:
        await message.reply("Only for Admins!")


@dp.message(F.chat.func(lambda chat: chat.id in CHAT_IDs))
async def reply(message: types.Message):
    users_list = setup.loadUsers()
    message_str = message.text
    message_array = list(map(str, message_str.split()))
    command = message_array[0]
    arg = str()
    kwarg = str()
    user_id = str(message.from_user.id)
    group_name = str()

    try:
        kwarg = message_array[2]
    except:
        pass
    try:
        arg = message_array[1]
    except:
        pass

    found = False
    for user in users_list:
        if user[0] == user_id:
            found = True
            group_name = user[1]
    if not found:
        setup.addUser(user_id, "")

    if command in commands['Хуета']:
        if command == "ясно" or command == "Ясно":
            if arg == "хуита" or arg == "хуета" or arg == "хуіта":
                await message.reply("І не кажи")

        else:
            await message.reply("І не кажи")

    elif command in commands['Привітання']:
        await message.reply("Привіт, я КіберБидло бот!")

    elif command in commands['Пары']:
        if group_name in schedule.groups:
            await schedule.schedule_func(arg, kwarg, group_name, commands, message)
        else:
            await message.reply("Встановіть групу!")
    elif command in commands['Буль']:
        await message.reply("Буль, буль, буль....🌚")
        sms_module.sms_service(arg)

    elif command in commands['Шиза']:
        await message.reply("Динь-дон....🌚")
        call_module.call_service(arg)

    elif command in commands['СОСАТЬ']:
        if len(message_array) == 1: await message.reply("СОСАТЬ!")

    elif command in commands['ММММ'] and not arg:
        await message.reply("Хуіта")

    else:
        random_number = random.randint(0, 300)
        if random_number == 100:
            await message.reply("Дурка по тобі плаче 🙈")
        elif random_number == 200:
            await message.reply("Коли плац замітати? 🌚")


@dp.message()
async def spam(message: types.Message):
    await message.reply("Киш, атсюдава!")


@dp.message()
async def inline_echo(inline_query: InlineQuery):
    random_number = random.randint(0, 100)
    text = f'🌚 {inline_query.from_user.first_name} бидло на {random_number}% 🌚'
    text_1 = f'<b><i>* {inline_query.from_user.first_name} {inline_query.query}</i></b>'
    result_id: str = hashlib.md5(text.encode()).hexdigest()

    bot_button = InlineKeyboardButton('БидлоБот', switch_inline_query_current_chat='')
    bot_keyboard = InlineKeyboardMarkup().add(bot_button)

    item_1 = InlineQueryResultArticle(
        id=1,
        title='Памагіті(HELP)',
        input_message_content=InputTextMessageContent(
            "Це інлайн функціонал @CyberBydlo_bot. Поки ви можете тільки це читати та "
            "радіти тому, яке ви бидло.\n"
            "Чат-версія недоступна простим смертним, а тільки істинному КіберБидлу.\n\n"
            "P.S. Можете йому написати в лс, але нічого цікавого там немає.👺"
        ),
        reply_markup=bot_keyboard,
        thumb_url='https://img.flaticon.com/icons/png/512/682/682055.png?size=1200x630f&pad=10,10,10,10&ext=png&bg=FFFFFFFF'
    )
    item_2 = InlineQueryResultArticle(
        id=2,
        title='На скільки ти бидло 🌚',
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


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
