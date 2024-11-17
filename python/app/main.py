import uvicorn
from fastapi import FastAPI, Form, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pymysql
import socket

app = FastAPI()

app.mount("/static", app=StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def getConnection():
  return pymysql.connect(
    host='fullenv-db-1',
    port=int(3306),
    db='pass_manage',
    user='root',
    passwd='root',
    charset='utf8',
  )

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.get('/password', response_class=HTMLResponse)
async def password(request: Request):
  conn = getConnection()
  cur = conn.cursor()
  sql = ('describe user;')
  cur.execute(sql)
  columns = cur.fetchall()
  sql =('select * from user order by company;')
  cur.execute(sql)
  datalist = cur.fetchall()

  cur.close()
  conn.close()
  return templates.TemplateResponse("password.html",{"request":request,"datalist":datalist,"columns":columns})

@app.get('/manual/{msg}', response_class=HTMLResponse)
async def manual(msg: str, request: Request):
  return templates.TemplateResponse("manual.html",{"request":request,"msg":msg})

@app.post('/manual/{msg}', response_class=HTMLResponse)
async def manual(msg: str, request: Request):
  return templates.TemplateResponse("manual.html",{"request":request,"msg":msg})

@app.get('/scraping')
async def scraping():
  return RedirectResponse(url='http://localhost:7900/?autoconnect=1&resize=scale&password=secret')

@app.post('/execution')
def execution(exe: str = Form()):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(("fullenv-selenium-chrome-1", 8000)) #クライアント側は相手ホスト名とポート番号を指定
  s.send(exe.encode("utf-8"))
  s.close()
  return RedirectResponse('/manual/'+exe)