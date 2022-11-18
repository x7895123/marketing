from tortoise import Model, fields


class MarketingBill(Model):
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

    cashbacks: fields.ReverseRelation["MarketingCashback"]

    class Meta:
        table = "marketing_bill"

    def __str__(self):
        return f"marketing_bill id:{self.id}, create_ts:{self.create_ts}, company:{self.company}, " \
               f"cashdesk:{self.cashdesk}, bill_no:{self.bill_no}, phone:{self.phone}, {self.amount}, " \
               f"paytime:{self.paytime}, bill:{self.bill}, task:{self.task}"


class MarketingCashback(Model):
    id = fields.IntField(pk=True)
    create_ts = fields.DatetimeField(auto_now_add=True)
    phone = fields.CharField(max_length=50, index=True)
    sent_ts = fields.DatetimeField(null=True)
    expiration_ts = fields.DatetimeField(null=True)
    deal = fields.JSONField(null=True)
    deal_status = fields.CharField(max_length=200, null=True)
    error_message = fields.CharField(max_length=255, null=True)
    recipient_address = fields.CharField(max_length=200, null=True)
    contract_address = fields.CharField(max_length=200, null=True)

    id_bill: fields.ForeignKeyRelation[MarketingBill] = fields.ForeignKeyField(
        "models.MarketingBill", related_name="cashbacks", to_field="id")

    class Meta:
        table = "marketing_cashback"

    def __str__(self):
        return f"marketing_cashback {self.id}, create_ts:{self.create_ts}, phone:{self.phone}, " \
               f"sent_ts:{self.sent_ts}, expiration_ts:{self.expiration_ts}, deal:{self.deal}, " \
               f"{self.deal_status}, error_message:{self.error_message}, recipient_address:{self.recipient_address}"
