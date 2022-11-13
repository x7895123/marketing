import datetime


class Gift:
    ids1 = [int]
    amounts1 = [int]
    phone = str
    msg = str
    bill_id = str
    delay = int
    send_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S +6')
