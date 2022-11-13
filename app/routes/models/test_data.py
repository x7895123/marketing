from routes.models.bill import Payment, Order, Bill

test_bill = Bill()
test_payment1 = Payment()
test_payment2 = Payment()
test_order1 = Order()
test_order2 = Order()

test_payment1 = {
    'payment_time': "2022-05-25 16:05:15",
    'payment_type': "cash",
    'payment_type_id': 0
}

test_payment2 = {
    'payment_time': "2022-05-25 16:05:15",
    'payment_type': "bank",
    'payment_type_id': 1
}

test_order1 = {
    'dish_id': 15,
    'dish_name': "суп",
    'quantity': 1,
    'price': 500
}

test_order2 = {
    'dish_id': 18,
    'dish_name': "шашлык",
    'quantity': 2,
    'price': 1500
}


test_bill = {
    'bill_no': "a123",
    "operation_time": "2022-05-25 16:05:15",
    "operation": "close",
    "amount": 3500,
    "phone": 77010000864,
    "dostyq_id": "",
    'payment': [test_payment1, test_payment2],
    "order": [test_order1, test_order2],
    "delivery_type": "table",
    "delivery_cost": 200
}

