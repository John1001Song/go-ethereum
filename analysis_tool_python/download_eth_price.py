import requests
import json
import urllib3
from bs4 import BeautifulSoup
import os
import re
from urllib.request import Request
from urllib import parse
import pandas as pd
from datetime import date
from datetime import time
from datetime import datetime

# https://api.coindesk.com/charts/data?output=csv&data=close&index=ETH&startdate=2015-08-31&enddate=2018-10-17&exchanges=bpi&dev=1
# use this link to download eth history price

def get_today_date():
	today = date.today()
	print(today)

def main():
	today_date = get_today_date()
	
if __name__ == '__main__':
	main()