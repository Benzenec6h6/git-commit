from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import os
import re
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
"""
念のために残してある
def profsleep(settime,locat):
  t=0
  while driver.find_elements(By.CSS_SELECTOR, locat)=="--％":
    sleep(1)
    t+=1
    if settime==t:
      break
"""
class scraping:
  def __init__(self, id, password, savename):
    self.id=id
    self.password=password
    self.savename=savename
    self.url = "https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETlgR001Control&_PageID=WPLETlgR001Rlgn50&_DataStoreID=DSWPLETlgR001Control&_ActionID=login&getFlg=on"

    #self.links=[]
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
    driver.implicitly_wait(30)

    username = WebDriverWait(driver, 30).until(lambda y: y.find_element(By.NAME, "user_id"))
    username.send_keys(self.id)

    password = WebDriverWait(driver, 30).until(lambda y: y.find_element(By.NAME, "user_password"))
    password.send_keys(self.password)

    login_btn = WebDriverWait(driver, 30).until(lambda y: y.find_element(By.NAME, "ACT_loginHome"))
    login_btn.click()

    WebDriverWait(driver, 30).until(lambda y: y.find_element(By.XPATH, "//*[@id='link02M']/ul/li[3]/a")).click()
    sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    self.companies = [name.getText() for name in soup.select('td.mtext>a')[2::2]]
    num=[]
    num = [i.parent.text for i in soup.select('td.mtext>a')[2::2]]
    for i in num:
        self.brand.extend(re.findall(r"^\d{4}", i))
    hold = soup.find_all('tr', attrs={'bgcolor': '#eaf4e8'})

    for h in hold:
        self.stocks.append(h.find('td').text)

    for j in self.brand:
        name=WebDriverWait(driver, 30).until(lambda y: y.find_element(By.ID, "top_stock_sec"))
        name.send_keys(j)
        WebDriverWait(driver, 30).until(lambda y: y.find_element(By.CSS_SELECTOR, "#srchK > a")).click()
        sleep(3)
        if len(driver.find_elements(By.ID, "posElem_190"))>0:
          WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#posElem_190>table>tbody>tr:nth-child(3)>td:nth-child(2)>p")))
          #profsleep(5,"#posElem_190>table>tbody>tr:nth-child(3)>td:nth-child(2)>p")
          html = driver.page_source
          soup = BeautifulSoup(html, 'html.parser')
          self.profits.append(soup.select_one('#posElem_190>table>tbody>tr:nth-child(3)>td:nth-child(2)>p').text)
          self.dividend.append(soup.select_one('#posElem_190>table>tbody>tr:nth-child(3)>td:nth-child(4)>p').text)
        else:
          WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#posElem_19-1>table>tbody>tr:nth-child(3)>td:nth-child(2)>p")))
          #profsleep(5,"#posElem_19-1>table>tbody>tr:nth-child(3)>td:nth-child(2)>p")
          html = driver.page_source
          soup = BeautifulSoup(html, 'html.parser')
          self.profits.append(soup.select_one('#posElem_19-1>table>tbody>tr:nth-child(3)>td:nth-child(2)>p').text)
          self.dividend.append(soup.select_one('#posElem_19-1>table>tbody>tr:nth-child(3)>td:nth-child(4)>p').text)        
        
        try:
            WebDriverWait(driver, 30).until(lambda y: y.find_element(By.CSS_SELECTOR, "td:nth-child(8)>span>a")).click()
            driver.implicitly_wait(60)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            yu=""
            y = soup.find('table', attrs={'summary': '優待内容'}).find('tbody').select("p.fm01")
            for j in y:
                yu+=j.text+'\n'
            self.yutai.append(yu.strip())
        except:
            self.yutai.append("情報無し")

    driver.quit()

  def calc(self):
    div = []
    d=[]
    s = [float(h.replace(',', '')) for h in self.stocks]

    for i in self.dividend:
        st0 = [float(d) for d in re.findall(r"(\d+(?:\.\d+)?)", i)]
        try:
            div.append([st0[0], st0[1]])
        except:
            div.append(st0[0])
    
    for i in range(0, len(div)):
        try:
            self.total.append(str(div[i][0] * s[i])+"~"+str(div[i][1] * s[i]))
        except:
            self.total.append(str(div[i] * s[i]))
            

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
cur.execute(sql,'SBI')
id_pas = cur.fetchall()
cur.close()
conn.close()

file_path=glob.glob('/app/csv/SBI*.csv')
for i in file_path:
  os.remove(i)

for users in id_pas:
  driver = webdriver.Remote(
    command_executor = os.environ["SELENIUM_URL"],
    options = webdriver.ChromeOptions()
  )
  info=scraping(users[1],users[2],users[3])
  info.access()
  info.calc()
  info.set_info()