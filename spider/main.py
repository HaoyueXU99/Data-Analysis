# -*- coding = utf-8 -*-
# @Time : 2021-07-07 13:51
# @Author : Haoyue XU
# @File : main.py
# @Software : PyCharm

import random
import time
import datetime

import requests
from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import ssl
import xlwt
import xlutils

DICT = {}  # 一个全局的变量储存 IP 地址


def main():
    start_time = time.time()  # 记录初始时间
    # 0.获得IPlist
    get_iplist()

    baseurl = "https://list.oilchem.net/140/1073/"  # 定义基本页面（可更改）

    # 1.爬取网页
    print("Start crawling ...")
    datalist = get_data(baseurl)

    # 2.保存数据
    savepath = "Enterprise_News02.xls"  # 保存数据的地址（可更改）
    save_file(savepath, datalist)  # 保存数据
    end_time = time.time()  # 记录结束时间
    total_time = end_time - start_time  # 记录总共用时
    print("Completed! Total time: %s" % total_time)


def get_data(baseurl):
    data = [""]
    my_columns = ["日期", "企业名称", "动态"]  # 定义列表名（可更改）
    data[0] = [my_columns]  # 初始化数组

    # 调用获取页面信息的函数 1 次
    for i in range(0, 5):  # （可更改）
        print("page %d ...." % (i + 1))
        url = baseurl + str(i + 1) + ".html"  # 调用第i+1页网页
        html = ask_url(url, i)  # 保存调用的网页
        row_list = parse_web(html)  # 解析网页，并获得新的一行数据
        for i in range(len(row_list)):
            data[0].append(row_list[i])  # 将新的一行数据保存在data 数组中
        time.sleep(random.uniform(1, 3))  # 随机睡眠1-3s,为了防止网页抓取数据过快被封

    # print(data)
    return data


def parse_web(html):
    row_list = []
    # 逐一解析数据
    bs = BeautifulSoup(html, "html.parser")
    divs = bs.find_all("div", {"class": "newslist"})  # 获取class属性为newslist的div模块
    # print(divs[0])
    t_list = divs[0].findAll("a", text=re.compile("\[甲醇\]"))  # 匹配"[甲醇]"字符获得相应的list  <a> .... </a>

    i = 0

    for link in t_list:  # 循环每一个需要的超链接列 <a> .... </a>
        # print(link)
        if 'href' in link.attrs:  # 如果<a>...</a>中有 href 的话
            new_url = link.attrs['href']  # 就把href存为新的url
            # print(new_url)
            if new_url.find("https") == -1:
                new_url = "https" + new_url  # 有些url的值可能会有缺失，要补全

            new_html = ask_url(new_url, i)  # 保存获取到的细节页面
            new_bs = BeautifulSoup(new_html, "html.parser")
            date1 = new_bs.find(text=re.compile("(\d{4}-\d{1,2}-\d{1,2})"))
            mat1 = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", date1)  # 获得第一个日期 2020-07-13

            divs = new_bs.find_all("div", {"id": "content"})  # 获取id为content的div模块
            #print(divs[0])
            content = divs[0].get_text()  # 获取里面的所有text
            # date2 = content.findAll(text=re.compile("(\d+月\d+日)")) # 如果由于页面的原因无法读取
            # if len(date2) == 0:                                 # 我们需要强行用别的方式判断，这一块在绝大部分代码中不需要
            #     date2 = [""]
            #     month_str = new_bs.findAll(text=re.compile("隆众资讯(\d+)"))
            #     month = re.search(r"(\d+)", month_str[0])
            #     day_str = new_bs.findAll(text=re.compile("月(\d+)日"))
            #     day = re.search(r"(\d+)", day_str[0])
            #     date2[0] = month[0] + "月" + day[0] + "日"
            #     # print(date2[0])
            #print(content)
            mat2 = re.findall(r"(\d+\D+\d+日)", content)  # 获得第二个日期

            checkdate, final_date = check_date(mat1[0], mat2[0])  # 判断两个日期是否匹配

            new_row = divide_mess(final_date, new_bs)  # 解析该页面的信息，返回值是一个数组
            row_list.append(new_row)
            time.sleep(random.uniform(0.2, 0.6))  # 随机睡眠0.2到0.6秒
            
        i += 1
    return row_list


def divide_mess(date, bs):
    row_list = ["" for x in range(0, 3)]  # 初始化一行数据
    row_list[0] = date  # 第一行记录日期

    name = bs.findAll(text=re.compile("\[甲醇\]：(.*?)甲醇"))
    a = re.search(r"\[甲醇\]：(.*?)甲醇", name[0])
    row_list[1] = a[1]

    divs = bs.find_all("div", {"id": "content"})  # 获取id为content的div模块
    content = divs[0].get_text()  # 获取里面的所有text
    result = re.search(r"报道：(.*)", content)  # 获得第二个日期
    row_list[2] = result[1]
    # print(row_list)

    return row_list


def check_date(date_new, date):
    a = datetime.datetime.strptime(date_new, '%Y-%m-%d').strftime('%m-%d')
    pattern = re.compile(r'(\d日\d日)')

    match = pattern.match(date)

    if match:
        b = datetime.datetime.strptime(date, '%m日%d日').strftime('%m-%d')
    else:
        b = datetime.datetime.strptime(date, '%m月%d日').strftime('%m-%d')

    if a == b:
        return True, date_new
    else:
        print("There is a date mismatch data, check the page with publishing time %s [index 1]" % date)
        print("the mismatch time is %s vs %s" % (a, b))
        a = datetime.datetime.strptime(date_new, '%Y-%m-%d').strftime('%Y')
        date_new = a + "-" + b
        return False, date_new


def get_iplist():
    pass


# 通过url像服务器发送请求，获得一个html的网页
def ask_url(url, i):
    # 用户代理，表示告诉服务器，我们式什么类型的机器，浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）

    head = {}
    # ----（可更改）----
    # head[
    #    "Cookie"] = "_pass=cnfpc54321; _user=futurepetro; _remberId=true; _member_user_tonken_=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZWMiOiIkMmEkMTAkbERCV08yRC9teG90RVh6MHlidzd5ZWRvTzVmVkJBdW9OYnAxVUtRdHAvMmJkSmxZWHFlT0MiLCJuaWNrTmFtZSI6IiIsInBpYyI6IiIsImV4cCI6MTYyNTgxNjIxMywidXNlcklkIjozODU3MTcsImlhdCI6MTYyMzIyNDIxMywianRpIjoiOWVjOWE5NDItYTE1ZS00Mzg3LTgyNjEtNDI3MTY5N2VlYWRkIiwidXNlcm5hbWUiOiJmdXR1cmVwZXRybyJ9.ygiPGO9XQA8Hc5tm1_bW2e3QulwAHKwMjVCizB19Dqw; refcheck=ok; refpay=0; refsite=; oilchem_refer_url=; Hm_lvt_47f485baba18aaaa71d17def87b5f7ec=1623206153,1623286756,1623308263,1623372604; Hm_lvt_e91cc445fdd1ff22a6e5c7ea9e9d5406=1623206153,1623286757,1623308263,1623372604; oilchem_land_url=https://coalchem.oilchem.net/coalchem/methanol.shtml; Hm_lpvt_e91cc445fdd1ff22a6e5c7ea9e9d5406=1623394110; Hm_lpvt_47f485baba18aaaa71d17def87b5f7ec=1623394110"
    # ----------------

    head["Cookie"] = "_user=futurepetro; _pass=cnfpc54321; refcheck=ok; refpay=0; refsite=; oilchem_refer_url=; oilchem_land_url=https://list.oilchem.net/140/4352/; Hm_lvt_e91cc445fdd1ff22a6e5c7ea9e9d5406=1625468121,1625469629,1625557603,1626015784; Hm_lvt_47f485baba18aaaa71d17def87b5f7ec=1625468127,1625469630,1625558042,1626015788; __snaker__id=IGj9Bc1tdpYoEKNs; gdxidpyhxdE=6ScGNlK2JtKpuBcjm9EtxdwDsTmVH0OCEMzChrPwyvKIxaCA46JCaNiqltpV3C5T2kIZx1gqg3CwwYO+0yP6\aJlnNWZRjmMhaut0E+2MJ9Psb4NxEmbKoOwULocHxDVg83QdnmKRafvJNNy48ajZD\AQwSTN4aIP6zhGrIBTpnokBk\:1626016695731; _9755xjdesxxd_=32; YD00126731780350:WM_NI=Q9p54DyyJDSfYlderU4ne4fgVgM8V4lAXBFmQpbanAmD+0R4mYlcNzQPLNwqnF+A/BDcNC84gOgzru6qHdTdRgUtu001v9pFk7gkouKOESzFFlBJOmd7KyAETvtObB79bTI=; YD00126731780350:WM_NIKE=9ca17ae2e6ffcda170e2e6eeccd780b2baa8b0b44fb48a8ba6c45a929a8abab6398e87fbb2f25b818a00a3c72af0fea7c3b92a93e7c0d6b750bba786a5d26e9bb4ac86f15ff8b2abd5e56d96b983d9d540b09f98a3c56793b0ae82ed4baf9ce5d1d140af87a484cd72939084aff67bae9ae5a2ae4a88bd82a4bb40a591a99bf17ff6af8885d77092b99b95f83cf4efbadaf34ea9e9a98cee7f89918bb4f94e86b48eabce67a8e9859ac44f98aabcb0e14af5e7aeb5cc37e2a3; YD00126731780350:WM_TID=F+5cBdn10MdFAVREFAN6zMNpQsVWFkAX; _imgCode=09e07c575ea947c3394464105b9ec873; _remberId=true; _member_user_tonken_=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZWMiOiIkMmEkMTAkZGdBQUZ5ejNUMER4a0RkRXhRSHZjLkNnaS5TbVBQcDJpTmYuTlVoa3doZHdQL0RLQ2hDb3kiLCJuaWNrTmFtZSI6IiIsInBpYyI6IiIsImV4cCI6MTYyODYwODM1OSwidXNlcklkIjozODU3MTcsImlhdCI6MTYyNjAxNjM1OSwianRpIjoiM2NkZDA1YTktOTZkYi00NDgxLWFjMDgtZDlhNDMyMGEwZjQ4IiwidXNlcm5hbWUiOiJmdXR1cmVwZXRybyJ9.AT46_4fXgPmkSEz1miVGXGn6bEdQYxfzTJhHUNBXu5A; Hm_lpvt_47f485baba18aaaa71d17def87b5f7ec=1626016359; Hm_lpvt_e91cc445fdd1ff22a6e5c7ea9e9d5406=1626016359"

    head[
        "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"

    # cookie中有登录后的用户信息，可以带上cookie来获取登录后可查看的信息
    # ！！！ 所以cookie需要根据不同的网站进行更改
    # User-Agent 必须要更改，因为要告诉服务器你不是一个机器人，而是一个正常的浏览器

    # 定义代理ip
    # 这里我们先暂时不管IP
    proxy_addr = "122.241.72.191:808"

    # 设置代理
    proxy = urllib.request.ProxyHandler({"http": proxy_addr})

    # 创建一个opener
    opener = urllib.request.build_opener(proxy, urllib.request.ProxyHandler)
    # 将opener安装为全局
    urllib.request.install_opener(opener)
    req = urllib.request.Request(url=url, headers=head)
    context = ssl._create_unverified_context()
    html = ""
    try:
        response = urllib.request.urlopen(req, context=context)
        html = response.read().decode('utf-8')
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    return html


# 保存数据
def save_file(savepath, datalist):
    print("save.....")
    workbook = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象

    for i in range(0, 1):  # 这里我们只需要一张工作表 （可更改）
        worksheet = workbook.add_sheet('sheet%d' % (i + 1))  # 创建工作表 将不同的数据放在不同的工作表中
        for list_index, output_list in enumerate(datalist[i]):
            for element_index, element in enumerate(output_list):
                worksheet.write(list_index, element_index, element)

    workbook.save(savepath)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

