# -*- coding: utf-8 -*-
from __future__ import print_function

import random
import sys


def mode_select():  # 以字符串形式获取玩家的输入并返回字符串
    print('1.请输入四位不重复阿拉伯数字')
    choice = raw_input()
    return choice


def guess_num_set():  # 游戏初始设置最初的数列随机四个0到9的数字，返回列表
    list1 = random.sample(range(0, 10), 4)
    return list1


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


def correct_check(list1, list2):  # 判断列表1和列表2有多少相同元素，有多少正确位置元素
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
    if rightNum == 4:  # 正确位置元素有4个，证明猜对了
        print('恭喜你猜对了！,重置答案且开始下一局')
        print('猜了', guessTime, '次就猜中了！')
        return 1


while 1:
    list_guessNum = guess_num_set()  # 初始化最初的问题
    guessTime = 0
    while 1:
        mode = mode_select()  # 模式选择
        if legal_check(mode):
            list_inputNum = list(map(int, mode))  # 将合法的答案转化为列表
            guessTime = guessTime + 1
            if correct_check(list_guessNum, list_inputNum):  # 对比答案的正确性
                list_guessNum = guess_num_set()  # 正确猜出答案了，换一道题
        elif mode == 'seeAnswer':  # 模式2偷看答案，输出答案
            print(list_guessNum)
        elif mode == 'resetAnswer':  # 模式3重置问题
            list_guessNum = guess_num_set()
            guessTime = 0
            print('已重新生成题目')
        elif mode == 'inputAnswer':  # 模式4自己输入问题
            guessNum = input_number()  # 输入要修改为的问题
            if legal_check(guessNum):  # 验证修改为的问题的合法性
                list_guessNum = list(map(int, guessNum))  # 将合法的问题转换为列表
                guessTime = 0
        elif mode == 'exitGame':
            sys.exit()
        else:
            print('输入不合法，请检查')
