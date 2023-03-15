from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import requests
import random

page = requests.get('http://quotes.toscrape.com/')
print(bs(page.content))

