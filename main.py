#Made by D&D Group 16, 2021

import pygame
import sys
import math
import os
import random 
import numpy as np
from queue import PriorityQueue

#Tile Object for each tile in the gameboard
class Tile:
    #load in images

    #Anthony Code:
    images = [
        pygame.image.load("C:/PYTHONSTUFF/RGuide/imgs/robot.jpg"),
        pygame.image.load("C:/PYTHONSTUFF/RGuide/imgs/goal.png"),
    ]

    #General Code:
    #images = [
    #    pygame.image.load("imgs/robot.jpg"),
    #    pygame.image.load("imgs/goal.png"),
    #]

    def __init__(self, rowval, colval):
        self.unit = "empty"
        self.neighbors = []
        self.rowval = rowval
        self.colval = colval
        self.img = self.images[0]

    #displays a single tile to the screen, depending on unit type
    def show(self, screen, color, w, h, unitType):
        if unitType == "robot":
            self.img = self.images[0]
            self.img = pygame.transform.scale(self.img, (int(w), int(h)))
            imageRect = self.img.get_rect()
            screen.blit(self.img, (self.colval * w, self.rowval * h), imageRect)
        if unitType == "goal":
            self.img = self.images[1]
            self.img = pygame.transform.scale(self.img, (int(w), int(h)))
            imageRect = self.img.get_rect()
            screen.blit(self.img, (self.colval * w, self.rowval * h), imageRect)
        if unitType == "empty":
            pygame.draw.rect(screen, color, (self.colval * w, self.rowval * h, w, h), 0)
        if unitType == "pit":
            pygame.draw.rect(screen, color, (self.colval * w, self.rowval * h, w, h), 0)
        
        pygame.draw.line(screen, (0,0,0), [self.colval * w, self.rowval*h], [self.colval * w + w, self.rowval*h], 1)
        pygame.draw.line(screen, (0,0,0), [self.colval * w, self.rowval*h], [self.colval * w, self.rowval*h + h], 1)
        pygame.display.update()


#Gameboard Class containing tiles indexed by row and column
class Gameboard:
    def __init__(self, side):
        self.side = side
        self.size = self.side * self.side

        #creates board 2D array of Tiles
        self.board = [[0 for i in range(self.side)] for j in range(self.side)]
        for i in range(self.side):
            for j in range(self.side):
                self.board[i][j] = Tile(i,j)

    #Randomly places the robot and goal on the map
    def newBoard(self):
        robotRow = random.randint(0, self.side-1)
        robotCol = random.randint(0, self.side-1)
        goalRow = random.randint(0, self.side-1)
        goalCol = random.randint(0, self.side-1)

        while (goalRow == robotRow and goalCol == robotCol):
            goalRow = random.randint(0, self.side-1)
            goalCol = random.randint(0, self.side-1)

        self.board[robotCol][robotRow].unit = "robot"
        self.board[goalCol][goalRow].unit = "goal"
        
    #creates pits
    def setPits(self):
        for i in range(0, self.side):
            #randomly chooses colomn val
            pitcol = random.randint(0, self.side-1)

            #cannot place pit on robot nor goal
            if (self.board[pitcol][i].unit == "empty"):
                self.board[pitcol][i].unit = "pit"
            

    #sets neighbors for all Tiles
    def setNeighbors(self):
        for i in range(self.side):
            for j in range(self.side):
                self.board[i][j].neighbors = []

                #goes through tiles diagonal and adjacent to the tile, and appends to neighbors list
                for k in range(-1, 2):
                    if (i+k < 0) or (i+k >= self.side):
                        continue
                    for l in range(-1, 2):
                        if (k == 0 and l == 0):
                            continue
                        if (j+l < 0) or (j+l >= self.side):
                            continue
                        self.board[i][j].neighbors.append(self.board[i + k][j + l])



    def position(self, value):
    #computes the index of value in the matrix interpreation of the array
        indx = math.floor(value/self.side)
        j = -indx*self.side + value
        if j >= 0:
            return [indx, j]
        return [-1, -1]

    def inv_position(self, i, j):
    #Converts position back to an array value
        if i >= self.side or i < 0:
            return -1
        if j >= self.side or j < 0:
            return -1
        return j + i * self.side

 


pygame.init()
#Creating a GameBoard object for visualization
screen = pygame.display.set_mode((1080, 720))

BOARD = Gameboard(9)
BOARD.newBoard()
BOARD.setPits()
BOARD.setNeighbors()


cols = BOARD.side
row = BOARD.side
w = 720 // cols
h = 720 // row

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)










#function used to refresh a tile on visualization
def showBoardUnit(screen, board, i, j):
    global w
    global h
    board[i][j].show(screen, (127,127,127), w, h, "empty")
    if board[j][i].unit == "robot":
        board[i][j].show(screen, red, w, h, "robot")
    if board[j][i].unit == "goal":
        board[i][j].show(screen, blue, w, h, "goal")
    if board[j][i].unit == "pit":
        board[i][j].show(screen, green, w, h, "pit")


#loops through entire board to create tiles
for i in range(cols):
    for j in range(row):
        showBoardUnit(screen, BOARD.board, i, j)

selectSecond = False
validDestination = False

#creates advance button, and 9 by 9 button
font = pygame.font.Font('freesansbold.ttf', 20)

pygame.draw.rect(screen, (250,250,250), [800, 80, 200, 40])
text2 = font.render('Advance Robot', True, (0,0,0))
screen.blit(text2, (850, 80))

pygame.draw.rect(screen, (250,250,250), [800, 140, 200, 40])
text3 = font.render('New 9x9', True, (0,0,0))
screen.blit(text3, (850, 140))

pygame.display.update()


#variable used to store selected unit
unitSelected = BOARD.board[0][0]

#variable used to store desired location
destination = BOARD.board[0][0]

#Initiates boolean for iterative robot movement
advanceOne = False

#This function is linked to the visualization loop
#when mouse clicks, selects player piece, or its desired location
def mousePress(x):
    global selectSecond
    global validDestination
    global advanceOne
    global unitSelected
    global destination
    global oneMoveOnly
    global BOARD
    global screen
    global cols
    global row
    global w
    global h
    a = x[0]
    b = x[1]
    g1 = a // (720 // cols)
    g2 = b // (720 // row)
    global prevTile

    

    #First Click (select robot or advance robot)
    if selectSecond == False:

        #OPTION 1: create new 9 by 9 board
        if (a < 1000 and a > 800 and b < 180 and b > 140):
            BOARD = Gameboard(9)
            BOARD.newBoard()
            BOARD.setPits()
            BOARD.setNeighbors()
            cols = BOARD.side
            row = BOARD.side
            w = 720 / cols
            h = 720 / row
            for i in range(cols):
                for j in range(row):
                    showBoardUnit(screen, BOARD.board, i, j)
                    
            selectSecond = False
            validDestination = False
            unitSelected = BOARD.board[0][0]
            destination = BOARD.board[0][0]
            advanceOne = False
            
            pygame.draw.rect(screen, (0,0,0), [800, 320, 200, 360])
            pygame.display.update()

        #OPTION 2: select unit
        elif (g1 < cols):
            unitSelected = BOARD.board[g1][g2]
            #tests if user clicks on the robot, or not
            if unitSelected.unit != "robot":
                print("invalid tile")
                return
            else:
                print("selected robot")
                selectSecond = True

                tilerect = pygame.Rect(g1 * h, g2 * h, h, h)
                screen.fill((80, 80, 0), tilerect, pygame.BLEND_RGB_ADD)
                prevTile = tilerect

                pygame.display.update()


        #OPTION 3: clicking advance robot
        elif (a < 1000 and a > 800 and b < 120 and b > 80):
            advanceOne = True



        #OPTION 4: clicking elsewhere
        else:
            print("invalid mouse press location")
            return
        



    #Second Click (choose destination of unit)
    else:
        if (g1 >= cols):
            selectSecond = False
            print("invalid destination")
            return


        destination = BOARD.board[g1][g2]
        #tests if destination is a neighbor;
        for neighbor in unitSelected.neighbors:
            if destination == neighbor:
                print("appropriate destination found")
                validDestination = True
        #returns to unit selection if invalid destination
        if validDestination == False:
            selectSecond = False
            print("invalid destination")
            showBoardUnit(screen, BOARD.board, g2, g1)
            return

        #resets booleans and obtains indices
        validDestination = False
        selectSecond = False
        Drow = destination.rowval
        Dcol = destination.colval
        Urow = unitSelected.rowval
        Ucol = unitSelected.colval

        #checks if destination is pit
        if destination.unit == "pit":
            print("you hit a pit")
            BOARD.board[Urow][Ucol].unit = "empty"
        else: 
            BOARD.board[Drow][Dcol].unit = "robot"
            BOARD.board[Urow][Ucol].unit = "empty"
        

        BOARD.setNeighbors()
        print("-----------")
        #updates visualization
        showBoardUnit(screen, BOARD.board, Dcol, Drow)
        showBoardUnit(screen, BOARD.board, Ucol, Urow)
        pygame.display.update()






""""
From this point on we are going to include the ai for the robot
""" 

def goalAbsence(GB):
    for i in range(GB.side):
        for j in range(GB.side):
            if GB.board[i][j].unit == "goal":
                return False
    return True
    

def get_pieces(GB, p_type):
    
    p_loc = [None]*0
    
    if p_type == "all":
        for i in range(GB.side):
            for j in range(GB.side):
                if GB.board[i][j].player == "agent":
                    p_loc.append(GB.board[i][j])
        
    else:
        for i in range(GB.side):
            for j in range(GB.side):
                if GB.board[i][j].player == "agent":
                    if GB.board[i][j].unit == p_type:
                        p_loc.append(GB.board[i][j])
    
    if(len(p_loc)==0):
        return None
    else: 
        return p_loc 
    
def get_ADV_pieces(GB,p_type): 
    p_loc = [None]*0
    for i in range(GB.side):
            for j in range(GB.side):
                if GB.board[i][j].player == "adversary":
                    if GB.board[i][j].unit == p_type:
                        #print(GB.board[i][j].player)
                        p_loc.append(GB.board[i][j]) 
    
    return p_loc
    

def win_matchup(p_type):
    if p_type == "mage":
        return "hero"
    elif p_type == "hero":
        return "wumpus"
    else:
        return "mage"

def euclid_dist(p1,p2):
    return  np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def closest_m(GB, pos, m_type):
    if m_type == "win": 
        #w_m = [ euclid_dist([pos.rowval,pos.colval],[p.rowval,p.colval]) 
        #for p in get_pieces(GB,win_matchup(pos.unit)) ]  
        w_m = [None]*0
        for p in get_ADV_pieces(GB,win_matchup(pos.unit)): 
            w_m.append(euclid_dist([pos.rowval,pos.colval],[p.rowval,p.colval]))
        print(pos.unit)
        for item in get_ADV_pieces(GB,win_matchup(pos.unit)):
            print([item.rowval,item.colval])
        print("\n")  
        return  min(w_m)
            
    else: 
        d_m = [ euclid_dist([pos.rowval,pos.colval],[p.rowval,p.colval]) 
        for p in get_pieces(GB,pos.unit) ]
        return min(d_m) 


def static_eval(GB,position): 
    
    return closest_m(GB,position,"win")
    #return random.randint(1,100)

def minimax(GB,position, tree_depth, maximizingPlayer):
     if tree_depth == 0 :#or goal(position,p_type):  
         #print(static_eval(GB,position)) 
         print(static_eval(GB,position))
         return static_eval(GB, position), position #static evaluation
     if maximizingPlayer:
         MaxOut = -math.inf
         p_moves = position.neighbors
         bestMove = position
         for move in p_moves:
             if move.player != "agent":
                bestMove = move 
        #print("Made it here")
         for move in p_moves:  # all spaces within one move of current pos
             if move.unit == "pit" or move.player == "agent":
                 #print("this aint good" + move.player + " " + move.unit)
                 continue    
             hold = move.unit 
             GB.board[move.rowval][move.colval].unit  = position.unit
             currEval, bs = minimax(GB,GB.board[move.rowval][move.colval]
             , tree_depth - 1, False) 
             GB.board[move.rowval][move.colval].unit = hold
             
             if MaxOut < currEval:
                 #print("Maxout "+str(MaxOut) + "currEval "+ str(currEval)) 
                 #print("Move " + str([move.rowval,move.colval]))
                 bestMove = move
                 MaxOut = currEval 
                #if tree_depth == 5: 
             #    return MaxOut, bestMove
            #MaxOut = max(MaxOut,currEval)
         return MaxOut, bestMove
     
     else: 
         MinOut = math.inf
         p_moves = position.neighbors
         bestMove = position
         for move in p_moves:
             if move.player != "agent":
                bestMove = move
         for move in p_moves:
             if move.unit == "pit" or move.player == "agent":
                 continue
             hold = move.unit 
             GB.board[move.rowval][move.colval].unit  = position.unit
             currEval, bs = minimax(GB,GB.board[move.rowval][move.colval] 
              , tree_depth - 1, True)
             GB.board[move.rowval][move.colval].unit = hold
             
             if MinOut > currEval:
                 bestMove = move
                 MinOut = currEval
             #MinOut = min(MinOut,currEval)
         return MinOut, GB.board[bestMove.rowval][bestMove.colval]

def alphaBetaPruning(GB, position, tree_depth, alpha, beta, maximizingPlayer):
     if tree_depth == 0 :#or goal(position,p_type):  
         return static_eval(GB, position), position #static evaluation
     if maximizingPlayer:
         value = -math.inf
         p_moves = position.neighbors
         bestMove = position
         for move in p_moves:
             if move.player != "agent":
                bestMove = move
         for move in p_moves: # all spaces within one move of current pos
             if move.unit == "pit" or move.player == "agent":
                 continue   
             hold = move.unit 
             GB.board[move.rowval][move.colval].unit  = position.unit
             currEval, bs = alphaBetaPruning(GB,GB.board[move.rowval][move.colval]
             , tree_depth - 1, alpha, beta, False) 
             GB.board[move.rowval][move.colval].unit = hold
             if value < currEval:
                 bestMove = move
                 value = currEval 
             alpha = max(alpha,value) 
             #MAIN CRUCIAL CHECK HERE!
             if beta <= alpha:
                 print("I made it here maximizingPlayer")
                 break
         return value, bestMove
     
     else: 
         value = math.inf
         p_moves = position.neighbors
         bestMove = position
         for move in p_moves:
             if move.player != "agent":
                bestMove = move 
         for move in p_moves:
             if move.unit == "pit" or move.player == "agent":
                 continue
             hold = move.unit 
             GB.board[move.rowval][move.colval].unit  = position.unit   
             currEval, bs = alphaBetaPruning(GB,GB.board[move.rowval][move.colval] 
             , tree_depth - 1, alpha, beta, True)
             GB.board[move.rowval][move.colval].unit = hold
             if value > currEval:
                 bestMove = move
                 value = currEval
             beta  = min(beta, value)
             #DON'T CHECK IF BETA <= ALPHA
             if beta <= alpha:
                 print("I made it here minimizingPlayer")
                 break
         return value, bestMove

def alphaBetaPruningPQ(GB, position, tree_depth, alpha, beta, maximizingPlayer):
     if tree_depth == 0 :#or goal(position,p_type):  
         return static_eval(GB, position), position #static evaluation
     if maximizingPlayer:
        value = -math.inf
        p_moves = position.neighbors
        bestMove = position
        for move in p_moves:
            if move.player != "agent":
                bestMove = move
        pqueue = PriorityQueue()
        for move in p_moves:
            pqueue.put(-static_eval(GB, move), move)
        while not pqueue.empty(): 
            #print("Look HERE")
            #print(pqueue.get())
            move = pqueue.get()
            if move.unit == "pit" or move.player == "agent":
                continue   
            hold = move.unit 
            GB.board[move.rowval][move.colval].unit  = position.unit
            currEval, bs = alphaBetaPruning(GB,GB.board[move.rowval][move.colval]
            , tree_depth - 1, alpha, beta, False) 
            GB.board[move.rowval][move.colval].unit = hold
            if value < currEval:
                bestMove = move
                value = currEval 
            alpha = max(alpha,value) 
            #MAIN CRUCIAL CHECK HERE!
            if beta <= alpha:
                print("I made it here maximizingPlayer")
                break
        return value, bestMove
     
     else: 
         value = math.inf
         p_moves = position.neighbors
         bestMove = position
         for move in p_moves:
             if move.player != "agent":
                bestMove = move 
         pqueue = PriorityQueue()
         for move in p_moves:
            pqueue.put(static_eval(GB, move), move)       
         while not pqueue.empty():
             move = pqueue.get()
             if move.unit == "pit" or move.player == "agent":
                 continue
             hold = move.unit 
             GB.board[move.rowval][move.colval].unit  = position.unit   
             currEval, bs = alphaBetaPruning(GB,GB.board[move.rowval][move.colval] 
             , tree_depth - 1, alpha, beta, True)
             GB.board[move.rowval][move.colval].unit = hold
             if value > currEval:
                 bestMove = move
                 value = currEval
             beta  = min(beta, value)
             #DON'T CHECK IF BETA <= ALPHA
             if beta <= alpha:
                 print("I made it here minimizingPlayer")
                 break
         return value, bestMove

def printArr(a, n):
	for i in range(n):
		print(a[i], end=" ")
	print()
 
# Generating permutation using Heap Algorithm
def heapPermutation(a, size, n):
    # if size becomes 1 then prints the obtained
    # permutation
    if (size == 1):
        printArr(a, n)
        return 
    for i in range(size):
        heapPermutation(a, size-1, n)
 
        # if size is odd, swap 0th i.e (first) 
        # and (size-1)th i.e (last) element
        # else If size is even, swap ith 
        # and (size-1)th i.e (last) element
        if size & 1:
            a[0], a[size-1] = a[size-1], a[0]
        else:
            a[i], a[size-1] = a[size-1], a[i]

#visualization loop
while True:
    ev = pygame.event.get()
    for event in ev:

        #Commands called when game is over
        if goalAbsence(BOARD):
            print("Goal Reached")



        #MAIN FUNCTION FOR AGENT

        if advanceOne:
            advanceOne = False
            #the unit(string value) that beats the piece that was just moved
            #pToMove = win_matchup(destination.unit) 
            #possiblePieces = get_pieces(BOARD, pToMove)
            possiblePieces = get_pieces(BOARD,"all") 
            pToMove = random.randrange(len(possiblePieces))
            while True:
                check = False
                for neighbor in possiblePieces[pToMove].neighbors:
                    if neighbor.player != "agent":
                        check = True
                if check == False:
                    pToMove = random.randrange(len(possiblePieces))
                else:
                    break
        
            #dummyVariable, destination = minimax(BOARD, possiblePieces[pToMove] 
            #, 6, True)
            #dummyVariable, destination = alphaBetaPruningPQ(BOARD, possiblePieces[pToMove] 
            #, 3, 0, 0, True)
            unitSelected = possiblePieces[pToMove] 
            #print("output from minimax"+ str(dummyVariable))
            print("final move"+ str([destination.rowval,destination.colval]))
            Drow = destination.rowval
            Dcol = destination.colval
            Urow = unitSelected.rowval
            Ucol = unitSelected.colval
            
            mp = "winning"
            if destination.player == "adversary":
                if destination.unit == unitSelected.unit:
                    mp = "even"
                if destination.unit == "hero" and unitSelected.unit == "wumpus": 
                    mp = "losing"
                if destination.unit == "wumpus" and unitSelected.unit == "mage": 
                    mp = "losing"
                if destination.unit == "mage" and unitSelected.unit == "hero": 
                    mp = "losing"

            #changes board according to action
            if mp == "even":
                BOARD.board[Drow][Dcol].player = "neutral"
                BOARD.board[Drow][Dcol].unit = "empty"
                BOARD.board[Urow][Ucol].player= "neutral"
                BOARD.board[Urow][Ucol].unit = "empty"
            elif mp == "losing":
                BOARD.board[Urow][Ucol].player= "neutral"
                BOARD.board[Urow][Ucol].unit = "empty"
            else:
                BOARD.board[Drow][Dcol].player = "agent"
                BOARD.board[Drow][Dcol].unit = unitSelected.unit
                BOARD.board[Urow][Ucol].player= "neutral"
                BOARD.board[Urow][Ucol].unit = "empty"
            

            BOARD.setNeighbors()
            #updates visualization
            showBoardUnit(screen, BOARD.board, Dcol, Drow)
            showBoardUnit(screen, BOARD.board, Ucol, Urow)
            pygame.display.update()









        #Extraneous code
        if event.type == pygame.QUIT:
            pygame.display.quit()


        #MAIN FUNCTION FOR MOUSE CLICKING
        if pygame.mouse.get_pressed()[0]:
            try:
                pos = pygame.mouse.get_pos()
                mousePress(pos)
            except AttributeError:
                pass

        #Extraneous code
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                loop = False
                break
