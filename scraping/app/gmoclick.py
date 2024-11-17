from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import os
import glob
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

class scraping:
    def __init__(self, id, password, savename):
        self.id=id
        self.password=password
        self.savename=savename
        self.url = "https://sec-sso.click-sec.com/loginweb/sso-redirect?s=01p=08"

        self.links=[]
        self.companies=[]
        #銘柄番号
        self.brand=[]
        #保有数
        self.stocks=[]
        #配当
        self.dividend=[]
        #利回り
        self.profits=[]
        #配当合計
        self.total=[]
        self.yutai=[]
        self.df=pd.DataFrame()

    def access(self):
        driver.get(self.url)
        driver.implicitly_wait(10)
        username = driver.find_element(By.NAME, "j_username")
        username = username.send_keys(self.id)

        password = driver.find_element(By.NAME, "j_password")
        password = password.send_keys(self.password)

        login_btn = driver.find_element(By.NAME, "LoginForm")
        login_btn.click()

        kabusiki = driver.find_element(By.CLASS_NAME, "js-kabu")
        driver.get(kabusiki.get_attribute("href"))
        hoyu = driver.find_element(By.ID, "kabuSubMenuGenPosition")
        driver.get(hoyu.get_attribute("href"))

        company=[]
        l=[]
        while True:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            link = soup.select('tbody.is-alternate>tr.is-selectable>td.col-02>a')
            self.links.extend([i.get('href') for i in link])
            for i in link:
                l=i.select('span')
                company.extend([i.getText() for i in l])
            stock = soup.select('tbody.is-alternate>tr.is-selectable>td.col-03>div:nth-child(1)')
            self.stocks.extend([i.getText().replace("\n", "") for i in stock])
            try:
                driver.find_element(By.ID, "nextJumpPage").click()
                sleep(1)
            except:
                break

        for i in range(0,len(company),2):
            self.companies.append(company[i])
            self.brand.append(company[i+1])

        yu = []
        d=[]
        for i in self.links:
            driver.get(i)
            driver.set_page_load_timeout(5)
            sleep(1)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            l = soup.select('td#probableDividendYield')
            self.profits.extend([i.getText().replace("\n", "") for i in l])
            d = soup.select('td#dpsYear')
            self.dividend.extend([i.getText().replace("\n", "").strip() for i in d])
            try:
                WebDriverWait(driver, 30).until(lambda y: y.find_element(By.XPATH, "//*[@id='yutaiLink']")).click()
                driver.implicitly_wait(30)
                sleep(1)
                yu = WebDriverWait(driver, 30).until(lambda y: y.find_element(By.CSS_SELECTOR, "table.m-table-03"))
                self.yutai.append(yu.find_element(By.TAG_NAME, "tbody").text)
            except:
                self.yutai.append("情報なし")

        st = [float(i.replace('株', '').replace(',', '')) for i in self.stocks]
        div = []
        for i in self.dividend:
            try:
                div.append(float(i.replace('円', '').replace(',', '')))
            except ValueError:
                div.append(0)

        for i in range(len(st)):
            self.total.append(st[i]*div[i])
        
        driver.quit()

    def set_info(self):
        dt=datetime.datetime.today()
        today=dt.strftime('%Y/%m/%d')
        self.df['brand']=self.brand
        self.df['companies']=self.companies
        self.df['profits']=self.profits
        self.df['stocks']=self.stocks
        self.df['dividend']=self.dividend
        self.df['total']=self.total
        self.df['yutai']=self.yutai
        self.df.set_index('brand',inplace=True)
        self.df.to_csv('csv/'+self.savename+today.replace("/","-")+'.csv')

conn = getConnection()
cur = conn.cursor()
sql = ('select * from user where company=%s;')
cur.execute(sql,'gmoclick')
id_pas = cur.fetchall()
cur.close()
conn.close()

file_path=glob.glob('/app/csv/gmoclick*.csv')
for i in file_path:
  os.remove(i)

for users in id_pas:
    driver = webdriver.Remote(
        command_executor = os.environ["SELENIUM_URL"],
        options = webdriver.ChromeOptions()
    )
    info=scraping(users[1],users[2],users[3])
    info.access()
    info.set_info()