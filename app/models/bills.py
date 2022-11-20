from tortoise import Model, fields


class MarketingBill(Model):
    id = fields.IntField(pk=True)
    create_ts = fields.DatetimeField(auto_now_add=True)
    modified_ts = fields.DatetimeField(auto_now=True)
    company = fields.CharField(max_length=200)
    cashdesk = fields.CharField(max_length=200)
    company_bill_id = fields.CharField(max_length=200, unique=True)
    phone = fields.CharField(max_length=50)
    amount = fields.IntField()
    paytime = fields.DatetimeField()
    original_bill = fields.JSONField()
    task = fields.JSONField(null=True)

    gifts: fields.ReverseRelation["MarketingGift"]

    class Meta:
        table = "marketing_bill"

    def __str__(self):
        return f"marketing_bill id:{self.id}, create_ts:{self.create_ts}, company:{self.company}, " \
               f"cashdesk:{self.cashdesk}, bill_id:{self.company_bill_id}, phone:{self.phone}, {self.amount}, " \
               f"paytime:{self.paytime}, bill:{self.original_bill}, task:{self.task}"


class MarketingGift(Model):
    id = fields.IntField(pk=True)
    assignment = fields.CharField(max_length=255, index=True)
    create_ts = fields.DatetimeField(auto_now_add=True)
    modified_ts = fields.DatetimeField(auto_now=True)
    phone = fields.CharField(max_length=50, index=True)
    sent_ts = fields.DatetimeField(null=True)
    expiration_ts = fields.DatetimeField(null=True)
    deal = fields.JSONField(null=True)
    note = fields.CharField(max_length=255, null=True)
    published = fields.BooleanField(null=True, default=False)

    bill: fields.ForeignKeyRelation[MarketingBill] = fields.ForeignKeyField(
        "models.MarketingBill", related_name="gifts", to_field="id")

    class Meta:
        table = "marketing_gift"

    def __str__(self):
        return f"marketing_cashback {self.id}, create_ts:{self.create_ts}, phone:{self.phone}, " \
               f"sent_ts:{self.sent_ts}, expiration_ts:{self.expiration_ts}, deal:{self.deal}, " \
               f"note:{self.note}"
