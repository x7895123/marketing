class Payment:
    payment_type = str
    payment_type_id = int
    payment = 1.1


class Bill:
    company_bill_id = str
    paytime = str
    amount = float
    phone = '+77010000864'
    payment = Payment
