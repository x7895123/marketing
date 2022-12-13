import datetime


class Payment:
    payment_type = str
    payment_type_id = int
    payment = float


class Bill:
    company_bill_id = str
    paytime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S +6')
    amount = 1.1
    phone = '+77010000864'
    payment = [Payment]


payment1 = Payment()
payment1.payment_type = 'cash'
payment1.payment_type_id = 0
payment1.payment = 100

payment2 = Payment()
payment2.payment_type = 'card'
payment2.payment_type_id = 1
payment2.payment = 200

DemoBill = Bill()
DemoBill.company_bill_id = '123'
DemoBill.paytime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S +6')
DemoBill.amount = 1.1
DemoBill.phone = '+77010000864'
DemoBill.payment = [payment1, payment2]
