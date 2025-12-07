import curses
import random
import time
import os

# ============ CONSTANTS ============
WIDTH = 14
HEIGHT = 26
SCORE_FILE = "tetris_highscore.txt"

SHAPES = [
    [[1,1,1,1]],

    [[1,1],
     [1,1]],

    [[0,1,0],
     [1,1,1]],

    [[1,0,0],
     [1,1,1]],

    [[0,0,1],
     [1,1,1]],

    [[1,1,0],
     [0,1,1]],

    [[0,1,1],
     [1,1,0]]
]

# Colors
COLORS = [curses.COLOR_CYAN, curses.COLOR_YELLOW, curses.COLOR_MAGENTA,
          curses.COLOR_BLUE, curses.COLOR_GREEN, curses.COLOR_RED,
          curses.COLOR_WHITE]

# ================= FUNCTIONS ===================

def load_high_score():
    if not os.path.exists(SCORE_FILE):
        return 0
    with open(SCORE_FILE, "r") as f:
        return int(f.read())

def save_high_score(score):
    with open(SCORE_FILE, "w") as f:
        f.write(str(score))

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def valid_position(board, shape, x, y):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if j + x < 0 or j + x >= WIDTH or i + y >= HEIGHT or board[i + y][j + x]:
                    return False
    return True

def add_shape(board, shape, x, y):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                board[i + y][j + x] = cell

def clear_lines(board):
    new_board = [row for row in board if any(v == 0 for v in row)]
    cleared = HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0]*WIDTH)
    return new_board, cleared

def draw(win, board, shape, offset_x, offset_y, score, high_score):
    win.erase()

    win.attron(curses.color_pair(1) | curses.A_BOLD)

    for i in range(HEIGHT + 2):
    	win.addstr(i, 0, "║")
    	win.addstr(i, WIDTH * 2 + 1, "║")

    win.addstr(HEIGHT + 2, 0, "═" * (WIDTH * 2 + 2))

    win.attroff(curses.color_pair(1) | curses.A_BOLD)

    # Score
    win.addstr(2, WIDTH * 2 + 5, f"SCORE: {score}")
    win.addstr(3, WIDTH * 2 + 5, f"HIGH : {high_score}")

    # Draw board
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell:
                win.attron(curses.color_pair(cell))
                win.addstr(i + 1, j * 2 + 1, "██")
                win.attroff(curses.color_pair(cell))

    # Draw current shape
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                win.attron(curses.color_pair(cell))
                win.addstr(i + 1 + offset_y, (j + offset_x) * 2 + 1, "██")
                win.attroff(curses.color_pair(cell))

    win.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    # Colors
    curses.start_color()
    for i, color in enumerate(COLORS, 1):
        curses.init_pair(i, color, curses.COLOR_BLACK)

    board = [[0]*WIDTH for _ in range(HEIGHT)]

    current_shape = random.choice(SHAPES)
    color = random.randint(1, 7)
    current_shape = [[cell * color for cell in row] for row in current_shape]

    x = WIDTH//2 - len(current_shape[0])//2
    y = 0

    score = 0
    high_score = load_high_score()

    speed = 0.555   # NORMAL SPEED
    last_fall = time.time()

    while True:
        if time.time() - last_fall > speed:
            if valid_position(board, current_shape, x, y + 1):
                y += 1
            else:
                add_shape(board, current_shape, x, y)
                board, cleared = clear_lines(board)

                if cleared:
                    score += cleared * 100
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

                current_shape = random.choice(SHAPES)
                color = random.randint(1, 7)
                current_shape = [[cell * color for cell in row] for row in current_shape]

                x = WIDTH//2 - len(current_shape[0])//2
                y = 0

                if not valid_position(board, current_shape, x, y):
                    stdscr.addstr(10, 5, "GAME OVER")
                    stdscr.addstr(12, 5, "Press Q to Exit")
                    stdscr.refresh()

                    while True:
                        if stdscr.getch() == ord('q'):
                            return

            last_fall = time.time()

        key = stdscr.getch()

        if key == ord('a') and valid_position(board, current_shape, x - 1, y):
            x -= 1

        elif key == ord('d') and valid_position(board, current_shape, x + 1, y):
            x += 1

        elif key == ord('s') and valid_position(board, current_shape, x, y + 1):
            y += 1

        elif key == ord('w'):
            rotated = rotate(current_shape)
            if valid_position(board, rotated, x, y):
                current_shape = rotated

        elif key == ord('q'):
            break

        draw(stdscr, board, current_shape, x, y, score, high_score)


# Run
curses.wrapper(main)
