import STcpClient
import numpy as np
import random
from copy import deepcopy

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
        elif self.x == -1 and self.y==0:
            return 2
        elif self.x == -1 and self.y==1:
            return 3
        elif self.x == 0 and self.y==-1:
            return 4
        elif self.x == 0 and self.y==0: # not use
            return 5
        elif self.x == 0 and self.y==1:
            return 6
        elif self.x == 1 and self.y==-1:
            return 7
        elif self.x == 1 and self.y==0:
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

'''
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=[x,y],代表起始位置
    
'''
def InitPos(mapStat):
    # init_pos = [0, 0]
    '''
        Write your code here

    '''
    def in_edge(mapStat,i,j):
        dx = [1,1,1,0,0,-1,-1,-1]
        dy = [1,0,-1,1,-1,1,0,-1]
        for k in range(8):
            newI = i+dx[k]
            newJ = j+dy[k]
            if newI < 0 or newJ < 0 or newI >= 12 or newJ >= 12:
                continue
            if mapStat[newI][newJ] == -1:
                return True
        return False

    options = []
    for i in range(12):
        for j in range(12):
            if mapStat[i][j]==0 and in_edge(mapStat,i,j):
                options.append([i,j])

    # return init_pos
    return random.choice(options)

def nextPos(pos, direction):
    return Pos(pos.x+direction.x,pos.y+direction.y)

def isEmpty(mapStat, pos):
    return mapStat[pos.x][pos.y] == 0

def straight_line_end(mapStat, pos, direction):
    currentPos = pos
    while True:
        if isEmpty(mapStat, nextPos(currentPos,direction)):
            currentPos = nextPos(currentPos,direction)
        else:
            break

    return currentPos

def getChildStates(playerID, state: GameState):
    mapStat = state.mapStat
    sheepStat = state.sheepStat
    actions = get_actions(playerID, state)
    childStates = []
    for action in actions:
        pos = action.pos
        farest_pos_in_the_direction = straight_line_end(mapStat, pos, action.direction)

        newMapStat = deepcopy(mapStat)
        newSheepStat = deepcopy(sheepStat)

        newSheepStat[pos.x][pos.y] -= action.sheep_number
        newSheepStat[farest_pos_in_the_direction.x][farest_pos_in_the_direction.y] += action.sheep_number

        newMapStat[farest_pos_in_the_direction.x][farest_pos_in_the_direction.y] = playerID

        childStates.append(GameState(newMapStat,newSheepStat))
    
    return childStates

def evaluation_function(state: GameState):
    pass

def find_max_value(playerID, state: GameState, alpha, beta, depth):
    if depth == 3:
        return evaluation_function(state)
    all_child_states = getChildStates(state)
    max_score = -1000000
    for child_state in all_child_states:
        score = find_min_value(playerID, child_state, alpha, beta, depth+1)
        max_score = max(score, max_score)
        if max_score >= beta:
            return max_score
        alpha = max(alpha, max_score)
        
    return max_score

def find_min_value(playerID, state: GameState, alpha, beta, depth):
    if depth == 3:
        return evaluation_function(state)
    all_child_states = getChildStates(state)
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
    for i in range(12):
        for j in range(12):
            if mapStat[i][j] == playerID:
                pos = Pos(i,j)
                for k in range(8):
                    farest_pos_in_the_direction = straight_line_end(mapStat,pos,Direction(dx[k],dy[k]))
                    if farest_pos_in_the_direction!=pos:
                        sheep_number_in_this_pos = sheepStat[pos.x][pos.y]
                        for n in range(1,int(sheep_number_in_this_pos)):
                            newActions.append(Action(pos,n,Direction(dx[k],dy[k])))

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

def GetStep(playerID, state: GameState):
    # step = [(0, 0), 0, 1]
    '''
    Write your code here
    
    '''
    mapStat = state.mapStat
    sheepStat = state.sheepStat
    actions = get_actions(playerID, state)
    max_value = -1000000
    for action in actions:
        pos = action.pos
        farest_pos_in_the_direction = straight_line_end(mapStat, pos, action.direction)
        newMapStat = deepcopy(mapStat)
        newSheepStat = deepcopy(sheepStat)
        newSheepStat[pos.x][pos.y] -= action.sheep_number
        newSheepStat[farest_pos_in_the_direction.x][farest_pos_in_the_direction.y] += action.sheep_number
        newMapStat[farest_pos_in_the_direction.x][farest_pos_in_the_direction.y] = playerID

        the_value = find_min_value(playerID, GameState(newMapStat,newSheepStat),-1000000,1000000,1)

        if the_value > max_value:
            max_value = the_value
            max_action = action

    step = [(max_action.pos.x,max_action.pos.y), max_action.sheep_number, max_action.direction.mapping()]

    return step


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
    Step = GetStep(playerID, GameState(mapStat, sheepStat)) # changed

    STcpClient.SendStep(id_package, Step)
