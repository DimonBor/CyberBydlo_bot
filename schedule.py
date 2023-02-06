import requests
import datetime
import json
import setup
import urllib3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup\


requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

groups = {
    'КБ-01/1': '1002732',
    'КБ-01/2': '1002733',
    'КБ-11': '1003272'
}

weekdays = {
    0: "Понеділок",
    1: "Вівторок",
    2: "Середа",
    3: "Четвер",
    4: "П'ятниця",
    5: "Субота ",
    6: "Неділя",
}


async def schedule_func(arg, kwarg, group_name, commands, message):

    urls = setup.loadURLs()
    group_code = str()
    output = ''
    stars = str()
    date_r = str()
    action = str()

    if arg:
        DATE = str(arg)
        if DATE in commands['Завтра']:
            date_input = datetime.date.today() + datetime.timedelta(days=1)
            date_array = list(map(str, (str(date_input)).split("-")))
            date_r = date_array[2]+"."+date_array[1]+"."+date_array[0]
        else:
            try:
                date_input = datetime.datetime.strptime(DATE, '%d\.%m\.%Y')
                date_array = list(map(str, (str(date_input.date())).split("-")))
                date_r = date_array[2]+"."+date_array[1]+"."+date_array[0]

            except ValueError:
                await message.reply("Пиши нормально, шизік. 🌚🚑")
                return 0

    elif kwarg:
        await message.reply("Пиши нормально, шизік. 🌚🚑")
        return 0

    else:
        date_input = datetime.date.today()
        date_array = list(map(str, (str(date_input)).split("-")))
        date_r = date_array[2]+"."+date_array[1]+"."+date_array[0]

    group_code = groups[group_name]

    if not group_code:
        output = "Вашої групи немає, лмао😄"
        await message.reply(output)
        return 0

    Data = {
        "id_grp": group_code,
        "date_beg": date_r,
        "date_end": date_r
    }

    try:
        response = requests.post('https://schedule.sumdu.edu.ua/index/json', data=Data, verify=False, timeout=10)
    except:
        await message.reply("Розкладу пизда, я не знаю, шо робити. 🌚")
        return 0

    schedule_json = json.loads(response.text)

    message_keyboard = InlineKeyboardMarkup()

    if not len(schedule_json):
        output = "Схоже, що пар немає 😇"
        await message.reply(output)
        return 0

    for i in schedule_json:
        action = i['NAME_STUD']
        try:
            if urls[group_code][i['ABBR_DISC']][action]:
                temp_button = InlineKeyboardButton(i['ABBR_DISC'], url=urls[group_code][i['ABBR_DISC']][action])
                if message_keyboard["inline_keyboard"]:
                    if temp_button not in message_keyboard["inline_keyboard"][0]:
                        message_keyboard.insert(temp_button)
                else: message_keyboard.insert(temp_button)
        except: pass

        temp_string = f"<i>⌚️ {i['TIME_PAIR']} (<b>{action}</b>)</i>"

        if i['NAME_AUD']: temp_string += f" <b>[{i['NAME_AUD']}]</b>\n"
        else: temp_string += "\n"
        if i['ABBR_DISC']: temp_string += f"<b>{i['ABBR_DISC']}</b>\n"
        if i['NAME_FIO']: temp_string +=  f"{i['NAME_FIO']}\n"
        if i['REASON']: temp_string += f"<i>{i['REASON']}\n</i>"

        output = temp_string + "---------------------------------------------\n" + output

    output = (f"📅 <b>{date_r}</b> | <i>{weekdays[datetime.datetime.weekday(date_input)]}</i> | <i><b>{schedule_json[0]['NAME_GROUP']}</b></i>"
        "<b>\n**********************************\n"
        "</b>---------------------------------------------\n" + output)

    await message.reply(output, reply_markup = message_keyboard)
