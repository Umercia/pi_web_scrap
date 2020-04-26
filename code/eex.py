# lib
from selenium import webdriver
import pandas as pd
import io    # io: use to parse a string as csv file for panda
import os 
import datetime
import time
from pathlib import Path
import logging
from pyvirtualdisplay import Display  # to make it work on rasp without GUI


# parameters
PRJT_NAME = 'eex_futur_fr_baseload'
DATE = str(datetime.date.today())  # 
ROOT_DIR = Path('/home/pi/Documents/RoR_Sync')  # '/home/mo/Documents/python_code/sandbox'
URL = 'https://www.eex.com/en/market-data/power/futures/french-futures'
CSS_YEAR_BUTTON = 'div.mv-button-base:nth-child(6)'
CSS_TABLE = '#baseloadwidget > table:nth-child(1) > tbody:nth-child(3)'
TIMEOUT = 30 # seconds

raw_file_name = f'raw_{PRJT_NAME}_{DATE}.txt'
data_file_name = f'{PRJT_NAME}_{DATE}.txt'
log_file_name = f'{PRJT_NAME}_{DATE}_log.txt'

raw_dir  = ROOT_DIR / f'data/{PRJT_NAME}/raw'
data_dir = ROOT_DIR / f'data/{PRJT_NAME}/data'
log_dir  = ROOT_DIR / f'data/{PRJT_NAME}/log'

if not raw_dir.exists(): 
    os.makedirs(raw_dir)
if not data_dir.exists():
    os.makedirs(data_dir)
if not log_dir.exists():
    os.makedirs(log_dir)
 

# logging set-up
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s -  %(levelname)s -  %(message)s',
            handlers=[logging.FileHandler(log_dir / log_file_name),
                              logging.StreamHandler()
                 ]
           )

logging.info(f'trading date: {DATE}')
logging.info(f'log file: {log_dir / log_file_name}')


# create a virtual display 
display = Display(visible=0, size=(800, 600))
display.start()

# open chrome browser
option = webdriver.ChromeOptions()
option.add_argument('--incognito')
browser_o = webdriver.Chrome(chrome_options=option)


# 1. navigate to  webpage
try:
    browser_o.get(URL)
    logging.info(f'nativage to {URL}')
    time.sleep(15)
except Exception as err:
    logging.error(f'Cannot reach url: {URL}') 
    logging.error(f'Error text: {str(err)}')
    exit()

# 2. click to display year table
try:
    elem = browser_o.find_element_by_css_selector(CSS_YEAR_BUTTON)
    elem.click()
    logging.info(f'click on the css selector: {CSS_YEAR_BUTTON}')
    time.sleep(15)
except Exception as err:
    logging.error(f'Fail to click on the css selector: {CSS_YEAR_BUTTON}') 
    logging.error(f'Error text: {str(err)}')
    exit()
    
# 3. extract data
content = browser_o.find_element_by_css_selector(CSS_TABLE)
content = content.text
with open(raw_dir / raw_file_name, 'w') as f:
            f.write(content)
logging.info(f'raw data saved to: {raw_dir / raw_file_name}') 


# 4. reshape
content = content.replace(',', '')
col_names = ['Name',
             'Last_Price_[EUR/MWh]', 
             'Last_Volume_[EUR/MWh]', 
             'Settlement_Price_[EUR/MWh]', 
             'Volume_Exchange_[MWh]', 
             'Volume_Trade_Registration_[MWh]', 
             'Open_Interest',]

data_df = pd.read_csv(io.StringIO(content), 
                   sep=' ', 
                   header=None, 
                   names=col_names, 
                   na_values='-')
logging.info(f'raw data parsed into dataFrame shape: {data_df.shape}')

# 5. save data
data_df.to_csv(data_dir / data_file_name, index=False)
logging.info(f'data saved to: {data_dir / data_file_name}')
logging.info('end of the program')

# close browser
browser_o.quit()
display.stop()