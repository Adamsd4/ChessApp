from pieces import PieceInfo


class Move:
    def __init__(self, start_pos, target_pos, board, promotion_type=None):
        self.start_pos = start_pos
        self.target_pos = target_pos

        self.en_passant = self.is_en_passant(board)
        self.castle = self.is_castle(board)

        if promotion_type is None:
            self.promotion = self.get_promotion(board)
        else:
            self.promotion = promotion_type

        self.captured_piece = self.get_captured_piece(board)

    def is_en_passant(self, board):
        piece = board[self.start_pos[0]][self.start_pos[1]]
        captured_piece = board[self.target_pos[0]][self.target_pos[1]]
        return PieceInfo.get_type(piece) == PieceInfo.pawn and self.start_pos[0] != self.target_pos[0] and captured_piece == PieceInfo.empty

    def is_castle(self, board):
        piece = board[self.start_pos[0]][self.start_pos[1]]
        return PieceInfo.get_type(piece) == PieceInfo.king and abs(self.start_pos[0] - self.target_pos[0]) >= 2

    def get_promotion(self, board):
        piece = board[self.start_pos[0]][self.start_pos[1]]
        return PieceInfo.queen if PieceInfo.get_type(piece) == PieceInfo.pawn and (self.target_pos[1] == 0 or self.target_pos[1] == 7) else PieceInfo.empty

    def get_captured_piece(self, board):
        if not self.en_passant:
            captured_piece = board[self.target_pos[0]][self.target_pos[1]]
        else:
            color = PieceInfo.get_color(board[self.start_pos[0]][self.start_pos[1]])
            d = 1 if color == PieceInfo.white else -1
            captured_piece = board[self.target_pos[0]][self.target_pos[1] + d]
        return captured_piece

    def get_moves(self, board, move:str):
        # move.replace("+", "").replace("#", "").replace("x", "").replace("-", "")
        pass

    def get_notation(self, board):
        pass