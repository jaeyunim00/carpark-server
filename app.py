from flask import Flask, request, render_template, jsonify, send_from_directory
import os

# 알고리즘위한 임포트
from algorithms import Current_maps, best_index, algo, get_shortest_path

app = Flask(__name__)

# 업로드될 때 어디로 갈지 지정, 그냥 두개로 나눠서 지정한거임.
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 이미지 핸들링해보기 예제
latest_filename = None


@app.route("/")
def upload_form():
    return render_template("upload.html", filename=latest_filename)


@app.route("/upload", methods=["POST"])
def upload_image():
    # 이건 뭐 그냥 기본 에러차리 위한거고
    if "carpark" not in request.files:
        return "No file part", 400
    # file 변수에 이미지 저장
    file = request.files["carpark"]
    if file.filename == "":
        return "No selected file", 400

    # 여기가 중요. 파일이 있을 때 처리
    if file:
        latest_filename = file.filename
        # 파일 위치 설정 및
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], latest_filename)
        file.save(file_path)
        # 파일 이름의 길이 반환
        return jsonify({"filename_length": len(file.filename)})

    return "File upload failed", 500


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# 가장 좋은 경로 GET하기
@app.route("/bestpath", methods=["GET"])
def bestpath():
    shortest_path = get_shortest_path()
    if shortest_path == "No path found":
        return jsonify({"message": shortest_path})
    else:
        return jsonify({"shortest_path": shortest_path})


if __name__ == "__main__":
    app.run(debug=True)
