# coding=utf-8
# python2.7
from __future__ import print_function

import socket
import random
import sys
import rsa
import threading
import pickle
import select
import time


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


def mode_select():  # 以字符串形式获取玩家的输入并返回字符串
    print('1.请输入四位不重复阿拉伯数字')
    choice = raw_input()
    if len(choice) <= 53:
        return choice
    else:
        return 'outSpace'


def answer_input():  # 以字符串形式获取玩家的输入并返回字符串
    print('1.请输入要修改为的答案')
    choice = raw_input()
    if len(choice) <= 53:
        return choice
    else:
        return 'outSpace'


def client_msg():
    client = socket.socket()  # 声明socket类型，同时生成链接对象
    host = socket.gethostname()  # 获取主机名
    try:
        client.connect((host, 6666))  # 建立链接
    except Exception as ex:
        print(ex.message)
        print('服务器连接失败,正在尝试重新连接')
    else:
        print('服务器连接成功')
        while True:
            try:
                msg = mode_select()  # 获取要执行的操作
                if msg == 'outSpace':
                    print('输入不合法')
                elif msg == 'exitGame':  # 正常退出游戏
                    SendMessage(client, 'exitGame')
                    print("退出游戏")
                    client.close()
                    sys.exit(0)
                elif msg == 'inputAnswer':  # 修改答案
                    SendMessage(client, 'inputAnswer')  # 告诉服务器要修改答案了
                    msg = answer_input()  # 输入要修改为的答案
                    SendMessage(client, msg)  # 把答案发送给服务器
                    data = RecvMessage(client)  # 接收信息，接收的大小为1024字节
                    print(format(data))  # 提示信息修改成功或提示输入不合法
                else:
                    SendMessage(client, msg)  # 发送信息
                    msg_r = RecvMessage(client)  # 接受信息
                    print(format(msg_r))  # 打印信息
                    if msg_r == '4A0B':  # 如果返回的信息是4A0B，则提示用户正确
                        print('您已获得胜利，自动开始新游戏')
                        SendMessage(client, 'resetGame')  # 向服务器发送指令，重置游戏
            except Exception as ex:
                print(ex.message)
                print('服务器掉线了或出现了特殊异常')
                break


if __name__ == '__main__':
    while True:
        client_msg()
