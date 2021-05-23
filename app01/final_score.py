import numpy as np
from numpy.linalg import solve
# 求解线性方程组的解
def solution(A, B):  # 例：A=[0.1,0.3] B=[0.4212,1]
    a = np.mat([A, [1, 1]])  # 系数矩阵
    b = np.mat(B).T  # 常数项列矩阵
    x = solve(a, b)  # 方程组的解
    return x[0, 0], x[1, 0]

# 模糊评价矩阵构建
def endpoint(item):  # x是某一指标
    if item <= 0.1:
        result = [item, 0, 0, 0, 0]
    elif item > 0.1 and item <= 0.3:
        result = [solution([0.1, 0.3], [item, 1])[0], solution([0.1, 0.3], [item, 1])[1], 0, 0, 0]
    elif item > 0.3 and item <= 0.5:
        result = [0, solution([0.3, 0.5], [item, 1])[0], solution([0.3, 0.5], [item, 1])[1], 0, 0]
    elif item > 0.5 and item <= 0.8:
        result = [0, 0, solution([0.5, 0.8], [item, 1])[0], solution([0.5, 0.8], [item, 1])[1], 0]
    elif item > 0.8 and item <= 1:
        result = [0, 0, 0, solution([0.8, 1], [item, 1])[0], solution([0.8, 1], [item, 1])[1]]
    else:
        result = [0, 0, 0, 0, item]
    return result

# 权重模型
def weight_model(X):
    test = [[1484644, 1574, 1379, 79435, 6622, 7830, 8524, 3.79, 0.87, 0.79],
            [3599846, 7132, 2147, 185748, 42608, 117018, 44675, 0.34, 0.74, 0.69],
            [2249092, 19276, 6243, 211258, 41133, 128318, 20081, 1.56, 0.34, 0.24],
            [2599116, 5849, 5495, 222636, 78081, 142437, 59696, 0.78, 0.98, 0.93],
            [698681, 5058, 1357, 60787, 8363, 23908, 5277, 6.98, 0.44, 0.32]]
    test.append(X)
    print(test)
    X = np.mat(test)
    n = X.shape[0]  # 矩阵行数
    m = X.shape[1]  # 矩阵列数

    # 各视频到子准则层（归一化）
    column_sum = X.sum(axis=0)  # 对矩阵每列求和
    x1 = np.mat(np.zeros((n, m)))
    for i in range(0, n):
        for j in range(0, m):
            x1[i, j] = X[i, j] / column_sum[:, j]

    # 子准则层到准则层
    # 首先把三个指标对应的子准则层分开处理，因情感分析的权重为1，故暂时不考虑
    z1 = np.mat(np.zeros((n, 3)))
    z2 = np.mat(np.zeros((n, 4)))
    z3 = np.mat(np.zeros((n, 2)))
    a1 = x1[:, 0:3]
    a2 = x1[:, 3:7]
    a4 = x1[:, 7:8]
    a3 = x1[:, 8:10]
    for i in range(0, n):
        for j in range(0, 3):
            z1[i, j] = a1[i, j] / np.sqrt(a1[:, j].T * a1[:, j])
        for j in range(0, 4):
            z2[i, j] = a2[i, j] / np.sqrt(a2[:, j].T * a2[:, j])
        for j in range(0, 2):
            z3[i, j] = a3[i, j] / np.sqrt(a3[:, j].T * a3[:, j])

    p1 = np.mat(np.zeros((n, 3)))
    p2 = np.mat(np.zeros((n, 4)))
    p3 = np.mat(np.zeros((n, 2)))
    for i in range(0, n):
        for j in range(0, 3):
            p1[i, j] = z1[i, j] / (np.sum(z1[:, j]))
        for j in range(0, 4):
            p2[i, j] = z2[i, j] / (np.sum(z2[:, j]))
        for j in range(0, 2):
            p3[i, j] = z3[i, j] / (np.sum(z2[:, j]))

    e1 = np.mat(np.zeros((1, 3)))
    e2 = np.mat(np.zeros((1, 4)))
    e3 = np.mat(np.zeros((1, 2)))
    for j in range(0, 3):
        e1[0, j] = -(p1[:, j].T * np.log(p1[:, j])) / np.log(n)
    for j in range(0, 4):
        e2[0, j] = -(p2[:, j].T * np.log(p2[:, j])) / np.log(n)
    for j in range(0, 2):
        e3[0, j] = -(p3[:, j].T * np.log(p3[:, j])) / np.log(n)

    d1 = np.mat(np.zeros((1, 3)))
    d2 = np.mat(np.zeros((1, 4)))
    d3 = np.mat(np.zeros((1, 2)))
    for j in range(0, 3):
        d1[0, j] = 1 - e1[0, j]
    for j in range(0, 4):
        d2[0, j] = 1 - e2[0, j]
    for j in range(0, 2):
        d3[0, j] = 1 - e3[0, j]

    w1 = np.mat(np.zeros((1, 3)))
    w2 = np.mat(np.zeros((1, 4)))
    w3 = np.mat(np.zeros((1, 2)))
    for j in range(0, 3):
        w1[0, j] = d1[0, j] / d1.sum(axis=1)  # 关注度权重矩阵（向量）
    for j in range(0, 4):
        w2[0, j] = d2[0, j] / d2.sum(axis=1)  # 好评度权重矩阵（向量）
    for j in range(0, 2):
        w3[0, j] = d3[0, j] / d3.sum(axis=1)  # 商品弹幕权重矩阵（向量）

    # 计算得分权重：关注度权重向量×归一化向量
    # 将结果分别存入指标列表：指标列表[视频1，视频2，……]
    cal_list = []
    attention_list = []
    for i in range(0, n):
        attention = w1 * a1[i, :].T / 0.5
        score = attention[0, 0]
        attention_list.append(attention[0, 0])
        print("视频", i + 1, "关注度得分", attention[0, 0])
    # print(attention_list)
    cal_list.append(attention_list)
    praise_list = []
    for i in range(0, n):
        praise = w2 * a2[i, :].T / 0.5
        praise_list.append(praise[0, 0])
        print("视频", i + 1, "好评度得分", praise[0, 0])
    # print(praise_list)
    cal_list.append(praise_list)
    emotion_list = []
    for i in range(0, n):
        emotion = a4[i][0].T / 0.5
        emotion_list.append(emotion[0, 0])
        print("视频", i + 1, "情感分析得分", emotion[0, 0])
    # print(emotion_list)
    cal_list.append(emotion_list)
    relative_list = []
    for i in range(0, n):
        relative = w3 * a3[i, :].T / 0.5
        relative_list.append(relative[0, 0])
        print("视频", i + 1, "广告弹幕得分", relative[0, 0])
    # print(relative_list)
    cal_list.append(relative_list)

    eva = [0 for r in range(0, n)]
    for i in range(0, n):
        eva[i] = np.mat(np.zeros((4, 5)))
        for j in range(0, 4):
            eva[i][j, :] = endpoint(cal_list[j][i])
        # print(eva[i])

    # 准则层到目标层
    a = np.mat('1 0.25 0.33333333 0.16666667;4 1 3 2;3 0.33333333 1 0.5;6 0.5 2 1')
    D, xx = np.linalg.eig(a)
    prop = xx[:, 0] / np.sum(xx[:, 0])

    final_list = []
    for i in eva:
        final = prop.T * i
        final_result = 0.1 * final.real[0, 0] + 0.3 * final.real[0, 1] + 0.5 * final.real[0, 2] + 0.7 * final.real[0, 3] + 1 * final.real[0, 4]
        print("视频", i, "的总得分为", final_result)
        final_list.append(final_result)
    return final_list[-1]