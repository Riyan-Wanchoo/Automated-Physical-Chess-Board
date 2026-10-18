import chess
from stockfish_operator import get_best_move


def find_move_from_occupancy(current_board: chess.Board, matrix, perspective):
  """Takes current board and a new 8x8 occupancy matrix ('X'/'').

  Finds which legal move matches the before-and-after occupancy change.
  """
  # Target occupancy from Matrix B ('X' means occupied, '' means empty)
  target_occupancy = [[cell == "X" for cell in row] for row in matrix]

  for move in current_board.legal_moves:
    temp_board = current_board.copy()
    temp_board.push(move)

    # Generate occupancy for the simulated move
    simulated_occupancy = []
    for row in range(8):
      simulated_row = []
      for col in range(8):
        if perspective == "w":
          # Your layout: row 0 is Rank 8 (7), row 7 is Rank 1 (0)
          board_row = 7 - row
          board_col = col
        else:
          # Flipped layout for Black: row 0 is Rank 1 (0), row 7 is Rank 8 (7)
          board_row = row
          board_col = 7 - col

        square_idx = chess.square(board_col, board_row)
        simulated_row.append(
            temp_board.piece_at(square_idx) is not None
        )
      simulated_occupancy.append(simulated_row)

    if simulated_occupancy == target_occupancy:
      return move

  return None


def print_ascii_board(board: chess.Board, perspective: str):
  """Prints the board state with actual piece characters (P, n, K, etc.).

  Respects whether you are playing from White's or Black's side.
  """
  print("\nCurrent Saved Board State:")
  print("  +-----------------+")

  # Determine row iteration order based on perspective
  rows = range(8) if perspective == "w" else range(7, -1, -1)
  cols = range(8) if perspective == "w" else range(7, -1, -1)

  rank_labels = (
      ["8", "7", "6", "5", "4", "3", "2", "1"]
      if perspective == "w"
      else ["1", "2", "3", "4", "5", "6", "7", "8"]
  )
  file_labels = (
      ["a", "b", "c", "d", "e", "f", "g", "h"]
      if perspective == "w"
      else ["h", "g", "f", "e", "d", "c", "b", "a"]
  )

  for r_idx, r in enumerate(rows):
    row_str = f"{rank_labels[r_idx]} | "
    for c in cols:
      square = chess.square(c, 7 - r)
      piece = board.piece_at(square)
      row_str += f"{piece.symbol() if piece else '.'} "
    row_str += "|"
    print(row_str)

  print("  +-----------------+")
  print(f"    {' '.join(file_labels)}\n")



def main():
  print("=== Chess Vision Occupancy & Move Validator Test ===")

  # 1. Ask user which side they are playing
  while True:
    perspective = (
        input("Do you want to play as White (w) or Black (b)? ").strip().lower()
    )
    if perspective in ["w", "b"]:
      break
    print("Please enter 'w' or 'b'.")

  # 2. Initialize python-chess board
  board = chess.Board()

  print(
      f"\nGame initialized! You are playing as {'White' if perspective == 'w' else 'Black'}."
  )

  # 3. Main tracking loop
  while not board.is_game_over():
    # Print current state with actual piece symbols
    print_ascii_board(board, perspective)

    print(
        f"Turn: {'White' if board.turn == chess.WHITE else 'Black'} to move."
    )

    if (board.turn == chess.WHITE and perspective == "w") or board.turn == chess.BLACK and perspective == "b":
      fen_string = board.fen()
      best_move = get_best_move(fen_string)
      parsed_move_from_uci = chess.Move.from_uci(best_move)
      board.push(parsed_move_from_uci)
      print_ascii_board(board, perspective)
      continue


    # Get the next occupancy matrix from terminal input
    matrix_inp = input()
    matrix_parsed = eval(matrix_inp)

    # Validate move
    legal_move = find_move_from_occupancy(board, matrix_parsed)

    if legal_move is not None:
      san_move = board.san(legal_move)
      board.push(legal_move)
      print(f"✅ Move Validated & Executed: {san_move}\n")
      print("-" * 40)
    else:
      print(
          "❌ No legal move matched your input matrix! Check your layout and"
          " try again.\n"
      )

  print("Game Over!")
  print(board.result())


if __name__ == "__main__":
  main()