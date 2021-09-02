import pygame
import math
from queue import PriorityQueue

#Setting up the fixed display 
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Pathfinding Visualizer")

#Color Coded for PyGame UI
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQOISE = (64, 224, 208)

#Creating a class for each little square in the grid with functions to dynamically update
#the node
class Node:
   
    #Constructor for Node Class
    def __init__(self, row, col, width, totalRows):
        self.row = row
        self.col = col
        #To track the X and Y Positions to get actual width size of nodes
        self.x = row * width
        self.y = col * width
        #Colors of normal nodes are just white
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.totalRows = totalRows
    
    #Finding the position of the current node
    def get_pos(self):
        return self.row, self.col

    #Checking if node is closed
    def is_closed(self):
        return self.color == RED

    #Checking if node is available to check
    def is_open(self):
        return self.color == GREEN
    
    #Checking if node is a wall / barrier
    def is_barrier(self):
        return self.color == BLACK

    #Checking if the node is a start node
    def is_start(self):
        return self.color == ORANGE

    #Checking if the node is an end node
    def is_end(self):
        return self.color == TURQOISE

    #Changing the node back to a default state
    def reset(self):
        self.color = WHITE

    #Changing node to a start node
    def make_start(self):
        self.color = ORANGE

    #Changing node to a visited node
    def make_closed(self):
        self.color = RED

    #Changing node to an unvisited node
    def make_open(self):
        self.color = GREEN
    
    #Changing node to a wall / barrier
    def make_barrier(self):
        self.color = BLACK

    #Changing node to an end node
    def make_end(self):
        self.color = TURQOISE

    #Changing nodes to a pathway
    def make_path(self):
        self.color = PURPLE
    
    #Drawing actual nodes into the screen
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        #Checking if able to move down
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        #Checking if able to move Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        #Checking if able to move Right
        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        #Checking if able to move Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
    #Comparing other nodes to neighboring nodes
    def __lt__(self, other):
        return False

#Heuristic Function utilizing Manhattan Distance (Taxicab Distance)
#p1 = Point 1
#p2 = Point 2
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

#Constructing the nodes taken to go from start to end
def reconstruct_path(came_from, current, draw, start):
    while current in came_from:
        current = came_from[current]
        if current != start:
            current.make_path()
            draw()

#A Star Algorithm
def algorithm(draw, grid, start, end):
    #Count is keeping track of when things are added to the Queue
    #If there is a "Tie" in terms of scores then the earlier one will be picked
    count = 0
    open_set = PriorityQueue()
    #Adding F score with the Start node
    open_set.put((0, count, start))
    #Keeping track of previous path
    came_from = {}
    #Current shortest distance between two nodes
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    #Current shortest distance between start to end
    f_score = {node: float("inf") for row in grid for node in row}
    #Estimate of how far away start is to end; just a placeholder pretty much
    f_score[start] = h(start.get_pos(), end.get_pos())

    #Tracking what is and isn't in the priority queue
    open_set_hash = {start}
    
    #A way to quit since Algorithm takes over main forcefully
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        #[2] because only want the "Node"
        current = open_set.get()[2]
        #Syncing with reg open_set to have no dupes
        open_set_hash.remove(current)

        #If found shortest path, drawing the actual path taken to get there
        if current == end:
            reconstruct_path(came_from, end, draw,start)
            end.make_end()
            return True

        #Assuming each edge is 1 distance, as well as keeping track of g score
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            
            #If temp is better than current g score, then update to keep better score
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                #Add in the neighbor if it's not already in the open_set
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != start:
            current.make_closed()

    return False

#Creating a grid
def makeGrid(rows, width):
    grid = []
    #How "wide" each node should be
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid

#Displaying the grid lines
def draw_grid(win, rows, width):
    gap  = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0,i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

#Displaying everything (Main Draw function)
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col

#Running the actual pygame program
def main(win, width):
    ROWS = 50
    grid = makeGrid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    #Keeps the program running until user presses 'X'
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue
            #Checks if the user left clicks
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
               #Checks if the current node clicked is a start node and is not end node
               #Creates start node
                if not start and node != end:
                    start = node
                    start.make_start()
               #Checks if current node is a end node or start node
               #Creates end node
                elif not end and node != start:
                    end = node
                    end.make_end()
               #Checks if start and end node is already created
               #If so, creates walls / barriers
                elif node != end and node != start:
                    node.make_barrier()
            #Checks if the user right clicks
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                #If right click on a Start Node, clear it
                if node == start:
                    start = None
                #If right click on an End Node, clear it
                elif node == end:
                    end = None
            #If user presses spacebar, start the algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    #Implementing the algorithm
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
               #If user presses 'C', clear whole maze
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = makeGrid(ROWS, width)



    pygame.quit()
main(WIN, WIDTH)
