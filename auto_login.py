# coding: utf-8
# Author：dota_st
# Date ：2021/1/21 17:43
# Tool ：PyCharm
import urllib3
import re
import requests
from urllib import request as RR
import json
from retrying import retry
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 定义通用的请求头
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
           }

SCKEY = ""
USER = ""
GITC = ""

# 使用qmsg酱发送消息


def push_message(message):
    data = {'msg': message}
    for x in data:
        if x == 'msg':
            msg = data[x]
    if SCKEY != "":
        return requests.post(f"https://qmsg.zendee.cn/send/{SCKEY}" + "?msg=" + USER + " 签到脚本已自动执行 " + '\n' + msg)
    else:
        return False

# 获取签到结果返回信息


def login_result(cookies):
    global headers
    headers['X-Requested-With'] = "XMLHttpRequest"
    headers['cookie'] = cookies
    req = RR.Request(url='https://ctf.bugku.com/user/checkin', headers=headers)  # 这样就能把参数带过去了
    # 下面是获得响应
    with RR.urlopen(req) as f:
        Data = f.read()
        data = json.loads(Data)
        print(data['msg'])
        push_message(data['msg'])

# 登录判断


def login_status(res):
    if ("登录成功" in res.text):
        print("cookie提取成功!")
        for i in res.headers['Set-Cookie'].split(','):
            if ('PHPSESSID' in i):
                login_result(i.strip())
                break

# 主函数


@retry(stop_max_attempt_number=3)
def main_fun():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
    keep = requests.Session()
    div = BeautifulSoup(keep.get("https://ctf.bugku.com/login".rstrip(), headers=headers, verify=False).text, 'lxml')
    git_url = div.find('a', class_='btn btn-floating btn-github')['href']
    git_cookie = 'user_session={git_line1}; __Host-user_session_same_site={git_line2};'.format(git_line1=GITC, git_line2=GITC)
    headers['cookie'] = git_cookie
    flag = keep.get("https://github.com/settings/profile", headers=headers, verify=False, allow_redirects=False)
    if flag.status_code != 200:
        push_message("github的cookie失效！")
    res = keep.get(git_url, headers=headers, verify=False)
    login_status(res)
    if "github.githubassets.com" in res.text:
        print(res.text)
        choose = res.text.split('<form action="')[1].split('<input type="hidden" name="scope"')[0]
        rule = re.compile('name="(.*?)".*?value="(.*?)"')
        form_data = rule.findall(choose)
        Data = {}
        for i in form_data:
            Data[i[0]] = i[1]
        Data['authorize'] = 1
        formurl = "https://github.com" + choose.split('"')[0]
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            "cookie": git_url
        }
        res = keep.post(formurl, data=Data, headers=headers, verify=False)
        login_status(res)
    elif("登录成功" not in res.text):
        push_message("超时错误")
    keep.cookies.clear()
    keep.close()


def main():
    main_fun()


if __name__ == '__main__':
    main()
