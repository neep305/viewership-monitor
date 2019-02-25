from Crawler import MbsCrawler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

import logging
import os
import Constants as const

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info('main start')
    mbs_live = MbsCrawler('mbsgs9','@gspw9',const.LIVE)
    # mbs_data = MbsCrawler('mbsgstc9','@gstcpw9',const.MYSHOP)

    # scheduler = BlockingScheduler()
    # scheduler.add_job(mbs_data.run_excel_download,trigger='cron',hour='1',minute='0')
    # scheduler.add_job(mbs_live.run_excel_download,trigger='cron',hour='1',minute='5')
    
    # scheduler.add_job(mbs_live.convert_to_csv,trigger='cron',hour='1',minute='15')
    # scheduler.add_job(mbs_data.convert_to_csv,trigger='cron',hour='1',minute='17')

    # logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    # try:
    #     scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
    #     scheduler.shutdown()

    # 테스트용
    mbs_live.run_excel_download()
    mbs_live.convert_to_csv()

def convert_to_csv(type):
    from datetime import datetime,timedelta
    import pandas as pd

    today = datetime.today() - timedelta(days=1)
    str_today = today.strftime('%Y%m%d')

    file_to_convert = None

    if type is const.LIVE:
        file_to_convert = '유형별시청형태_채널_GS SHOP_시간별_1d_' + str_today + '.xlsx'
    else:
        file_to_convert = '유형별시청형태_채널_GS MY SHOP_시간별_1d_' + str_today + '.xlsx'

    if os.path.exists('./' + file_to_convert) == True:
        logger.info('file to convert is exist : ' + file_to_convert)
        
        excel_result = pd.read_excel('./' + file_to_convert, sheet_name='유형별>시간별_시청가구상세테이블',index_col=None, header=2)
        
        index =  range(1, len(excel_result))
        temp = []
        for i in index:
            temp.append(i)

        rearranged_excel = pd.DataFrame(excel_result)
        rearranged_excel.columns = ['time','cnt']

        df = rearranged_excel.reset_index()

        df_to_csv = df.iloc[1:,].assign(srvc=type)

        df_to_csv.iloc[:,1] = str_today + df_to_csv['time'].str.replace(r'(시|분)','')

        #######################################
        #           Extract CSV
        #######################################
        path_to_extract = None

        if os.name == 'nt':
            path_to_extract = './csv/'
            if os.path.exists('./csv') != True:
                os.mkdir('./csv')
        else:
            file_path = '/applications/anaconda3/mbs/data/'

        if df_to_csv['srvc'][1] == 'T':
            df_to_csv[['cnt','time','srvc']].to_csv(path_to_extract + str_today + '_myshop_channel_hourly.csv', header=False)
        else:
            df_to_csv[['cnt','time','srvc']].to_csv(path_to_extract + str_today + '_gsshop_channel_hourly.csv', header=False)

        os.remove('./'+file_to_convert)
    else:
        raise FileNotFoundError("excel file doesn't exist in the path")
if __name__ == "__main__":
    
    main()
    # convert_to_csv(const.LIVE)
