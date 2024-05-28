from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import sqlite3
import json

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


@app.route("/upload", methods=["POST"])
def upload_image():
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
        best_path = getPath(file.filename, 1, 0)
        best_path_json = json.dumps(best_path)  # 리스트를 JSON 문자열로 변환

        # SQLite에 저장
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO paths (filename, best_path) VALUES (?, ?)",
                (file.filename, best_path_json),
            )
            conn.commit()

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


if __name__ == "__main__":
    app.run(debug=True)
