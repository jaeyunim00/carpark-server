import math
from collections import deque
from PIL import Image
import numpy as np
import cv2


def getPath(img_name):
    def calculation_distance(maps, entry):
        distances = []

        for i in range(len(maps)):
            for j in range(len(maps[0])):
                if maps[i][j] == 1:
                    distance = math.sqrt((i - entry[0]) ** 2 + (j - entry[1]) ** 2)
                    distances.append((distance, (i, j)))

        return sorted(distances, key=lambda x: x[0])

    def algo(maps, st, en):  # maps 는 2차원 배열, st는 시작점, en은 끝점
        rows, cols = len(maps), len(maps[0])  # 배열의 크기를 확인
        queue = deque([(st[0], st[1], [])])  # 큐(deque)초기화

        while queue:  # queue가 빌때까지
            x, y, path = (
                queue.popleft()
            )  # 큐에서 요소를 꺼내 현재 위치 x,y와 해당 위치까지 출력

            if (x, y) == en:
                return path + [(x, y)]

            if (
                not (0 <= x < rows and 0 <= y < cols)
                or maps[x][y] == 1
                or maps[x][y] == -1
                or maps[x][y] == 3
                or maps[x][y] == 2
            ):
                continue

            maps[x][y] = -1

            for dx, dy in [
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),
            ]:  # 현재 위치에서 이동 가능한 모든 방향에 대해 새로운 위치를 계산, 새로운 위치와 현재까지의 경로를 큐에 추가
                new_x, new_y = x + dx, y + dy
                queue.append((new_x, new_y, path + [(x, y)]))

        return None

    def convert_to_decimal(array):
        return [[float(item) for item in row] for row in array]

    def invert_array(arr):
        inverted_arr = np.array([[255 - pixel for pixel in row] for row in arr])
        return inverted_arr

    def compress_array(original_array, new_size):

        new_array = np.zeros(new_size)

        row_size = len(original_array)
        col_size = len(original_array[0])

        rows = row_size // 16
        cols = col_size // 18

        for i in range(new_size[0]):
            for j in range(new_size[1]):

                start_row = i * rows
                start_col = j * cols

                avg_value = np.mean(
                    original_array[
                        start_row : start_row + rows, start_col : start_col + cols
                    ]
                )

                new_array[i][j] = avg_value

        return new_array

    def detection(value):
        if value > 135:
            value = 2
        else:
            value = 1

        return value

    def mapping(gray_maps, maps_arr):
        i = j = 0
        for i in range(len(maps_arr)):
            for j in range(len(maps_arr[0])):
                if maps_arr[i][j] == 1:
                    val = detection(gray_maps[i][j])
                    maps_arr[i][j] = val

        return maps_arr

    def compress_2X2_array(arr):
        compressed_arr = []
        for i in range(0, len(arr), 2):
            row = []
            for j in range(0, len(arr[0]), 2):
                # 2x2 부분 배열을 압축하여 하나의 값으로 만듭니다.
                compressed_value = arr[i][j]  # (i,j) 부분 배열의 왼쪽 위 값
                row.append(compressed_value)
            compressed_arr.append(row)
        return compressed_arr

    def compress_indices(indices):

        compressed_indices = []

        for i, j in indices:
            # 16x18 배열의 인덱스를 8x9 배열의 인덱스로 변환
            new_i = i // 2
            new_j = j // 2

            compressed_indices.append((new_i, new_j))

        return compressed_indices

    def compress_index_indices(indices):

        compressed_index_indices = []
        seen = set()

        for index in indices:
            if index not in seen:
                compressed_index_indices.append(index)
                seen.add(index)

        return compressed_index_indices

    def cut_image(image_path):

        image = cv2.imread(image_path)  # 이미지 로드

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 그레이 스케일로 변환

        _, binary = cv2.threshold(
            gray, 50, 255, cv2.THRESH_BINARY_INV
        )  # 검은색 선을 찾기 위해 역치화

        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )  # 윤곽선 검출

        rightmost_contour = max(
            contours,
            key=lambda cnt: cv2.boundingRect(cnt)[0] + cv2.boundingRect(cnt)[2],
        )  # 가장 오른쪽에 있는 검은색 선의 윤곽선 선택

        x, y, w, h = cv2.boundingRect(
            rightmost_contour
        )  # 가장 오른쪽에 있는 윤곽선의 x 좌표 찾기
        right_bound = x + w

        cropped_image = image[:, :right_bound]  # 오른쪽 여백 자르기

        return cropped_image

    # latest_uploaded_image_name = uploaded_image_name

    input_image_path = "uploads/" + img_name  # 입력 이미지 경로

    cut_image = cut_image(input_image_path)
    image = Image.fromarray(cv2.cvtColor(cut_image, cv2.COLOR_BGR2RGB))

    image.convert("RGB")
    image = image.convert("L")

    image_array = np.array(image)

    inverted_image_array = invert_array(image_array)

    new_size = (16, 18)
    original_array = inverted_image_array
    compressed_array = compress_array(original_array, new_size)

    compressed = np.array(compressed_array)

    compressed = convert_to_decimal(compressed)

    maps = [
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # 0행
        [3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3],  # 1행
        [3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3],  # 2행
        [3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3],  # 3행
        [3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3],  # 4행
        [3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3],  # 5행
        [3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3],  # 6행
        [3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3, 3, 1, 0, 0, 1, 3],  # 7행
        [3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3],  # 8행
        [3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3],  # 9행
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 1, 0, 0, 1, 3],  # 10행
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 1, 0, 0, 1, 3],  # 11행
        [3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3],  # 12행
        [3, 3, 3, 3, 3, 3, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3],  # 13행
        [3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],  # 14행
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    ]  # 15행

    fin_map = mapping(compressed, maps)

    entry = (0, 12)

    result = calculation_distance(fin_map, entry)

    best = result.pop(0)[1]

    start = (13, 8)  # 고정
    end = best

    li = algo(fin_map, start, end)

    compressed_array = compress_2X2_array(fin_map)

    compressed_indices = compress_indices(li)

    indexing = compress_index_indices(compressed_indices)

    load_map = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 18, 19, 20, 21, 0, 0, 9, 0],
        [0, 17, 0, 0, 22, 0, 0, 8, 0],
        [0, 16, 0, 0, 23, 0, 0, 7, 0],
        [0, 15, 14, 13, 12, 11, 10, 6, 0],
        [0, 0, 0, 0, 0, 0, 0, 5, 0],
        [0, 0, 0, 0, 1, 2, 3, 4, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    values = [load_map[i][j] for i, j in indexing]

    values_slice = values[:-1]

    return values_slice
