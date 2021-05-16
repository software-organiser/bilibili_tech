import datetime
import json
import operator
import re
import requests
from bs4 import BeautifulSoup
import time
from aip import AipNlp
from snownlp import SnowNLP
#连接百度API
APP_ID = '24046158' #你的ID
API_KEY = '7QDKkjF0XSG8isNeQCvobUtQ' #你的 AK 密钥
SECRET_KEY = 'vz7XSVuFpNjYdKNiDqQKip63CXQN6sIW' #你的 SK 密钥
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
class catch_up():
    def __init__(self,url):#设置头部初始参数
        self.url = url#设置要传入的url属性参数
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
        }#设置请求头
        self.res = 'BV[A-Za-z0-9]{10}'#设置正则表达式用来匹配url中的BV号
        self.web_inter = 'https://api.bilibili.com/x/web-interface/view?bvid='#设置用来获取oid号的web接口信息
        self.bullet_list = 'https://api.bilibili.com/x/v1/dm/list.so?oid='#设置用来获取弹幕列表的接口号
        self.get_date_url = 'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid='
        '''定义相关函数'''
    def get_text(self):
        resp = requests.get(url=self.url,headers=self.headers)
        return resp.text
    def get_web_detail(self):#用来通过url中的BV号找寻web接口，从中获取视频的oid号
        resp = re.findall(self.res,self.url)#从输入的url中获取视频的BV号，返回一个只有一个元素的列表
        bv = resp[0]#取出bv号，此时为字符串类型
        response = requests.get(url = self.web_inter+bv, headers = self.headers)#调用requests模块下的get写入url和请求头获取接口里的页面信息
        dirt = json.loads(response.text)
        return dirt#将获取到的页面信息解析成json格式
    def get_oid(self):
        oid = self.get_web_detail()['data']['cid']#通过键值对索引找到oid号
        oid = str(oid)#将获取到的oid转化为字符串类型
        return oid#返回最终的oid值
    def get_basic_info(self):
        title = self.get_web_detail()['data']['title']
        up = self.get_web_detail()['data']['owner']['name']
        view = self.get_web_detail()['data']['stat']['view']
        like = self.get_web_detail()['data']['stat']['like']
        fav = self.get_web_detail()['data']['stat']['favorite']
        coin = self.get_web_detail()['data']['stat']['coin']
        share = self.get_web_detail()['data']['stat']['share']
        danmu = self.get_web_detail()['data']['stat']['danmaku']
        reply = self.get_web_detail()['data']['stat']['reply']
        return [title,up,view,like,fav,coin,share,danmu,reply]
    def get_update(self):
        time = datetime.datetime.fromtimestamp(self.get_web_detail()['data']['pubdate'])
        res_day = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
        time1 = re.findall(res_day, str(time))
        res_time = '[0-9]{2}:[0-9]{2}:[0-9]{2}'
        time2 = re.findall(res_time, str(time))
        print(time1[0] + " " + time2[0])
        return time1[0] + " " + time2[0]
    def set_time(self,t):#将时间设置成指定的格式
        timePlus = int(t)
        m = timePlus // 60
        s = timePlus - m * 60
        return str(m) + ':' + str(s).zfill(2)
    def get_danmu_list(self):
        resp = requests.get(url=self.bullet_list + self.get_oid(), headers=self.headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup
    def get_all_danmu(self):
        commentList = {}
        for comment in self.get_danmu_list().find_all('d'):
            time = float(comment.attrs['p'].split(',')[0])  # tag.attrs（标签属性，字典类型）
            commentList[time] = comment.string
        newDict = sorted(commentList.items(), key=operator.itemgetter(0))  # 字典排序
        commentList = dict(newDict)
        return commentList
    def get_danmu_by_date(self,date):
        commentList = {}

    def sentiment_judge(self,value):
        if value > 0.8:
            polarity = 2
        elif value < 0.3:
            polarity = 0
        else:
            polarity = 1
        return polarity
    def main(self):
        contents = {}
        list1 = self.get_basic_info()
        list2 =self.get_all_danmu()
        info = []
        info.append("title:"+str(list1[0]))
        info.append("up:"+str(list1[1]))
        info.append("播放量:"+str(list1[2]))
        info.append("点赞数:" + str(list1[3]))
        info.append("收藏数:" + str(list1[4]))
        info.append("投币数:" + str(list1[5]))
        info.append("转发数:" + str(list1[6]))
        info.append("弹幕数:" + str(list1[7]))
        info.append("评论数:" + str(list1[8]))
        contents['info']=info
        # contents['title'] = str(list1[0])
        # contents['up'] = str(list1[1])
        # contents['播放量'] = str(list1[2])
        # contents['点赞数'] = str(list1[3])
        # contents['收藏数'] = str(list1[4])
        # contents['投币数'] = str(list1[5])
        # contents['转发数'] = str(list1[6])
        # contents['弹幕数'] = str(list1[7])
        # contents['评论数'] = str(list1[8])
        i = 0
        results = []
        for ti, string in list2.items():
            if i<10:  # 目前是只测试了前10条
                """ 调用情感倾向分析 """
                result = client.sentimentClassify(string)
                results.append(result)
            i +=1
            # time.sleep(0.2)  # 每次发送请求后都等待，防止调用过于频繁
        contents['results']=results
        return contents
    def main2(self):
        contents = {}
        list1 = self.get_basic_info()
        info = []
        info.append("title:" + str(list1[0]))
        info.append("up:" + str(list1[1]))
        info.append("播放量:" + str(list1[2]))
        info.append("点赞数:" + str(list1[3]))
        info.append("收藏数:" + str(list1[4]))
        info.append("投币数:" + str(list1[5]))
        info.append("转发数:" + str(list1[6]))
        info.append("弹幕数:" + str(list1[7]))
        info.append("评论数:" + str(list1[8]))
        contents['info'] = info
        # 统计指标：正负比
        positive = 0
        negative = 0
        neutral = 0
        results = []
        for i, j in self.get_all_danmu().items():
            results_dict = dict()
            s = SnowNLP(j)
            result = s.sentiments
            polarity = self.sentiment_judge(result)
            results_dict['text'] = j
            results_dict['positive_probability'] = result
            results_dict['sentiment'] = polarity
            results.append(results_dict)
        for line in results:
            dict1 = eval(str(line))
            emotion_res = dict1['sentiment']
            if emotion_res == 2:
                positive += 1
            elif emotion_res == 1:
                neutral += 1
            else:
                negative += 1
        emo_cal = positive / negative
        contents["emo_cal"]=emo_cal
        return contents

