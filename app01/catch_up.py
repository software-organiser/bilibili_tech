import datetime
import json
import operator
import re
import requests
from bs4 import BeautifulSoup
import time
from aip import AipNlp
from snownlp import SnowNLP
import re
import jieba
import codecs
import numpy as np
from numpy.linalg import solve
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
    def get_oid(self):
        oid = self.get_web_detail()['data']['cid']#通过键值对索引找到oid号
        oid = str(oid)#将获取到的oid转化为字符串类型
        return oid#返回最终的oid值
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
        return [title, up, view, reply, danmu, like, fav, coin, share]
    def get_update(self):
        time = datetime.datetime.fromtimestamp(self.get_web_detail()['data']['pubdate'])
        res_day = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
        time1 = re.findall(res_day, str(time))
        res_time = '[0-9]{2}:[0-9]{2}:[0-9]{2}'
        time2 = re.findall(res_time, str(time))
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
        commentList = []
        for comment in self.get_danmu_list().find_all('d'):
            #time = float(comment.attrs['p'].split(',')[0])  # tag.attrs（标签属性，字典类型）
            commentList.append(comment.string)
        # newDict = sorted(commentList.items(), key=operator.itemgetter(0))  # 字典排序
        # commentList = dict(newDict)
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

    # 求解线性方程组的解
    # def solution(self, A, B):  # 例：A=[0.1,0.3] B=[0.4212,1]
    #     a = np.mat([A, [1, 1]])  # 系数矩阵
    #     b = np.mat(B).T  # 常数项列矩阵
    #     x = solve(a, b)  # 方程组的解
    #     return x[0, 0], x[1, 0]
    #
    # # 模糊评价矩阵构建
    # def endpoint(self, item):  # x是某一指标
    #     if item <= 0.1:
    #         result = [item, 0, 0, 0, 0]
    #     elif item > 0.1 and item <= 0.3:
    #         result = [self.solution([0.1, 0.3], [item, 1])[0], self.solution([0.1, 0.3], [item, 1])[1], 0, 0, 0]
    #     elif item > 0.3 and item <= 0.5:
    #         result = [0, self.solution([0.3, 0.5], [item, 1])[0], self.solution([0.3, 0.5], [item, 1])[1], 0, 0]
    #     elif item > 0.5 and item <= 0.8:
    #         result = [0, 0, self.solution([0.5, 0.8], [item, 1])[0], self.solution([0.5, 0.8], [item, 1])[1], 0]
    #     elif item > 0.8 and item <= 1:
    #         result = [0, 0, 0, self.solution([0.8, 1], [item, 1])[0], self.solution([0.8, 1], [item, 1])[1]]
    #     else:
    #         result = [0, 0, 0, 0, item]
    #     return result
    #
    # # 权重模型
    # def weight_model(self):
    #     X = self.get_basic_info()
    #     X.pop(0)
    #     X.pop(0)
    #     X.append(self.emotion_cal())
    #     X.append(self.seg_words())
    #     X.append(self.keyword())
    #     X = np.mat(X)
    #     n = X.shape[0]  # 矩阵行数
    #     m = X.shape[1]  # 矩阵列数
    #
    #     # 各视频到子准则层（归一化）
    #     column_sum = X.sum(axis=0)  # 对矩阵每列求和
    #     x1 = np.mat(np.zeros((n, m)))
    #     for i in range(0, n):
    #         for j in range(0, m):
    #             x1[i, j] = X[i, j] / column_sum[:, j]
    #
    #     # 子准则层到准则层
    #     # 首先把三个指标对应的子准则层分开处理，因情感分析的权重为1，故暂时不考虑
    #     z1 = np.mat(np.zeros((n, 3)))
    #     z2 = np.mat(np.zeros((n, 4)))
    #     z3 = np.mat(np.zeros((n, 2)))
    #     a1 = x1[:, 0:3]
    #     a2 = x1[:, 3:7]
    #     a4 = x1[:, 7:8]
    #     a3 = x1[:, 8:10]
    #     for i in range(0, n):
    #         for j in range(0, 3):
    #             z1[i, j] = a1[i, j] / np.sqrt(a1[:, j].T * a1[:, j])
    #         for j in range(0, 4):
    #             z2[i, j] = a2[i, j] / np.sqrt(a2[:, j].T * a2[:, j])
    #         for j in range(0, 2):
    #             z3[i, j] = a3[i, j] / np.sqrt(a3[:, j].T * a3[:, j])
    #
    #     p1 = np.mat(np.zeros((n, 3)))
    #     p2 = np.mat(np.zeros((n, 4)))
    #     p3 = np.mat(np.zeros((n, 2)))
    #     for i in range(0, n):
    #         for j in range(0, 3):
    #             p1[i, j] = z1[i, j] / (np.sum(z1[:, j]))
    #         for j in range(0, 4):
    #             p2[i, j] = z2[i, j] / (np.sum(z2[:, j]))
    #         for j in range(0, 2):
    #             p3[i, j] = z3[i, j] / (np.sum(z2[:, j]))
    #
    #     e1 = np.mat(np.zeros((1, 3)))
    #     e2 = np.mat(np.zeros((1, 4)))
    #     e3 = np.mat(np.zeros((1, 2)))
    #     for j in range(0, 3):
    #         e1[0, j] = -(p1[:, j].T * np.log(p1[:, j])) / np.log(n)
    #     for j in range(0, 4):
    #         e2[0, j] = -(p2[:, j].T * np.log(p2[:, j])) / np.log(n)
    #     for j in range(0, 2):
    #         e3[0, j] = -(p3[:, j].T * np.log(p3[:, j])) / np.log(n)
    #
    #     d1 = np.mat(np.zeros((1, 3)))
    #     d2 = np.mat(np.zeros((1, 4)))
    #     d3 = np.mat(np.zeros((1, 2)))
    #     for j in range(0, 3):
    #         d1[0, j] = 1 - e1[0, j]
    #     for j in range(0, 4):
    #         d2[0, j] = 1 - e2[0, j]
    #     for j in range(0, 2):
    #         d3[0, j] = 1 - e3[0, j]
    #
    #     w1 = np.mat(np.zeros((1, 3)))
    #     w2 = np.mat(np.zeros((1, 4)))
    #     w3 = np.mat(np.zeros((1, 2)))
    #     for j in range(0, 3):
    #         w1[0, j] = d1[0, j] / d1.sum(axis=1)  # 关注度权重矩阵（向量）
    #     for j in range(0, 4):
    #         w2[0, j] = d2[0, j] / d2.sum(axis=1)  # 好评度权重矩阵（向量）
    #     for j in range(0, 2):
    #         w3[0, j] = d3[0, j] / d3.sum(axis=1)  # 商品弹幕权重矩阵（向量）
    #
    #     # 计算得分权重：关注度权重向量×归一化向量
    #     # 将结果分别存入指标列表：指标列表[视频1，视频2，……]
    #     cal_list = []
    #     attention_list = []
    #     for i in range(0, n):
    #         attention = w1 * a1[i, :].T / 0.5
    #         score = attention[0, 0]
    #         attention_list.append(attention[0, 0])
    #         print("视频", i + 1, "关注度得分", attention[0, 0])
    #     # print(attention_list)
    #     cal_list.append(attention_list)
    #     praise_list = []
    #     for i in range(0, n):
    #         praise = w2 * a2[i, :].T / 0.5
    #         praise_list.append(praise[0, 0])
    #         print("视频", i + 1, "好评度得分", praise[0, 0])
    #     # print(praise_list)
    #     cal_list.append(praise_list)
    #     emotion_list = []
    #     for i in range(0, n):
    #         emotion = a4[i][0].T / 0.5
    #         emotion_list.append(emotion[0, 0])
    #         print("视频", i + 1, "情感分析得分", emotion[0, 0])
    #     # print(emotion_list)
    #     cal_list.append(emotion_list)
    #     relative_list = []
    #     for i in range(0, n):
    #         relative = w3 * a3[i, :].T / 0.5
    #         relative_list.append(relative[0, 0])
    #         print("视频", i + 1, "广告弹幕得分", relative[0, 0])
    #     # print(relative_list)
    #     cal_list.append(relative_list)
    #
    #     eva = [0 for r in range(0, n)]
    #     for i in range(0, n):
    #         eva[i] = np.mat(np.zeros((4, 5)))
    #         for j in range(0, 4):
    #             eva[i][j, :] = self.endpoint(cal_list[j][i])
    #         # print(eva[i])
    #
    #     # 准则层到目标层
    #     a = np.mat('1 0.25 0.33333333 0.16666667;4 1 3 2;3 0.33333333 1 0.5;6 0.5 2 1')
    #     D, xx = np.linalg.eig(a)
    #     prop = xx[:, 0] / np.sum(xx[:, 0])
    #
    #     final_list = []
    #     for i in eva:
    #         final = prop.T * i
    #         final_result = 0.1 * final.real[0, 0] + 0.3 * final.real[0, 1] + 0.5 * final.real[0, 2] + 0.7 * final.real[0, 3] + 1 * final.real[0, 4]
    #         print("视频", i, "的总得分为", final_result)
    #         final_list.append(final_result)
    #     return final_list[0]
    def main(self):
        contents = {}
        list1 = self.get_basic_info()
        contents['title'] = str(list1[0])
        contents['up'] = str(list1[1])
        contents['update'] = self.get_update()
        contents['view'] = str(list1[2])
        contents['reply'] = str(list1[3])
        contents['danmu'] = str(list1[4])
        contents['like'] = str(list1[5])
        contents['fav'] = str(list1[6])
        contents['coin'] = str(list1[7])
        contents['share'] = str(list1[8])
        contents['p_n'] = self.emotion_cal()
        contents['rel'] = str(self.seg_words())
        contents['rate'] = self.keyword()
        # contents['core'] = self.weight_model()
        return contents

n = np.log(5)
print(n)