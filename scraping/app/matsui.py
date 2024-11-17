from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from PIL import Image
from time import sleep
import pyocr.builders
import os
import glob
import shutil
import pandas as pd
import pymysql
import datetime

def getConnection():
  return pymysql.connect(
    host='completed-db-1',
    port=int(3306),
    db='pass_manage',
    user='root',
    passwd='root',
    charset='utf8',
  )

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

class scraping:
    def __init__(self, id, password, savename):
        self.id=id
        self.password=password
        self.savename=savename
        self.url = "https://trade.matsui.co.jp/mgap/login"

        self.companies=[]
        #銘柄番号
        self.brand=[]
        #保有数
        self.stocks=[]
        #配当
        self.dividend=[]
        #利回り
        self.profits=[]
        #優待利回り
        self.yu_prof=[]
        #配当合計
        self.total=[]
        self.yutai=[]
        self.df=pd.DataFrame()
        #ocr
        self.tools = pyocr.get_available_tools()
        self.tool = self.tools[0]

    def access(self):
        driver.get(self.url)
        username = driver.find_element(By.ID, "login-id")
        username.send_keys(self.id)

        password = driver.find_element(By.ID, "login-password")
        password.send_keys(self.password)

        login_btn = driver.find_element(By.CLASS_NAME, "login-form-submit")
        login_btn.click()

        try:
            WebDriverWait(driver, 5).until(lambda x: x.find_element(By.CSS_SELECTOR, "div#popup_deal>img")).click()
        except:
            pass
        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CLASS_NAME, "btn-menu-spot-sell")).click()
        sleep(3)
        p=WebDriverWait(driver, 30).until(lambda x: x.find_elements(By.CSS_SELECTOR, "select#grid-paging-select>option"))
        j=0
        for i in range(len(p)):
            sleep(3)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            self.companies.extend(i.getText() for i in soup.select('span.body-text')[0::2])
            self.brand.extend(i.getText().replace("\xa0東証", "").replace("\xa0名証", "").replace("\xa0札証", "") for i in soup.select('span.body-text')[1::2])

            w = driver.execute_script('return document.body.scrollWidth')
            h = driver.execute_script('return document.body.scrollHeight')
            driver.set_window_size(w, h)

            # 範囲を指定してスクリーンショットを撮る
            png=WebDriverWait(driver, 30).until(lambda x: x.find_elements(By.CLASS_NAME, 'stockBalance'))

            # ファイルに保存
            for k in png:
                s=k.screenshot_as_png
                with open('./stock/stock'+str(j)+'.png', 'wb') as f:
                    f.write(s)
                j+=1
            try:
                WebDriverWait(driver, 5).until(lambda x: x.find_element(By.CSS_SELECTOR, "a.next-page-btn")).click()
            except:
                break

        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.XPATH, "//*[@id='common-header']/div[2]/ul[1]/li[10]")).click()
        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.XPATH, "//*[@id='information-retrieval-top']/div/div[1]/ul[1]")).click()
        sleep(1)
        driver.switch_to.window(driver.window_handles[1])

        for i in self.brand:
            s = WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, "input.form-control.input.symbol-input"))
            s.send_keys(i)
            WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, "div.btn.btn-default-green.btn-search-header")).click()
            WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, "#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div.tab-header > ul > li:nth-child(1)")).click()
            sleep(3)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            p=soup.select_one("#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div:nth-child(2) > div > div > div > div.stock-basic-info > div:nth-child(3) > div > div:nth-child(2) > div.value")
            d=soup.select_one("#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div:nth-child(2) > div > div > div > div.stock-basic-info > div:nth-child(3) > div > div:nth-child(3) > div.value")
            y=soup.select_one("#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div:nth-child(2) > div > div > div > div.stock-basic-info > div:nth-child(3) > div > div:nth-child(1) > div.value > div").text
            self.profits.append(p.text)
            self.dividend.append(d.text)
            if y=="あり":
                WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR,"div.value.link-text")).click()
                sleep(3)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                self.yu_prof.append(soup.select_one('#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div.col-contents-block > div > div > div.shareholder-middle > div.shareholder-data > div.shareholder-value > div:nth-child(2) > div.value').getText())
                e=""
                try:
                    y=soup.select_one('#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div.col-contents-block > div > div > div.shareholder-bottom > div:nth-child(3) > div').getText()
                    table=soup.select_one('#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div.col-contents-block > div > div > div.shareholder-bottom > div:nth-child(3) > table > tbody')
                    td=table.find_all('td')
                    t=""
                    for u in td:
                        t+=(u.text+"\n")
                    e=y+"\n"+t
                except:
                    pass
                y=soup.select_one('#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div.col-contents-block > div > div > div.shareholder-bottom > div.col-contents-block > div').getText()
                table=soup.select_one('#root > div:nth-child(2) > div > div > div > div > div > div > div > div.stocks-body > div.col-contents-block > div > div > div.shareholder-bottom > div:nth-child(2) > table > tbody')
                td=table.find_all('td')
                t=""
                for u in td:
                    t+=(u.text+"\n")
                if e!="":
                    self.yutai.append(e+"\n"+y+"\n"+t)
                else:
                    self.yutai.append(y+"\n"+t)
            else:
                self.yu_prof.append("0%")
                self.yutai.append("情報なし")
        driver.close()
        driver.quit()

    def picture(self):
        dir_path = "./stock"
        file_list = os.listdir(dir_path)
        size = len(file_list)
        for i in range(size):
            img = Image.open("./stock/stock"+str(i)+".png")
            img = img.crop((80, 0, 135, 16))
            img =add_margin(img,5,10,0,0,(255,255,255))

            text = self.tool.image_to_string(
                img,
                lang="eng",
                builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
            )
            self.stocks.append(text.replace(".",""))

    def sum(self):
        for i in range(len(self.stocks)):
            try:
                div=float(self.dividend[i].replace("円",""))
                self.total.append(div*float(self.stocks[i]))
            except:
                self.total.append(0)

    def set_info(self):
        dt=datetime.datetime.today()
        today=dt.strftime('%Y/%m/%d')
        self.df['銘柄コード']=self.brand
        self.df['社名']=self.companies
        self.df['配当利回り']=self.profits
        self.df['優待利回り']=self.yu_prof
        self.df['保有数']=self.stocks
        self.df['配当']=self.dividend
        self.df['合計']=self.total
        self.df['優待']=self.yutai
        self.df.set_index('銘柄コード',inplace=True)
        self.df.to_csv('csv/'+self.savename+today.replace("/","-")+'.csv')

conn = getConnection()
cur = conn.cursor()
sql = ('select * from user where company=%s;')
cur.execute(sql,'matsui')
id_pas = cur.fetchall()
cur.close()
conn.close()

file_path=glob.glob('/app/csv/matsui*.csv')
for i in file_path:
  os.remove(i)

for users in id_pas:
    driver = webdriver.Remote(
        command_executor = os.environ["SELENIUM_URL"],
        options = webdriver.ChromeOptions()
    )
    info=scraping(users[1],users[2],users[3])
    info.access()
    info.picture()
    info.sum()
    info.set_info()
    shutil.rmtree('stock')
    os.mkdir('stock')