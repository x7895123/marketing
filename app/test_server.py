import requests
from base64 import b64encode

url = "http://127.0.0.1:8000/login"

userAndPass = b64encode(b"kiiik:LYCbYsgRb-").decode("ascii")
print(userAndPass)
headers = {
  'content-type': "application/json",
  'Authorization': f'Basic {userAndPass}'
}
response = requests.post(url, headers=headers)

# auth = ('john', 'hello')
# response = requests.post(url, headers=headers, auth=auth, data=payload)

print(response.status_code)
print(response.text)


bill_info = {
  "bill_no": str, # Номер счета в iiko
  "operation_time": "yyyy-MM-dd HH:mm:ss",
  "operation": "close|refund",
  "payment": [
    {
      "payment_time": "yyyy-MM-dd HH:mm:ss",
      "payment_type": "cash|bank|bonus_name", # Название в справочнике iiko
      "payment_type_id": int, # id в справочнике iiko
      "payment": decmal
     }
  ],
  "order": [
    {"dish_id": int,  # id в справочнике iiko
     "dish_name": str,
     "quantity": decmal,
     "price": decmal
     }
  ],
  "delivery_type": "table|delivery|takeout",
  "delivery_cost": decmal
}