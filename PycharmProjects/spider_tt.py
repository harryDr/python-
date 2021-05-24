#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/4/15 10:33
# @Author  : DR

import requests
from bs4 import BeautifulSoup
import csv, re, shlex, random


class BaseDownLoad(object):
    def __init__(self, page):
        self.page = page
        self.fileName = 'stock_0419.csv'
        self.targetUrl = 'https://fundapi.eastmoney.com/fundtradenew.aspx' \
                         '?ft=gp&sc=1n&st=desc&pi={0}&pn=100&cp=&ct=&cd=&ms=&fr=&plevel=&fst=&ftype=&fr1=&fl=0&isab=1'.format(
            self.page)  # 需要获取列表的url

        # 偏股型
        # self.targetUrl = 'https://fundapi.eastmoney.com/fundtradenew.aspx' \
        #                  '?ft=pg&sc=1n&st=desc&pi={0}&pn=100&cp=&ct=&cd=&ms=&fr=&plevel=&fst=&ftype=&fr1=&fl=0&isab=1'.format(
        #     self.page)
        # 混合型  --没有成功
        # self.targetUrl = 'http://fund.eastmoney.com/data/FundGuideapi.aspx?' \
        #                  'dt=4&ft=hh&sd=&ed=&sc=3y&st=desc&pi={0}&pn=20&zf=diy&sh=list&rnd={1}'.format(self.page,random.random())
        # self.baseUrl = 'https://www.npmjs.com'
        self.urls = []  # 需要获取的url存放处
        self.header = ['name', 'name0', 'pos0', 'name1', 'pos1', 'name2', 'pos2', 'name3', 'pos3', 'name4', 'pos4',
                       'name5', 'pos5', 'name6', 'pos6', 'name7', 'pos7', 'name8', 'pos8', 'name9', 'pos9',
                       'positionRatio', 'scale', 'establishDay']  # 数据列名
        self.dict = []

    """
        获取下载链接
    """

    def get_downLoad_url(self):
        req = requests.get(self.targetUrl)
        # 正则匹配
        pattern = re.compile(r"datas:(.*),allRecords")
        resStr = pattern.search(req.text).group(1)
        # 将字符串中的[,]替换成空值
        resStr = re.sub(r'\[', '', resStr)
        resStr = re.sub(r'\]', '', resStr)
        # 根据逗号将字符串切割
        # ""内的都好部分割
        temp1 = resStr.strip()
        temp1 = shlex.shlex(temp1)
        temp1.whitespace = ','
        temp1.whitespace_split = True
        resStrList = list(temp1)

        for each in resStrList:
            each = re.sub(r'\"', '', each)
            self.urls.append('http://fund.eastmoney.com/{0}.html'.format(each.split('|')[0]))
        # print(self.urls)

    """
        获取内容并解析 
    """

    def get_content(self, url):
        temp = {}
        req = requests.get(url)
        res = BeautifulSoup(req.text.encode('ISO-8859-1').decode('utf-8'), 'lxml')
        scale = res.find_all(class_='infoOfFund')
        if (scale):
            for each in scale:
                temp1 = each.find_all('td')[1]
                temp2 = each.find_all('td')[3]
                temp.update({'scale': str(temp1).split('</a>：')[1].split('</td>')[0],
                             'establishDay': str(temp2).split('：')[1].split('</td>')[0]})

        text = res.find_all('td', class_='alignLeft')
        for (index, item) in enumerate(text):
            if (index < 10):
                if (not item.find('a') is None):
                    temp.update({'name' + str(index): item.find('a').get_text()})

        pos = res.find_all('td', class_='alignRight bold')
        for (index, item) in enumerate(pos):
            if (index < 20):
                if (not item is None and (index % 2) == 0):
                    temp.update({'pos' + str(index // 2): item.get_text()})

        positionRatio = res.select('#position_shares > div.poptableWrap > p > span.sum-num')
        if (positionRatio):
            temp.update({'positionRatio': positionRatio[0].get_text()})

        name = res.select('#body > div:nth-child(11) > div > div > div.fundDetail-header > div.fundDetail-tit > div')
        if (name):
            temp.update({'name': name[0].get_text()})
            print('Get started {0} content.'.format(name[0].get_text()))
        self.dict.append(temp)
        return self.dict

    """
        存数据
    """

    def save(self, data):
        with open(self.fileName, 'a+', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应。
            writer.writeheader()  # 写入列名
            writer.writerows(data)  # 写入数据
        print('the {0} is Saved!'.format(self.fileName))


if __name__ == "__main__":
    # 1，17股票型   1，63 混合型
    for page in range(1, 17):
        dl = BaseDownLoad(page)
        dl.get_downLoad_url()
        print('start download {0} page.'.format(page))
        for i in range(len(dl.urls)):
            dl.get_content(dl.urls[i])
        print('Save the {0} page.'.format(page))
        dl.save(dl.dict)
    print('success!')
