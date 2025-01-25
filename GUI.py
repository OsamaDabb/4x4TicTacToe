import sys
import pygame
import time

from request_get import create_game, send_move, get_moves, end_game
import threading

GAME_ID = "250"
running = True

pygame.init()
WIDTH, HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4x4 Tic-Tac-Toe")

BG_COLOR = (40, 50, 60)
LINE_COLOR = (180, 180, 180)
X_COLOR = (255, 7, 58)   # Neon red for X
O_COLOR = (0, 255, 255)  # Neon blue for O
TEXT_COLOR = (0, 0, 0)
WIN_BOX_COLOR = (220, 220, 220)
TITLE_COLOR = (255, 111, 97)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Fonts
TITLE_FONT = pygame.font.Font(None, 100)  # Font for the title
BUTTON_FONT = pygame.font.Font(None, 50)  # Font for the button text
my_symbol = ""
opp_symbol = ""
my_turn = False


# Draw Text on Screen
def draw_text(message, font, color, x, y):
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    SCREEN.blit(text_surface, text_rect)


# Draw Button
def draw_button(text, x, y, width, height, bg_color, text_color):
    pygame.draw.rect(SCREEN, bg_color, (x, y, width, height), border_radius=10)
    draw_text(text, BUTTON_FONT, text_color, x + width // 2, y + height // 2)
    return pygame.Rect(x, y, width, height)


LINE_WIDTH = 3
PADDING = 20
SHAPE_SIZE = 50
SHAPE_THICKNESS = 6

pygame.font.init()
font = pygame.font.Font(None, 80)

game_board = [
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None]]


def draw_grid(replace=True):

    if replace:
        SCREEN.fill(BG_COLOR)
    # Horizontal Lines
    for i in range(3):
        pygame.draw.line(SCREEN, LINE_COLOR,
                         (PADDING, (i+1) * HEIGHT // 4),
                         (WIDTH - PADDING,  (i+1) * HEIGHT // 4),
                         LINE_WIDTH)

    # Vertical Lines
    for i in range(3):
        pygame.draw.line(SCREEN, LINE_COLOR,
                         ((i+1) * WIDTH // 4, PADDING),
                         ((i+1) * WIDTH // 4, HEIGHT - PADDING),
                         LINE_WIDTH)


def clear_column(board, col):

    for i in range(4):
        board[i][col] = None

    pygame.draw.rect(SCREEN, BG_COLOR, (col * WIDTH // 4, 0, WIDTH//4, HEIGHT))

    draw_grid(False)


# Start Screen Function
def start_screen():
    global opp_symbol, my_symbol, my_turn
    running = True
    while running:
        SCREEN.fill(BG_COLOR)  # Background color

        # Title
        draw_text("4x4 Tic-Tac-Toe", TITLE_FONT, TITLE_COLOR, WIDTH // 2, HEIGHT // 3)

        # Instructions
        draw_text("Four in a row to win", BUTTON_FONT, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
        draw_text("Filling a column clears it", BUTTON_FONT, WHITE, WIDTH//2, HEIGHT // 2 + 20)

        # Start Button
        start_button = draw_button("Start", WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 60, O_COLOR, BLACK)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):  # Check if the button is clicked

                    response = create_game(GAME_ID)
                    print(response)
                    my_symbol = "O" if response["message"] == "Game ID already exists" else "X"
                    opp_symbol = "X" if my_symbol == "O" else "X"
                    if my_symbol == "X":
                        my_turn = True
                    return  # Exit the start screen and proceed to the game

        pygame.display.update()


def update_board(board, player, x, y):

    row, col = 0, 0
    for i in range(3):
        if x > (i+1) * WIDTH // 4:
            col += 1
        if y > (i+1) * HEIGHT // 4:
            row += 1

    center_x = (col * WIDTH // 4) + WIDTH // 8
    center_y = (row * HEIGHT // 4) + HEIGHT // 8

    if board[row][col] is not None:
        return False, False

    board[row][col] = player

    # Check for win or clear
    # conditions: (col_win, row_win, diag_win, clear)
    conditions = [True, True, True, True]
    for i in range(4):
        # win conditions
        if board[row][i] != player:
            conditions[0] = False
        if board[i][col] != player:
            conditions[1] = False
        if (row != col or board[i][i] != player) and (row + col != 3 or board[i][3-i] != player):
            conditions[2] = False

        # clear condition
        if board[i][col] is None:
            conditions[3] = False

    # Draw the symbol
    if player == "X":
        pygame.draw.line(SCREEN, X_COLOR,
                         (center_x - SHAPE_SIZE, center_y - SHAPE_SIZE),
                         (center_x + SHAPE_SIZE, center_y + SHAPE_SIZE), SHAPE_THICKNESS)
        pygame.draw.line(SCREEN, X_COLOR,
                         (center_x + SHAPE_SIZE, center_y - SHAPE_SIZE),
                         (center_x - SHAPE_SIZE, center_y + SHAPE_SIZE), SHAPE_THICKNESS)
    elif player == "O":
        pygame.draw.circle(SCREEN, O_COLOR, (center_x, center_y), SHAPE_SIZE, SHAPE_THICKNESS)

    if conditions[0] or conditions[1] or conditions[2]:
        text_surface = font.render(player + " WINS!", True, TEXT_COLOR)  # True enables anti-aliasing
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))  # Center the text
        # Create a rectangle with padding
        padding = 5
        rect_x = text_rect.x - padding
        rect_y = text_rect.y - padding
        rect_width = text_rect.width + 2 * padding
        rect_height = text_rect.height + padding
        pygame.draw.rect(SCREEN, WIN_BOX_COLOR, (rect_x, rect_y, rect_width, rect_height))
        SCREEN.blit(text_surface, text_rect)

        return True, True

    if conditions[3]:

        pygame.display.update()
        time.sleep(0.25)
        clear_column(board, col)

    return True, False


def poll_moves():
    """Poll the server for opponent moves."""
    global my_turn, opp_symbol

    while True:
        if not my_turn:
            moves = get_moves(GAME_ID)
            print(moves)
            if len(moves) == 0:
                time.sleep(0.5)
                continue
            move = tuple(moves[-1])
            if move[2] != my_symbol:
                x, y = map(int, move[:2])

                success, win = update_board(game_board, move[2], x, y)

                if success:
                    my_turn = True

                if win:
                    pygame.display.update()
                    end_game(GAME_ID)
                    global running
                    while True:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

        time.sleep(0.5)


# Main Loop
def main():

    start_screen()

    draw_grid()
    global running, my_turn, my_symbol, opp_symbol
    threading.Thread(target=poll_moves, daemon=True).start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and my_turn:

                x, y = pygame.mouse.get_pos()
                success, win = update_board(game_board, my_symbol, x, y)
                pygame.display.update()

                if success:
                    result = send_move(GAME_ID, (x, y, my_symbol))
                    print(result)
                    my_turn = False

                if win:
                    pygame.display.update()
                    while True:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                end_game(GAME_ID)
                                pygame.quit()
                                sys.exit()

        pygame.display.update()

    end_game(GAME_ID)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
