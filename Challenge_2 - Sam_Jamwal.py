import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib as plt


from pymongo import MongoClient
import pprint

import copy
import pandas as pd

# Requests sends and recieves HTTP requests.
import requests

# Beautiful Soup parses HTML documents in python.
from bs4 import BeautifulSoup

import re
from time import sleep

#list of aircraft
#aicraft_list = ['Pilatus PC-12', 'Cessna Caravan', 'Beechcraft Super King Air 200', 'Cessna Citation Excel/XLS']

aircraft = input('Enter Aircraft Name:')

#function to retrieve webpage
def request(web):

  r = requests.get(web)
  client = MongoClient('localhost', 27017)
  db = client.metroid
  pages = db.pages
  pages.insert_one({'html': r.content})
  soup = (BeautifulSoup(r.content, "html.parser"))
  return soup

#function to find the code for each aircraft - this will help when looking through webpage
#can be removed if code is given instead of name
def find_aircraft(name):
  soup = request('https://flightaware.com/live/aircrafttype/')
  #table has 2 classes
  table = soup.find_all(class_ = 'smallrow1')
  table2 = soup.find_all(class_ = 'smallrow2')

  name = name.replace(' ', '').lower()

  #iterate though both tables to find code - when found stops function
  for row in table:
    columns = row.find_all('td')
    aircraft = columns[2].text.strip()

    aircraft = aircraft.replace(' ', '').lower()

    if aircraft == name:
      code = (columns[1].text.strip())
      break
    else:
      continue

  for row in table2:
    columns = row.find_all('td')
    aircraft = columns[2].text.strip()

    aircraft = aircraft.replace(' ', '').lower()
    if aircraft == name:
      code = (columns[1].text.strip())
      break
    else:
      continue

  return code


def aircraftinfo(name):

  code = find_aircraft(name)

  new_table = pd.DataFrame(columns = ['Ident', 'Type', 'Origin', 'Destination', 'Depature', 'Arrival Time', 'Time in Route'])

  #to look at more than one page shows, have to iterate - max of 500 flights will be found

  for num in range(0,500, 20):
    web = f'https://flightaware.com/live/aircrafttype/{code};offset={num}'
    soup = request(web)

    table = soup.find('table', class_ = 'prettyTable fullWidth')
    rows = table.find_all('tr')

    for x in rows:
      col = x.find_all('td')
      row = [i.text for i in col]
      if len(row) == 7:
        n_row = pd.DataFrame([row], columns = ['Ident', 'Type', 'Origin','Destination', 'Depature', 'Arrival Time', 'Time in Route'])
        new_table = new_table.append(n_row )
      else:
        continue

  new_table['Time in Route'] = pd.to_datetime(new_table['Time in Route']).dt.strftime('%H:%M:%S')
  avg = pd.to_timedelta(new_table['Time in Route']).mean()





  return(new_table)


(aircraftinfo(aircraft))




