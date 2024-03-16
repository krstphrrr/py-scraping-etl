# 1. save style to file
# 2. save a row of assorted data from a page into a row in a db
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

# test
# use json

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"

html = session.get(url).content

soup = bs(html, "html.parser")

print(soup)
css_files = []
for css in soup.find_all("link"):
    if css.attrs.get("href"):
        css_file = urljoin(url,css.attrs.get("href"))
        css_files.append(css_file)


import os
fileName = os.path.basename(css_files[-1])
text = requests.get(css_files[-1]).text
with open(fileName, 'w', encoding="utf-8") as f:
    f.write(text)
