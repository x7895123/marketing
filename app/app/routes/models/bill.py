import datetime


class Payment:
    payment_type = 'cash'
    payment_type_id = 0
    payment = 1.1


class Bill:
    company_bill_id = '123'
    paytime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S +6')
    amount = 1.1
    phone = '+77010000864'
    payment = [Payment]
