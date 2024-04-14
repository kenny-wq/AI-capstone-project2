# Team Name: Eevee Lovers
# Team ID: 10
### MEMBERS ###
# 陳清海 0816199
# 范恩宇 109550135
# 李耕雨 109550055

#python -m PyInstaller --onefile team10_agent4.py --name Sample_4.exe

import STcpClient
import numpy as np
import random
from copy import deepcopy
import math
import time

start_time = time.time()

class GameState:
    def __init__(self, mapStat, sheepStat):
        self.mapStat = mapStat
        self.sheepStat = sheepStat

'''
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
            4 X 5
            7 8 9
'''
class GameSimulation:
    def __init__(self, board_size=12):
        self.board_size = board_size

    def reverse_pos(self, pos):
        x, y = pos
        return (y, x)

    # reverse direction of the action, but x&y be the same
    def reverse_action(self, action):
        direcs = {1: 1, 2: 4, 3: 7, 4: 2, 6: 8, 7: 3, 8: 6, 9: 9}
        x, y = action[0]
        m = action[1]
        dir = action[2]

        newx, newy = x, y
        newdir = direcs[dir]
        return [(newx, newy), m, newdir]

    # directions that are possible
    def dir_possible(self):
        # center = 5
        return [1, 2, 3, 4, 6, 7, 8, 9]

    # mapping directions
    def dir_value(self, dir):
        direction_map = {
            1: (-1, -1), 2: (-1, 0), 3: (-1, 1), 4: (0, -1),
            6: (0, 1),   7: (1, -1), 8: (1, 0),  9: (1, 1)
        }
        return direction_map[dir]

    # check if initial pos is valid
    def init_pos_valid(self, mapStat, init_pos): 
        x, y = init_pos
        if mapStat[x][y] != 0:
            return False

        map_expanded = np.pad(mapStat.copy(), pad_width=1, mode='constant', constant_values=0)
        window = map_expanded[x:x+3, y:y+3]
        return np.any(window == -1)

    # check if pos is within bound
    def bound_valid(self, x, y, board_size):
        if x >= 0 and x < board_size and y >= 0 and y < board_size :
            return 1 

    def set_init_pos(self, mapStat, board_size=12):
        realm = [
            (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
            (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
            (0, -2),  (0, -1),           (0, 1),  (0, 2),
            (1, -2),  (1, -1),  (1, 0),  (1, 1),  (1, 2),
            (2, -2),  (2, -1),  (2, 0),  (2, 1),  (2, 2)
        ]

        max_ct = -1
        best_init = [0, 0]

        for i in range(board_size):
            for j in range(board_size):
                init_pos = [i, j]
                if not self.init_pos_valid(mapStat, init_pos):
                    continue
                ct = 0

                for dx, dy in realm:
                    nx, ny = init_pos[0] + dx, init_pos[1] + dy
                    if self.bound_valid(nx, ny, board_size) and mapStat[nx][ny] == 0:
                        ct += 1

                if ct > max_ct:
                    best_init = init_pos
                    max_ct = ct

        return best_init

    # check direction when reach boundary of the map / hit something not 0
    def straight_line_end(self, x, y, dir, mapStat):
        dx, dy = self.dir_value(dir)
        while True:
            if not (0 <= x + dx < len(mapStat) and 0 <= y + dy < len(mapStat[0])):
                break

            if mapStat[x + dx][y + dy] != 0:
                break

            x += dx
            y += dy
        return (x, y)

    # apply action to get new states
    def getChildStates(self, state, action):
        playerID, mapStat, sheepStat = state
        newMapStat = deepcopy(mapStat)
        newSheepStat = deepcopy(sheepStat)
        
        x, y = action[0]
        m = action[1]
        dir = action[2]

        newx, newy = self.straight_line_end(x, y, dir, mapStat)
        # update map & sheep state, playerID
        newMapStat[newx][newy] = playerID
        newSheepStat[x][y] -= m
        newSheepStat[newx][newy] = m
        newPlayerID = playerID % 4 + 1

        return (newPlayerID, newMapStat, newSheepStat)

    # get possible space to move
    def remain_space(self, state):
        playerID, mapStat, sheepStat = state
        actions = []
        height, width = len(mapStat), len(mapStat[0])
        # find all splitable sheep group and add their index into a list
        sheep_splitable = []
        for i in range(height):
            for j in range(width):
                if mapStat[i][j] == playerID and int(sheepStat[i][j]) > 1:
                    sheep_splitable.append((i, j))
        for i, j in sheep_splitable:
            for dir in self.dir_possible():
                newx, newy = self.straight_line_end(i, j, dir, mapStat)
                if newx == i and newy == j:
                    continue
                m = int(sheepStat[i][j]) // 2
                actions.append([(i, j), m, dir])
        return actions

    # check if state still have space to move
    def is_leaf(self, state):
        return not self.remain_space(state)

    # check if game ends
    def game_end(self, state):
        for i in range(1, 5):
            if self.remain_space((i, state[1], state[2])):
                return False
            
        return True

    def dfs(self, mapStat, playerID, visited, i, j):
        if i < 0 or i >= self.board_size or j < 0 or j >= self.board_size or visited[i][j] or mapStat[i][j] != playerID:
            return 0
        visited[i][j] = True
        #i-1, i+1, j-1, j+1
        return 1 + self.dfs(mapStat, playerID, visited, i - 1, j) \
                    + self.dfs(mapStat, playerID, visited, i + 1, j) \
                    + self.dfs(mapStat, playerID, visited, i, j - 1) \
                    + self.dfs(mapStat, playerID, visited, i, j + 1)

    def get_connected_cell(self, mapStat, playerID):
        connected_cell = []
        visited = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
        for i in range(self.board_size):
            for j in range(self.board_size):
                # go through cells connected but unvisited
                if mapStat[i][j] == playerID and not visited[i][j]:
                    connected_cell.append(self.dfs(mapStat, playerID, visited, i, j))
        return connected_cell

    def get_score(self, state):
        playerID, mapStat, sheepStat = state
        cells = self.get_connected_cell(mapStat, playerID)
        return round(sum([cell ** 1.25 for cell in cells]))

    def get_winner_group(self, state):
        scores = [self.get_score((i, state[1], state[2])) for i in range(1, 5)]
        if scores[0] + scores[2] > scores[1] + scores[3]:
            return 1
        else:
            return 2

###################################--MCTS--###################################

class Node:
    def __init__(self, state, action=None, parent=None):
        self.state = state    # current player of the node
        self.action = action  # how to move from parent to here
        self.parent = parent
        self.children = []
        self.visit_time = 0   # times this position was visited
        self.reward = 0       # average reward (wins-losses) from this position

class Tree:
    def __init__(self, state):
        self.root = Node(state)

class UctMctsAgent:
    def __init__(self, state, rule_id):
        self.tree = Tree(state)
        self.playerID = state[0]
        self.rule_id = rule_id
        self.node_ct = 250                        # number of search iterations
        self.game_simulation = GameSimulation(12) # for changing size if needed

    def select_node(self, node):
        while node.children:
            node = max(node.children, key=lambda n: self.ucb(n))
        return node

    def add_child(self, node):
        actions = self.game_simulation.remain_space(node.state)#self.remain_space(node.state)
        for action in actions:
            new_states = self.game_simulation.getChildStates(node.state, action)
            new_node = Node(new_states, action, node)
            node.children.append(new_node)

    # simulate game process
    def game_process(self, state):
        while not self.game_simulation.game_end(state):
            actions = self.game_simulation.remain_space(state)
            if not actions:
                state = (state[0] % 4 + 1, state[1], state[2])
                continue

            action = random.choice(actions)
            state = self.game_simulation.getChildStates(state, action)

        # team up 1+3 & 2+4, self.rule_id == 4
        group_pair = 1
        if self.playerID == 1 or self.playerID == 3:
            group_pair = 1    
        else: 
            group_pair = 2
        winner_group = self.game_simulation.get_winner_group(state)

        if group_pair == winner_group:
            return 1
        else:
            return -1

    # backpropagation, calculate the reward for player who just played at the node 
    def back_pg(self, node, reward):
        while node:
            node.visit_time += 1
            node.reward += reward
            node = node.parent

    def ucb(self, node):
        if node.visit_time == 0:
            return float('inf')
        return node.reward / node.visit_time + (2 * np.log(node.parent.visit_time) / node.visit_time) ** 0.5

    def best_move(self):
        # find cell with more spaces around the starting point
        root = self.tree.root
        for _ in range(self.node_ct):
            target = self.select_node(root)
            if target.children is not None:#
                self.add_child(target)

            added_node = target 
            if self.game_simulation.is_leaf(target.state):
                added_node = target 
            else:
                added_node = random.choice(target.children)
            reward = self.game_process(added_node.state)
            self.back_pg(added_node, reward)

        best_child = max(root.children, key=lambda n: n.visit_time) # node with most visit time should be the best choice
        return best_child.action
    
'''
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=[x,y],代表起始位置
    
'''

def InitPos(mapStat):
    init_pos = GameSimulation().set_init_pos(mapStat)
    init_pos = GameSimulation().reverse_pos(init_pos) # backpropagation
    return init_pos

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
            4 X 5
            7 8 9
'''
def GetStep(playerID, mapStat, sheepStat):
    #mapStat = state.mapStat
    #sheepStat = state.sheepStat
    uct_mcts = UctMctsAgent((playerID, mapStat, sheepStat), 4)

    actions = uct_mcts.best_move()
    actions = GameSimulation().reverse_action(actions)
    return actions

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
