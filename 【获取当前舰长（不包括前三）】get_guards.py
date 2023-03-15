import json
import requests


def get_guards(url):
    guards = []
    guard = requests.get(url)
    code = guard.json()["code"]
    if code == 0:
        guards = guard.json()["data"]["list"]
    else:
        print("错误代码：{}".format(code))
        message = guard.json()["message"]
        print("错误信息：{}".format(message))
    return guards


def get_all_guards(room_id, ruid):
    base_url = "https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList?roomid=ROOM_ID&page=PAGE&ruid=RUID&page_size=30"
    print("正在获取舰长列表")
    base_url = base_url.replace('ROOM_ID', room_id).replace('RUID', ruid)
    guard_list = []
    i = 1
    while True:
        url = base_url.replace('PAGE', str(i))
        guards = get_guards(url)
        guard_list.extend(guards)
        if guards == []:
            print("舰长列表获取完毕")
            return guard_list
        i = i+1


print("请输入直播间id：")
room_id = input()
print("请输入uid：")
ruid = input()
guard_list = get_all_guards(room_id, ruid)
path = "guards.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(guard_list, f, indent=4, ensure_ascii=False)
    print("文件已写入到{}".format(path))
