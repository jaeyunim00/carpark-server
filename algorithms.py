import math
from collections import deque

# Current maps 데이터
Current_maps = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 0행
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 1행
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 2행
    [1, 0, 0, 3, 1, 0, 0, 1, 3, 0, 0, 1],  # 3행
    [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],  # 4행
    [1, 0, 0, 1, 3, 0, 0, 1, 1, 0, 0, 1],  # 5행
    [3, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],  # 6행
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],  # 7행
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 8행
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1],  # 9행
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1],  # 10행
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],  # 11행
    [1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 1],  # 12행
    [1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1],
]  # 13행


def best_index():
    entry = (0, 9)
    result = calculation_distance(Current_maps, entry)
    best = result.pop(0)[1]
    return best


def calculation_distance(maps, entry):
    distances = []
    for i in range(len(maps)):
        for j in range(len(maps[0])):
            if maps[i][j] == 1:
                distance = math.sqrt((i - entry[0]) ** 2 + (j - entry[1]) ** 2)
                distances.append((distance, (i, j)))
    return sorted(distances, key=lambda x: x[0])


def algo(maps, st, en):
    rows, cols = len(maps), len(maps[0])
    queue = deque([(st[0], st[1], [])])

    while queue:
        x, y, path = queue.popleft()

        if (x, y) == en:
            return path + [(x, y)]

        if not (0 <= x < rows and 0 <= y < cols) or maps[x][y] == 1 or maps[x][y] == -1:
            continue

        maps[x][y] = -1

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            queue.append((new_x, new_y, path + [(x, y)]))

    return None


def get_shortest_path():
    start = (12, 4)  # 고정
    end = best_index()
    shortest_path = algo(Current_maps, start, end)

    # 일단 그냥 테스트용 리턴 할꺼임
    return [1, 2, 3, 4, 5, 6, 10, 11, 12, 23, 22, 21]

    if shortest_path:
        return shortest_path
    else:
        return "No path found"
