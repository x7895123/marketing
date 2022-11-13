from dateutil.tz import *
from dateutil.parser import parse
from datetime import datetime


def parse_date_tz(self, date_str):
    date = parse(date_str)
    # self.logger.debug(f'date without tz {date}')
    print(date)
    if date.tzinfo is None:
        date = date.replace(tzinfo=tzoffset(None, 21600))
    # self.logger.debug(f'date with tz +6 {date}')
    print(date)
    return date.strftime('%Y-%m-%d %H:%M:%S')


send_date_str = '2022-10-01'
print(parse_date_tz(1, send_date_str))


