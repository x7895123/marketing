import time

from datetime import datetime, timedelta, timezone
import jwt

dt = datetime.now(tz=timezone.utc) + timedelta(seconds=2)
encoded_token = jwt.encode({'user_id': "abc", 'email': "nancy@gmail.com", 'exp': dt }, 'secret', algorithm='HS256')
print(encoded_token)

time.sleep(1)

try:
    decoded = jwt.decode(encoded_token, "secret", algorithms=["HS256"])
    print(decoded)
except jwt.ExpiredSignatureError as e:
    print(f'not valid {e}')