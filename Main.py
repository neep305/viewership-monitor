#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crawler import MbsCrawler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

import logging
import os
import Constants as const

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info('main() started')
    mbs_live = MbsCrawler('mbsgs9','@gspw9',const.LIVE)
    mbs_data = MbsCrawler('mbsgstc9','@gstcpw9',const.MYSHOP)

    scheduler = BlockingScheduler()
    scheduler.add_job(mbs_data.run_excel_download,trigger='cron',hour=const.START_HOUR,minute=const.START_MINUTE)
    scheduler.add_job(mbs_live.run_excel_download,trigger='cron',hour=const.START_HOUR,minute=const.START_MINUTE+5)
    
    scheduler.add_job(mbs_live.convert_to_csv,trigger='cron',hour=const.START_HOUR,minute=const.START_MINUTE+10)
    scheduler.add_job(mbs_data.convert_to_csv,trigger='cron',hour=const.START_HOUR,minute=const.START_MINUTE+12)

    logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    
    main()