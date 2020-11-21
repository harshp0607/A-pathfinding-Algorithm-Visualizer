import pygame
import math
from queue import PriorityQueue

# creating board in pygame

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* PathFinder")

# initializing all the colors that we will be using to clarify what state each node is in

RED = (255, 0, 0)  # closed node
GREEN = (0, 255, 0)  # open node
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)  # unchecked node
BLACK = (0, 0, 0)  # barrier node
PURPLE = (128, 0, 128)  # path node
ORANGE = (255, 165, 0)  # start node
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:

    def __init__(self, row, col, width, total_rows):  # initializing the nodes
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):  # returns the row and column of the node
        return self.row, self.col

    def is_closed(self):  # checks if node has already been checked
        return self.color == RED

    def is_open(self):  # checks if node is open
        return self.color == GREEN

    def is_barrier(self):  # is this node an obstacle
        return self.color == BLACK

    def is_start(self):  # starting node
        return self.color == ORANGE

    def is_end(self):  # end node
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):  # draws the window in pygame
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][
            self.col].is_barrier():  # checks if there is even a row below and that it is not a barrier.
            self.neighbors.append(grid[self.row + 1][self.col])  # Bottom neighbor
        if self.row > 0 and not grid[self.row - 1][
            self.col].is_barrier():  # checks if there is a row above and that it does not contain a barrier
            self.neighbors.append(grid[self.row - 1][self.col])  # top neighbor
        if self.col < self.total_rows - 1 and not grid[self.row][
            self.col + 1].is_barrier():  # checks if there is a column to the right and that it is not a barrier
            self.neighbors.append(grid[self.row][self.col + 1])  # right neighbor
        if self.col > 0 and not grid[self.row][
            self.col - 1].is_barrier():  # checks if there is a column to the left and that it is not a barrier
            self.neighbors.append(grid[self.row][self.col - 1])  # left neighbor

    def __lt__(self, other):
        return False


# finds the cab drivers distance which is practically the shortest distance that can be achieved by going in straight
# lines up or down

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def make_grid(rows, width):  # creates the actual grid
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw_grid(win, rows, width):  # draws the grid
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))  # draws the horizontal lines
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))  # draws the vertical lines


def draw(win, grid, rows, width):
    win.fill(WHITE)  # fills initial grid with white cubes

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def get_clicked_pos(pos, rows, width):  # helper method to find which node was actually clicked by the mouse
    gap = width // rows
    y, x = pos

    row = y // gap  # divides the y value by the gap for each box as to find which node
    col = x // gap

    return row, col


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():  # checks all the actions that have happened
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:  # left mouse button click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start:
                    start = node
                    start.make_start()

                elif not end:
                    end = node
                    end.make_end()

                elif node != start and node != end:
                    node.make_barrier()


            elif pygame.mouse.get_pressed()[2]:  # right mouse button click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

    pygame.quit()


main(WIN, WIDTH)
