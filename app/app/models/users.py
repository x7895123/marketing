from tortoise import Model, fields
from .bills import MarketingBill


class Users(Model):
    id = fields.IntField(pk=True)
    create_ts = fields.DatetimeField(auto_now_add=True)
    modified_ts = fields.DatetimeField(auto_now=True)
    company = fields.CharField(max_length=200)
    cashdesk = fields.CharField(max_length=200)
    name = fields.CharField(max_length=200, unique=True)
    password = fields.CharField(max_length=1000)
    code = fields.CharField(max_length=1000, null=True)

    bills: fields.ReverseRelation["MarketingBill"]

    def __str__(self):
        return f"marketing_bill id:{self.id}, create_ts:{self.create_ts}, " \
               f"company:{self.company}, cashdesk:{self.cashdesk}, " \
               f"name:{self.name}, password_hash:{self.password}, " \
               f"code {self.code}"