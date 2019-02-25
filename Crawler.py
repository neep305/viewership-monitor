from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import ElementNotVisibleException,NoSuchElementException,TimeoutException,WebDriverException

import os
import os.path
import time
import logging
from datetime import datetime,timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import Constants as const

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MbsCrawler:
    def __init__(self,id,pwd,type):
        self.domain = 'https://mbs.kt.com:8080'
        self.id = id
        self.pwd = pwd
        self.type = type
        # self.driver = self.get_firefox_driver()
        self.driver = self.get_chrome_driver()

    def login_by_selenium(self):
        driver = self.driver

        driver.get(self.domain + '/login.do')
        elem_id = driver.find_element_by_id('loginId')
        elem_id.clear()
        elem_id.send_keys(self.id)

        elem_pw = driver.find_element_by_id('loginPw')
        elem_pw.clear()
        elem_pw.send_keys(self.pwd)
        elem_pw.send_keys(Keys.RETURN)

    # finding element of excel download button in headless mode
    def headless_srch_download_btn(self):
        driver = self.driver       
        driver.get(self.domain + '/timely/channel/hourlyMain.do')
        
        try:
            # Popup check
            popup_is_displayed = driver.find_element_by_xpath('//*[@id="popNotice"]').is_displayed

            logger.info('Popup Displayed : ' + str(popup_is_displayed()))
            
            is_displayed = WebDriverWait(driver,timeout=100).until_not(lambda driver: driver.find_element_by_class_name('loader-visible').is_displayed)

            time.sleep(4)

            if is_displayed:
                driver.find_element_by_xpath('//*[@id="searchFrm"]/div/fieldset/div/button').click()

            time.sleep(15)
            is_displayed = WebDriverWait(driver,timeout=100).until_not(lambda driver: driver.find_element_by_class_name('loader-visible').is_displayed)

            if is_displayed:
                elem_btn_download = WebDriverWait(self.driver,timeout=10).until(ec.presence_of_element_located((By.CLASS_NAME,'btn_download')))
                logger.info(elem_btn_download.get_attribute('class'))
                elem_btn_download.click()
                
            time.sleep(30)
        except TimeoutException as e:
            logger.error('TimeoutException waiting for search input field: {}'.format(e))
        finally: 
            logger.info('Automation finished')
            self.driver.quit()

    # headless firefox driver setting
    def get_firefox_driver(self):

        driver = None

        profile = webdriver.FirefoxProfile()

        profile.set_preference("browser.download.panel.shown", False)
        profile.set_preference("browser.download.manager.showWhenStarting",False)
        profile.set_preference("browser.helperApps.neverAsk.openFile", 'application/msexcel')
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/msexcel')
        profile.set_preference("browser.download.folderList", 2)

        options = Options()
        options.set_headless(headless=True)

        # path_to_download = None
        # if os.name == 'nt':
        #     path_to_download = os.getcwd()
        # else:
        #     path_to_download = '/applications/anaconda3/mbs/data/'
        
        profile.set_preference("browser.download.dir", os.getcwd())

        driver = webdriver.Firefox(executable_path=os.getcwd() + '\\driver\\geckodriver.exe', firefox_profile=profile)
        
        driver.set_page_load_timeout(50)
        driver.set_script_timeout(70)

        return driver

    # headless chrome driver setting
    def get_chrome_driver(self):

        driver = None

        options = webdriver.ChromeOptions()
        
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1366x768")
        
        if os.name == 'nt':    
            driver = webdriver.Chrome(options=options, executable_path=os.getcwd()+'\\driver\\chromedriver.exe')
        else:
            driver = webdriver.Chrome(options=options, executable_path=os.getcwd()+'/driver/chromedriver')

        driver.set_page_load_timeout(50)
        driver.set_script_timeout(50)

        self.enable_download_in_headless_chrome(driver,os.getcwd())
            
        return driver

    # To make it possible to download a file with headless mode
    def enable_download_in_headless_chrome(self, driver, download_dir):
        #add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        driver.execute("send_command", params)

    # function to use as a job
    def run_excel_download(self):
        self.login_by_selenium()
        time.sleep(3)
        self.headless_srch_download_btn()

    def convert_to_csv(self):
        
        today = datetime.today() - timedelta(days=1)
        str_today = today.strftime('%Y%m%d')

        file_to_convert = None
        type = self.type
        
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
            if os.path.exists('./csv') != True:
                os.mkdir('./csv')
            
            path_to_export = './csv/'
            # path_to_export = None

            # if os.name == 'nt':
            #     path_to_export = './csv/'
            # else:
            #     path_to_export = '/applications/anaconda3/mbs/data/'

            if df_to_csv['srvc'][1] == 'T':
                df_to_csv[['cnt','time','srvc']].to_csv(path_to_export + str_today + '_myshop_channel_hourly.csv', header=False)
            else:
                df_to_csv[['cnt','time','srvc']].to_csv(path_to_export + str_today + '_gsshop_channel_hourly.csv', header=False)
            
            os.remove('./'+file_to_convert)
        else:
            raise FileNotFoundError("excel file doesn't exist in the path")