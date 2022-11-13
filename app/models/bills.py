from tortoise import Model, fields


class Bills(Model):
    id = fields.IntField(pk=True)
    office = fields.TextField()
    cashdesk = fields.TextField()
    cashier = fields.TextField()
    bill = fields.TextField()
    used = fields.TextField()
    amount = fields.IntField()
    pc = fields.IntField()
    phone = fields.TextField()
    paytime = fields.DatetimeField()

    def __str__(self):
        return f"Bill {self.id}, {self.bill}, {self.phone}, {self.amount}"