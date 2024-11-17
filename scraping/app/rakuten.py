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
    self.url = "https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html"
    self.b_url = "https://member.rakuten-sec.co.jp"
    self.df=pd.DataFrame()
    self.links=[]
    self.companies=[]
    #銘柄コード
    self.brand=[]
    #保有数
    self.stocks=[]
    #株価
    self.price=[]
    #配当
    self.dividend=[]
    #利回り
    self.profits=[]
    #配当合計
    self.total=[]
    self.yutai=[]

  def access(self):
    driver.get(self.url)
    driver.implicitly_wait(5)
    username = driver.find_element(By.NAME, "loginid")
    username = username.send_keys(self.id)

    password = driver.find_element(By.NAME, "passwd")
    password = password.send_keys(self.password)

    login_btn = driver.find_element(By.NAME, "submit%template")
    login_btn.click()

    menu = driver.find_element(By.CSS_SELECTOR, "li.pcm-gl-g-header-nav__item.pcm-gl-g-header-nav__item--menu>button")
    menu.click()

    hoyu = driver.find_element(By.XPATH, "//*[@id='megaMenu']/div/div[1]/div[2]/div/div/div[1]/ul/li[1]/ul/li[1]/a")
    hoyu.click()

    driver.implicitly_wait(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    num = soup.select('td.align-C.R0')
    self.brand.extend([i.getText().replace("\n", "").replace("\t", "") for i in num])
    link = soup.select('td.align-L.valign-M>a')
    self.companies.extend([i.getText().replace("\n", "").replace("\t", "") for i in link])
    self.links.extend([self.b_url+i.get('href') for i in link])
    hoyu = soup.select('a.tooltip')
    self.stocks.extend([i.getText().replace("\n", "").replace("\t", "") for i in hoyu])

    for i in self.links:
        driver.get(i)
        self.dividend.append(driver.find_element(By.XPATH, "//*[@id='auto_update_field_info_jp_stock_price']/tbody/tr/td[1]/form[2]/div[2]/div[2]/table[2]/tbody/tr[1]/td[2]").text)
        p=driver.find_element(By.CLASS_NAME, "price-01").text
        self.price.append(float(p.replace(",", "")))

        link = driver.find_element(By.CLASS_NAME, "last-child")
        l = link.find_element(By.TAG_NAME, "a").get_attribute('href')
        driver.get(l)

        driver.switch_to.frame('J010101-011-1')
        try:
            yu = driver.find_elements(By.CLASS_NAME, "tbl-data-02")[1]
            self.yutai.append(yu.find_element(By.TAG_NAME, "tbody").text)
        except:
            self.yutai.append("情報なし")

    st = [float(i.replace(",", "").replace("株", "")) for i in self.stocks]
    for i in range(len(self.dividend)):
        div = float(self.dividend[i])
        a = round((div / self.price[i])*100, 2)
        self.profits.append(str(a)+"%")
        self.total.append(div*st[i])

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
cur.execute(sql,'rakuten')
id_pas = cur.fetchall()
cur.close()
conn.close()

file_path=glob.glob('/app/csv/rakuten*.csv')
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