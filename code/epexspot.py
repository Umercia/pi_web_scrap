# lib
import numpy as np
import pandas as pd
import requests
import datetime
import bs4
import re
import os
from pathlib import Path
import logging

# parameters
prjt_name = 'epexspot'
COUNTRY_CODE = 'FR'
TRADING_DATE = str(datetime.date.today())
DELIVERY_DATE = str(datetime.date.today() + datetime.timedelta(days=1))
TRADING_MODALITY = 'Auction'
SUB_MODALITY = 'DayAhead'
file_name = f'RAW_{COUNTRY_CODE}_{TRADING_MODALITY}_{SUB_MODALITY}_{TRADING_DATE}_{DELIVERY_DATE}.txt'
log_file = f'{TRADING_DATE}_{prjt_name}_log.txt'
url = f'https://www.epexspot.com/en/market-data?market_area={COUNTRY_CODE}&trading_date={TRADING_DATE}&delivery_date={DELIVERY_DATE}&underlying_year=&modality=Auction&sub_modality=DayAhead&product=60&data_mode=table&period='


# folder's path set-up
# os.chdir('..')
# print(os.getcwd())
root_dir = Path('/home/pi/Documents/RoR_Sync')
raw_dir  = root_dir / f'data/{prjt_name}/raw'
data_dir = root_dir / f'data/{prjt_name}/data'
log_dir  = root_dir / f'data/{prjt_name}/log'

if not raw_dir.exists():
    os.makedirs(raw_dir)
if not data_dir.exists():
    os.makedirs(data_dir)
if not log_dir.exists():
    os.makedirs(log_dir)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s -  %(levelname)s -  %(message)s',
            handlers=[logging.FileHandler(log_dir / log_file),
                              logging.StreamHandler()
                 ]
           )

logging.info(f'trading date: {TRADING_DATE}')
logging.info(f'log file: {log_dir / log_file}')
# request
logging.info(f'request url: {url}')
res = requests.get(url)
res.raise_for_status()  # stop in case of error
logging.info(f'request status code: {res.status_code}')

raw_path = raw_dir / file_name
logging.info(f'{raw_path} exists: {raw_path.exists()}')
with open(raw_dir / file_name, 'wb') as f:
    for chunk in res.iter_content(100000):
            f.write(chunk)
logging.info(f'{raw_path} exists: {raw_path.exists()}') 
 
# read HTML file
with open(raw_dir / file_name, 'rb') as f:
    soup = bs4.BeautifulSoup(f.read(), features="html.parser")


# parse time stamps
extract_txt = soup.select('#epex-md-common-data-container > div > section > div.content.js-md-widget > div > div > div.fixed-column.js-table-times > ul > li')
ts_li = re.findall(r'[0-9][0-9] - [0-9][0-9]', str(extract_txt))
ts_li = [f'{DELIVERY_DATE} {x[:2]}:00' for x in ts_li]
logging.info(f'len of parsed hours: {len(ts_li)}/24')


# parse values
extract_txt = soup.select('#epex-md-common-data-container > div > section > div.content.js-md-widget > div > div > div.js-table-values > table > tbody')
data_li = extract_txt[0].text
data_li = data_li.replace('\n', ' ').replace(',','').split()
logging.info(f'len of data chuck: {len(data_li)}/({24*4})')


# reschape data
data_ar = np.array(data_li).reshape((len(ts_li),4))
df = pd.DataFrame(data=data_ar, index = ts_li, columns = ['Buy Volume [MWh]', 
                                            'Sell Volume [MWh]',
                                            'Volume [MWh]',
                                            'Price [Euro/MWh]'])
df.index.name = 'time_stamp'
logging.info(f'dataFrame shape: {df.shape}')

# save
df.to_csv(data_dir / f'{COUNTRY_CODE}_{TRADING_MODALITY}_{SUB_MODALITY}_{TRADING_DATE}_{DELIVERY_DATE}.csv')
logging.info('end of the program')
