#Made by D&D Group 16, 2021

import pygame
import sys
import math
import os
import random 
import numpy as np
from queue import PriorityQueue

#Tile Object for each tile in the Map
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


#Map Class containing tiles indexed by row and column
class Map:
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

    def goalAbsence(self):
    #code used to determine when robot reaches goal
        for i in range(self.side):
            for j in range(self.side):
                if self.board[i][j].unit == "goal":
                    return False
        return True
    

 


pygame.init()
#Creating a Map object for visualization
screen = pygame.display.set_mode((1080, 720))

MAP = Map(18)
MAP.newBoard()
MAP.setPits()
MAP.setNeighbors()


cols = MAP.side
row = MAP.side
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
        showBoardUnit(screen, MAP.board, i, j)

selectSecond = False
validDestination = False

#CREATES BUTTON VISUALIZATION
font = pygame.font.Font('freesansbold.ttf', 20)

pygame.draw.rect(screen, (250,250,250), [800, 80, 200, 40])
text2 = font.render('Advance Robot', True, (0,0,0))
screen.blit(text2, (850, 80))

pygame.draw.rect(screen, (250,250,250), [800, 140, 200, 40])
text3 = font.render('New 9x9', True, (0,0,0))
screen.blit(text3, (850, 140))

pygame.display.update()






#variable used to store selected unit
unitSelected = MAP.board[0][0]

#variable used to store desired location
destination = MAP.board[0][0]

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
    global MAP
    global screen
    global cols
    global row
    global w
    global h
    a = x[0]
    b = x[1]
    g1 = a // (720 // cols)
    g2 = b // (720 // row)

    

    #First Click (select robot or advance robot)
    if selectSecond == False:

        #OPTION 1: create new 9 by 9 board
        if (a < 1000 and a > 800 and b < 180 and b > 140):
            MAP = Map(9)
            MAP.newBoard()
            MAP.setPits()
            MAP.setNeighbors()
            cols = MAP.side
            row = MAP.side
            w = 720 / cols
            h = 720 / row
            for i in range(cols):
                for j in range(row):
                    showBoardUnit(screen, MAP.board, i, j)
                    
            selectSecond = False
            validDestination = False
            unitSelected = MAP.board[0][0]
            destination = MAP.board[0][0]
            advanceOne = False
            
            pygame.draw.rect(screen, (0,0,0), [800, 320, 200, 360])
            pygame.display.update()

        #OPTION 2: select unit
        elif (g1 < cols):
            unitSelected = MAP.board[g1][g2]
            #tests if user clicks on the robot, or not
            if unitSelected.unit != "robot":
                print("invalid tile")
                return
            else:
                print("selected robot")
                selectSecond = True

                tilerect = pygame.Rect(g1 * h, g2 * h, h, h)
                screen.fill((80, 80, 0), tilerect, pygame.BLEND_RGB_ADD)

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


        destination = MAP.board[g1][g2]
        #tests if destination is a neighbor;
        for neighbor in unitSelected.neighbors:
            if destination == neighbor:
                print("appropriate destination found")
                validDestination = True
        #returns to unit selection if invalid destination
        if validDestination == False:
            selectSecond = False
            print("invalid destination")
            showBoardUnit(screen, MAP.board, g2, g1)
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
            print("robot has hit a pit")
            MAP.board[Urow][Ucol].unit = "empty"
        else: 
            MAP.board[Drow][Dcol].unit = "robot"
            MAP.board[Urow][Ucol].unit = "empty"
        

        MAP.setNeighbors()
        print("-----------")
        #updates visualization
        showBoardUnit(screen, MAP.board, Dcol, Drow)
        showBoardUnit(screen, MAP.board, Ucol, Urow)
        pygame.display.update()







""""
From this point on we are going to include the ai for the robot
""" 






    
#visualization loop
while True:
    ev = pygame.event.get()
    for event in ev:

        #Commands called when game is over
        if MAP.goalAbsence():
            print("Goal Reached")




        #MAIN FUNCTION FOR AGENT
        #to be coded
        if advanceOne:
            advanceOne = False









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
