from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import requests
import random

page = requests.get('http://quotes.toscrape.com/')
soup = bs(page.content, 'html.parser')

quotes = [i.text for i in soup.find_all(class_ = 'text')]
authors = [i.text for i in soup.find_all(class_='author')]
print(authors[0]);