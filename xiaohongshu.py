import re
import time
import pymysql
import requests
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class searchXiaoHoneShu():
    def __init__(self, timeout=None, service_args=[],proxy=None):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.4.4; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36"')
        # chrome_options.add_argument('lang=zh_CN.UTF-8')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('window-size=375x812')
        chrome_options.add_argument('--proxy-server=http://' + proxy)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.baseUrl = 'https://www.xiaohongshu.com/search/keyword?q='
        self.urllist = []
        self.site = []
        self.exceptCount = 0
        self.deep_count = 0

    def __del__(self):
        self.browser.close()

    def saveResult(self, result):
        db = pymysql.connect(host='mysql', user='root', password='root', port=3306, db='Maoyan')
        cursor = db.cursor()
        sql = 'INSERT INTO xiaohongshu(url, author, time, content) values(%s, %s, %s, %s)'
        try:
            cursor.execute(sql, (result['url'], result['author'], result['time'], result['content']))
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()

    def getResult(self):
        num = 0
        for url in self.urllist:
            num += 1
            time.sleep(5)
            print('剩余' + str(len(self.urllist) - num) + '条')
            if url in self.site:
                print('重复链接')
                continue
            print(url)
            self.site.append(url)
            try:
                self.browser.get(url)
                time.sleep(3)
                try:
                    if (self.browser.find_element_by_css_selector('.publish-date').get_attribute('textContent') is not None and re.match('N', self.browser.find_element_by_css_selector('.publish-date').get_attribute('textContent'))):
                        self.browser.close()
                        proxy = self.getProxy()
                        chrome_options = webdriver.ChromeOptions()
                        # chrome_options.add_argument('--headless')
                        chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.4.4; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36"')
                        # chrome_options.add_argument('lang=zh_CN.UTF-8')
                        chrome_options.add_argument('--proxy-server=http://' + proxy)
                        self.browser = webdriver.Chrome(chrome_options=chrome_options)
                        self.browser.get(url)
                except:
                    print('匹配不到')
                    continue
                result = {}
                result['url'] = url
                result['content'] = self.browser.find_element_by_css_selector('.content .content').text
                print(result['content'])
                result['time'] = self.browser.find_element_by_css_selector('.publish-date span').get_attribute('textContent')
                print(result['time'])
                result['author'] = self.browser.find_element_by_class_name('nickname').get_attribute('textContent')
                print(result['author'])
                self.saveResult(result = result)
                print('success')
                time.sleep(2)
                if self.deep_count <= 3:
                    self.deep_count += 1
                    if self.browser.find_elements_by_css_selector('[class="note-item note"] a'):
                        panelUrls = self.browser.find_elements_by_css_selector('[class="note-item note"]  a')
                        for panelUrl in panelUrls:
                            panelUrl = panelUrl.get_attribute('href')
                            if panelUrl not in self.site:
                                self.urllist.append(panelUrl)
                        print('有相关笔记')
                    else:
                        print('无相关笔记')
                else:
                    self.deep_count = 0
            except:
                self.exceptCount += 1
                print('采集失败：' + str(self.exceptCount) + '次')
                if self.exceptCount % 2 == 0:
                    self.browser.close()
                    proxy = self.getProxy()
                    chrome_options = webdriver.ChromeOptions()
                    # chrome_options.add_argument('--headless')
                    chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.4.4; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36"')
                    # chrome_options.add_argument('lang=zh_CN.UTF-8')
                    chrome_options.add_argument('--proxy-server=http://' + proxy)
                    self.browser = webdriver.Chrome(chrome_options=chrome_options)
                continue

    def getKeyword(self):
        db = pymysql.connect(host='mysql', user='root', passwd='root', port=3306, db='Maoyan')
        cursor = db.cursor()
        sql = 'select * from keywords'
        cursor.execute(sql)
        datas = cursor.fetchall()
        db.close()
        for data in datas:
            try:
                self.browser.get(self.baseUrl + data[1])
                urls = self.browser.find_elements_by_css_selector('.note > a')
                if len(urls) == 0:
                    self.browser.close()
                    proxy = self.getProxy()
                    chrome_options = webdriver.ChromeOptions()
                    # chrome_options.add_argument('--headless')
                    chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.4.4; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36"')
                    # chrome_options.add_argument('lang=zh_CN.UTF-8')
                    chrome_options.add_argument('--proxy-server=http://' + proxy)
                    self.browser = webdriver.Chrome(chrome_options=chrome_options)
                    self.browser.get(self.baseUrl + data[1])
            except:
                continue
            for url in urls:
                url = url.get_attribute('href')
                if url not in self.site:
                    self.urllist.append(url)
            self.getResult()

    def getProxy(self):
        params = {
            # 'num' : 1,	
            # 'pro' : '',	
            # 'city' : 0,	
            # 'regions' : '',	
            # 'yys' : 0,	
            # 'port' : 1,	
            # 'type' : 2,
            # 'ts' : 0,	
            # 'ys' : 0,	
            # 'cs' : 0,	
            # 'lb' : 1,
            # 'mr' : 1,
            # 'pb' : 4,
            # 'sb' : 1,
            # 'time': 1	
        }
        apiUrl = ''
        r = requests.get(apiUrl, params=params)
        content = r.json()
        ip = content['data'][0]['ip']
        port = content['data'][0]['port']
        proxy = str(ip) + ':' + str(port)
        print('更换代理:' + proxy)
        return proxy

    def restartBrowser():
        self.browser.close()
        proxy = self.getProxy()
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.4.4; HTC D820u Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36"')
        # chrome_options.add_argument('lang=zh_CN.UTF-8')
        chrome_options.add_argument('--proxy-server=http://' + proxy)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

        
if __name__ == '__main__':
    firstProxy = ''
    main = searchXiaoHoneShu(proxy=firstProxy)
    main.getKeyword()







