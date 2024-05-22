from flask import Flask, request, render_template, jsonify, send_from_directory, session
import os

# 알고리즘 위한 임포트
from bestpath import getPath

app = Flask(__name__)

# 업로드될 때 어디로 갈지 지정
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"  # session을 사용하기 위해 필요한 secret key 설정

# 서버 시작 시 업로드된 파일들을 리스트로 저장
uploaded_files = []


def load_uploaded_files():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    global uploaded_files
    uploaded_files = sorted(
        os.listdir(UPLOAD_FOLDER),
        key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)),
        reverse=True,
    )


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
        temp = getPath(file.filename)
        session["temp"] = temp  # temp 변수를 session에 저장
        return jsonify({"최단경로": temp})

    return "File upload failed", 500


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/bestpath", methods=["GET"])
def bestpath():
    temp = session.get("temp")  # session에서 temp 변수를 읽어옴
    if temp is None:
        return "No path found", 400
    return jsonify({"shortest_path": temp})


if __name__ == "__main__":
    app.run(debug=True)
