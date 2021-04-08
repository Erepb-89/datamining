import requests
import bs4

url = "https://magnit.ru/promo/?geo=moskva"

response = requests.get(url)

soup = bs4.BeautifulSoup(response.text, "lxml")

catalog_main = soup.find('div', attrs={"class": "сatalogue__main"})
#for tag in catalog_main:
#    print(tag)

#old_price = soup.find("div", attrs={"class": "label__price-integer"}.contents)
#print(old_price)
sale_header = soup.find("div", attrs={"class": "card-sale__header"}).text
sale_date = soup.find("div", attrs={"class": "card-sale__date"}).text
old_price = soup.find("div", attrs={"class": "label__price_old"}).text
new_price = soup.find("div", attrs={"class": "label__price_new"}).text
image_url = soup.find("img").attrs['src']
date_from = sale_date.split('\n')[1]
date_to = sale_date.split('\n')[2]

print(1)
