#Made by D&D Group 16, 2021

import pygame
import sys
import math
import os
import random 
import numpy as np
import queue
from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)




#Initiate map gui
pygame.init()
screen = pygame.display.set_mode((1080, 720))

#Tile Object for each tile in the Map
class Tile:
    #load in images

    #Anthony Code:
    images = [
        pygame.image.load("D:/Code/PYTHONSTUFF/RGuide/imgs/robot.jpg"),
        pygame.image.load("D:/Code/PYTHONSTUFF/RGuide/imgs/goal.png"),
    ]
    #General Code:
    #images = [
    #    pygame.image.load(".imgs/robot.jpg"),
    #    pygame.image.load(".imgs/goal.png"),
    #]

    def __init__(self, rowval, colval):
        self.unit = "empty"
        self.neighbors = []
        self.rowval = rowval
        self.colval = colval
        self.altitude = 0
        self.path = False
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
            if self.path == True:
                pygame.draw.rect(screen, (255-self.altitude * 16, 0, 0), (self.colval * w, self.rowval * w, w, w), 0)
            else:
                pygame.draw.rect(screen, (0, 0, 255-self.altitude * 16), (self.colval * w, self.rowval * w, w, w), 0)
        
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


    

    def setAltitudes(self): 
    #randomly creates altitudes for each tile

        #chooses starting tiles
        a = random.randint(0, self.side-1)
        b = random.randint(0, self.side-1)
        startTile = self.map[a][b]
        #assigns random altitude ranging from values from 3 to 12
        startTile.altitude = random.randint(3, 12)
        startTile.parsed = True
        #assigns altitudes to the rest of the map
        queue = []
        queue.append(startTile)
        tempAlt = startTile.altitude
        #BFS assigning
        while queue:
            #obtains tile from queue
            tile = queue.pop(0)
            #sets altitude of the tile
            increment = random.randint(-1, 1)
            if (tempAlt + increment < 0):
                tile.altitude = 0
                tempAlt = 0
            elif (tempAlt + increment > 15):
                tile.altitude = 15
                tempAlt = 15
            else:
                tile.altitude = tempAlt + increment
                tile.altitude = tempAlt + increment

            #appends neighbors to the queue
            for neighbor in tile.neighbors:
                if (neighbor.parsed == False):
                    queue.append(neighbor)
                    neighbor.parsed = True
            self.setNeighbors()
        
        #resets parsed boolean values
        for i in range(self.side):
            for j in range(self.side):
                self.map[i][j].parsed = False
        self.setNeighbors()



    def goalAbsence(self):
    #code used to determine when robot reaches goal
        for i in range(self.side):
            for j in range(self.side):
                if self.map[i][j].unit == "goal":
                    return False
        return True
    
    def showMapUnit(self, screen, i, j):
    #function used to refresh a tile on visualization
        self.map[i][j].show(screen, self.side, self.map[i][j].unit)

    

    #insert dijkstras here
    def dijkstra(self, sRow, sCol, dRow, dCol):
        #initiates distance and parent matrices
        distance = [[sys.maxsize for i in range(self.side)] for j in range(self.side)]
        parents = [[[-1,-1] for i in range(self.side)] for j in range(self.side)]
        
        #assigns start distance to 0 and adds first tile to priority queue
        #because tilequeue is priority queue, tiles that are closer to the goal will be parsed first
        distance[sRow][sCol] = 0
        tileQueue = queue.PriorityQueue()
        tileQueue.put(PrioritizedItem(abs(sRow-dRow) + abs(sCol-dCol) + 1, self.map[sRow][sCol]))
        self.map[sRow][sCol].parsed = True
        self.setNeighbors()
        #print("Tile Row: ")
        #print(sRow)
        #print(self.map[sRow][sCol].rowval)
        #print("Col: ")
        #print(sCol)
        #print(self.map[sRow][sCol].colval)

        #loops through all tile neighbors until reaching the point where there are no more tiles to check
        while not(tileQueue.empty()):
            #print("loop")
            cTile = tileQueue.get().item
            cTile = self.map[cTile.rowval][cTile.colval]
            
            #adjusts distance costs and previous tile for each neighbor of the parsed tile
            #main location for introducing weights
            for neighbor in cTile.neighbors:
                weight = neighbor.altitude - cTile.altitude + 2
                #ignores neighbors with an incompatible altitude difference
                if weight < 1 or weight > 3:
                    continue
                #out of all potential neighbors, assigns the parent of the tile to the most energy efficient tile
                if distance[neighbor.rowval][neighbor.colval] > distance[cTile.rowval][cTile.colval] + weight:
                    distance[neighbor.rowval][neighbor.colval] = distance[cTile.rowval][cTile.colval] + weight
                    parents[neighbor.rowval][neighbor.colval] = [cTile.rowval,cTile.colval]
                    #print("new distance/parent")

                #inserts each unparsed neighbor into the tileQueue
                if neighbor.parsed == False:
                    self.map[neighbor.rowval][neighbor.colval].parsed = True
                    tileQueue.put(PrioritizedItem(abs(neighbor.rowval-dRow) + abs(neighbor.colval-dCol) + 1, self.map[neighbor.rowval][neighbor.colval]))
            
            #print("Tile Row: ")
            #print(cTile.rowval)
            #print("Col: ")
            #print(cTile.colval)

            self.setNeighbors()
            print("looping")
        
        #resets parsed boolean values
        for i in range(self.side):
            for j in range(self.side):
                self.map[i][j].parsed = False
        

        self.setNeighbors()
        return parents



 


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
screen.blit(text2, (830, 80))

pygame.draw.rect(screen, (250,250,250), [800, 140, 200, 40])
text3 = font.render('New 20x20', True, (0,0,0))
screen.blit(text3, (830, 140))

pygame.draw.rect(screen, (250,250,250), [800, 200, 200, 40])
text4 = font.render('Dijkstra Find Path', True, (0,0,0))
screen.blit(text4, (830, 200))

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
    gcol = a // (720 // cols)
    grow = b // (720 // rows)
    tilePath = queue.LifoQueue()
    

    #First Click (select robot or advance robot)
    if selectSecond == False:

        #OPTION 1: create new 20 by 20 map
        if (a < 1000 and a > 800 and b < 180 and b > 140):
            newMapVisual(20)

        #OPTION 2: select unit
        elif (gcol < cols):
            unitSelected = MAP.map[grow][gcol]
            #tests if user clicks on the robot, or not
            if unitSelected.unit != "robot":
                print("invalid tile")
                return
            else:
                print("selected robot")
                selectSecond = True

                tilerect = pygame.Rect(gcol * h, grow * h, h, h)
                screen.fill((80, 80, 0), tilerect, pygame.BLEND_RGB_ADD)

                pygame.display.update()

        #OPTION 3: clicking advance robot
        elif (a < 1000 and a > 800 and b < 120 and b > 80):
            advanceOne = True

        #OPTION 4: clicking Dijkstra Path Find
        elif (a < 1000 and a > 800 and b < 240 and b > 200):
            #find the robot and store its values
            robotRow = -1
            robotCol = -1
            goalRow = -1
            goalCol = -1
            for i in range(MAP.side):
                for j in range(MAP.side):
                    if MAP.map[i][j].unit == "robot":
                        robotRow = i
                        robotCol = j
                    if MAP.map[i][j].unit == "goal":
                        goalRow = i
                        goalCol = j
            print(robotRow)
            print(robotCol)
            print(goalRow)
            print(goalCol)
            #calls the dijkstra method
            parents = MAP.dijkstra(robotRow,robotCol,goalRow,goalCol)
            print("got to this point")
            print(MAP.map[goalRow][goalCol].unit)
            print(MAP.map[goalRow][goalCol].rowval)
            print(MAP.map[goalRow][goalCol].colval)
            print("got to this point")
            print(parents[goalRow][goalCol][0])
            print(parents[goalRow][goalCol][1])
            
            #creates a variable to store the tile that is the parent of the goal tile
            tileInPath = MAP.map[parents[goalRow][goalCol][0]][parents[goalRow][goalCol][1]]
            #creates a queue to store the indexes of the goal tile, for use in "advance robot"
            tilePath.put([goalRow,goalCol])
            while True:
                
                print("Loop:retrieving path")
                #sets current tile to true, so that we will color it red
                MAP.map[tileInPath.rowval][tileInPath.colval].path = True
                #adds the current tile to the path queue
                tilePath.put([tileInPath.rowval,tileInPath.colval])
                #the next tile to be part of the path is the parent stored at the current tile
                tileInPath = MAP.map[parents[tileInPath.rowval][tileInPath.colval][0]][parents[tileInPath.rowval][tileInPath.colval][1]]

                #if we arrive at the robot's tile, we stop
                if parents[tileInPath.rowval][tileInPath.colval][0] == -1:
                    break


            
            for i in range(MAP.side):
                for j in range(MAP.side):
                    MAP.showMapUnit(screen, i, j)
            MAP.setNeighbors()
            print("-----------")
            #updates visualization
            pygame.display.update()

                



        #OPTION 5: clicking elsewhere
        else:
            print("invalid mouse press location")
            return
        



    #Second Click (choose destination of unit)
    else:
        if (gcol >= cols):
            selectSecond = False
            print("invalid destination")
            return

        destination = MAP.map[grow][gcol]
        #tests if destination is a neighbor;
        for neighbor in unitSelected.neighbors:
            if destination == neighbor:
                if ((unitSelected.altitude - neighbor.altitude) < 2 and (unitSelected.altitude - neighbor.altitude) > -2):
                    print("appropriate destination found")
                    validDestination = True
                else:
                    print("cannot traverse this high altitude difference")
                    return
        #returns to unit selection if invalid destination
        if validDestination == False:
            selectSecond = False
            print("invalid destination")
            MAP.showMapUnit(screen, grow, gcol)
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
        
        #removes tilePath queue
        while not(tilePath.empty()):
            tilePath.get()
        for i in range(cols):
            for j in range(rows):
                MAP.map[i][j].path = False

        MAP.setNeighbors()
        print("-----------")
        #updates visualization
        MAP.showMapUnit(screen, Drow, Dcol)
        MAP.showMapUnit(screen, Urow, Ucol)
        pygame.display.update()



#insert BFS here




    
end = False
#visualization loop
while True:
    if end:
        break
    ev = pygame.event.get()
    for event in ev:
        #Commands called when game is over
        if MAP.goalAbsence():
            print("Goal Reached")
            end = True
            break

        #MAIN FUNCTION FOR AGENT
        #to be coded/calls Dijkstra's and others 
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
