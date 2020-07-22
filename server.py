# coding=utf-8
# python2.7
from __future__ import print_function

import socket
import random
import sys
import threading
import pickle
import time
import rsa
import inspect
import ctypes


def guess_num_set():  # 游戏初始设置最初的数列随机四个0到9的数字，返回列表
    list1 = random.sample(range(0, 10), 4)
    return list1


def RsaEncrypt(str1):  # rsa加密模块
    (PubKey, PrivateKey) = rsa.newkeys(512)  # 生成rsa秘钥
    Encrypt_Str = rsa.encrypt(str1, PubKey)  # 对信息加密
    return Encrypt_Str, PrivateKey


def RsaDecrypt(str1, pk):  # rsa解密模块
    Decrypt_Str = rsa.decrypt(str1, pk)  # 对收到信息解密
    return Decrypt_Str


def SendMessage(conn1, c_msg_r1):  # 信息发送模块
    SendData = c_msg_r1
    (encryptdata, PrivateKey) = RsaEncrypt(SendData)  # 将要发送的信息进行加密
    Message = pickle.dumps([encryptdata, PrivateKey])  # 将信息与秘钥打包发送
    if len(Message) > 0:
        conn1.send(Message)


def RecvMessage(conn1):  # 信息接受模块
    Message = conn1.recv(2048)
    (recvdata, PrivateKey) = pickle.loads(Message)  # 将收到的信息解包
    decryptdata = RsaDecrypt(recvdata, PrivateKey)  # 将信息解密出来
    if len(Message) > 0:
        return decryptdata


class GuessTime:  # 记录玩家猜中的次数
    def __init__(self, name):
        self.times = 0
        self.name = name

    def addTime(self, times):  # 增加已猜次数
        self.times += times

    def resetTime(self):  # 重置已猜的次数
        self.times = 0


def extra_same_elem(list1, list2):  # 对比列表1和列表2有多少个相同的元素，返回由相同元素组成的字符串
    set1 = set(list1)
    set2 = set(list2)
    iset = set1.intersection(set2)
    return list(iset)


def legal_check(str1):  # 依次判断是否为纯数字，是否输入了重复数字，是否只输入了四位数字，并返还标识符，确认合法性
    if str1.isdigit():  # 如果为纯整数
        list_str1 = list(map(int, str1))  # 字符串转换为列表
        set_list_str1 = set(list_str1)  # 剔出重复元素后的列表
        if len(set_list_str1) == len(list_str1):  # 原列表与剔除重复元素后列表位数是否相同
            if len(list_str1) == 4:  # 列表长度为4
                isLegal = 1
            else:
                isLegal = 0
        else:
            isLegal = 0
    else:
        isLegal = 0
    return isLegal


def answer_check(list1, list2):  # 判断列表1和列表2有多少相同元素，有多少正确位置元素
    list_same = extra_same_elem(list1, list2)  # 对比列表1和列表2有多少个相同的元素
    existNum = len(list_same)  # 判断相同元素的数量
    rightNum = 0
    for i in range(0, 4):  # 正确位置元素数量加1，相同元素数量就要减1，对比四个位数
        if list1[i] == list2[i]:
            rightNum = rightNum + 1
            existNum = existNum - 1
    rightStr = str(rightNum)
    existStr = str(existNum)
    print('{}{}{}{}'.format(rightStr, 'A', existStr, 'B'))
    answerRespond = str(rightStr + 'A' + existStr + 'B')

    return answerRespond


def correct_check(list1):  # 判断列表1和列表2有多少相同元素，有多少正确位置元素
    if list1[0] == '4':  # 正确位置元素有4个，证明猜对了
        return 1


def main():
    print('服务器已启动，等待客户端连接')
    server = socket.socket()  # 创建socket对象
    host = socket.gethostname()  # 获取主机名
    server.bind((host, 6666))  # 主机名，端口绑定
    server.listen(5)  # 开始监听
    while True:
        conn, ip_addr = server.accept()
        print('客户端已连接')
        print(conn, ip_addr)
        t = threading.Thread(target=server_msg, args=(conn, ip_addr))  # 根据端口来创建新线程
        t.start()



def server_msg(conn, ip_addr):
    while True:
        list_guessNum = guess_num_set()  # 初始化最初的问题
        guessTime = GuessTime(ip_addr)  # 初始化这个线程的次数计数器
        threadClose = 0  # 标识符,特定情况下关闭线程
        while True:
            # c_msg = conn.recv(1024)  # 接收数据
            try:
                c_msg = RecvMessage(conn)  # 接受信息
                legalCheck = legal_check(c_msg)  # 对收到的信息合法性检测
                if c_msg == 'exitGame':  # 收到消息为over时，结束通信
                    c_msg_r = 'GameOver'
                    # conn.send(c_msg_r)  # 返回消息
                    SendMessage(conn, c_msg_r)
                    conn.close()
                    threadClose = 1
                elif c_msg == 'seeAnswer':  # 模式2偷看答案，输出答案
                    c_msg_r = str(list_guessNum)
                    # conn.send(c_msg_r)  # 返回消息
                    SendMessage(conn, c_msg_r)
                elif c_msg == 'resetAnswer':  # 模式3重置问题
                    list_guessNum = guess_num_set()
                    guessTime.resetTime()
                    c_msg_r = '已重新生成题目'
                    # conn.send(c_msg_r)  # 返回消息
                    SendMessage(conn, c_msg_r)
                elif c_msg == 'inputAnswer':  # 模式4自己输入问题
                    print('输入要修改为的答案')
                    # c_msg = conn.recv(1024)  # 接收数据
                    c_msg = RecvMessage(conn)
                    legalCheck = legal_check(c_msg)
                    if legalCheck:  # 验证修改为的问题的合法性
                        list_guessNum = list(map(int, c_msg))  # 将合法的问题转换为列表
                        guessTime.resetTime()
                        c_msg_r = '问题修改成功'
                        # conn.send(c_msg_r)  # 返回消息
                        SendMessage(conn, c_msg_r)
                    else:
                        c_msg_r = '输入不合法，请检查'
                        # conn.send(c_msg_r)  # 返回消息
                        SendMessage(conn, c_msg_r)
                        break
                elif legalCheck:
                    list_inputNum = list(map(int, c_msg))  # 将合法的答案转化为列表
                    guessTime.addTime(1)
                    answerCheck = answer_check(list_guessNum, list_inputNum)
                    correctCheck = correct_check(answerCheck[0])
                    if correctCheck:  # 对比答案的正确性
                        list_guessNum = guess_num_set()  # 正确猜出答案了，换一道题
                        c_msg_r = str('GuessTime=' + str(guessTime.times))
                        guessTime.resetTime()
                        # conn.send(c_msg_r)  # 返回消息
                        SendMessage(conn, c_msg_r)
                    else:
                        c_msg_r = answerCheck
                        # conn.send(c_msg_r)  # 返回消息
                        SendMessage(conn, c_msg_r)
                else:
                    c_msg_r = '输入不合法，请检查'
                    # conn.send(c_msg_r)  # 返回消息
                    SendMessage(conn, c_msg_r)
                    break
            except:
                print('客户端掉线了')
                threadClose = 1
                break
        if threadClose == 1:
            break


if __name__ == '__main__':
    main()
