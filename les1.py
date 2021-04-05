from pathlib import Path
import requests


"""
HTTPs
Head - Headers
Body

GET -
POST -
PUT
PATCH
DELETE

STATUS CODES:
1 - INFO
2 - OK
3 - Redirect
4 - Client Error
5 - Server Error
"""

headers = {"User-Agent": "Phillip Kirkorov"}

params = {
    "store": None,
    "records_per_page": 12,
    "page": 1,
    "categories": None,
    "ordering": None,
    "price_promo__gte": None,
    "price_promo__lte": None,
    "search": "молоко",
}

url = "https://5ka.ru/api/v2/special_offers/"

response: requests.Response = requests.get(url, headers=headers, params=params)

print(1)

file = Path(__file__).parent.joinpath("5ka.json")

file.write_text(response.text)

# data = json.loads(response.text)

print(1)
