import cv2
import numpy as np
import chess
import time
from getImage import getImage
from get_board_state_from_uncropped_img import get_board_state_from_uncropped_img
from chess_state_validator import find_move_from_occupancy, print_ascii_board
from stockfish_operator import get_best_move



'''
Shift this to another module handling image taking from api
Input Image to Analyse



image_path = "Test/14.jpeg"
frame = cv2.imread(image_path)

if frame is None:
    print(f"Error: Could not load image from Webcam")
    exit()



'''


pic_taking_frequency = 1

#using android app called IP Webcam
local_server_path = "http://192.168.1.15:8080/photo.jpg"
# frame, e = getImage(local_server_path)




def main():
    print("=== Welcome to our ChessBot ===")

    last_printed_move = -1
    last_invalid_state = None

    perspective_to_chess_obj_dict = {
        "w": chess.WHITE,
        "b": chess.BLACK
    }


    prevState = [
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.'],
        ['.','.','.','.','.','.','.','.']
    ]




    while True:
        perspective = (
            input("Do you want to play as White (w) or Black (b)? ").strip().lower()
        )
        if perspective in ["w", "b"]:
          break
        print("Please enter 'w' or 'b'.")

    print("Starting chess bot in 5 seconds. Get your pieces ready to their initial positions!")
    time.sleep(5)
    
    board = chess.Board()


    print(
        f"\nGame initialized! You are playing as {'White' if perspective == 'w' else 'Black'}."
    )
    if perspective=="w":
        print("Play out the first move of your choice")



    while not board.is_game_over():
        frame,e = getImage(local_server_path)

        if e==None:
            if len(board.move_stack) != last_printed_move and perspective_to_chess_obj_dict[perspective] != board.turn:
                # Print current state with actual piece symbols
                print_ascii_board(board, perspective)
                print(
                    f"Turn: {'White' if board.turn == chess.WHITE else 'Black'} to move."
                )
                last_printed_move = len(board.move_stack)

            thisState, msg, flag = get_board_state_from_uncropped_img(frame)

            if thisState!=None:
                if flag == "hand" or flag == "Fallen":
                    time.sleep(pic_taking_frequency)
                    continue
                else:
                    our_player_color = chess.WHITE if perspective == 'w' else chess.BLACK
                    ourChance = board.turn == our_player_color

                    if (prevState == thisState):
                        #Waiting for opponent/our player to move
                        time.sleep(pic_taking_frequency)
                        continue
                    elif (prevState != thisState) and (not ourChance):
                        #Our player just played a move, thisState shows that move played by our player, modifying the prevState and Waiting for opponent to make a move
                        # Validate move
                        legal_move = find_move_from_occupancy(board, thisState, perspective)
                        if legal_move is not None:
                            san_move_moved_by_opp = board.san(legal_move)
                            board.push(legal_move)
                            prevState = thisState
                            if board.is_game_over():
                                outcome = board.outcome()
                                winner_color = (
                                    "White" if outcome.winner == chess.WHITE else "Black"
                                )
                                print("Game over")
                                print(f"{winner_color} has won the game")
                                break
                            else:
                                fen_string = board.fen()
                                best_move = get_best_move(fen_string)
                                print_ascii_board(board, perspective)
                                print(f"Valid move Played by our opponent: {san_move_moved_by_opp}")
                                print(f"Best move to play in this position is: {best_move[:2]} to {best_move[2:]}")
                                print("-" * 40)
                                time.sleep(pic_taking_frequency)
                                continue
                            
                    elif (prevState != thisState) and (ourChance):
                        #Opponent just played a move, thisState shows that move played by the opponent, modifying the prevState, suggesting best move and Waiting for our player to make a move
                        legal_move = find_move_from_occupancy(board, thisState, perspective)
                        if legal_move is not None:
                            san_move_moved_by_opp = board.san(legal_move)
                            board.push(legal_move)
                            prevState = thisState
                            if board.is_game_over():
                                outcome = board.outcome()
                                winner_color = (
                                    "White" if outcome.winner == chess.WHITE else "Black"
                                )
                                print("Game over")
                                print(f"{winner_color} has won the game")
                                break
                            else:
                                fen_string = board.fen()
                                best_move = get_best_move(fen_string)
                                print_ascii_board(board, perspective)
                                print(f"Valid move Played by our player: {san_move_moved_by_opp}")
                                
                                print("-" * 40)
                                time.sleep(pic_taking_frequency)
                                continue
                            
            else:
                continue
        else:
            print(e)


if __name__ == "__main__":
    main()