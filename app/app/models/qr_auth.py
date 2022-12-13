from tortoise import Model, fields


class QrAuth(Model):
    id = fields.IntField(pk=True)
    create_ts = fields.DatetimeField(auto_now_add=True)
    modified_ts = fields.DatetimeField(auto_now=True)
    username = fields.CharField(max_length=200, index=True)
    assignment = fields.CharField(max_length=255, index=True)
    request_id = fields.CharField(max_length=200, index=True)
    phone = fields.CharField(max_length=50, null=True, index=True)

    class Meta:
        table = "qr_auth"

    def __str__(self):
        return f"marketing_bill id:{self.id}, create_ts:{self.create_ts}, " \
               f"company:{self.username}, request_id:{self.request_id}," \
               f"phone:{self.phone}"
