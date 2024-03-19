import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json
import os, os.path
import re
import pandas as pd
import string


def Merge(dict1, dict2):
    return dict1.update(dict2)

def all_pages():
    """
    Compiles a list of workin links ( success code 200 ) of letter pages
    """
    alphabet = string.ascii_lowercase
    link_list = [f"https://www.thegoodscentscompany.com/rawmatex-{letter}.html" for letter in alphabet]
    ok_link_list = []
    ind = 0

    # test if link works
    for link in link_list:
        response = requests.options(link)
        if response.ok:
            # print("link is ok: ", link)
            ok_link_list.append(link)
            ind+=1
        else:
            pass
    return ok_link_list


def all_chemical_pages_per_letter(url):
    """
    Using a letter page as an argument, compiles a dictionary of all available
    links of individual chemicals in a letter page. The dictionary has chemical
    names as keys, and the links as values.
    """
    links_per_letter ={}
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    html = session.get(url).content
    soup = bs(html, "html.parser")
    tags = [row for row in soup.find_all("a") if row.get('onclick')!=None]

    onclick_pattern = "(?P<onclick>(openMainWindow\(\'))(?P<link>(.+))(?P<endlink>(\'\)\;[A-z]+\s[A-z]+\;))"
    chem_names_pattern = "^(?P<chemname>(.+))(?P<namestop>(\\r\\n))(?P<cas>(.+))(?P<therest>(.+))$"


    for tag in tags:
        # print(tag.string)
        if "NF" in re.match(chem_names_pattern,tag.parent.text).group("cas") or "CAS" not in re.match(chem_names_pattern,tag.parent.text).group("namestop"):
            links_per_letter[re.match(chem_names_pattern,tag.parent.text).group("chemname")] = re.match(onclick_pattern, tag.attrs['onclick']).group('link')
        else:
            print(f"passed {re.match(chem_names_pattern,tag.parent.text).group('chemname')}")
            pass
    return links_per_letter

#
# df = full_df()

def full_df():
    """
    This function will run all the other functions and concatenate each produced
    dataframe row into a complete dataframe.
    """
    list_of_pages = all_pages()
    list_of_pages = list_of_pages[:4]
    chemical_links = {}
    dfs = []

    for link in list_of_pages:
        print("ON LINK: ", link)
        temp_dict = all_chemical_pages_per_letter(link)
        Merge(chemical_links, temp_dict)
    if len(chemical_links.keys())>0:
        for chem in chemical_links.keys():
            print("ON CHEMICAL: ", chem)
            df = site_df(chemical_links[chem])
            dfs.append(df)
    if len(dfs)>0:
        return pd.concat(dfs)



def create_soup(url):
    """
    debugging function to quickly get back the html page of a url
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    html = session.get(url).content
    # response.content
    soup = bs(html, "html.parser")
    return soup

def site_df(url):
    """
    Using the url of a single chemical, this function leverages beautifulsoup to
    pull together the html tags of interest and store them in a dataframe of a
    single row.
    """
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    html = session.get(url).content
    soup = bs(html, "html.parser")

    # tablecolumns ->  chemical name | cas | type | strength | substantivity | description |
    # beautiful soup search -> title [0] | title [1] | qinfr2 | radw5 [Strength:] | radw5 [Substantivity:] | radw5[Odor Description:]
    cols = ["chemical", "cas", "type"]
    vals = []
    cond1 = len([i.text for i in soup.find_all("title")])>0
    cond2 = len([i.text for i in soup.find_all("td", class_="qinfr2")])>0
    cond3 = len(soup.find_all("td", {"class":"radw8"}))>0

    conds = [cond1, cond2, cond3]

    if all(conds):
        # check if flavor or odor
        flavor_pattern = r"(?P<pagetype>(\w+))(?P<therest>(\s\w+\W\s\w+))"
        if 'flavor' in re.match(flavor_pattern, [i.text for i in soup.find_all("td", class_="qinfr2")][0]).group('pagetype').lower():
            pass
        else:
            # cas using title
            title_cas_wholestring = [i.text for i in soup.find_all("title")][0]
            # name_pattern = r"(?P<chemical>(.+)+)(,\s)(?P<cas>([0-9]+-[0-9]+-[0-9]+))"
            name_pattern = r"((?P<chemical>(.+))(,\s)(?P<cas>([0-9]+-[0-9]+-[0-9]+)))|(?P<chem2>(.+))"
            cas_name_match = re.match(name_pattern, title_cas_wholestring).group("chemical")
            if cas_name_match!=None:
                chemical_grp = cas_name_match
                cas_grp = re.match(name_pattern, title_cas_wholestring).group("cas")

            else:
                chemical_grp = re.match(name_pattern, title_cas_wholestring).group("chem2")

                if "Name" in soup.find_all("td", {"class":"radw8"})[0].parent.text:
                    cas_string = soup.find_all("td", {"class":"radw8"})[1].parent.text
                else:
                    cas_string = soup.find_all("td", {"class":"radw8"})[0].parent.text
                cas_pattern = r"((?P<castitle>([A-z]+\s[A-z]+\W\s))(?P<cas>([0-9]+-[0-9]+-[0-9]+))(?P<therest>()))|(?P<castitle2>(.+not\sfound))"
                cas_match = re.match(cas_pattern, cas_string).group("cas")
                if cas_match!=None:
                    cas_grp = re.match(cas_pattern, cas_string).group("cas")
                else:
                    cas_grp = None
                    pass

            # type
            type_string = [i.text for i in soup.find_all("td", class_="qinfr2")][0]
            type_pattern = r"(?P<pretype>(Odor\sType))(:\s)(?P<type>[A-z]+)"
            type_grp =re.match(type_pattern, type_string).group("type")

            # appending cols
            vals.append(chemical_grp)
            vals.append(cas_grp)
            vals.append(type_grp)

            df = pd.DataFrame([vals], columns=cols)
            return df
    else:
        pass
