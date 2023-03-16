from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import requests
import random

def get_column_names(table):
  columnsElements = table.find('thead').find_all('th')

  columns = []
  for element in columnsElements:
    columns.append(element.text)

  columns[-1] = columns[-1].replace('-', '')

  return columns;

def main():
  page = requests.get('https://www.theguardian.com/education/ng-interactive/2022/sep/24/the-guardian-university-guide-2023-the-rankings')
  soup = bs(page.content, 'html.parser')
  table = soup.select('table.c-table')[0]

  columns = get_column_names(table);

  print(columns)

if __name__ == "__main__":
  main()