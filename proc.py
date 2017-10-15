#!/usr/bin/env python3

from bs4 import BeautifulSoup
import json
import requests

url = "https://timelines.issarice.com/api.php?action=parse&page=Timeline_of_The_Sierra_Club"

payload = {
    "action": "parse",
    "page": "Timeline of Airbnb",
    "format": "json",
}

r = requests.get("https://timelines.issarice.com/api.php", params=payload)
result = r.json()
text = result["parse"]["text"]["*"]
soup = BeautifulSoup(text, "lxml")
tables = soup.find_all("table")

# subtract one from number of rows to compensate for header row
print(list(map(lambda t: len(t.find_all("tr")) - 1, tables)))
