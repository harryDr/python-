import requests
import time
import re
class EastMoneySpider:
    def request(self,page):
        dt = int(round(time.time() * 1000))
        url = "http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=1&lx=1&letter=&gsid=&text=&sort=zdf,desc&" \
              "page={0},200&dt={1}&atfc=&onlySale=0".format(page,dt)
        heads = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
        response = requests.get(url,headers = heads)
        self.convertStr2List(response.text)
    # 将字符串转换为列表
    def convertStr2List(self,resText):
        # 获取datas中的数据
        pattern = re.compile(r"datas:(.*),count")
        resStr = pattern.search(resText).group(1)
        # 将字符串中的[,]替换成空值
        resStr = re.sub(r'\[', '', resStr)
        resStr = re.sub(r'\]', '', resStr)
        # 根据逗号将字符串切割
        resStrList = resStr.split(',')
        result = []
        tmpList = []
        i = 0
        # 每21个数据就是属于同一基金的
        # 放到同一个列表中
        for resStr in resStrList:
            tmpList.append(resStr)
            i = i + 1
            if i % 21 == 0:
                result.append(tmpList)
                tmpList = []
        print("将字符串转换为列表为：", result)

if __name__ == "__main__":
    moneySpider = EastMoneySpider()
    for page in range(1,3):
        print("Spider page{0}------".format(page))
        moneySpider.request(page)
