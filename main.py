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

def full_dataset():
    """
    Iterates over all material categories ('oil', 'fragrance', 'absolute', etc.)
    and builds a complete DataFrame containing all chemicals.
    """
    categories = ["oil", "absolute", "fragrance", "raw", "bases", "natural", "resins"]
    all_dfs = []

    for category in categories:
        print(f"Processing category: {category}...")
        list_of_pages = all_pages(category)  # Get category pages
        chemical_links = {}

        # Iterate through each page in the category
        for link in list_of_pages:
            print(f"  Scraping page: {link}")
            temp_dict = all_chemical_pages_per_letter(link)  # Extract chemical links
            Merge(chemical_links, temp_dict)  # Merge with main dictionary

        # Extract chemical data for each URL
        category_dfs = []
        for chem_name, chem_url in chemical_links.items():
            print(f"    Extracting data for: {chem_name}")
            try:
                df = get_chemical_data(chem_url)  # Extract data
                df["category"] = category  # Add category column
                category_dfs.append(df)
            except Exception as e:
                print(f"Error processing {chem_name}: {e}")

        if category_dfs:
            all_dfs.append(pd.concat(category_dfs))  # Append category DataFrame

    # Combine all categories into one final DataFrame
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        return final_df

    return None  # Return None if no data was found

def all_pages(category):
    """
    Compiles a list of working links (success code 200) for letter pages or a single page
    based on the category argument: "oil", "absolute", "fragrance", or "raw".
    """
    alphabet = string.ascii_lowercase
    ok_link_list = []

    # Determine link format based on category
    if category == "oil":
        link_template = "https://www.thegoodscentscompany.com/essentlx-{letter}.html"
        link_list = [link_template.format(letter=letter) for letter in alphabet]
        link_list.append("https://www.thegoodscentscompany.com/essentlx-jk.html")
        link_list.append("https://www.thegoodscentscompany.com/essentlx-wx.html")
    elif category == "absolute":
        # Single page for "absolute", no substitution needed
        link_list = ["https://www.thegoodscentscompany.com/abs-az.html"]
    elif category == "fragrance":
        link_template = "https://www.thegoodscentscompany.com/fragonly-{letter}.html"
        link_list = [link_template.format(letter=letter) for letter in alphabet]
    elif category == "raw":
        # Default raw link format
        link_template = "https://www.thegoodscentscompany.com/rawmatex-{letter}.html"
        link_list = [link_template.format(letter=letter) for letter in alphabet]
        link_list.append("https://www.thegoodscentscompany.com/rawmatex-jk.html")
        link_list.append("https://www.thegoodscentscompany.com/rawmatex-wx.html")
    elif category == "bases":
        link_list = ["https://www.thegoodscentscompany.com/peb-az.html"]
    elif category == "natural":
        link_template = "https://www.thegoodscentscompany.com/naturocc-{letter}.html"
        link_list = [link_template.format(letter=letter) for  letter in alphabet]
        link_list.append("https://www.thegoodscentscompany.com/naturocc-jk.html")
        link_list.append("https://www.thegoodscentscompany.com/naturocc-wx.html")
    elif category == "resins":
        link_template = "https://www.thegoodscentscompany.com/resinx-{letter}.html"
        link_list = [link_template.format(letter=letter) for  letter in alphabet]
        link_list.append("https://www.thegoodscentscompany.com/resinx-jk.html")
        link_list.append("https://www.thegoodscentscompany.com/resinx-wx.html")

    else:
        raise ValueError("Invalid category. Choose 'oil', 'absolute', 'fragrance', or 'raw'.")

    # Test if link works
    for link in link_list:
        response = requests.options(link)
        if response.ok:
            ok_link_list.append(link)

    return ok_link_list

def all_chemical_pages_per_letter(url):
    """
    Parses a Good Scents category page (like essentlx-g.html or peb-az.html)
    and extracts chemical names and their URLs.
    """
    links_per_letter = {}

    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0"
    html = session.get(url).content
    soup = bs(html, "html.parser")

    # Find all <a> tags with onclick attributes
    tags = [row for row in soup.find_all("a") if row.get('onclick') is not None]

    # Updated regex for extracting links from onclick attributes
    onclick_pattern = r"openMainWindow\('(?P<link>.+?)'\)"

    for tag in tags:
        chem_name = tag.text.strip()  # Get the text inside <a>
        onclick_value = tag.get("onclick", "")

        # Extract the link using regex
        match = re.search(onclick_pattern, onclick_value)
        if match:
            chem_link = match.group("link")
            links_per_letter[chem_name] = chem_link

    return links_per_letter


def full_df():
    """
    This function will run all the other functions and concatenate each produced
    dataframe row into a complete dataframe.
    """
    list_of_pages = all_pages("oil")
    # list_of_pages = [list_of_pages[]]
    list_of_pages = list_of_pages[:]
    chemical_links = {}
    dfs = []

    for link in list_of_pages:
        print("ON LINK: ", link)
        temp_dict = all_chemical_pages_per_letter(link)
        Merge(chemical_links, temp_dict)
    if len(chemical_links.keys())>0:
        for chem in chemical_links.keys():
            print("ON CHEMICAL: ", chem)
            # df = site_df(chemical_links[chem])
            df = get_chemical_data(chemical_links[chem])
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

def get_chemical_data(url):
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0"
    html = session.get(url).content
    soup = bs(html, "html.parser")

    # Step 1: Try to extract chemical name & CAS from the <title> tag
    title = soup.find("title").text.strip()
    name_pattern = r"(?P<name>.+),\s(?P<cas>\d{2,7}-\d{2}-\d)"
    match = re.match(name_pattern, title)

    if match:
        chemical_name = match.group("name")
        cas_number = match.group("cas")
    else:
        # Step 2: If no CAS is found, try to extract the name from <h1> itemprop="name"
        name_element = soup.find("h1", itemscope=True)
        if name_element:
            chemical_name = name_element.find("span", itemprop="name").get_text(strip=True)
        else:
            chemical_name = "Unknown Chemical"

        cas_number = None  # Allow missing CAS numbers

    # Step 3: Extract boiling point, vapor pressure, and molecular weight
    boiling_point = None
    vapor_pressure = None
    molecular_weight = None

    # Locate the cheminfo table
    cheminfo_table = soup.find("table", class_="cheminfo")
    if cheminfo_table:
        rows = cheminfo_table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 1:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)

                if "Boiling Point" in label:
                    boiling_point = value
                elif "Vapor Pressure" in label:
                    vapor_pressure = value
                elif "Molecular Weight" in label:
                    molecular_weight = value

    # Step 4: Extract odor type
    type_element = soup.find("td", class_="qinfr2")
    odor_type = type_element.get_text(strip=True).replace("Odor Type: ", "") if type_element else "Unknown"

    # Step 5: Extract odor description
    odor_descriptions = []
    for element in soup.find_all("td", class_="radw5"):
        if "Odor Description:" in element.text:
            spans = element.find_all("span")
            description_text = " ".join(span.text.strip() for span in spans)
            odor_descriptions.append(description_text)
    odor_description = " | ".join(odor_descriptions) if odor_descriptions else "No description"

    # Step 6: Extract substantivity
    substantivity = None
    for element in soup.find_all("td", class_="radw5"):
        if "Substantivity:" in element.text:
            substantivity_str = element.find_next("span").text.strip()
            match = re.search(r"(\d+\.?\d*) hour\(s\) at (\d+\.?\d*) %", substantivity_str)
            if match:
                hours = float(match.group(1))
                concentration = float(match.group(2))
                substantivity = hours / concentration

    # Step 7: Extract synonyms
    synonyms = []
    synonym_header = soup.find("div", class_="sectionclass", string="Synonyms:")
    if synonym_header:
        synonym_table = synonym_header.find_next_sibling("table", class_="cheminfo")
        if synonym_table:
            rows = synonym_table.find_all("tr", itemtype="https://schema.org/Thing")
            for row in rows:
                cells = row.find_all("td")
                synonym = " ".join(cell.get_text(strip=True) for cell in cells if cell.get_text(strip=True))
                if synonym:
                    synonyms.append(synonym)
    synonyms_string = ", ".join(synonyms) if synonyms else "No synonyms"

    # Step 8: Create a DataFrame with the extracted data
    data = {
        "name": [chemical_name],
        "cas_number": [cas_number],
        "type": [odor_type],
        "description": [odor_description],
        "substantivity": [substantivity],
        "boiling_point": [boiling_point],
        "vapor_pressure": [vapor_pressure],
        "molecular_weight": [molecular_weight],
        "synonyms": [synonyms_string]
    }

    df = pd.DataFrame(data)
    return df

































#
