import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json
import os, os.path
import re

def site_df(url):
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    html = session.get(url).content
    soup = bs(html, "html.parser")

    # tablecolumns ->  chemical name | cas | type | strength | substantivity | description |
    # beautiful soup search -> title [0] | title [1] | qinfr2 | radw5 [Strength:] | radw5 [Substantivity:] | radw5[Odor Description:]

    # cas using title
    title_cas_wholestring = [i.text for i in soup.find_all("title")][0]
    cas_pattern = r"(?P<chemical>(.+)+)(,\s)(?P<cas>([0-9]+-[0-9]+-[0-9]+))"
    cas_grp = re.match(cas_pattern, title_cas_wholestring).group("cas")
    chemical_grp = re.match(cas_pattern, title_cas_wholestring).group("chemical")

    # type
    type = [i.text for i in soup.find_all("td", class_="qinfr2")][0]
