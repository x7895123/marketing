class Payment:
    payment_type = str
    payment_type_id = int
    payment = float


class Bill:
    company_bill_id = str
    paytime = str
    amount = float
    phone = str
    payment = Payment
