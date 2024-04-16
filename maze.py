from sense_hat import SenseHat
from time import sleep

sense = SenseHat()
O = (0, 0, 0)
X = (255,255,255)
black = (0,0,0)
white = (255,255,255)
green = (255,0,255)
skyblue = (255,0,0)

block = [
    [O,X,O,O,O,O,O,O],
    [O,X,X,X,X,X,X,O],
    [O,O,O,O,O,O,X,O],
    [O,X,X,X,X,O,X,O],
    [O,O,X,O,O,O,X,O],
    [O,O,X,O,X,X,X,O],
    [O,X,X,O,O,O,O,O],
    [O,O,O,O,X,X,X,O]
]

for i in range(0, 8):
    for j in range(0, 8):
        sense.set_pixel(j, i, block[i][j])

sense.set_pixel(7, 7, green)

dy = (-1, 1, 0, 0)
dx = (0, 0, -1, 1)

answer = []
num = 0

starty = 0
startx = 0

def dfs(answer, visited, sy, sx):
    visited = [row[:] for row in visited]

    visited[sy][sx] = 1

    if sy == 7 and sx == 7:
        answer.append(visited)
        return

    for i in range(4):
        ny = sy + dy[i]
        nx = sx + dx[i]
        if not (0 <= ny <= 7 and 0 <= nx <= 7):
            continue
        if block[ny][nx] == X:
            continue
        if visited[ny][nx] == 1:
            continue
        if not visited[ny][nx]:
            dfs(answer, visited, ny, nx)
            
    visited[sy][sx] = 0

# 갈 수 있는 모든 경로 탐색 
def find_path(nowy, nowx):
    visited = [[0] * 8 for _ in range(8)]
    while len(answer):
        answer.pop()
    dfs(answer, visited, nowy, nowx)


# 버튼 누를 때마다 경로 그리기
# 모든 경로 다 돌았으면 다시 처음 경로부터 그리기
def push_middle(num):
    clear(starty, startx)

    for i in range(8):
        nowAns = answer[num][i]
        for j in range(8):
            if nowAns[j] == 1:   
                sense.set_pixel(j, i, skyblue)
    sleep(1)

    # 복구
    for i in range(8):
        nowAns = answer[num][i]
        for j in range(8):
            if nowAns[j] == 1:
                sense.set_pixel(j, i, black)

    sense.set_pixel(startx, starty, green)
    sense.set_pixel(7, 7, green)

def print_path():
    global num
    for event in sense.stick.get_events():
        if event.action == "pressed" and event.direction == "middle":
            push_middle(num)
            num += 1
            if num == len(answer): 
                num = 0
                return

# 최단경로 찾기
def dijkstra(sy, sx):
    visited = [[100] * 8 for _ in range(8)]
    queue = [[sy, sx]]
    visited[sy][sx] = 0

    while len(queue) != 0:
        now = queue.pop(0)

        if now[0] == 7 and now[1] == 7:
            queue.clear()
            break

        for i in range(4):
            ny = now[0] + dy[i]
            nx = now[1] + dx[i]

            if ny < 0 or ny > 7 or nx < 0 or nx > 7: continue
            if block[ny][nx] == X or visited[ny][nx] <= visited[now[0]][now[1]] + 1: continue

            visited[ny][nx] = visited[now[0]][now[1]] + 1
            queue.append([ny, nx])

    # 목적지부터 탐색
    nowy = 7
    nowx = 7
    cnt = visited[7][7] - 1
    road = [[nowy, nowx]]
    
    while cnt >= 0:
        for i in range(4):
            ny = nowy + dy[i]
            nx = nowx + dx[i]

            if ny < 0 or ny > 7 or nx < 0 or nx > 7: continue
            if block[ny][nx] == X or visited[ny][nx] != cnt: continue

            road.append([ny, nx])
            nowy, nowx = ny, nx
            cnt -= 1      
            break
    return road      

# 최단 경로 그리기
def min_path(road):
    sense.set_pixel(road[0][1], road[0][0], green)
    sense.set_pixel(road[-1][1], road[-1][0], green)
    for i in range(1, len(road) - 1):
        sense.set_pixel(road[i][1], road[i][0], skyblue)

# 초기화 
def clear(sy, sx):
    for i in range(8):
        for j in range(8):
            if block[i][j] == X:
                sense.set_pixel(j, i, white)
            else:
                sense.set_pixel(j, i, black)
    sense.set_pixel(sx, sy, green)
    sense.set_pixel(7, 7, green)

# 처음 경로 
find_path(starty, startx)


while True:
    ori = sense.get_orientation_degrees()
    x = ori['pitch']
    y = ori['roll']
    print(f"Degree :  X:{x}, Y:{y}")

    tempy = starty
    tempx = startx

    # 기존에 있던 곳 끄기
    sense.set_pixel(startx, starty, black)

    if 50 <= y <= 130:
        if starty + 1 <= 7 and block[starty + 1][startx] == O:
            starty += 1
            moving = 1

    elif 320 <= y <= 340:
        if starty - 1 >= 0 and block[starty - 1][startx] == O:
            starty -= 1
            moving = 1

    elif 20 <= x <= 90:
        if startx - 1 >= 0 and block[starty][startx - 1] == O:
            startx -= 1
            moving = 1

    elif 280 <= x <= 340:
        if startx + 1 <= 7 and block[starty][startx + 1] == O:
            startx += 1
            moving = 1

    # 현재 있는 곳 켜기
    sense.set_pixel(startx, starty, green)

    # 이동한 거라면 그곳에서 갈 수 있는 경로 찾기
    if tempy != starty or tempx != startx:
        clear(starty, startx)
        find_path(starty, startx)

    # 현재 위치의 최단 경로 그리기
    min_path(dijkstra(starty, startx))

    print(len(answer))
    print_path()

    sleep(0.1)
    