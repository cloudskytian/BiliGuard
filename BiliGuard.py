# -*- coding: UTF-8 -*-

import calendar
import csv
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
    print("3.将得到的内容并粘贴到 cookies.json\n")
    print("得到 文本格式 cookies 的方法")
    print("1.浏览器打开B站，按 F12")
    print("2.进入控制台，输入 document.cookie")
    print("3.复制得到的内容并粘贴到 cookies.txt\n")
    print("按任意键结束程序\n")
    input()
    sys.exit()


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
    # return gift_list

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
    guards = []
    for gift in gift_list:
        if gift["gift_id"] == gift_id:
            guards.append(gift)
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


GUARDS = dict()

# 获取某个月的舰长
def get_month_guards(year, month):
    if year in GUARDS and month in GUARDS[year]:
        return GUARDS[year][month]
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
            if len(day_guards[1]) + len(day_guards[2]) + len(day_guards[3]) != 0:
                struct_time = time.strptime(day_text, "%Y-%m-%d")
                timestamp = time.mktime(struct_time)
                if START == 0 or timestamp < START:
                    START = timestamp
                if timestamp > END:
                    END = timestamp
            for level in day_guards:
                if level not in month_guards:
                    month_guards[level] = day_guards[level]
                else:
                    month_guards[level].extend(day_guards[level])
    if year not in GUARDS:
        GUARDS[year] = dict()
    if month not in GUARDS:
        GUARDS[year][month] = month_guards
    return month_guards


# 导出 csv
def export_csv(guards, file_name):
    with open(file_name + ".csv", "w", encoding="utf-8-sig", newline="") as f:
        writer_zh = csv.DictWriter(f, fieldnames=["时间", "用户名", "用户ID", "舰长类型", "数量"])
        writer_zh.writeheader()
        writer = csv.DictWriter(
            f,
            fieldnames=["time", "uname", "uid", "gift_name", "gift_num"],
            extrasaction="ignore",
        )
        for level in guards:
            for guard in guards[level]:
                writer.writerow(guard)
    print("已保存到 {}".format(file_name + ".csv"))


# 导出 xlsx
def export_xlsx(guards, file_name):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    row = ("时间", "用户名", "用户ID", "舰长类型", "数量")
    sheet.append(row)
    num = 2
    for level in guards:
        for guard in guards[level]:
            row = (
                guard["time"],
                guard["uname"],
                str(guard["uid"]),
                guard["gift_name"],
                guard["gift_num"],
            )
            sheet.append(row)
            cell = sheet["C" + str(num)]
            cell.number_format = "@"
            num += 1
    sheet.column_dimensions["A"].width = 20
    sheet.column_dimensions["B"].width = 15
    sheet.column_dimensions["C"].width = 20
    sheet.column_dimensions["D"].width = 10
    sheet.column_dimensions["E"].width = 5
    workbook.save(file_name + ".xlsx")
    print("已保存到 {}".format(file_name + ".xlsx"))


def parse_args(args):
    now = time.time()
    localtime = time.localtime(now)
    year1 = localtime.tm_year
    month1 = localtime.tm_mon
    year2 = year1
    month2 = month1
    if not args:
        args = input()
    if args == "":
        guards = get_month_guards(year1, month1)
        start = START
        end = END
    else:
        args = args.split(" ")
        if len(args) == 1 and args[0] != "":
            args[0] = args[0].split("-")
            if len(args[0]) == 1:
                month1 = int(args[0][0])
            elif len(args[0]) == 2:
                year1 = int(args[0][0])
                month1 = int(args[0][1])
            else:
                print("参数错误，请重新输入：")
                parse_args(None)
                return
            guards = get_month_guards(year1, month1)
            start = START
            end = END
        elif len(args) == 2:
            for i in range(0, 2):
                args[i] = args[i].split("-")
            if len(args[0]) == 1 and len(args[1]) == 1:
                month1 = int(args[0][0])
                month2 = int(args[1][0])
            elif len(args[0]) == 2 and len(args[1]) == 2:
                year1 = int(args[0][0])
                month1 = int(args[0][1])
                year2 = int(args[1][0])
                month2 = int(args[1][1])
            else:
                print("参数错误，请重新输入：")
                parse_args(None)
                return
            guards = {1: [], 2: [], 3: []}
            start = START
            end = END
            if year1 > year2:
                year1, year2 = year2, year1
                month1, month2 = month2, month1
            if year1 < year2:
                for month in range(month1, 13):
                    month_guards = get_month_guards(year, month)
                    for level in guards:
                        guards[level].extend(month_guards[level])
                    if start == 0 or start > START:
                        start = START
                    if end < END:
                        end = END
                for year in range(year1 + 1, year2):
                    for month in range(1, 13):
                        month_guards = get_month_guards(year, month)
                        for level in guards:
                            guards[level].extend(month_guards[level])
                        if start == 0 or start > START:
                            start = START
                        if end < END:
                            end = END
                for month in range(1, month2 + 1):
                    month_guards = get_month_guards(year, month)
                    for level in guards:
                        guards[level].extend(month_guards[level])
                    if start == 0 or start > START:
                        start = START
                    if end < END:
                        end = END
            elif year1 == year2:
                if month1 > month2:
                    month1, month2 = month2, month1
                for month in range(month1, month2 + 1):
                    month_guards = get_month_guards(year1, month)
                    for level in guards:
                        guards[level].extend(month_guards[level])
                    if start == 0 or start > START:
                        start = START
                    if end < END:
                        end = END
        else:
            print("参数错误，请重新输入：")
            parse_args(None)
            return
    start = time.localtime(start)
    start = time.strftime("%Y-%m-%d", start)
    end = time.localtime(end)
    end = time.strftime("%Y-%m-%d", end)
    file_name = "BiliGuard_{}_{}".format(start, end)
    export_csv(guards, file_name)
    export_xlsx(guards, file_name)


if __name__ == "__main__":
    print("按回车获取本月舰长")
    print("直接输入【月份】获取该月份的舰长，如：")
    print("6")
    print("输入【年份-月份】获取该年该月份的舰长，如：")
    print("2022-6")
    print("输入【月份A 月份B】或【年份-月份A 年份-月份B】获取两个月之间的舰长（用空格分隔），如：")
    print("6 12")
    print("或：")
    print("2022-6 2022-12")
    print("受B站限制，最多只支持半年内的记录")
    args = None
    parse_args(args)
