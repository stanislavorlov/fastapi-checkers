def parse_and_map_board(board_string: str) -> list[list[str]]:
    # 1. Parse the string to get only the 32 playable square characters.
    parts = board_string.split('#')
    dark_squares_data = "".join([part for part in parts if part])

    # 2. Initialize an empty 8x8 board with '.' for light squares.
    board = [['.' for _ in range(8)] for _ in range(8)]

    # Keep track of which piece to place next.
    data_index = 0

    # 3. Iterate through each square of the board to map the pieces.
    for row in range(8):
        for col in range(8):
            # Check if the square is a dark square.
            # On a standard board, if (row + col) is odd, it's a dark square.
            if (row + col) % 2 != 0:
                if data_index < len(dark_squares_data):
                    board[row][col] = dark_squares_data[data_index]
                    data_index += 1

    return board


# The input string from the previous context.
fen_string = "######rrrrrrrr#rrrr0000#0000wwww#wwwwwwww#####"

# Generate the board array.
board_array = parse_and_map_board(fen_string)

# Print the resulting board in a visually clear format.
print("Parsed 8x8 Board:")
for row_data in board_array:
    print(" ".join(row_data))