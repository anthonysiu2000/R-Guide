#Made by D&D Group 16, 2021

import pygame
import sys
import math
import os
import random 
import numpy as np
from queue import PriorityQueue


#Initiate map gui
pygame.init()
screen = pygame.display.set_mode((1080, 720))

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
        self.altitude = 0
        self.parsed = False
        self.img = self.images[0]

    #displays a single tile to the screen, depending on unit type
    def show(self, screen, side, unitType):
        w = 720 / side
        if unitType == "robot":
            self.img = self.images[0]
            self.img = pygame.transform.scale(self.img, (int(w), int(w)))
            imageRect = self.img.get_rect()
            screen.blit(self.img, (self.colval * w, self.rowval * w), imageRect)
        if unitType == "goal":
            self.img = self.images[1]
            self.img = pygame.transform.scale(self.img, (int(w), int(w)))
            imageRect = self.img.get_rect()
            screen.blit(self.img, (self.colval * w, self.rowval * w), imageRect)
        if unitType == "empty":
            pygame.draw.rect(screen, (0, 0, 255-self.altitude * 16), (self.colval * w, self.rowval * w, w, w), 0)
        if unitType == "pit":
            pygame.draw.rect(screen, (0, 255, 0), (self.colval * w, self.rowval * w, w, w), 0)
        
        pygame.draw.line(screen, (0,0,0), [self.colval * w, self.rowval * w], [self.colval * w + w, self.rowval * w], 1)
        pygame.draw.line(screen, (0,0,0), [self.colval * w, self.rowval * w], [self.colval * w, self.rowval * w + w], 1)
        pygame.display.update()


#Map Class containing tiles indexed by row and column
class Map:
    def __init__(self, side):
        self.side = side
        self.size = self.side * self.side

        #creates map 2D array of Tiles
        self.map = [[0 for i in range(self.side)] for j in range(self.side)]
        for i in range(self.side):
            for j in range(self.side):
                self.map[i][j] = Tile(i,j)

    #Randomly places the robot and goal on the map
    def newMap(self):
        robotRow = random.randint(0, self.side-1)
        robotCol = random.randint(0, self.side-1)
        goalRow = random.randint(0, self.side-1)
        goalCol = random.randint(0, self.side-1)

        while (goalRow == robotRow and goalCol == robotCol):
            goalRow = random.randint(0, self.side-1)
            goalCol = random.randint(0, self.side-1)

        self.map[robotCol][robotRow].unit = "robot"
        self.map[goalCol][goalRow].unit = "goal"
        
    #creates pits
    def setPits(self):
        for i in range(0, self.side):
            #randomly chooses colomn val
            pitcol = random.randint(0, self.side-1)

            #cannot place pit on robot nor goal
            if (self.map[pitcol][i].unit == "empty"):
                self.map[pitcol][i].unit = "pit"
            

    #sets neighbors for all Tiles
    def setNeighbors(self):
        for i in range(self.side):
            for j in range(self.side):
                self.map[i][j].neighbors = []

                #goes through tiles diagonal and adjacent to the tile, and appends to neighbors list
                for k in range(-1, 2):
                    if (i+k < 0) or (i+k >= self.side):
                        continue
                    for l in range(-1, 2):
                        if (k == 0 and l == 0):
                            continue
                        if (j+l < 0) or (j+l >= self.side):
                            continue
                        self.map[i][j].neighbors.append(self.map[i + k][j + l])


    #recursive method to assign altitudes to neighboring tiles
    def recursiveSetAltitude(self, tile):
        for neighbor in tile.neighbors:
            if (neighbor.parsed == True):
                continue

            #sets altitude of the neighbor
            increment = random.randint(-1, 1)
            if (tile.altitude + increment < 0):
                neighbor.altitude = 0
            elif (tile.altitude + increment > 15):
                neighbor.altitude = 15
            else:
                neighbor.altitude = tile.altitude + increment
                
            #sets boolean so we not repeat neighbors
            neighbor.parsed = True

            #recursion
            self.recursiveSetAltitude(neighbor)
        return


    def setAltitudes(self): 
    #randomly creates altitudes for each tile

        #chooses starting tiles
        a = random.randint(0, self.side-1)
        b = random.randint(0, self.side-1)
        starttile = self.map[a][b]
            #assigns random altitude ranging from values from 3 to 12
        starttile.altitude = random.randint(3, 12)
        starttile.parsed = True
            #assigns altitudes to the rest of the map
        self.recursiveSetAltitude(starttile)



        
        #resets parsed boolean values
        for i in range(self.side):
            for j in range(self.side):
                self.map[i][j].parsed = False




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
                if self.map[i][j].unit == "goal":
                    return False
        return True
    
    def showMapUnit(self, screen, i, j):
    #function used to refresh a tile on visualization
        self.map[i][j].show(screen, self.side, self.map[j][i].unit)

 


#Creating a Map object for visualization
MAP = Map(1)

#boolean used to determine which ordinal mouse click we are on
selectSecond = False

#boolean used to determine if robot chooses a tile that is possible to move to
validDestination = False

#variable used to store selected unit
unitSelected = MAP.map[0][0]

#variable used to store desired location
destination = MAP.map[0][0]

#Initiates boolean for iterative robot movement
advanceOne = False



#function to create a brand new map visualization
def newMapVisual(dimension):
    global MAP
    global selectSecond
    global validDestination
    global unitSelected
    global destination
    global advanceOne
    MAP = Map(dimension)
    MAP.newMap()
    MAP.setNeighbors()
    MAP.setAltitudes()
    for i in range(MAP.side):
        for j in range(MAP.side):
            MAP.showMapUnit(screen, i, j)
            
    selectSecond = False
    validDestination = False
    unitSelected = MAP.map[0][0]
    destination = MAP.map[0][0]
    advanceOne = False
         
    pygame.draw.rect(screen, (0,0,0), [800, 320, 200, 360])
    pygame.display.update()



#Initializing the map for visualization
newMapVisual(20)

#CREATES BUTTON VISUALIZATION on the right side of the screen
font = pygame.font.Font('freesansbold.ttf', 20)

pygame.draw.rect(screen, (250,250,250), [800, 80, 200, 40])
text2 = font.render('Advance Robot', True, (0,0,0))
screen.blit(text2, (850, 80))

pygame.draw.rect(screen, (250,250,250), [800, 140, 200, 40])
text3 = font.render('New 20x20', True, (0,0,0))
screen.blit(text3, (850, 140))

pygame.display.update()





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
    cols = MAP.side
    rows = MAP.side
    w = 720 / cols
    h = 720 / rows
    a = x[0]
    b = x[1]
    g1 = a // (720 // cols)
    g2 = b // (720 // rows)

    

    #First Click (select robot or advance robot)
    if selectSecond == False:

        #OPTION 1: create new 20 by 20 map
        if (a < 1000 and a > 800 and b < 180 and b > 140):
            newMapVisual(20)




        #OPTION 2: select unit
        elif (g1 < cols):
            unitSelected = MAP.map[g1][g2]
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


        destination = MAP.map[g1][g2]
        #tests if destination is a neighbor;
        for neighbor in unitSelected.neighbors:
            if destination == neighbor:
                print("appropriate destination found")
                validDestination = True
        #returns to unit selection if invalid destination
        if validDestination == False:
            selectSecond = False
            print("invalid destination")
            MAP.showMapUnit(screen, g2, g1)
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
            MAP.map[Urow][Ucol].unit = "empty"
        else: 
            MAP.map[Drow][Dcol].unit = "robot"
            MAP.map[Urow][Ucol].unit = "empty"
        

        MAP.setNeighbors()
        print("-----------")
        #updates visualization
        MAP.showMapUnit(screen, Dcol, Drow)
        MAP.showMapUnit(screen, Ucol, Urow)
        pygame.display.update()







""""
From this point on we are going to include the ai for the robot
""" 

#insert dijkstras here




    
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
