import time
import json
import requests
from flask import Flask, render_template, jsonify
from threading import Thread
import os

# 初始化 Flask 应用
app = Flask(__name__, template_folder=os.getcwd())

# id列表
id_list = [
    1542516095, 1827139579, 56748733, 7706705, 690608698, 1932862336, 2039332008, 434334701, 1954091502, 2124647716,
    1048135385, 690608704, 666726799, 1609526545, 6853766, 14387072, 529249, 1323355750, 690608691, 477317922,
    434401868, 392505232, 1609795310, 1711724633, 1789460279, 61639371, 690608693, 1116072703, 2040984069, 690608709,
    421267475, 1570525137, 472877684, 558070433, 1978590132, 1296515170, 2080519347, 1297910179, 12485637, 2057377595,
    690608688, 1694351351, 1567394869, 690608710, 1405589619, 176836079, 480675481,474369808,480680646,666726801,490331391,
    1217754423,1900141897,1660392980,1878154667,1526446007,1616183604,1739085910,1484169431,
]

# API URLs
ranking_url = "https://api.vtbs.moe/v1/guard/"  # 按照v的id查询舰长
live_status_url = "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids"

# 全局数据存储
ranking_data = {}
user_data = {}

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def fetch_data():
    global ranking_data, user_data

    while True:
        try:
            for v_id in id_list:
                try:
                    # 获取舰长数据
                    ranking_response = requests.get(ranking_url + str(v_id), headers=headers)
                    ranking_response.raise_for_status()
                    ranking_list = ranking_response.json()

                    # 计算主播的总分数和各等级总数
                    total_score = 0
                    total_governor = 0
                    total_admiral = 0
                    total_captain = 0
                    for rank in ranking_list:
                        level = rank['level']
                        if level == 0:
                            total_score += 19998
                            total_governor += 1
                        elif level == 1:
                            total_score += 1998
                            total_admiral += 1
                        elif level == 2:
                            total_score += 168
                            total_captain += 1

                    # 获取直播状态
                    live_status_response = requests.post(live_status_url, json={"uids": [v_id]}, headers=headers)
                    live_status_response.raise_for_status()
                    live_status_data = live_status_response.json()['data'].get(str(v_id), {})

                    # 更新数据
                    ranking_data[v_id] = {
                        "uid": v_id,
                        "score": total_score,
                        "uname": live_status_data.get('uname', '未知主播'),
                        "face": live_status_data.get('face', ''),
                        "live_status": live_status_data.get('live_status', 0),
                        "room_id": live_status_data.get('room_id', None),
                        "live_title": live_status_data.get('title', ""),
                        "area_name": live_status_data.get('area_v2_name', ""),
                        "total_governor": total_governor,
                        "total_admiral": total_admiral,
                        "total_captain": total_captain
                    }
                except Exception as e:
                    print(f"Error fetching data for v_id {v_id}: {e}")

            time.sleep(3)
        except Exception as e:
            print(f"Error in fetch_data: {e}")


# 启动后台数据线程
thread = Thread(target=fetch_data)
thread.daemon = True
thread.start()


@app.route('/')
def index():
    return render_template('vr.html')


@app.route('/get_ranking')
def get_ranking():
    # 将字典转换为列表并按分数排序
    sorted_ranking = sorted(ranking_data.values(), key=lambda x: x['score'], reverse=True)
    # 重新赋值rank
    for idx, rank in enumerate(sorted_ranking):
        rank['rank'] = idx + 1
    return jsonify({'ranking': sorted_ranking})

# 启动 Flask 应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2992)