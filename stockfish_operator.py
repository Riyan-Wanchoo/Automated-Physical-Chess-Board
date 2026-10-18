from stockfish import Stockfish


stockfish = Stockfish(path="./Stockfish_Engine/stockfish/stockfish.exe")


def get_best_move(fen):
    isFenValid = stockfish.is_fen_valid(fen)

    if isFenValid:
        stockfish.set_fen_position(fen)
        best_move = stockfish.get_best_move()
        return best_move
    else:
        print("Given FEN is Invalid")