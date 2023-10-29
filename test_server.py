import requests
# from database.models import Data
from main import Data
data = {'name': 'franta', 'msg': 'ma hlavu jako banan'}
my_test_data = Data.model_validate(data)
# print(my_test_data.model_dump_json())




print(requests.post(f"http://127.0.0.1:8000/db/", json=my_test_data.model_dump()))
print(requests.get("http://127.0.0.1:8000/db/").text)

# print(requests.get("http://127.0.0.1:8000/button/").text)