import re

import phonenumbers
from dateutil.tz import *
from dateutil.parser import parse
from sanic.log import logger


def coalesce(*args):
    for x in args:
        if x is not None:
            logger.debug(f'coalesce {x}')
            return x


def clock_emoji(t):
    emoji = {
        "0000": "🕛",
        "0030": "🕧",
        "0100": "🕐",
        "0130": "🕜",
        "0200": "🕑",
        "0230": "🕝",
        "0300": "🕒",
        "0330": "🕞",
        "0400": "🕓",
        "0430": "🕟",
        "0500": "🕔",
        "0530": "🕠",
        "0600": "🕕",
        "0630": "🕡",
        "0700": "🕖",
        "0730": "🕢",
        "0800": "🕗",
        "0830": "🕣",
        "0900": "🕘",
        "0930": "🕤",
        "1000": "🕙",
        "1030": "🕥",
        "1100": "🕚",
        "1130": "🕦",
        "1200": "🕛",
        "1230": "🕧",
    }

    m = t.minute
    m = '00' if m < 30 else '30'
    t = t.strftime('%I') + m
    result = emoji.get(t)
    logger.debug(f'number_emoji {result}')
    return result


def number_emoji(n):
    emoji = {
        "0": "0️⃣",
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
        "10": "🔟"
    }

    number = ''
    for numeral in str(n):
        number += emoji.get(numeral)
    logger.debug(f'number_emoji {number}')
    return number


def correct_phone(phone):
    phone = re.sub("[^0-9]", "", phone)
    if len(phone) > 11 or len(phone) < 10:
        return None
    phone = phonenumbers.parse(phone, "KZ")
    phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
    logger.debug(f'correct_phone {phone}')
    return phone


def parse_date_tz(date_str):
    date = parse(date_str)
    logger.debug(f'date without tz {date}')
    # print(date)
    if date.tzinfo is None:
        date = date.replace(tzinfo=tzoffset(None, 21600))
    logger.debug(f'date with tz +6 {date}')
    # print(date)
    return date.strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    pass
