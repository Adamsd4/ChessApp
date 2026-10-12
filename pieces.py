
class PieceInfo:
    white = 8
    black = 16

    empty =  0
    pawn = 1
    knight = 2
    bishop = 3
    rook = 4
    queen = 5
    king = 6

    symbol_to_type_dict = {"p": pawn, "n": knight, "b": bishop, "r": rook, "q": queen, "k": king, "_": empty}
    type_to_symbol_dict = {pawn: "p", knight: "n", bishop: "b", rook: "r", queen: "q", king: "k", empty: "_"}

    promotion_option = [knight, bishop, rook, queen]

    white_pawn = pawn + white
    black_pawn = pawn + black
    white_knight = knight + white
    black_knight = knight + black
    white_bishop = bishop + white
    black_bishop = bishop + black
    white_rook = rook + white
    black_rook = rook + black
    white_queen = queen + white
    black_queen = queen + black
    white_king = king + white
    black_king = king + black


    @staticmethod
    def get_piece(piece_type, color):
        return piece_type + color

    @staticmethod
    def get_color(piece:int):
        return piece - (piece%8)

    @staticmethod
    def get_type(piece: int):
        return piece % 8

    @staticmethod
    def opponent_color(color):
        return 24 - color

    @staticmethod
    def symbol_to_color(piece:str) -> int:
        return PieceInfo.white if piece.isupper() else PieceInfo.black

    @staticmethod
    def symbol_to_type(piece:str) -> int:
        return PieceInfo.symbol_to_type_dict[piece.lower()]

    @staticmethod
    def get_symbol(piece: int) -> str:
        piece_char = PieceInfo.type_to_symbol_dict[PieceInfo.get_type(piece)]
        return piece_char if PieceInfo.get_color(piece) == PieceInfo.black else piece_char.upper()

    @staticmethod
    def get_valid_moves(piece, board, x, y, en_passant_file):
        piece_type = PieceInfo.get_type(piece)
        valid_moves = []

        if piece_type == PieceInfo.king:
            valid_moves = PieceInfo.get_king_moves(piece, board, x, y)
        elif piece_type == PieceInfo.pawn:
            valid_moves = PieceInfo.get_pawn_moves(piece, board, x, y, en_passant_file)
        elif piece_type == PieceInfo.knight:
            valid_moves = PieceInfo.get_knight_moves(piece, board, x, y)
        elif piece_type == PieceInfo.bishop:
            valid_moves = PieceInfo.get_diagonal_moves(piece, board, x, y)
        elif piece_type == PieceInfo.rook:
            valid_moves = PieceInfo.get_orthogonal_moves(piece, board, x, y)
        elif piece_type == PieceInfo.queen:
            valid_moves = PieceInfo.get_orthogonal_moves(piece, board, x, y) + PieceInfo.get_diagonal_moves(piece, board, x, y)

        return valid_moves

    @staticmethod
    def get_moves_from_directions(piece, board, x, y, directions):
        valid_moves = []
        for direction in directions:
            for d in range(1, 8):
                nx = x + d * direction[0]
                ny = y + d * direction[1]

                if nx > 7 or nx < 0 or ny > 7 or ny < 0:
                    break
                else:
                    if board[nx][ny] == PieceInfo.empty:
                        valid_moves.append((nx, ny))
                    elif PieceInfo.get_color(board[nx][ny]) != PieceInfo.get_color(piece):
                        valid_moves.append((nx, ny))
                        break
                    else:
                        break
        return valid_moves

    @staticmethod
    def get_orthogonal_moves(piece, board, x, y):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        return PieceInfo.get_moves_from_directions(piece, board, x, y, directions)

    @staticmethod
    def get_diagonal_moves(piece, board, x, y):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return PieceInfo.get_moves_from_directions(piece, board, x, y, directions)

    @staticmethod
    def get_king_moves(piece, board, x, y):
        valid_moves = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx = x + i
                ny = y + j

                if nx < 0 or nx >= 8 or ny < 0 or ny >=8:
                    continue
                if PieceInfo.get_color(board[nx][ny]) != PieceInfo.get_color(piece):
                    valid_moves.append((nx, ny))

        return valid_moves

    @staticmethod
    def get_pawn_moves(piece, board, x, y, en_passant_file):
        valid_moves = []
        is_white =  PieceInfo.get_color(piece) == PieceInfo.white
        forward = -1 if is_white else 1
        first_row = 6 if is_white else 1
        can_en_passant = 3 == y if is_white else 4 == y

        if board[x][y+forward] == PieceInfo.empty:
            valid_moves.append((x, y+forward))

            if y == first_row and board[x][y + 2*forward] == PieceInfo.empty:
                valid_moves.append((x, y + 2*forward))

        opponent_color = PieceInfo.opponent_color(PieceInfo.get_color(piece))

        if x > 0:
            if PieceInfo.get_color(board[x - 1][y + forward]) == opponent_color or (can_en_passant and en_passant_file == x-1):
                valid_moves.append((x - 1, y + forward))

        if x < 7:
            if PieceInfo.get_color(board[x + 1][y + forward]) == opponent_color or (can_en_passant and en_passant_file == x+1):
                valid_moves.append((x + 1, y + forward))

        return  valid_moves

    @staticmethod
    def get_knight_moves(piece, board, x, y):
        valid_moves = []

        color = PieceInfo.get_color(piece)
        if x > 1:
            if y > 0:
                if PieceInfo.get_color(board[x - 2][y - 1]) != color:
                    valid_moves.append((x - 2, y - 1))

            if y < 7:
                if PieceInfo.get_color(board[x - 2][y + 1]) != color:
                    valid_moves.append((x - 2, y + 1))

        if x < 6:
            if y > 0:
                if PieceInfo.get_color(board[x + 2][y - 1]) != color:
                    valid_moves.append((x + 2, y - 1))

            if y < 7:
                if PieceInfo.get_color(board[x + 2][y + 1]) != color:
                    valid_moves.append((x + 2, y + 1))

        if y > 1:
            if x > 0:
                if PieceInfo.get_color(board[x - 1][y - 2]) != color:
                    valid_moves.append((x - 1, y - 2))

            if x < 7:
                if PieceInfo.get_color(board[x + 1][y - 2]) != color:
                    valid_moves.append((x + 1, y - 2))

        if y < 6:
            if x > 0:
                if PieceInfo.get_color(board[x - 1][y + 2]) != color:
                    valid_moves.append((x - 1, y + 2))

            if x < 7:
                if PieceInfo.get_color(board[x + 1][y + 2]) != color:
                    valid_moves.append((x + 1, y + 2))

        return valid_moves
