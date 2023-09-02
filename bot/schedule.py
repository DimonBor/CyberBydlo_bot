import requests
import datetime
import json
import ssl
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder
from bot import setup


groups = {
    'КБ-01': '1002512',
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


class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


async def schedule_func(arg, kwarg, group_name, commands, message):

    urls = setup.loadURLs()
    output = ''

    if arg:
        DATE = str(arg)
        if DATE in commands['Завтра']:
            date_input = datetime.date.today() + datetime.timedelta(days=1)
            date_array = list(map(str, (str(date_input)).split("-")))
            date_r = date_array[2]+"."+date_array[1]+"."+date_array[0]
        else:
            try:
                date_input = datetime.datetime.strptime(DATE, '%d.%m.%Y')
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
        "method": "getSchedules",
        "id_grp": group_code,
        "date_beg": date_r,
        "date_end": date_r
    }

    try:
        session = requests.session()
        session.mount('https://', TLSAdapter())
        response = session.get('https://schedule.sumdu.edu.ua/index/json', params=Data, verify=False, timeout=10)
    except:
        await message.reply("Розкладу пизда, я не знаю, шо робити. 🌚")
        return 0

    schedule_json = json.loads(response.text)

    message_keyboard = InlineKeyboardBuilder()

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

        temp_string = f"<i>⌚️ {i['NAME_PAIR']}, {i['TIME_PAIR']} (<b>{action}</b>)</i>"

        if i['NAME_AUD']: temp_string += f" <b>[{i['NAME_AUD']}]</b>\n"
        else: temp_string += "\n"
        if i['ABBR_DISC']: temp_string += f"<b>{i['ABBR_DISC']}</b>\n"
        if i['NAME_FIO']: temp_string +=  f"{i['NAME_FIO']}\n"
        if i['REASON']: temp_string += f"<i>{i['REASON']}\n</i>"

        output += temp_string + "---------------------------------------------\n"

    output = (f"📅 <b>{date_r}</b> | <i>{weekdays[datetime.datetime.weekday(date_input)]}</i> | <i><b>{schedule_json[0]['NAME_GROUP']}</b></i>"
        "<b>\n**********************************\n"
        "</b>---------------------------------------------\n" + output)

    await message.reply(output, reply_markup=message_keyboard.as_markup())
