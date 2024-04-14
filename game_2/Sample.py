# Team Name: Eevee Lovers
# Team ID: 10
### MEMBERS ###
# 陳清海 0816199
# 范恩宇 109550135
# 李耕雨 109550055

import STcpClient
import numpy as np
import random
from copy import deepcopy
import math
import time

size=15
start_time = time.time()

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Direction:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def mapping(self):
        if self.x == -1 and self.y==-1:
            return 1
        elif self.x == 0 and self.y==-1:
            return 2
        elif self.x == 1 and self.y==-1:
            return 3
        elif self.x == -1 and self.y==0:
            return 4
        elif self.x == 0 and self.y==0: # not use
            return 5
        elif self.x == 1 and self.y==0:
            return 6
        elif self.x == -1 and self.y==1:
            return 7
        elif self.x == 0 and self.y==1:
            return 8
        elif self.x == 1 and self.y==1:
            return 9

class GameState:
    def __init__(self, mapStat, sheepStat):
        self.mapStat = mapStat
        self.sheepStat = sheepStat
class ChildState:
    def __init__(self, mapStat, sheepStat, changed_pos: Pos, changed_sheep_number, direction: Direction):
        self.mapStat = mapStat
        self.sheepStat = sheepStat
        self.changed_pos = changed_pos
        self.changed_sheep_number = changed_sheep_number
        self.direction = direction

class Action:
    def __init__(self, pos, sheep_number, direction):
        self.pos = pos
        self.sheep_number = sheep_number
        self.direction = direction

def reverse_board(board):
    new_board = deepcopy(board)
    for i in range(len(board)):
        for j in range(len(board[0])):
            new_board[j][i] = board[i][j]
    return new_board

def print_sheepStat(sheepStat):
    print("sheep stat")
    for y in range(size):
        for x in range(size):
            if sheepStat[y][x]==0:
                print(".",end=" ")
            else:
                print(int(sheepStat[y][x]),end=" ")
        print("")

def print_mapStat(mapStat):
    print("map stat")
    for y in range(size):
        for x in range(size):
            if mapStat[y][x]<=4 and mapStat[y][x]>=1:
                print(int(mapStat[y][x]),end=" ")
            elif mapStat[y][x]==-1:
                print("x",end=" ")
            else:
                print(".",end=" ")
        print("")
'''
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=[x,y],代表起始位置
    
'''
def init_pos_valid(mapStat, init_pos): 
        x, y = init_pos
        if mapStat[x][y] != 0:
            return False
        
        map_expanded = np.pad(mapStat.copy(), pad_width=1, mode='constant', constant_values=0)
        window = map_expanded[x:x+3, y:y+3]
        return np.any(window == -1)

def bound_valid(x, y, board_size):
        return (x >= 0) and (x < board_size) and (y >= 0) and (y < board_size)

def reverse_pos(pos):
        x, y = pos
        return (y, x)

def set_init_pos(mapStat, board_size=15):
        surrounding = [
            (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
            (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
            (0, -2),  (0, -1),           (0, 1),  (0, 2),
            (1, -2),  (1, -1),  (1, 0),  (1, 1),  (1, 2),
            (2, -2),  (2, -1),  (2, 0),  (2, 1),  (2, 2)
        ]

        max_count = -1
        best_init_pos = [0, 0]

        for i in range(board_size):
            for j in range(board_size):
                init_pos = [i, j]

                if not init_pos_valid(mapStat, init_pos):
                    continue

                count = 0
                for dx, dy in surrounding:
                    nx, ny = init_pos[0] + dx, init_pos[1] + dy
                    if bound_valid(nx, ny, board_size) and mapStat[nx][ny] == 0:
                        count += 1

                if count > max_count:
                    max_count = count
                    best_init_pos = init_pos

        return best_init_pos

def InitPos(mapStat):
    init_pos = set_init_pos(mapStat)
    init_pos = reverse_pos(init_pos) # backpropagation
    return init_pos

def nextPos(pos, direction):
    return Pos(pos.x+direction.x,pos.y+direction.y)

def inBoard(pos: Pos):
    return pos.x>=0 and pos.x<size and pos.y>=0 and pos.y<size

def isEmpty(mapStat, pos):
    return mapStat[pos.y][pos.x] == 0

# def isAlly(playerID, mapStat, pos):
#     return mapStat[pos.y][pos.x] == playerID

def straight_line_end(mapStat, pos, direction):
    currentPos = pos
    while True:
        nextpos = nextPos(currentPos,direction)
        if inBoard(nextpos) and isEmpty(mapStat, nextpos):
            currentPos = nextPos(currentPos,direction)
        else:
            break

    return currentPos

def getChildStates(playerID, state: GameState):
    mapStat = state.mapStat
    sheepStat = state.sheepStat
    childStates = []

    for cur_playerID in range(1,5):
        if cur_playerID == playerID:  ## Only consider enemy actions
            continue
        actions = get_actions_half(cur_playerID, state)
        for action in actions:
            if time.time() - start_time > 2.8:
                print("end prematurely")
                break
            pos = action.pos
            farest_pos_in_the_direction = straight_line_end(mapStat, pos, action.direction)

            newMapStat = deepcopy(mapStat)
            newSheepStat = deepcopy(sheepStat)

            newSheepStat[pos.y][pos.x] -= action.sheep_number
            newSheepStat[farest_pos_in_the_direction.y][farest_pos_in_the_direction.x] += action.sheep_number

            newMapStat[farest_pos_in_the_direction.y][farest_pos_in_the_direction.x] = cur_playerID

            childStates.append(GameState(newMapStat,newSheepStat))
        
    return childStates

def evaluation_function(playerID,state: GameState):
    mapStat = state.mapStat
    sheepStat = state.sheepStat

    def calculate_free_side(pos):
        dx = [1,1,1,0,0,-1,-1,-1]
        dy = [1,0,-1,1,-1,1,0,-1]

        x = pos.x
        y = pos.y

        count = 0
        for k in range(8):
            newPos = Pos(x+dx[k],y+dy[k])
            if inBoard(newPos) and isEmpty(mapStat,newPos):
                count += 1
        return count
    
    # def calculate_adjacent_ally(pos):
    #     dx = [1,1,1,0,0,-1,-1,-1]
    #     dy = [1,0,-1,1,-1,1,0,-1]

    #     x = pos.x
    #     y = pos.y

    #     count = 0
    #     for k in range(8):
    #         newPos = Pos(x+dx[k],y+dy[k])
    #         if inBoard(newPos) and isAlly(playerID, mapStat, pos):
    #             count += 1
    #     return count

    value = 0
    free_side = 0
    stuck_penalty = 0
    for y in range(size):
        for x in range(size):
            if mapStat[y][x]>=1 and mapStat[y][x]<=4 and sheepStat[y][x] > 1:
                num_free_side = calculate_free_side(Pos(x,y))
                if mapStat[y][x] == playerID:
                    free_side += num_free_side * sheepStat[y][x]
                    if num_free_side == 0:
                        stuck_penalty += sheepStat[y][x] - 1 
                else:
                    free_side -= num_free_side * sheepStat[y][x]
    
    ### Weights 
    w_free_side = 0.5
    w_stuck_penalty = 100

    value = w_free_side * free_side + get_score(playerID,state) - w_stuck_penalty * stuck_penalty
   
    return value

def dfs(mapStat, playerID, board_size, visited, i, j):
        if i < 0 or i >= board_size or j < 0 or j >= board_size or visited[i][j] or mapStat[i][j] != playerID:
            return 0
        visited[i][j] = True
        return 1 + dfs(mapStat, playerID, board_size, visited, i - 1, j) \
                    + dfs(mapStat, playerID, board_size, visited, i + 1, j) \
                    + dfs(mapStat, playerID, board_size, visited, i, j - 1) \
                    + dfs(mapStat, playerID, board_size, visited, i, j + 1)

def get_connected_cell(mapStat, playerID, board_size=15):
    connected_cell = []
    visited = [[False for _ in range(board_size)] for _ in range(board_size)]
    for i in range(board_size):
        for j in range(board_size):
            # go through cells connected but unvisited
            if mapStat[i][j] == playerID and not visited[i][j]:
                connected_cell.append(dfs(mapStat, playerID, board_size, visited, i, j))
    return connected_cell

def get_score(playerID, state:GameState):
    mapStat = state.mapStat
    sheepStat = state.sheepStat
    cells = get_connected_cell(mapStat, playerID)
    return round(sum([cell ** 1.25 for cell in cells]))

def find_max_value(playerID, state: GameState, alpha, beta, depth):
    if depth == 2:
        return evaluation_function(playerID,state)
    all_child_states = getChildStates(playerID,state)
    max_score = -1000000
    for child_state in all_child_states:
        score = find_min_value(playerID, child_state, alpha, beta, depth+1)
        max_score = max(score, max_score)
        if max_score >= beta:
            return max_score
        alpha = max(alpha, max_score)
        
    return max_score

def find_min_value(playerID, state: GameState, alpha, beta, depth):
    if depth == 2:
        return evaluation_function(playerID,state)
    all_child_states = getChildStates(playerID, state)
    min_score = 1000000
    for child_state in all_child_states:
        score = find_max_value(playerID, child_state, alpha, beta, depth+1)
        min_score = min(score, min_score)
        if min_score <= alpha:
            return min_score
        beta = min(beta, min_score)
    return min_score

def get_actions(playerID, state: GameState) -> list[Action]:
    dx = [1,1,1,0,0,-1,-1,-1]
    dy = [1,0,-1,1,-1,1,0,-1]
    mapStat = state.mapStat
    sheepStat = state.sheepStat
    newActions = []
    for y in range(size):
        for x in range(size):
            if mapStat[y][x] == playerID and sheepStat[y][x]>1:
                pos = Pos(x,y)
                for k in range(8):
                    farest_pos_in_the_direction = straight_line_end(mapStat,pos,Direction(dy[k],dx[k]))
                    if farest_pos_in_the_direction!=pos:
                        sheep_number_in_this_pos = sheepStat[pos.y][pos.x]

                        # newActions.append(Action(pos,1,Direction(dy[k],dx[k]))) # Split 1 sheep into new cell

                        for n in range(1,int(sheep_number_in_this_pos), max(1, math.floor(sheep_number_in_this_pos / 5)) ):
                            newActions.append(Action(pos,n,Direction(dy[k],dx[k])))

                        # newActions.append(Action(pos,int(sheep_number_in_this_pos) - 1,Direction(dy[k],dx[k]))) # Split maximum possible sheep into new cell

    return newActions

def get_actions_half(playerID, state: GameState) -> list[Action]: # Get actions but only consider half sheep split
    dx = [1,1,1,0,0,-1,-1,-1]
    dy = [1,0,-1,1,-1,1,0,-1]
    mapStat = state.mapStat
    sheepStat = state.sheepStat
    newActions = []
    for y in range(size):
        for x in range(size):
            if mapStat[y][x] == playerID and sheepStat[y][x]>1:
                pos = Pos(x,y)
                for k in range(8):
                    farest_pos_in_the_direction = straight_line_end(mapStat,pos,Direction(dy[k],dx[k]))
                    if farest_pos_in_the_direction!=pos:
                        sheep_number_in_this_pos = sheepStat[pos.y][pos.x]
                        newActions.append(Action(pos,math.floor(sheep_number_in_this_pos/2),Direction(dy[k],dx[k])))

    return newActions
'''
    產出指令
    
    input: 
    playerID: 你在此局遊戲中的角色(1~4)
    mapStat : 棋盤狀態(list of list), 為 12*12矩陣, 
              0=可移動區域, -1=障礙, 1~4為玩家1~4佔領區域
    sheepStat : 羊群分布狀態, 範圍在0~16, 為 12*12矩陣

    return Step
    Step : 3 elements, [(x,y), m, dir]
            x, y 表示要進行動作的座標 
            m = 要切割成第二群的羊群數量
            dir = 移動方向(1~9),對應方向如下圖所示
            1 2 3
            4 X 6
            7 8 9
'''

def GetStep(playerID, mapStat, sheepStat):
    # step = [(0, 0), 0, 1]
    '''
    Write your code here
    
    '''
    global start_time
    start_time = time.time()

    mapStat = reverse_board(mapStat)
    sheepStat = reverse_board(sheepStat)

    state = GameState(mapStat, sheepStat)
    actions = get_actions(playerID, state)
    max_value = -10000000
    for action in actions:
        pos = action.pos
        farest_pos_in_the_direction = straight_line_end(mapStat, pos, action.direction)
        newMapStat = deepcopy(mapStat)
        newSheepStat = deepcopy(sheepStat)
        newSheepStat[pos.y][pos.x] -= action.sheep_number
        newSheepStat[farest_pos_in_the_direction.y][farest_pos_in_the_direction.x] += action.sheep_number
        newMapStat[farest_pos_in_the_direction.y][farest_pos_in_the_direction.x] = playerID

        the_value = find_min_value(playerID, GameState(newMapStat,newSheepStat),-1000000,1000000,1)

        if the_value > max_value:
            max_value = the_value
            max_action = action
    
    #print_mapStat(mapStat)
    #print_sheepStat(sheepStat)

    if max_action:
        step = [(max_action.pos.x,max_action.pos.y), max_action.sheep_number, max_action.direction.mapping()]
    else:
        step = []

    end_time = time.time()
    print("Time took: ", end_time - start_time, "seconds")

    return step

    # print(actions)
    
    # if len(actions)>0:
    #     max_action = actions[0]
    #     print(max_action.direction.x, max_action.direction.y)
    #     step = [(max_action.pos.x,max_action.pos.y), max_action.sheep_number, max_action.direction.mapping()]

    #     return step
    # else:
    #     return []

# player initial
(id_package, playerID, mapStat) = STcpClient.GetMap()
init_pos = InitPos(mapStat)
STcpClient.SendInitPos(id_package, init_pos)

# start game
while (True):
    (end_program, id_package, mapStat, sheepStat) = STcpClient.GetBoard()
    if end_program:
        STcpClient._StopConnect()
        break
    Step = GetStep(playerID, mapStat, sheepStat)

    STcpClient.SendStep(id_package, Step)
