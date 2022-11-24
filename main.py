import pygame
import pygame.locals
import pygame.freetype
import numpy as np
import argparse


def non_negative_int_input(value):
    """
    A function for checking if an input value is a non-negative integer.

    :param value: the input value.
    :return: the non-negative integer value if this holds otherwise raises an exception.
    """

    try:
        # try to convert input value to integer
        value = int(value)

        # if conversion is successful check if the integer is non-negative
        if value < 0:
            # raise an exception if the integer is not a non-negative integer
            raise argparse.ArgumentTypeError(f"{value} is not a non-negative integer")
    except ValueError:

        # if conversion to integer fails then the input is not an integer
        raise argparse.ArgumentTypeError(f"{value} is not an integer.")

    # return the non-negative integer value if every process is successfully completed
    return value


def count_neighbors(generation: np.ndarray, x: int, y: int, rows: int, cols: int) -> int:
    """
    A function for counting the number of alive neighbors in a cell's neighborhood (the edges are wrapped around).

    :param generation: the 2D numpy array containing the current generation
    :param x: the x coordinate of the cell
    :param y: the y coordinate of the cell
    :param rows: the number of rows in the grid
    :param cols: the number of columns in the grid
    :return: the number of alive neighbors as an integer
    """

    # compute the number of alive neighbors of a cell in position (x,y) including central element
    cardinality = 0
    for offsetX in [-1, 0, 1]:
        for offsetY in [-1, 0, 1]:
            cardinality += generation[(x + offsetX + rows) % rows, (y + offsetY + cols) % cols]

    # subtract out the central element
    cardinality -= generation[x, y]

    # return the number of alive neighbors
    return cardinality


def conways_game_of_life(width: int, height: int, res: int, prob0: int, update_speed: int) -> None:
    """
    A function for playing the Conway's Game of Life. The game is initialized by randomly selecting the state of each
    cell contained in the grid.

    :param width: the width of the window.
    :param height: the height of the window.
    :param res: the grid resolution.
    :param prob0: the probability of sampling a dead cell during game initialization (First Generation).
    :param update_speed: The time it takes to refresh the frame.
    :return: None
    """

    # compute the number of rows and columns of the grid given the specified grid resolution
    box_num_rows, box_num_cols = height // res, width // res

    # initialize screen
    pygame.init()

    # initialize pre-game text, with Times New Roman Font and size scaled based on window width
    title_pos_x, title_pos_y = width / 8, height / 8
    normal_text_size = width // 20
    title_font = pygame.freetype.SysFont(name="Times New Roman", size=normal_text_size + 10)
    font = pygame.freetype.SysFont(name="Times New Roman", size=normal_text_size)

    # set up the screen and window title
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Conway's Game of Life")

    # initialize the variables for the current and previous generation
    previous_generation = None
    current_generation = None

    # repeat as long as the game is in running state (game main loop)
    running = True
    game_start = False
    while running:

        # check if we are on pre game phase
        if not game_start:

            # fill the background with black color
            screen.fill(COLOR_BLACK)

            # render the pre-game dialog
            title_font.render_to(screen, (title_pos_x, title_pos_y),
                                 "Conway's Game of Life", COLOR_WHITE)
            font.render_to(screen, (title_pos_x, title_pos_y + (2 * normal_text_size)),
                           "Press the Space key to start the game", COLOR_WHITE)
            font.render_to(screen, (title_pos_x, title_pos_y + (4 * normal_text_size)),
                           "Press the R key to restart the game", COLOR_WHITE)

            # update the frame
            pygame.display.flip()

        # check for events
        for event in pygame.event.get():

            # check if user has pressed the x window's button (quit event)
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                running = False

            # check if a key is pressed
            elif event.type == pygame.locals.KEYDOWN:

                # check if the key "r" was pressed while the game is running
                if event.key == pygame.K_r and game_start:

                    # restart the game
                    game_start = False

                # check if the key "Space" was pressed while the game is in pre game phase
                elif event.key == pygame.K_SPACE and not game_start:

                    # start the game
                    game_start = True

                    # fill the background with black color
                    screen.fill(COLOR_BLACK)

                    # game initialization
                    previous_generation = np.random.choice([0, 1],
                                                           size=(box_num_rows, box_num_cols),
                                                           p=[prob0, 1 - prob0]).astype(np.uint8)
                    current_generation = np.zeros((box_num_rows, box_num_cols)).astype(np.uint8)

        # execute the following lines only if the quit event does not exist and the game has started
        if running and game_start:
            for i in range(box_num_rows):
                for j in range(box_num_cols):

                    # get the cell state
                    # 0 -> dead state
                    # 1 -> alive state
                    cell_state = previous_generation[i, j]

                    # obtain the color of the state
                    rect_state = COLOR_BLACK if cell_state == 0 else COLOR_WHITE

                    # draw the rectangle with state color
                    pygame.draw.rect(screen, rect_state, [i * res, j * res, res, res], 1)

                    # compute the alive neighbors of the pixel's neighborhood in position (i,j)
                    cardinality = count_neighbors(previous_generation, i, j, box_num_rows, box_num_cols)

                    # Apply the rules of the game
                    if cell_state == 1 and (cardinality < 2 or cardinality > 3):

                        # the alive cell becomes dead due to underpopulation or overpopulation
                        current_generation[i, j] = 0

                    elif cell_state == 0 and cardinality == 3:

                        # the dead cell becomes alive due to reproduction
                        current_generation[i, j] = 1

            # copy the current generation to the previous one
            np.copyto(previous_generation, current_generation)

            # wait for an amount of milliseconds (update_speed milliseconds) before moving to the next iteration
            pygame.time.delay(update_speed)

            # update frame
            pygame.display.flip()


if __name__ == "__main__":
    # define the colors for the alive and dead state
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)

    # create and parse arguments
    parser = argparse.ArgumentParser(description="A python script for the Conway's Game of Life.")

    parser.add_argument("--height", type=non_negative_int_input,
                        action="store", required=False,
                        default=500, help="The window height.")
    parser.add_argument("--width", type=non_negative_int_input,
                        action="store", required=False,
                        default=500, help="The window width.")
    parser.add_argument("--resolution", type=non_negative_int_input,
                        action="store", required=False,
                        default=10, help="The grid resolution.")
    parser.add_argument("--prob0", type=non_negative_int_input,
                        action="store", required=False,
                        default=0.7, help="The probability of sampling a dead cell during game initialization")
    parser.add_argument("--updateSpeed", type=non_negative_int_input,
                        action="store", required=False,
                        default=75, help="The time it takes to refresh the frame.")
    args = parser.parse_args()

    # start the conway's game of life
    conways_game_of_life(width=args.width, height=args.height, res=args.resolution, prob0=args.prob0,
                         update_speed=args.updateSpeed)
