from bs4 import BeautifulSoup as bs
import requests
import boto3
import re


def get_column_names(table) -> list:
  '''
    Looks through table headers.
    Returns a list of all column headings.
  '''
  columnsElements = table.find('thead').find_all('th')

  columns: list = []
  for element in columnsElements:
    columns.append(element.text)

  columns[-1] = columns[-1].replace('-', '')

  return columns


def get_rows(table) -> list:
  '''
    Looks through table rows.
    Returns a list of all rows.
  '''
  rows: list = []
  rowsToRemove = []
  for row in table.find_all('tr', {'class': 'c-table__row--data'}):
    rowsToRemove.append([el.text.strip() for el in row.find_all('td')])

  for row in table.find_all('tr', {'class': 'c-table__row'}):
    rows.append([el.text.strip() for el in row.find_all('td')])

  for rowToRemove in rowsToRemove:
    if rowToRemove in rows:
      rows.remove(rowToRemove)

  return rows


def arrange_data(headers, rows) -> list:
  '''
    Create list of dictionaries, eg: [{ 'institution' : 'Oxford', 'ranking': 2, ...}, ...]
    Returns list of dictionaries.
  '''
  data = []
  for row in rows:
    rowData = {}
    for i, header in enumerate(headers):
      rowData[header] = row[i]
    data.append(rowData)

  return data


def add_ids(data: list) -> list:
  '''
    Add IDs to each dictionary in the list.
    Returns list of dictionaries.
  '''
  data_with_ids = []

  for idx, row in enumerate(data):
    item_to_add = { 'id': str(idx) }
    item_to_add.update(row)
    data_with_ids.append(item_to_add)

  return data_with_ids


def get_links(table) -> list:
  '''
    Looks through table and collects links to each university page in The Guardian.
    Returns list of links
  '''
  links = []
  for row in table.find_all('a', {'class': 'js-institution-link'}):
    links.append(row.get('href'))

  return links


def scrape_uni_website_links(links) -> list:
  '''
    Goes through each link and finds the university website on that page.
    Returns list of university website links
  '''
  university_links = []
  for link in links:
    if link != '':
      page = requests.get(link)
      soup = bs(page.content, 'html.parser')

      link_sibling_elements = soup.find('strong', string=re.compile('[W|w]eb.*'))
      try:
        if (link_sibling_elements != None):
          university_links.append(link_sibling_elements.find_next('a').get('href'))
        else:
          link_alternate = soup.find('a', href=re.compile('.*ac.uk[^@]')).get('href')
          university_links.append(link_alternate)
      except:
        print('ERROR')
    else:
      university_links.append('/')

  return university_links


def add_university_website(data: list, university_links: list) -> list:
  final_data = []
  for idx, row in enumerate(data):
    try:
      item_to_add = {'website': university_links[idx]}
      row.update(item_to_add)
      final_data.append(row)
    except:
      print('ERROR: ' + str(idx))

  return final_data


def main():
  # Get data
  print('Collecting data...')
  page = requests.get('https://www.theguardian.com/education/ng-interactive/2022/sep/24/the-guardian-university-guide-2023-the-rankings')
  soup = bs(page.content, 'html.parser')
  table = soup.select('table.c-table')[0]
  columns: list = get_column_names(table);
  rows: list = get_rows(table);

  # Arrange data and add extra info
  data = arrange_data(columns, rows)
  data = add_ids(data)

  print('Adding university website links...')
  universityPages = get_links(table)
  universityLinks = scrape_uni_website_links(universityPages)

  final_data = add_university_website(data, universityLinks)

  # Add data to DynamoDB
  print('Add data to DynamoDB...')
  dynamodb = boto3.resource('dynamodb')
  table = dynamodb.Table('university-table')

  for item in final_data:
    table.put_item(Item=item)

  print('Complete.')


if __name__ == "__main__":
  main()