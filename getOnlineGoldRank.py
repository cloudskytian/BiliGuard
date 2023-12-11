import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
}


def get_ogr_users(url, headers=HEADERS):
    ogr_users = []
    ogr_user = requests.get(url, headers=headers)
    code = ogr_user.json()["code"]
    if code == 0:
        ogr_users = ogr_user.json()["data"]["OnlineRankItem"]
    else:
        print("错误代码：{}".format(code))
        message = ogr_user.json()["message"]
        print("错误信息：{}".format(message))
    return ogr_users


def get_all_ogr_users(room_id, ruid):
    base_url = "https://api.live.bilibili.com/xlive/general-interface/v1/rank/getOnlineGoldRank?ruid=RUID&roomId=ROOM_ID&page=PAGE&pageSize=50"
    print("正在获取高能榜列表")
    base_url = base_url.replace('ROOM_ID', room_id).replace('RUID', ruid)
    ogr_user_list = []
    i = 1
    while True:
        url = base_url.replace('PAGE', str(i))
        ogr_users = get_ogr_users(url)
        ogr_user_list.extend(ogr_users)
        if ogr_users == []:
            print("高能榜列表获取完毕")
            return ogr_user_list
        i = i+1


print("请输入直播间id：")
room_id = input()
print("请输入uid：")
ruid = input()
ogr_user_list = get_all_ogr_users(room_id, ruid)
path = "OnlineGoldRank.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(ogr_user_list, f, indent=4, ensure_ascii=False)
    print("文件已写入到{}".format(path))
    print("按任意键继续")
    input()
    
