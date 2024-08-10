import zipfile36 as zipfile
import requests
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from io import BytesIO
import datetime as dt
import os
import pandas as pd
import numpy as np
import holidays


header = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/111.0.0.0 Safari/537.36",
    "Sec-Fetch-User": "?1", "Accept": "*/*", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate",
    "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    }

def nse_url_fetch(url):
    r_session = requests.session()
    nse_live = r_session.get("http://nseindia.com", headers=header)
    return r_session.get(url, headers=header)


def fno_bhav_copy(trade_date: str):
    """
    new CM-UDiFF Common NSE future option bhav copy from 2018 on wards
    :param trade_date: eg:'01-06-2023'
    :return: pandas Data frame
    """
    # trade_date = datetime.strptime(trade_date, dd_mm_yyyy)
    trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
    url = 'https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'
    payload = f"{str(trade_date.strftime('%Y%m%d'))}_F_0000.csv.zip"
    request_bhav = nse_url_fetch(url + payload)
    bhav_df = pd.DataFrame()
    if request_bhav.status_code == 200:
        zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
        for file_name in zip_bhav.filelist:
            if file_name:
                bhav_df = pd.read_csv(zip_bhav.open(file_name))
    elif request_bhav.status_code == 403:
        url2 = "https://www.nseindia.com/api/reports?archives=" \
             "%5B%7B%22name%22%3A%22F%26O%20-%20Bhavcopy(csv)%22%2C%22type%22%3A%22archives%22%2C%22category%22" \
             f"%3A%22derivatives%22%2C%22section%22%3A%22equity%22%7D%5D&date={str(trade_date.strftime('%d-%b-%Y'))}" \
             f"&type=equity&mode=single"
        request_bhav = nse_url_fetch(url2)
        if request_bhav.status_code == 200:
            zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
            for file_name in zip_bhav.filelist:
                if file_name:
                    bhav_df = pd.read_csv(zip_bhav.open(file_name))
        elif request_bhav.status_code == 403:
            raise FileNotFoundError(f' Data not found, change the date...')
    # bhav_df = bhav_df[['INSTRUMENT', 'SYMBOL', 'EXPIRY_DT', 'STRIKE_PR', 'OPTION_TYP', 'OPEN', 'HIGH', 'LOW',
    #                    'CLOSE', 'SETTLE_PR', 'CONTRACTS', 'VAL_INLAKH', 'OPEN_INT', 'CHG_IN_OI', 'TIMESTAMP']]
    return bhav_df


start_date = "01-01-2024"
end_date = "09-08-2024"
# start_date and end date format %m-%d-%Y or %m/%d/%Y
# output format: 2024-01-05 00:00:00 in datetime format
date_range = pd.bdate_range(start = start_date, end = end_date, freq ='C',holidays = holidays.holidays(2024))

# print(date_range)
for index, cday in enumerate(date_range):
    # print(cday)
    temp_date = cday.date()
    curr_date = temp_date.strftime("%d-%m-%Y")
    print(curr_date, index)

    bhawcopy_df = fno_bhav_copy(curr_date)
    
    date_obj = datetime.strptime(curr_date, "%d-%m-%Y")
    # Format to YYYY-MM-DD
    new_date_str = date_obj.strftime("%Y-%m-%d")
    path = r"E:\Bhawcopy_2024\\"
    filename = path + new_date_str + "_bhawcopy.csv"
    bhawcopy_df.to_csv(filename, index=False)
    # break