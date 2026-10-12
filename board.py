from pieces import PieceInfo
from position import PositionInfo, CurrentState, FenUtility
from move import Move

class Board:
    def __init__(self, fen=FenUtility.start_pos_fen):
        self.position = PositionInfo(fen)

        self.piece_pos = {PieceInfo.black_queen: [], PieceInfo.white_queen: [],
                          PieceInfo.black_king: [], PieceInfo.white_king: [],
                          PieceInfo.black_rook: [], PieceInfo.white_rook: [],
                          PieceInfo.black_knight: [], PieceInfo.white_knight: [],
                          PieceInfo.black_bishop: [], PieceInfo.white_bishop: [],
                          PieceInfo.black_pawn: [], PieceInfo.white_pawn: []}
        self.all_game_moves = []
        self.game_ended = False
        self.winner = None

    def move_piece(self, piece, start, target):
        self.position.board[start[0]][start[1]] = PieceInfo.empty
        self.position.board[target[0]][target[1]] = piece

    def make_move(self, move:Move):
        piece = self.position.board[move.start_pos[0]][move.start_pos[1]]

        target_x, target_y = move.target_pos

        if move.en_passant:
            d = 1 if self.position.white_to_move else -1
            self.position.board[target_x][target_y+d] = PieceInfo.empty

        self.move_piece(piece, move.start_pos, move.target_pos)

        if move.castle:
            kingside = target_x == 6
            rook_start = (target_x + 1, target_y) if kingside else (target_x - 2, target_y)
            rook_target = (target_x - 1, target_y) if kingside else (target_x + 1, target_y)

            rook = self.position.board[rook_start[0]][rook_start[1]]
            self.move_piece(rook, rook_start, rook_target)

        if move.promotion != PieceInfo.empty:
            self.position.board[target_x][target_y] = PieceInfo.get_piece(move.promotion, self.position.move_color)

    def update_board(self, move:Move):
        piece = self.position.board[move.start_pos[0]][move.start_pos[1]]

        self.make_move(move)

        if PieceInfo.get_type(piece) == PieceInfo.pawn and abs(move.target_pos[1] - move.start_pos[1]) == 2:
            self.position.en_passant_file = move.target_pos[0]
        else:
            self.position.en_passant_file = None

        # Update castling rights
        if PieceInfo.get_type(piece) == PieceInfo.king:
            if self.position.white_to_move:
                self.position.white_castle_kingside = False
                self.position.white_castle_queenside = False
            else:
                self.position.black_castle_kingside = False
                self.position.black_castle_queenside = False
        h1 = (7, 7)
        a1 = (0, 7)
        h8 = (7, 0)
        a8 = (0, 0)
        if move.target_pos == h1 or move.start_pos == h1:
            self.position.white_castle_kingside = False
        if move.target_pos == a1 or move.start_pos == a1:
            self.position.white_castle_queenside = False
        if move.target_pos == h8 or move.start_pos == h8:
            self.position.black_castle_kingside = False
        if move.target_pos == a8 or move.start_pos == a8:
            self.position.black_castle_queenside = False

        # Update 50 move counter
        if move.captured_piece != PieceInfo.empty or PieceInfo.get_type(piece) == PieceInfo.pawn:
            self.position.fifty_move_count = 0
        else:
            self.position.fifty_move_count += 1

        self.position.white_to_move = not self.position.white_to_move
        self.position.move_color = PieceInfo.white if self.position.white_to_move else PieceInfo.black

        # Check end of game /!\ A finir : Répetition / manque de materiel
        if not self.get_all_moves():
            self.game_ended = True
            king_pos = self.position.search_king()
            if king_pos in self.position.get_threats():
                self.winner = PieceInfo.opponent_color(self.position.move_color)
        if self.position.fifty_move_count >= 50:
            self.game_ended = True

        self.position.nb_moves += 1

    def unmake_move(self, move):
        moved_piece = self.position.board[move.target_pos[0]][move.target_pos[1]]

        if move.promotion != PieceInfo.empty:
            moved_piece = PieceInfo.get_piece(PieceInfo.pawn, self.position.move_color)

        self.move_piece(moved_piece, move.target_pos, move.start_pos)

        capture_square_x, capture_square_y = move.target_pos
        if move.en_passant:
            capture_square_y = capture_square_y + (1 if self.position.white_to_move else -1)

        self.position.board[capture_square_x][capture_square_y] = move.captured_piece

        if move.castle:
            target_x, target_y = move.target_pos
            kingside = target_x == 6
            rook_start = (target_x + 1, target_y) if kingside else (target_x - 2, target_y)
            rook_target = (target_x - 1, target_y) if kingside else (target_x + 1, target_y)
            rook = self.position.board[rook_target[0]][rook_target[1]]
            self.move_piece(rook, rook_target, rook_start)

    def restore_board(self, move, current_state):
        self.game_ended = False
        self.winner = None

        self.position.white_to_move = not self.position.white_to_move
        self.position.move_color = PieceInfo.white if self.position.white_to_move else PieceInfo.black

        self.unmake_move(move)

        self.position.copy_state(current_state)
        self.position.nb_moves -= 1

    def get_piece_moves(self, x, y):
        piece = self.position.board[x][y]

        if PieceInfo.get_color(piece) != self.position.move_color:
            return []

        valid_targets = PieceInfo.get_valid_moves(piece, self.position.board, x, y , self.position.en_passant_file)

        valid_moves = []
        for target in valid_targets:
            move = Move((x, y), target, self.position.board)

            self.make_move(move)

            king_pos = self.position.search_king()
            if king_pos not in self.position.get_threats():
                valid_moves.append(target)

            self.unmake_move(move)


        if PieceInfo.get_type(piece) == PieceInfo.king:
            enemy_threats = self.position.get_threats()
            if (x, y) not in enemy_threats:
                castle_kingside = (self.position.move_color == PieceInfo.white and self.position.white_castle_kingside) or (self.position.move_color == PieceInfo.black and self.position.black_castle_kingside)
                if castle_kingside:
                    if not any((self.position.board[col][y] != PieceInfo.empty or (col, y) in enemy_threats) for col in range(x + 1, 7)):
                        valid_moves.append((6, y))

                castle_queenside = (self.position.move_color == PieceInfo.white and self.position.white_castle_queenside) or (self.position.move_color == PieceInfo.black and self.position.black_castle_queenside)
                if castle_queenside:
                    if not any((self.position.board[col][y] != PieceInfo.empty or (col, y) in enemy_threats) for col in range(x - 1, 0, -1)):
                        valid_moves.append((2, y))

        return valid_moves

    def get_all_moves(self):
        moves = []
        for x in range(8):
            for y in range(8):
                piece = self.position.board[x][y]
                if PieceInfo.get_color(piece) == self.position.move_color:
                    for target in self.get_piece_moves(x, y):
                        if PieceInfo.get_type(piece) == PieceInfo.pawn and (target[1] == 0 or target[1] == 7):  # Rajoute tous les types de promotion
                            for promotion_piece in PieceInfo.promotion_option:
                                moves.append(Move((x, y), target, self.position.board, promotion_piece))
                        else:
                            moves.append(Move((x, y), target, self.position.board))

        return moves


















