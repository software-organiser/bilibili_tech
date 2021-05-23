import datetime
import json
import operator
import re
import requests
from bs4 import BeautifulSoup
from snownlp import SnowNLP
import re
import jieba
class catch_up():
    def __init__(self, url, pro_name):#设置头部初始参数
        self.url = url#设置要传入的url属性参数
        self.pro_name = pro_name#设置传入的商品名称
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
        }#设置请求头
        self.res = 'BV[A-Za-z0-9]{10}'#设置正则表达式用来匹配url中的BV号
        self.web_inter = 'https://api.bilibili.com/x/web-interface/view?bvid='#设置用来获取oid号的web接口信息
        self.bullet_list = 'https://api.bilibili.com/x/v1/dm/list.so?oid='#设置用来获取弹幕列表的接口号
        self.get_date_url = 'https://api.bilibili.com/x/v2/dm/web/history/seg.so?type=1&oid='
        '''定义相关函数'''
    def get_text(self):
        resp = requests.get(url=self.url, headers=self.headers)
        return resp.text
    def get_web_detail(self):#用来通过url中的BV号找寻web接口，从中获取视频的oid号
        resp = re.findall(self.res, self.url)#从输入的url中获取视频的BV号，返回一个只有一个元素的列表
        bv = resp[0]#取出bv号，此时为字符串类型
        response = requests.get(url=self.web_inter+bv, headers=self.headers)#调用requests模块下的get写入url和请求头获取接口里的页面信息
        dirt = json.loads(response.text)
        return dirt#将获取到的页面信息解析成json格式
    def get_update(self):
        time = datetime.datetime.fromtimestamp(self.get_web_detail()['data']['pubdate'])
        res_day = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
        time1 = re.findall(res_day, str(time))
        res_time = '[0-9]{2}:[0-9]{2}:[0-9]{2}'
        time2 = re.findall(res_time, str(time))
        return time1[0] + " " + time2[0]
    def get_basic_info(self):
        title = self.get_web_detail()['data']['title']
        up = self.get_web_detail()['data']['owner']['name']
        view = self.get_web_detail()['data']['stat']['view']
        reply = self.get_web_detail()['data']['stat']['reply']
        danmu = self.get_web_detail()['data']['stat']['danmaku']
        like = self.get_web_detail()['data']['stat']['like']
        fav = self.get_web_detail()['data']['stat']['favorite']
        coin = self.get_web_detail()['data']['stat']['coin']
        share = self.get_web_detail()['data']['stat']['share']
        return [title, up, self.get_update(), view, reply, danmu, like, fav, coin, share]
    def get_oid(self):
        oid = self.get_web_detail()['data']['cid']  # 通过键值对索引找到oid号
        oid = str(oid)  # 将获取到的oid转化为字符串类型
        return oid  # 返回最终的oid值
    def get_danmu_list(self):
        resp = requests.get(url=self.bullet_list + self.get_oid(), headers=self.headers)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup
    def get_all_danmu(self):
        commentList = []
        for comment in self.get_danmu_list().find_all('d'):
            commentList.append(comment.string)
        return commentList
    def get_danmu_by_date(self,date):
        commentList = {}

    def sentiment_judge(self, value):
        if value > 0.8:
            polarity = 2
        elif value < 0.3:
            polarity = 0
        else:
            polarity = 1
        return polarity
    def emotion_cal(self):
        # 统计指标：正负比
        positive = 0
        negative = 0
        neutral = 0
        results = []
        for j in self.get_all_danmu():
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
        return emo_cal
    def seg_words(self):
        contents = self.get_all_danmu()
        # 分词
        seg_result = []
        len1 = len(contents)
        for i in contents:
            i = str(i)
            seg_list = jieba.lcut(i)
            for w in seg_list:
                seg_result.append(w)

        # 读取停用词词典
        stopwords = set()
        fr = open('D:/bilibili/bilibili_tech/app01/停用词1.txt',  mode='r', encoding='utf-8')
        for word in fr:
            stopwords.add(word.strip())
        fr.close()
        # 去除停用词
        contents = list(filter(lambda x: x not in stopwords, seg_result))

        # 匹配情感词典
        emotion_words = set()
        ft = open('D:/bilibili/bilibili_tech/app01/情感词典1.txt',  mode='r', encoding='utf-8')
        for w in ft:
            emotion_words.add(w.strip())
        ft.close()
        contents_final = list(filter(lambda y: y in emotion_words, contents))
        len2 = len(contents_final)
        relevancy = len2/len1
        return relevancy  # 仅分词改成seg_result，仅停用词过滤改成contents

    def keyword(self):
        keywords = self.pro_name
        contents = self.get_all_danmu()
        keycontents = []
        count = 0
        lens = len(contents)
        for i in contents:
            if str(i).find(keywords) != -1:
                keycontents.append(str(i))
                count += 1
        rate=count / lens
        return rate
    def main(self):
        info = self.get_basic_info()
        info.append(self.emotion_cal())
        info.append(self.seg_words())
        info.append(self.keyword())
        return info

