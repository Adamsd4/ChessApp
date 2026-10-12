from pieces import PieceInfo


string_column = "abcdefgh"

def symbol_to_column(symbol):
    return string_column.index(symbol)

def symbol_to_row(symbol):
    return 8 - int(symbol)

def column_to_symbol(column):
    return string_column[column]

def row_to_symbol(row):
    return str(8-row)


def get_move_from_notation(board, algebraic_move: str):
    algebraic_move = algebraic_move.replace("+", "")
    algebraic_move = algebraic_move.replace("#", "")
    algebraic_move = algebraic_move.replace("x", "")
    algebraic_move = algebraic_move.replace("-", "")

    all_moves = board.get_all_moves()

    for move in all_moves:
        piece = board.position.board[move.start_pos[0]][move.start_pos[1]]

        if algebraic_move == "00":
            if move.castle and move.start_pos[0] - move.target_pos[0] == 2:
                return move
        elif algebraic_move == "000":
            if move.castle and move.start_pos[0] - move.target_pos[0] == -2:
                return move
        elif algebraic_move[0] in string_column:
            if PieceInfo.get_type(piece) != PieceInfo.pawn:
                continue

            if symbol_to_column(algebraic_move[0]) == move.start_pos[0]:
                if "=" in algebraic_move:
                    if move.target_pos[1] == 0 or move.target_pos[1] == 7:
                        if len(algebraic_move) == 5: # exd6=Q -> ed6=Q
                            if symbol_to_column(algebraic_move[1]) != move.target_pos[0]:
                                continue
                        promotion_char = algebraic_move[-1]
                        if move.promotion != PieceInfo.symbol_to_type(promotion_char.upper()):
                            continue

                        return move
                else:
                    target_x = symbol_to_column(algebraic_move[-2])
                    target_y = symbol_to_row(algebraic_move[-1])
                    if target_x != move.target_pos[0] or target_y != move.target_pos[1]:
                        continue
                    return move
        else:
            move_piece_char = algebraic_move[0]
            if PieceInfo.get_type(piece) != PieceInfo.symbol_to_type(move_piece_char):
                continue

            if len(algebraic_move) == 4:
                if algebraic_move[1] in string_column:
                    if symbol_to_column(algebraic_move[1]) != move.start_pos[0]:
                        continue
                else:
                    if symbol_to_row(algebraic_move[1]) != move.start_pos[1]:
                        continue

            if len(algebraic_move) == 5:
                if symbol_to_column(algebraic_move[1]) != move.start_pos[0] or symbol_to_row(algebraic_move[2]) != move.start_pos[1]:
                    continue

            target_x = symbol_to_column(algebraic_move[-2])
            target_y = symbol_to_row(algebraic_move[-1])
            if target_x != move.target_pos[0] or target_y != move.target_pos[1]:
                continue
            return move

    return None


def get_notation_from_move(position, move):
    algebraic_move = ""
    piece = position.board[move.start_pos[0]][move.start_pos[1]]

    if move.castle:
        if move.start_pos[0] - move.target_pos[0] == 2:
            return "0-0-0"
        elif move.start_pos[0] - move.target_pos[0] == -2:
            return "0-0"

    if PieceInfo.get_type(piece) != PieceInfo.pawn:
        algebraic_move += PieceInfo.get_symbol(piece).upper()

    if position.board[move.target_pos[0]][move.target_pos[1]] != PieceInfo.empty or move.en_passant:
        if PieceInfo.get_type(piece) == PieceInfo.pawn:
            algebraic_move += column_to_symbol(move.start_pos[0])
        algebraic_move += "x"

    # Rajouter move ambigue
    if PieceInfo.get_type(piece) != PieceInfo.pawn and PieceInfo.get_type(piece) != PieceInfo.king:
        ambiguity = False
        same_col = False
        same_row = False
        fake_piece = PieceInfo.get_piece(PieceInfo.get_type(piece), PieceInfo.opponent_color(PieceInfo.get_color(piece)))
        valid_moves = PieceInfo.get_valid_moves(fake_piece, position.board, move.target_pos[0], move.target_pos[1], position.en_passant_file)
        for x, y in valid_moves:
            if (x, y) != move.start_pos and PieceInfo.get_type(piece) == PieceInfo.get_type(position.board[x][y]):
                ambiguity = True
                if x == move.start_pos[0]:
                    same_col = True
                if y == move.start_pos[1]:
                    same_row = True
        if ambiguity and same_row and same_col:
            algebraic_move += column_to_symbol(move.start_pos[0]) + row_to_symbol(move.start_pos[1])
        elif ambiguity and same_col:
            algebraic_move += row_to_symbol(move.start_pos[1])
        elif ambiguity:
            algebraic_move += column_to_symbol(move.start_pos[0])


    algebraic_move += column_to_symbol(move.target_pos[0]) + row_to_symbol(move.target_pos[1])

    if move.promotion != PieceInfo.empty:
        algebraic_move += "=" + PieceInfo.get_symbol(move.promotion).upper()

    # Rajouter echec (mat)

    return algebraic_move
