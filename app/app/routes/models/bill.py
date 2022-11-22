class Payment:
    payment_time = str
    payment_type = str
    payment_type_id = int
    payment = float


class Order:
    dish_id = int
    dish_name = str
    quantity = float
    price = float


class Bill:
    bill_no = str
    operation_time = str
    operation = str
    amount = float
    phone = str
    payment = Payment
    order = Order
    delivery_type = str
    delivery_cost = float
