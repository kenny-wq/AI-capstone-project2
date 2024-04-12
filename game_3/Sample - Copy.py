import STcpClient
import numpy as np
import random

'''
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=[x,y],代表起始位置
    
    Select starting position
    Selection is limited to site edges (walls in at least one direction)

    return: init_pos
    init_pos=[x,y], represents the starting position
'''


def InitPos(mapStat):
    init_pos = [0, 0]
    '''
        Write your code here

    '''
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
            4 X 6
            7 8 9

    Output instructions
    
    input:
    playerID: your role in this game (1~4)
    mapStat: chessboard status (list of list), 12*12 matrix,
            0=movable area, -1=obstacle, 1~4 are areas occupied by players 1~4
    sheepStat: sheep distribution status, ranging from 0 to 16, 12*12 matrix

    return Step
    Step: 3 elements, [(x,y), m, dir]
            x, y represent the coordinates of the action to be performed
            m = number of sheep to be cut into the second flock
            dir = moving direction (1~9), the corresponding direction is as shown in the figure below
            1 2 3
            4 X 6
            7 8 9
'''


def GetStep(playerID, mapStat, sheepStat):
    step = [(0, 0), 0, 1]
    '''
    Write your code here
    
    '''
    return step


# player initial
(id_package, playerID, mapStat) = STcpClient.GetMap()
init_pos = InitPos(mapStat)
STcpClient.SendInitPos(id_package, init_pos)

# start game
while (True):
    (end_program, id_package, mapStat, sheepStat) = STcpClient.GetBoard()
    sheepStat = np.where(mapStat == playerID, sheepStat, 0) # hide other player's sheep number
    # hide other player's sheep number
    if end_program:
        STcpClient._StopConnect()
        break
    Step = GetStep(playerID, mapStat, sheepStat)

    STcpClient.SendStep(id_package, Step)
# DON'T MODIFY ANYTHING IN THIS WHILE LOOP OR YOU WILL GET 0 POINT IN THIS QUESTION