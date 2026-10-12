from pieces import PieceInfo
from utility import column_to_symbol, row_to_symbol

class PositionInfo:
    def __init__(self, fen):
        # self.fen = fen

        self.board = [[PieceInfo.empty for _ in range(8)] for _ in range(8)]
        sections = fen.split(" ")
        x = 0
        y = 0
        for c in sections[0]:
            if c == "/":
                y += 1
                x = 0
            elif c.isdigit():
                x += int(c)
            else:
                color = PieceInfo.symbol_to_color(c)
                piece_type = PieceInfo.symbol_to_type(c)
                self.board[x][y] = PieceInfo.get_piece(piece_type, color)
                x += 1

        self.white_to_move = (sections[1] == "w")
        self.move_color = PieceInfo.white if self.white_to_move else PieceInfo.black

        self.white_castle_kingside = "K" in sections[2]
        self.white_castle_queenside = "Q" in sections[2]
        self.black_castle_kingside = "k" in sections[2]
        self.black_castle_queenside = "q" in sections[2]

        self.en_passant_file = None
        self.fifty_move_count = 0
        self.nb_moves = 0

        if len(sections) > 3:
            file_name = sections[3][0]
            if file_name in "abcdefgh":
                self.en_passant_file = "abcdefgh".index(file_name)

        if len(sections) > 4:
            self.fifty_move_count = int(sections[4])
        if len(sections) > 5:
            full_move = int(sections[5])
            self.nb_moves = (full_move-1)*2 + (not self.white_to_move) # Correspond au nombre de demi coups joués

    def get_fen(self):
        fen = ""
        for y in range(8):
            empty_squares = 0
            for x in range(8):
                piece = self.board[x][y]

                if piece != 0:

                    if empty_squares != 0:
                        fen += str(empty_squares)
                        empty_squares = 0

                    fen += PieceInfo.get_symbol(piece)

                else:
                    empty_squares += 1

            if empty_squares != 0:
                fen += str(empty_squares)
            if y != 7:
                fen += "/"

        fen += " "
        fen += "w" if self.white_to_move else "b"

        fen += " "
        fen += "K" if self.white_castle_kingside else ""
        fen += "Q" if self.white_castle_queenside else ""
        fen += "k" if self.black_castle_kingside else ""
        fen += "q" if self.black_castle_queenside else ""
        fen += "-" if not (self.white_castle_kingside or self.white_castle_queenside or self.black_castle_kingside or self.black_castle_queenside) else ""

        fen += " "
        if self.en_passant_file is not None:
            pawn_y = 3 if self.white_to_move else 4
            is_en_passant = False
            if self.en_passant_file > 0:
                piece = self.board[self.en_passant_file-1][pawn_y]
                if PieceInfo.get_color(piece) == self.move_color and PieceInfo.get_type(piece) == PieceInfo.pawn:
                    is_en_passant = True
            if self.en_passant_file < 7:
                piece = self.board[self.en_passant_file+1][pawn_y]
                if PieceInfo.get_color(piece) == self.move_color and PieceInfo.get_type(piece) == PieceInfo.pawn:
                    is_en_passant = True

            if is_en_passant:
                d = -1 if self.white_to_move else 1
                fen += column_to_symbol(self.en_passant_file) + row_to_symbol(pawn_y+d)
            else:
                fen += "-"
        else:
            fen += "-"

        fen += f" {self.fifty_move_count} "

        fen += str(self.nb_moves // 2 + 1)

        return fen

    def copy_state(self, state):
        self.white_castle_kingside = state.white_castle_kingside
        self.white_castle_queenside = state.white_castle_queenside
        self.black_castle_kingside = state.black_castle_kingside
        self.black_castle_queenside = state.black_castle_queenside
        self.en_passant_file = state.en_passant_file

    def get_threats(self, enemy_threats=True):
        enemy_moves = []
        color = PieceInfo.opponent_color(self.move_color) if enemy_threats else self.move_color
        for y in range(8):
            for x in range(8):
                piece = self.board[x][y]
                if PieceInfo.get_color(piece) == color:
                    enemy_moves += PieceInfo.get_valid_moves(piece, self.board, x, y, self.en_passant_file)
        return enemy_moves

    def search_king(self, enemy_king=False):
        color = PieceInfo.opponent_color(self.move_color) if enemy_king else self.move_color
        for y in range(8):
            for x in range(8):
                piece = self.board[x][y]
                if PieceInfo.get_type(piece) == PieceInfo.king and PieceInfo.get_color(piece) == color:
                    return x, y
        return None


class FenUtility:
    start_pos_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class CurrentState:
    def __init__(self, position):
        self.white_castle_kingside = position.white_castle_kingside
        self.white_castle_queenside = position.white_castle_queenside
        self.black_castle_kingside = position.black_castle_kingside
        self.black_castle_queenside = position.black_castle_queenside

        self.en_passant_file = position.en_passant_file
