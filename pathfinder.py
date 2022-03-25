import pygame
import math
from queue import PriorityQueue

WIDTH_OF_DISPLAY = 600
# display is 600x600, a square.
DISPLAY = pygame.display.set_mode((WIDTH_OF_DISPLAY, WIDTH_OF_DISPLAY))

pygame.display.set_caption("pathfinder algorithm")

# below are colors used for differentiating blocks on the grid from each other when displaying things like starting point, end-
# point, path taken, blocks visted, and boundary lines.
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:
    # Each block on the grid is a node, all nodes start off as white in color because they have not been set to anything yet.
    def __init__(self, row, column, width_of_display, total_rows):
        self.row = row
        self.column = column
        self.x = row * width_of_display
        self.y = column * width_of_display
        self.color = WHITE
        self.neighbors = []
        self.width_of_display = width_of_display
        self.total_rows = total_rows

# getter methods
    def get_position(self):
        return self.row, self.column

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

# setter methods
    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_path(self):
        self.color = PURPLE

    def draw(self, display):
        # This functions purpose is to allow me to draw the node object and it's color on the grid in it's respective block.
        pygame.draw.rect(display, self.color,
                         (self.x, self.y, self.width_of_display, self.width_of_display))

    def update_neighbors(self, grid):
        # update neighbors function checks all the neighboring blocks that are not barriers and adds them to the neighbors list for the node object,
        # I want to have every neighbor for each node stored in each individual node to make traversal between nodes easier.
        self.neighbors = []

        # check down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.column])

        # check up
        if self.row > 0 and not grid[self.row - 1][self.column].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.column])

        # check right
        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column + 1])

        # check left
        if self.column > 0 and not grid[self.row][self.column - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.column - 1])

    def __lt__(self, other):
        # method below is used for comparing two node objects.
        return False


def manhattan_distance(p1, p2):
    # the manhattan distance is used as a heuristic function which allows me to get a guess of how far I am from the end node.
    # manhattan distance works in a L shape on a graph.
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)


def make_grid(number_of_rows, width_of_display):
    # this function is called by the main function to initialize the grid with a size of x, x is the number of nodes in each row and column.
    grid = []
    gap = width_of_display // number_of_rows
    for i in range(number_of_rows):
        grid.append([])
        for j in range(number_of_rows):
            # each node is that is going to be on the grid is initialized and added to the list for grid.
            node = Node(i, j, gap, number_of_rows)
            grid[i].append(node)
    return grid


def draw_grid(display, number_of_rows, width_of_display):
    # the previous function makes the grid, this function draws the grid.
    gap = width_of_display // number_of_rows
    for i in range(number_of_rows):
        pygame.draw.line(display, GREY, (0, i*gap), (width_of_display, i*gap))
        for j in range(number_of_rows):
            pygame.draw.line(display, GREY, (j*gap, 0),
                             (j*gap, width_of_display))


def update_grid(display, grid, number_of_rows, width_of_display):
    # this function updates the grid every time it is called
    # to showcase the algorithm working it's way to the end node.
    display.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(display)
    draw_grid(display, number_of_rows, width_of_display)
    pygame.display.update()


def get_clicked_position(position, number_of_rows, width_of_display):
    # this function aids in finding the coordinates of the nodes the user clicks on so that they-
    # can be updated to either the start node, end node, or a barrier.
    gap = width_of_display // number_of_rows
    y, x = position
    row = y // gap
    column = x // gap
    return row, column


def reconstruct_path(came_from, current, update_grid):
    # this function uses the came_from dictionary which stores the steps taken to find the optimal-
    # path the algorithm took from the start node to the end node.
    while current in came_from:
        current = came_from[current]
        # color of nodes on the path changed to highlight the optimal path.
        current.make_path()
        update_grid()


# Implementation of A* algorithm below.
# Priority Queue is used as it employs the heap sort algorithm to weigh the different values inside it-
# and give us back the node with the most potential to be on path to the end node first.
# G-score is the score of how many nodes needed to be traversed to reach the current node. So for-
# example, start has a g-score of 0 as it is where we started and didn't need to move to it.
# F-score is an estimate of the distance left till the end node is reached, it is found using a heuristic-
# function. In this case, we use the manhattan distance and add it to the g-score to get the f-score.
# Because of the a* algorithm, the function will only look at the neighbors of the nodes going closer-
# to the end and save time not looking at nodes in the wrong direction.
def algorithm(update_grid, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    # The priority queue will hold lists containing unique nodes with their f-score and count from start.
    open_set.put((0, count, start))

    # came-from stores the nodes that came before the current, creating a path back to start.
    came_from = {}

    # every node's f and g score is set to infinity to begin with and if a better g score is found-
    # then the g-score is overwritten and a new f-score is calculated for the current node.
    # the g-score and f-score help the algorithm find the shortest path between the start and end node.
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = manhattan_distance(
        start.get_position(), end.get_position())

    # when open-set-hash is empty, we have reached the end node.
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():  # functionality for allowing user to quit.
            if event.type == pygame.QUIT:
                pygame.quit()

        # current will be assigned the node in the index 2 of the list in the Priority queue.
        current = open_set.get()[2]
        # current node removed from hash set as it's been visited now.
        open_set_hash.remove(current)

        if current == end:
            # once the algorithm reaches end, the shortest path is traced and highlighted.
            reconstruct_path(came_from, end, update_grid)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            # The distance between the current node and it's neighbors is always 1, so the g-score of-
            # the neightbor is always the g-score of the current node + 1.
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                # If the calculated g-score above is less than the neighbor's current g-score, the-
                # algorithm overwrites the g and f score then updates the path to the neighbor node.
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    manhattan_distance(
                        neighbor.get_position(), end.get_position())
                if neighbor not in open_set_hash:
                    # If the neighbor node was never visited before, store it in the priority queue and-
                    # open-set-hash where it's neighbors will be evaluated next.
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        # after each iteration of all the neighbor nodes of the current node, refresh grid.
        update_grid()

        if current != start:
            # all nodes not apart of the shortest path are highlighted red.
            current.make_closed()

    # if path not found, false returned to end loop in main function.
    return False


def main(display, width_of_display):
    # main function will create the grid and run the algorithm based on user inputs.
    ROWS = 50
    grid = make_grid(ROWS, width_of_display)

    start = None
    end = None

    run = True
    while run:
        update_grid(display, grid, ROWS, width_of_display)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # left mouse click
                # the first block clicked will become the start node and the second one clicked will be-
                # the end node. Each subsequent node clicked is a barrier.
                pos = pygame.mouse.get_pos()
                row, column = get_clicked_position(pos, ROWS, width_of_display)
                node = grid[row][column]
                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right mouse click
                # right click will remove a node from the grid, if the start or end node is removed, they-
                # will be implemented first again when the user clicks the any node on the screen.
                pos = pygame.mouse.get_pos()
                row, column = get_clicked_position(pos, ROWS, width_of_display)
                node = grid[row][column]
                node.reset()
                if node == start:
                    start = None

                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                # space bar starts the algorithm when start and end node are present.
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            # all neighbors for each node on screen is going to be set
                            node.update_neighbors(grid)
                    # lambda used to simplify algorithm and reconstruct path functions so that they-
                    # don't need a lot of inputs just to update grid.
                    algorithm(lambda: update_grid(display, grid, ROWS, width_of_display),
                              grid, start, end)

                if event.key == pygame.K_c:
                    # c key restarts the path finder when it's not running and iterating over the grid.
                    start = None
                    end = None
                    grid = make_grid(ROWS, width_of_display)

    pygame.quit()


# below we run the main function which should pop up a display on your screen so that you can use the
# pathfinding algorithm.
main(DISPLAY, WIDTH_OF_DISPLAY)
