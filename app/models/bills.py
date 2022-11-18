from tortoise import Model, fields


class marketing_bill(Model):
    id = fields.IntField(pk=True)
    create_ts = fields.DatetimeField(auto_now_add=True)
    company = fields.CharField(max_length=200)
    cashdesk = fields.CharField(max_length=200)
    bill_no = fields.CharField(max_length=200, unique=True)
    phone = fields.CharField(max_length=50)
    amount = fields.IntField()
    paytime = fields.DatetimeField()
    bill = fields.JSONField()
    task = fields.JSONField(null=True)

    cashbacks: fields.ReverseRelation["marketing_cashback"]

    def __str__(self):
        return f"Bill {self.id}, {self.bill_no}, {self.phone}, {self.amount}"


class marketing_cashback(Model):
    id = fields.IntField(pk=True)
    phone = fields.CharField(max_length=50, index=True)
    create_ts = fields.DatetimeField(auto_now_add=True)
    sent_ts = fields.DatetimeField(null=True)
    expiration_ts = fields.DatetimeField(null=True)
    deal = fields.JSONField(null=True)
    deal_status = fields.CharField(max_length=200, null=True)
    error_message = fields.CharField(max_length=255, null=True)
    recipient_address = fields.CharField(max_length=200, null=True)
    contract_address = fields.CharField(max_length=200, null=True)

    id_bill: fields.ForeignKeyRelation[marketing_bill] = fields.ForeignKeyField(
        "models.marketing_bill", related_name="cashbacks", to_field="id")

    def __str__(self):
        return f"Bill {self.id}, {self.deal_status}, {self.phone}, {self.sent_ts}"
