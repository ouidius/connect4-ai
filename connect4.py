import numpy as np
import pygame
import sys
import math
import random

# Define color constants
BLUE=(0,0,255)
WHITE=(255,255,255)
RED=(255,0,0)
GREEN=(0,255,0)
BLACK=(0,0,0)

# Define game-related constants
ROW_COUNT=6
COLUMN_COUNT=7
PLAYER=0
AI=1
PLAYER_PIECE=1
AI_PIECE=2
WINDOW_LENGTH = 4
EMPTY=0

# Create the game board
def create_board():
    
    # Initialize an empty game board (6x7 grid)
    board=np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

# Drop a game piece into a column
def drop_piece(board,row,col,piece):
    
    # Update the board with the player's or AI's piece in the specified position
    board[row][col] = piece


# Check if a location is a valid move
def is_valid_location(board,col):

    # Check if the top row in the specified column is empty (valid move)
    return board[5][col]==0

# Find the next open row in a column
def get_next_open_row(board,col):

    # Iterate through rows in the specified column and find the first empty row
    for r in range(ROW_COUNT):
        if board[r][col]==0:
            return r
    
# Print the game board
def print_board(board):

    # Print the game board, flipped vertically for display
    print(np.flip(board,0))


# Check if a player has a winning move
def winning_move(board,piece):
    # Check for winning moves in all directions (horizontal, vertical, diagonals)
    #horizontal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c]==piece and board[r][c+1]==piece and board[r][c+2]==piece and board[r][c+3]==piece:
                return True

    #vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c]==piece and board[r+1][c]==piece and board[r+2][c]==piece and board[r+3][c]==piece:
                return True


    #positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c]==piece and board[r+1][c+1]==piece and board[r+2][c+2]==piece and board[r+3][c+3]==piece:
                return True   


    #negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3,ROW_COUNT):
            if board[r][c]==piece and board[r-1][c+1]==piece and board[r-2][c+2]==piece and board[r-3][c+3]==piece:
                return True 


# Evaluate a window for a player
def evaluate_window(window,piece):

    score=0
    opp_piece = PLAYER_PIECE #opponent piece
    if piece ==PLAYER_PIECE:
        opp_piece=AI_PIECE


    if window.count(piece)==4:
        # Four pieces in a row - a winning move
        score += 100
    elif window.count(piece) ==3 and window.count(EMPTY)==1:
        # Three pieces in a row with one empty space
        score += 5  
    elif window.count(piece)==2 and window.count(EMPTY)==2:
        # Two pieces with two empty spaces
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        # Opponent has three pieces with one empty space - block the opponent
        score -= 4

    return score


# Calculate the score for a given board position
def score_position(board,piece):

    score=0

    #center score

    center_array = [int(i) for i in list(board[:,COLUMN_COUNT//2])]
    center_count=center_array.count(piece)
    score += center_count * 3

    #horizontal score


    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window,piece)


    #vertical score

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window,piece)



    #positively sloped diagonal score

    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window,piece)

    #negatively sloped diagonal score
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window,piece)


    return score


# Check if the current board is a terminal node
def is_terminal_node(board):
    return winning_move(board,PLAYER_PIECE) or winning_move(board,AI_PIECE) or len(get_valid_locations(board)) == 0


# Implement the alphabeta algorithm for AI move selection
def alphabeta(board,depth,alpha,beta,maximizingPlayer):
    #if depth = 0 or node is a terminal node(winned game or all of the board is full) then return the heuristic value of node
    valid_locations=get_valid_locations(board)
    is_terminal=is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board,AI_PIECE):
                return (None, 1000000000000000)
            elif winning_move(board,PLAYER_PIECE):
                return (None,-1000000000000000)
            else:
                return (None,0) #game over, no more valid move

        else: #depth is zero
            #finding heuristic value
            return (None,score_position(board,AI_PIECE))

    #if maximizingPlayer then value= -sonsuz
        #for each child of node do value = max(value,alphabeta(board,depth-1,False))
        #return value
    #else --> minimizingPlayer then value=+sonsuz
        #for each child of node (board) do value=min(value,alphabeta(board,depth-1,True))
        #return value


    if maximizingPlayer: #AI's Turn
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row=get_next_open_row(board,col)
            b_copy=board.copy()
            drop_piece(b_copy,row,col,AI_PIECE)
            new_score= alphabeta(b_copy,depth-1,alpha,beta,False)[1]
            if new_score>value:
                value=new_score
                column=col
            alpha=max(alpha,value)
            if alpha>=beta:
                break
        return column,value


    else: #minimizingPlayer #Player's Turn
        value=math.inf
        column=random.choice(valid_locations)
        for col in valid_locations:
            row=get_next_open_row(board,col)
            b_copy=board.copy()
            drop_piece(b_copy,row,col,PLAYER_PIECE)
            new_score=alphabeta(b_copy,depth-1,alpha,beta,True)[1]
            if new_score<value:
                value=new_score
                column=col
            beta=min(beta,value)
            if alpha>=beta:
                break
        return column,value



# Get a list of valid move locations
def get_valid_locations(board):
    valid_locations=[]
    for col in range(COLUMN_COUNT):
        if is_valid_location(board,col):
            valid_locations.append(col)

    return valid_locations


# Select the best move for the AI
def pick_best_move(board,piece):

    valid_locations = get_valid_locations(board)
    best_score=-10000

    best_col=random.choice(valid_locations)

    for col in valid_locations:
        row = get_next_open_row(board,col)
        temp_board=board.copy()
        drop_piece(temp_board,row,col,piece)
        score=score_position(temp_board,piece)
        if score > best_score:
            best_score=score
            best_col=col

    return best_col
        

# Draw the game board
def draw_board(board):
    board=np.flip(board,0)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen,WHITE,(c*SQUARESIZE,r*SQUARESIZE+SQUARESIZE,SQUARESIZE,SQUARESIZE))
            pygame.draw.circle(screen,BLACK,(int(c*SQUARESIZE+SQUARESIZE/2),int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)),RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen,RED,(int(c*SQUARESIZE+SQUARESIZE/2),int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)),RADIUS)
            elif board[r][c]== AI_PIECE:
                pygame.draw.circle(screen,GREEN,(int(c*SQUARESIZE+SQUARESIZE/2),int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)),RADIUS)

    pygame.display.update()

# Main game loop
board =create_board()
print_board(board)
game_over=False
turn=random.randint(PLAYER,AI)

pygame.init()

SQUARESIZE=100
width=COLUMN_COUNT*SQUARESIZE
height=(ROW_COUNT+1)*SQUARESIZE

size=(width,height)

RADIUS=int(SQUARESIZE/2-5)

screen=pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont=pygame.font.SysFont("monospace",75)

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen,BLACK,(0,0,width,SQUARESIZE))
            posx=event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen,RED,(posx,int(SQUARESIZE/2)),RADIUS)
            
        pygame.display.update()
        
        
        if event.type==pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen,BLACK,(0,0,width,SQUARESIZE))
            if turn==PLAYER:
                posx=event.pos[0]
                col=int(math.floor(posx/SQUARESIZE))

                if is_valid_location(board,col):
                    row=get_next_open_row(board,col)
                    drop_piece(board,row,col,PLAYER_PIECE)

                    if winning_move(board,PLAYER_PIECE):
                        label=myfont.render("PLAYER 1 WINS!",1,RED)
                        screen.blit(label,(40,10))
                        game_over=True

                    turn += 1
                    turn = turn % 2
                    print_board(board)
                    draw_board(board)
                           


        
    if turn==AI and not game_over:


        #col= random.randint(0,COLUMN_COUNT-1)

        #col=pick_best_move(board,AI_PIECE)

        col,alphabeta_score=alphabeta(board,5,-math.inf,math.inf,True)  #alphabeta(node,depth,maximizingPlayer)

        if is_valid_location(board,col):
            pygame.time.wait(500)
            row=get_next_open_row(board,col)
            drop_piece(board,row,col,AI_PIECE)

            if winning_move(board,AI_PIECE):
                    label=myfont.render("PLAYER 2 WINS!",2,GREEN)
                    screen.blit(label,(40,10))
                    game_over=True
    
            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2


    if game_over:
        pygame.time.wait(3000)