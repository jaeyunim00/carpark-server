from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import sqlite3
import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# 알고리즘 위한 임포트
from bestpath import getPath

app = Flask(__name__)

# 업로드될 때 어디로 갈지 지정
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# SQLite 데이터베이스 파일
DATABASE = "bestpath.db"

# 서버 시작 시 업로드된 파일들을 리스트로 저장
uploaded_files = []

# 트리거 할 주소들
urls = [
    "http://172.20.170.162:8000/send_path",
    "http://172.20.181.60:8000/send_path",
    "http://172.20.104.41:8000/send_path",
]

url_info = [
    [1, 2, 3, 4, 5, 6, 7],
    [16, 17, 18, 19, 20, 21, 22, 23],
    [8, 9, 10, 11, 12, 13, 14, 15],
]

# 스페셜 센서
special_sensor = 0


def fetch_urls(urls, max_workers=3):
    def fetch_url(url):
        try:
            response = requests.get(url)
            return response.status_code, response.text
        except requests.RequestException as e:
            return None, str(e)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_url, url) for url in urls]

        for future in futures:
            status_code, content = future.result()
            results.append((status_code, content))
            print(f"Status Code: {status_code}")
            print(f"Content: {content}")

    return results


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS paths (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filename TEXT UNIQUE,
                            best_path TEXT
                          )"""
        )
        conn.commit()


def load_uploaded_files():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    global uploaded_files
    uploaded_files = sorted(
        os.listdir(UPLOAD_FOLDER),
        key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)),
        reverse=True,
    )


init_db()
load_uploaded_files()


@app.route("/")
def upload_form():
    return render_template("upload.html", filenames=uploaded_files)

# 트리거 할 주소들
urls = [
    "http://172.20.170.162:8000/send_path",
    "http://172.20.181.60:8000/send_path",
    "http://172.20.104.41:8000/send_path",
]

url_info = [
    [1, 2, 3, 4, 5, 6, 7],
    [16, 17, 18, 19, 20, 21, 22, 23],
    [8, 9, 10, 11, 12, 13, 14, 15],
]


@app.route("/upload", methods=["POST"])
def upload_image():
    global special_sensor
    if "carpark" not in request.files:
        return "No file part", 400
    file = request.files["carpark"]
    if file.filename == "":
        return "No selected file", 400

    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        print(file_path)
        file.save(file_path)
        uploaded_files.append(file.filename)

        # 최단 경로 계산 및 저장
        best_path = getPath(file.filename, 1, special_sensor)
        # best_path = [1,2,3,4,5,6,10,11,12,13,14,15,16]
        best_path_json = json.dumps(best_path)  # 리스트를 JSON 문자열로 변환

        # SQLite에 저장
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO paths (filename, best_path) VALUES (?, ?)",
                (file.filename, best_path_json),
            )
            conn.commit()

        if (best_path == -1):
            try:
                response = requests.get("http://172.20.104.41:5050/full")
                return response.status_code, response.text
            except requests.RequestException as e:
                return None, str(e)

        fetch_urls(urls)

        time.sleep(3)

        for value in best_path:
            print(value)
            if value in url_info[0]:
                response = requests.post("http://172.20.170.162:8000/receive_path", json={"off_path": [value]})
                print(
                    f"Sent {value} to {"http://172.20.170.162:8000/receive_path"}, response: {response.status_code}"
                )
                time.sleep(1)
            elif value in url_info[1]:
                response = requests.post("http://172.20.181.60:8000/receive_path", json={"off_path": [value]})
                print(
                    f"Sent {value} to {"http://172.20.181.60:8000/receive_path"}, response: {response.status_code}"
                )
                time.sleep(1)
            elif value in url_info[2]:
                response = requests.post("http://172.20.104.41:8000/receive_path", json={"off_path": [value]})
                print(
                    f"Sent {value} to {"http://172.20.104.41:8000/receive_path"}, response: {response.status_code}"
                )
                time.sleep(1)
            else:
                return "오류"

            # time.sleep(1)  # 1초 지연

        special_sensor = 0

        return jsonify({"최단경로": best_path})

    return "File upload failed", 500


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/bestpath", methods=["GET"])
def bestpath():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT best_path FROM paths ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

    if result is None:
        return jsonify({"error": "No paths found"}), 404

    best_path = json.loads(result[0])  # JSON 문자열을 파이썬 객체로 변환
    return jsonify({"shortest_path": best_path})


# 센서 트리거
@app.route("/trigger_sensor", methods=["GET"])
def trigger_sensor():
    global special_sensor
    special_sensor = 1
    return jsonify({"message": "Sensor triggered", "special_sensor": special_sensor})


@app.route("/reset_sensor", methods=["GET"])
def reset_sensor():
    global special_sensor
    special_sensor = 0
    return jsonify({"message": "Sensor reset", "special_sensor": special_sensor})


@app.route("/delete_all_paths", methods=["DELETE"])
def delete_all_paths():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM paths")
            conn.commit()
        # 업로드된 파일 목록도 초기화
        global uploaded_files
        uploaded_files = []
        return jsonify({"message": "All paths deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
