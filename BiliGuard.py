# -*- coding: UTF-8 -*-

import calendar
import json
import requests
import sys
import time
import os
import openpyxl

print("当前路径：{}\n".format(os.getcwd()))

BASE_URL = "https://api.live.bilibili.com/xlive/revenue/v1/giftStream/getReceivedGiftStreamNextList?limit=99999999&coin_type=0&begin_time="


# 获取 json 格式的 cookies
# 得到 json 格式 cookies 的方法：
# 1.Chrome 系浏览器使用扩展 EditThisCookie：https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
# 2.浏览器打开B站，使用 EditThisCookie 导出 cookies 到剪切板
# 3.将得到的内容并粘贴到 cookies.json
def get_cookies_json(json_path):
    try:
        cookies = dict()
        with open(json_path, "r", encoding="utf-8") as file:
            cookies_json = json.load(file)
        for c in cookies_json:
            cookies[c["name"]] = c["value"]
        return cookies
    except:
        return None


# 获取 文本格式的 cookies
# 得到 文本格式 cookies 的方法：
# 1.浏览器打开B站，按 F12
# 2.进入控制台，输入 document.cookie
# 3.复制得到的内容并粘贴到 cookies.txt
def get_cookies_text(text_path):
    try:
        cookies = dict()
        with open(text_path, "r", encoding="utf-8") as file:
            cookies_text = file.read()
        if cookies_text[0] == '"':
            cookies_text = cookies_text[1:]
        if cookies_text[-1] == '"':
            cookies_text = cookies_text[:-1]
        cookies_list = cookies_text.split(";")
        for cookie in cookies_list:
            cookie = cookie.split("=")
            cookies[cookie[0].strip()] = cookie[1].strip()
        return cookies
    except:
        return None


def cookies_help():
    print()
    print("得到 json 格式 cookies 的方法：")
    print(
        "1.Chrome 系浏览器使用扩展 EditThisCookie（需翻墙）：https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg"
    )
    print("2.浏览器打开B站，使用 EditThisCookie 导出 cookies 到剪切板")
    print("3.将得到的内容并粘贴到 cookies.json")
    print()
    print("得到 文本格式 cookies 的方法")
    print("1.浏览器打开B站，按 F12")
    print("2.进入控制台，输入 document.cookie")
    print("3.复制得到的内容并粘贴到 cookies.txt")
    print()


# json 格式的 cookies 优先级高于 文本格式的 cookies
def get_cookies(text_path, json_path):
    try:
        print("正在获取 json 格式 cookies")
        cookies_json = get_cookies_json(json_path)
        if cookies_json:
            print("json 格式 cookies 获取成功，优先使用 json 格式 cookie\n")
            return cookies_json
        print("正在获取 文本格式 cookies")
        cookies_text = get_cookies_text(text_path)
        if cookies_text:
            print("文本格式 cookies 获取成功\n")
            return cookies_text
    except:
        None
    print("cookies 格式错误，请先获取 cookies")
    cookies_help()
    print("按任意键结束程序")
    input()
    sys.exit()


TEXT_PATH = "cookies.txt"
JSON_PATH = "cookies.json"
COOKIES = get_cookies(TEXT_PATH, JSON_PATH)

START = 0
END = 0


# 获取礼物列表
def get_gift_list(url, cookies):
    # # 加载本地礼物列表，调试用
    # with open("gifts.json", "r", encoding="utf-8") as file:
    #     gifts_json = json.load(file)
    # gift_list = gifts_json["data"]["list"]
    gift_list = []
    gifts = requests.get(url, cookies=cookies)
    code = gifts.json()["code"]
    if code == 0:
        gift_list = gifts.json()["data"]["list"]
    else:
        print("错误代码：{}".format(code))
        message = gifts.json()["message"]
        print("错误信息：{}".format(message))
        if code == -101:
            print("可能是 cookies 设置错误")
            cookies_help()
    if gift_list == []:
        print("这一天没有人上舰")
    return gift_list


# 获取舰长列表
# level：1表示总督，2表示提督，3表示舰长
def get_guards(gift_list, level):
    gift_id = 10000 + level
    guards = dict()
    for gift in gift_list:
        if gift["gift_id"] == gift_id:
            key = str(gift["uid"]) + str(gift["id"])
            guards[key] = gift
    return guards


# 获取某天的舰长
def get_day_guards(day_text):
    print("正在获取 {} 的舰长".format(day_text))
    url = BASE_URL + day_text
    gift_list = get_gift_list(url, COOKIES)
    day_guards = dict()
    for level in range(1, 4):
        day_guards[level] = get_guards(gift_list, level)
    return day_guards


# 获取某个月的舰长
def get_month_guards(year, month):
    global START
    global END
    month_guards = dict()
    month_calendar = calendar.monthcalendar(year, month)
    if month < 10:
        month_text = "0" + str(month)
    else:
        month_text = str(month)
    for week in month_calendar:
        for day in week:
            if day == 0:
                continue
            if day < 10:
                day_text = "0" + str(day)
            else:
                day_text = str(day)
            day_text = "{}-{}-{}".format(year, month_text, day_text)
            day_guards = get_day_guards(day_text)
            if len(day_guards[1]) + len(day_guards[2]) + len(
                    day_guards[3]) != 0:
                struct_time = time.strptime(day_text, "%Y-%m-%d")
                timestamp = time.mktime(struct_time)
                if START == 0 or timestamp < START:
                    START = timestamp
                if timestamp > END:
                    END = timestamp
            month_guards.update(day_guards)
    return month_guards


if __name__ == "__main__":
    now = time.time()
    localtime = time.localtime(now)
    year = localtime.tm_year
    month = localtime.tm_mon
    if len(sys.argv) == 1:
        print("按回车获取本月舰长")
        print("输入月份获取该月份的舰长")
        print("输入年份和月份获取该年该月份的舰长（用空格分隔）")
        print("最多只支持半年内的记录")
        argv = input()
        argv = argv.split(" ")
    else:
        argv = sys.argv[1:]
    if len(argv) == 1 and argv[0] != "":
        month = int(argv[0])
    elif len(argv) == 2:
        year = int(argv[0])
        month = int(argv[1])
    guards = get_month_guards(year, month)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    row = ("舰长id", "时间", "用户名", "用户ID", "舰长类型")
    sheet.append(row)
    for level in guards:
        for guard in guards[level]:
            row = (guards[level][guard]["id"], guards[level][guard]["time"],
                   guards[level][guard]["uname"], guards[level][guard]["uid"],
                   guards[level][guard]["gift_name"])
            sheet.append(row)
    start = time.localtime(START)
    start = time.strftime("%Y-%m-%d", start)
    end = time.localtime(END)
    end = time.strftime("%Y-%m-%d", end)
    file_name = "BiliGuard_{}_{}.xlsx".format(start, end)
    workbook.save(file_name)
    print("已保存到 {}".format(file_name))
