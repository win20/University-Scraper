from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import boto3
import uuid

def get_column_names(table) -> list:
  columnsElements = table.find('thead').find_all('th')

  columns: list = []
  for element in columnsElements:
    columns.append(element.text)

  columns[-1] = columns[-1].replace('-', '')

  return columns;


def get_rows(table) -> list:
  rows: list = []
  rowsToRemove = []
  for i, row in enumerate(table.find_all('tr', {'class': 'c-table__row--data'})):
    rowsToRemove.append([el.text.strip() for el in row.find_all('td')])

  for i, row in enumerate(table.find_all('tr', {'class': 'c-table__row'})):
    rows.append([el.text.strip() for el in row.find_all('td')])

  for rowToRemove in rowsToRemove:
    if rowToRemove in rows:
      rows.remove(rowToRemove)

  return rows


def arrange_data(headers, rows):
  data = []
  for row in rows:
    rowData = {}
    for i, header in enumerate(headers):
      rowData[header] = row[i]
    data.append(rowData)

  return data


def add_ids(data: list) -> list:
  data_with_ids = []

  for idx, row in enumerate(data):
    item_to_add = { 'id': str(idx) }
    item_to_add.update(row)
    data_with_ids.append(item_to_add)

  return data_with_ids


def main():
  page = requests.get('https://www.theguardian.com/education/ng-interactive/2022/sep/24/the-guardian-university-guide-2023-the-rankings')
  soup = bs(page.content, 'html.parser')
  table = soup.select('table.c-table')[0]

  columns: list = get_column_names(table);
  rows: list = get_rows(table);

  data = arrange_data(columns, rows)
  data = add_ids(data)

  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('university-table')

  for item in data:
    table.put_item(Item=item)


if __name__ == "__main__":
  main()