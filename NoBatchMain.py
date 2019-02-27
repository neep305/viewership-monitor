from Crawler import MbsCrawler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

import logging
import os
import Constants as const

import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info('main() started')

    channel = sys.argv[1]
    logger.info('selected channel : {}'.format(channel))
    
    if channel is 'L':
        mbs_live = MbsCrawler('mbsgs9','@gspw9',const.LIVE)
        mbs_live.run_excel_download()
        mbs_live.convert_to_csv()
    elif channel is 'T':
        mbs_data = MbsCrawler('mbsgstc9','@gstcpw9',const.MYSHOP)
        mbs_data.run_excel_download()
        mbs_data.convert_to_csv()
    else:
        logger.info('Exit : Channel is not selected')
        exit(0)

    

if __name__ == "__main__":
    
    main()