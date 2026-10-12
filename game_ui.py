import pygame

from pieces import PieceInfo
from utility import get_notation_from_move, get_move_from_notation
from board import Board
from move import Move


class Game:
    def __init__(self):
        self.board = Board()
        size = 720
        self.game_ui = GameUI(size)
        self.clock = pygame.time.Clock()

        self.flip_side_mode = False
        self.side = PieceInfo.white
        self.selected_piece_pos = None
        self.previous_move = None
        self.valid_moves = []
        self.piece_held = False

    def run(self):
        while True:
            self.clock.tick(60)
            self.tick()

    def tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.selected_piece_pos is None:
                            self.select_piece()
                        else:
                            if not self.piece_held:
                                self.place_piece()
                            else:
                                self.piece_held = False
                    elif event.button == 3:
                        self.unselect()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.piece_held:
                            self.place_piece()


        self.game_ui.draw_board(self.side, self.board.position.board, self.previous_move, self.valid_moves, self.selected_piece_pos, self.piece_held)
        pygame.display.flip()

    def select_piece(self):
        x, y = self.game_ui.get_mouse_co(self.side)
        piece = self.board.position.board[x][y]

        if PieceInfo.get_color(piece) != PieceInfo.empty:
            self.selected_piece_pos =  x, y
            self.valid_moves = self.board.get_piece_moves(self.selected_piece_pos[0], self.selected_piece_pos[1])
            self.piece_held = True

    def unselect(self):
        self.selected_piece_pos = None
        self.valid_moves = []
        self.piece_held = False

    def place_piece(self):
        x, y = self.game_ui.get_mouse_co(self.side)

        if (x, y) in self.valid_moves:
            move = Move((self.selected_piece_pos[0], self.selected_piece_pos[1]), (x, y), self.board.position.board)
            self.board.update_board(move)
            self.previous_move = move
            self.unselect()
            if self.flip_side_mode:
                self.flip_side()
        elif self.piece_held:
            self.piece_held = False
        else:
            piece = self.board.position.board[x][y]
            if PieceInfo.get_color(piece) != PieceInfo.empty:
                self.select_piece()
            else:
                self.unselect()

    def flip_side(self):
        if self.side == PieceInfo.white:
            self.side = PieceInfo.black
        else:
            self.side = PieceInfo.white

class GameUI:
    def __init__(self, size):
        self.square_size = size//8
        self.WHITE = (235, 236, 208) # rgba(202, 203, 179)
        self.BLACK = (115, 149, 82)  # rgba(99, 128, 70)
        self.PREVIOUS_MOVE = (255, 255, 50, 127)
        self.VALID_MOVES = (0, 0, 0, 35)
        self.HELD_MOVES = (240, 240, 240, 125)

        self.win = pygame.display.set_mode((size, size), pygame.DOUBLEBUF)
        pygame.display.set_caption("Chess")
        self.images = {
            PieceInfo.black_king: pygame.transform.scale(pygame.image.load("images/neo/bk.png"), (self.square_size, self.square_size)),
            PieceInfo.black_queen: pygame.transform.scale(pygame.image.load("images/neo/bq.png"), (self.square_size, self.square_size)),
            PieceInfo.black_rook: pygame.transform.scale(pygame.image.load("images/neo/br.png"), (self.square_size, self.square_size)),
            PieceInfo.black_knight: pygame.transform.scale(pygame.image.load("images/neo/bn.png"), (self.square_size, self.square_size)),
            PieceInfo.black_bishop: pygame.transform.scale(pygame.image.load("images/neo/bb.png"), (self.square_size, self.square_size)),
            PieceInfo.black_pawn: pygame.transform.scale(pygame.image.load("images/neo/bp.png"), (self.square_size, self.square_size)),
            PieceInfo.white_king: pygame.transform.scale(pygame.image.load("images/neo/wk.png"), (self.square_size, self.square_size)),
            PieceInfo.white_queen: pygame.transform.scale(pygame.image.load("images/neo/wq.png"), (self.square_size, self.square_size)),
            PieceInfo.white_rook: pygame.transform.scale(pygame.image.load("images/neo/wr.png"), (self.square_size, self.square_size)),
            PieceInfo.white_knight: pygame.transform.scale(pygame.image.load("images/neo/wn.png"), (self.square_size, self.square_size)),
            PieceInfo.white_bishop: pygame.transform.scale(pygame.image.load("images/neo/wb.png"), (self.square_size, self.square_size)),
            PieceInfo.white_pawn: pygame.transform.scale(pygame.image.load("images/neo/wp.png"), (self.square_size, self.square_size)),
        }

    def draw_rect_alpha(self, color, rect, width=0):
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), width=width)
        self.win.blit(shape_surf, rect)

    def draw_circle_alpha(self, color, center, radius, width=0):
        target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(shape_surf, color, (radius, radius), radius, width=width)
        self.win.blit(shape_surf, target_rect)

    def get_image(self, piece):
        return self.images[piece]

    def draw_board(self, side, board, previous_move, valid_moves, selected_piece_pos, piece_held):
        self.draw_background()

        if previous_move is not None:
            self.draw_previous_move(previous_move, side)

        if selected_piece_pos is not None:
            self.draw_selected_piece(selected_piece_pos, side)

        self.draw_valid_moves(valid_moves, board, side)

        for y in range(8):
            for x in range(8):
                if board[x][y] != PieceInfo.empty:
                    piece = board[x][y]
                    if not (piece_held and (x, y) == selected_piece_pos):
                        self.draw_piece(side, piece, x, y)

        if piece_held:
            self.draw_held_piece(board[selected_piece_pos[0]][selected_piece_pos[1]])

    def draw_background(self):
        self.win.fill(self.WHITE)
        for y in range(8):
            for x in range(8):
                if (y+x) % 2 == 1:
                    pygame.draw.rect(self.win, self.BLACK, (x*self.square_size, y*self.square_size, self.square_size, self.square_size))

    def draw_piece(self, side, piece, x, y):
        if side == PieceInfo.white:
            self.win.blit(self.get_image(piece), (x*self.square_size, y*self.square_size))
        else:
            self.win.blit(self.get_image(piece), ((7-x) * self.square_size, (7-y) * self.square_size))

    def draw_held_piece(self, piece):
        souris_x, souris_y = pygame.mouse.get_pos()
        x = souris_x // self.square_size
        y = souris_y // self.square_size
        souris_x -= self.square_size // 2
        souris_y -= self.square_size // 2

        self.draw_rect_alpha(self.HELD_MOVES,(x * self.square_size, y * self.square_size, self.square_size, self.square_size), width=(self.square_size//16))
        self.win.blit(self.get_image(piece), (souris_x, souris_y))

    def draw_selected_piece(self, piece_pos, side):
        if side == PieceInfo.white:
            self.draw_rect_alpha(self.PREVIOUS_MOVE, (piece_pos[0] * self.square_size, piece_pos[1] * self.square_size, self.square_size, self.square_size))
        else:
            self.draw_rect_alpha(self.PREVIOUS_MOVE, ((7 - piece_pos[0]) * self.square_size, (7 - piece_pos[1]) * self.square_size, self.square_size, self.square_size))

    def draw_previous_move(self, move, side):
        if side == PieceInfo.white:
            self.draw_rect_alpha(self.PREVIOUS_MOVE, (move.start_pos[0] * self.square_size, move.start_pos[1] * self.square_size, self.square_size, self.square_size))
            self.draw_rect_alpha(self.PREVIOUS_MOVE, (move.target_pos[0] * self.square_size, move.target_pos[1] * self.square_size, self.square_size, self.square_size))
        else:
            self.draw_rect_alpha(self.PREVIOUS_MOVE,((7 - move.start_pos[0]) * self.square_size, (7 - move.start_pos[1]) * self.square_size, self.square_size, self.square_size))
            self.draw_rect_alpha(self.PREVIOUS_MOVE,((7 - move.target_pos[0]) * self.square_size, (7 - move.target_pos[1]) * self.square_size, self.square_size, self.square_size))

    def draw_valid_moves(self, valid_moves, board, side):
        for (x, y) in valid_moves:
            nx = x if side == PieceInfo.white else 7 - x
            ny = y if side == PieceInfo.white else 7 - y

            if board[x][y] == PieceInfo.empty:
                self.draw_circle_alpha(self.VALID_MOVES, (nx*self.square_size+self.square_size/2, ny*self.square_size+self.square_size/2), self.square_size/6)
            else:
                self.draw_circle_alpha(self.VALID_MOVES, (nx*self.square_size+self.square_size/2, ny*self.square_size+self.square_size/2), self.square_size/2, width=(self.square_size//12))

    def get_mouse_co(self, side):
        souris_x, souris_y = pygame.mouse.get_pos()
        x = souris_x // self.square_size
        y = souris_y // self.square_size
        x = x if side == PieceInfo.white else 7 - x
        y = y if side == PieceInfo.white else 7 - y
        return x, y
