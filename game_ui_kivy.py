import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.input.motionevent import MotionEvent

# ── Imports moteur ────────────────────────────────────────────────────────────
from pieces import PieceInfo
from board import Board
from move import Move

# ── Palette (fidèle à pygame) ─────────────────────────────────────────────────
def _norm(r, g, b, a=255):
    return r/255, g/255, b/255, a/255

C_WHITE  = _norm(230, 232, 217)
C_BLACK  = _norm(78,  162,  74)
C_MOVE   = _norm(230, 220, 115, 125)
C_BG     = _norm(30,  30,   30)
C_PANEL  = _norm(20,  20,   20)
C_TEXT   = _norm(220, 215, 200)
C_ACCENT = _norm(242, 192,  52)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

# Correspondance PieceInfo → fichier image (même convention que ton code pygame)
PIECE_IMAGE_FILES = {
    PieceInfo.black_king:   "bK.png",
    PieceInfo.black_queen:  "bQ.png",
    PieceInfo.black_rook:   "bR.png",
    PieceInfo.black_knight: "bKN.png",
    PieceInfo.black_bishop: "bB.png",
    PieceInfo.black_pawn:   "bP.png",
    PieceInfo.white_king:   "wK.png",
    PieceInfo.white_queen:  "wQ.png",
    PieceInfo.white_rook:   "wR.png",
    PieceInfo.white_knight: "wKN.png",
    PieceInfo.white_bishop: "wB.png",
    PieceInfo.white_pawn:   "wP.png",
}

def piece_image_path(piece) -> str:
    filename = PIECE_IMAGE_FILES.get(piece)
    if filename:
        return os.path.join(IMAGES_DIR, filename)
    return ""


# ─────────────────────────────────────────────────────────────────────────────
#  BoardWidget  —  le plateau de jeu complet
# ─────────────────────────────────────────────────────────────────────────────
class BoardWidget(FloatLayout):
    """
    Gère à la fois le rendu du plateau et toute la logique d'interaction
    (sélection, piece_held, flip_side) — symétrique à la classe Game de pygame.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ── État jeu ──────────────────────────────────────────────────────────
        self.chess_board        = Board()
        self.flip_side_mode     = False
        self.side               = PieceInfo.white
        self.selected_piece_pos = None
        self.valid_moves        = []
        self.piece_held         = False
        self._drag_pos          = (0, 0)   # position souris/doigt en cours

        # ── Images préchargées (on ne charge qu'une fois par pièce) ───────────
        self._images: dict = {}   # { piece_code: source_path }
        for piece, path in PIECE_IMAGE_FILES.items():
            self._images[piece] = os.path.join(IMAGES_DIR, path)

        # ── Widgets ───────────────────────────────────────────────────────────
        # Calque de dessin du plateau (cases + indicateurs)
        self._board_layer = Widget()
        self.add_widget(self._board_layer)

        # Calque des pièces (une KivyImage par case occupée)
        self._piece_widgets: dict = {}   # (x,y) → KivyImage
        self._piece_layer = FloatLayout()
        self.add_widget(self._piece_layer)

        # Pièce tenue (draggée) — toujours au-dessus
        self._held_img = KivyImage(
            allow_stretch=True, keep_ratio=True,
            size_hint=(None, None), opacity=0,
        )
        self.add_widget(self._held_img)

        self.bind(pos=self._full_refresh, size=self._full_refresh)

    # ── Taille d'une case ─────────────────────────────────────────────────────
    @property
    def sq(self) -> float:
        return min(self.width, self.height) / 8

    # ── Conversion coordonnées écran → case ───────────────────────────────────
    def _screen_to_board(self, sx: float, sy: float):
        """Retourne (x, y) dans le repère plateau, en tenant compte du flip."""
        ox = self.x + (self.width  - self.sq * 8) / 2
        oy = self.y + (self.height - self.sq * 8) / 2
        bx = int((sx - ox) / self.sq)
        by = int((sy - oy) / self.sq)
        # Kivy : y=0 en bas ; le plateau a y=0 en haut → on inverse y
        by = 7 - by
        if self.side == PieceInfo.black:
            bx = 7 - bx
            by = 7 - by
        bx = max(0, min(7, bx))
        by = max(0, min(7, by))
        return bx, by

    # ── Conversion case → coin bas-gauche écran ───────────────────────────────
    def _board_to_screen(self, bx: int, by: int):
        ox = self.x + (self.width  - self.sq * 8) / 2
        oy = self.y + (self.height - self.sq * 8) / 2
        if self.side == PieceInfo.black:
            bx = 7 - bx
            by = 7 - by
        # Kivy y=0 est en bas, plateau y=0 est en haut
        sx = ox + bx * self.sq
        sy = oy + (7 - by) * self.sq
        return sx, sy

    # ─────────────────────────────────────────────────────────────────────────
    #  Rendu
    # ─────────────────────────────────────────────────────────────────────────
    def _full_refresh(self, *_):
        self._draw_background()
        self._draw_valid_moves()
        self._update_piece_widgets()
        self._update_held_piece()

    def _draw_background(self):
        self._board_layer.canvas.clear()
        sq = self.sq
        ox = self.x + (self.width  - sq * 8) / 2
        oy = self.y + (self.height - sq * 8) / 2
        with self._board_layer.canvas:
            for row in range(8):          # row = y dans Kivy (0 = bas)
                for col in range(8):      # col = x
                    if (row + col) % 2 == 1:
                        Color(*C_WHITE)
                    else:
                        Color(*C_BLACK)
                    Rectangle(pos=(ox + col*sq, oy + row*sq), size=(sq, sq))

    def _draw_valid_moves(self):
        # Dessinés par-dessus le fond, dans le même canvas
        sq = self.sq
        board = self.chess_board.position.board
        with self._board_layer.canvas:
            for (bx, by) in self.valid_moves:
                sx, sy = self._board_to_screen(bx, by)
                Color(*C_MOVE)
                if board[bx][by] == PieceInfo.empty:
                    # Point central
                    r = sq / 6
                    Ellipse(
                        pos=(sx + sq/2 - r, sy + sq/2 - r),
                        size=(r*2, r*2),
                    )
                else:
                    # Cercle épais sur case occupée
                    w = max(2, int(sq / 16))
                    Line(
                        circle=(sx + sq/2, sy + sq/2, sq/2 - w),
                        width=w,
                    )

    def _update_piece_widgets(self):
        """Recrée les KivyImage pour chaque pièce sur le plateau."""
        # Supprimer les anciens widgets
        for img in list(self._piece_widgets.values()):
            self._piece_layer.remove_widget(img)
        self._piece_widgets.clear()

        board = self.chess_board.position.board
        sq = self.sq
        for bx in range(8):
            for by in range(8):
                piece = board[bx][by]
                if piece == PieceInfo.empty:
                    continue
                # Ne pas dessiner la pièce tenue (elle suit le doigt)
                if self.piece_held and (bx, by) == self.selected_piece_pos:
                    continue
                path = self._images.get(piece, "")
                if not path or not os.path.exists(path):
                    continue
                sx, sy = self._board_to_screen(bx, by)
                img = KivyImage(
                    source=path,
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint=(None, None),
                    size=(sq, sq),
                    pos=(sx, sy),
                )
                self._piece_layer.add_widget(img)
                self._piece_widgets[(bx, by)] = img

    def _update_held_piece(self):
        if self.piece_held and self.selected_piece_pos:
            bx, by = self.selected_piece_pos
            piece  = self.chess_board.position.board[bx][by]
            path   = self._images.get(piece, "")
            sq     = self.sq
            dx, dy = self._drag_pos
            self._held_img.source  = path if (path and os.path.exists(path)) else ""
            self._held_img.size    = (sq, sq)
            self._held_img.pos     = (dx - sq/2, dy - sq/2)
            self._held_img.opacity = 1
        else:
            self._held_img.opacity = 0

    # ─────────────────────────────────────────────────────────────────────────
    #  Logique jeu  (portage direct de game.py)
    # ─────────────────────────────────────────────────────────────────────────
    def select_piece(self, sx, sy):
        x, y = self._screen_to_board(sx, sy)
        piece = self.chess_board.position.board[x][y]
        if PieceInfo.get_color(piece) == self.chess_board.position.move_color:
            self.selected_piece_pos = (x, y)
            self.valid_moves = self.chess_board.get_piece_moves(x, y)
            self.piece_held  = True
            self._drag_pos   = (sx, sy)

    def unselect(self):
        self.selected_piece_pos = None
        self.valid_moves        = []
        self.piece_held         = False

    def place_piece(self, sx, sy):
        x, y = self._screen_to_board(sx, sy)
        if (x, y) in self.valid_moves:
            self.chess_board.make_move(
                Move(
                    (self.selected_piece_pos[0], self.selected_piece_pos[1]),
                    (x, y),
                    self.chess_board.position.board,
                )
            )
            self.unselect()
            if self.flip_side_mode:
                self._flip_side()
        elif self.piece_held:
            self.piece_held = False
        else:
            piece = self.chess_board.position.board[x][y]
            if PieceInfo.get_color(piece) == self.chess_board.position.move_color:
                self.select_piece(sx, sy)
            else:
                self.unselect()

    def _flip_side(self):
        self.side = (
            PieceInfo.black if self.side == PieceInfo.white else PieceInfo.white
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  Événements tactiles / souris
    # ─────────────────────────────────────────────────────────────────────────
    def on_touch_down(self, touch: MotionEvent):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)

        if touch.button == "right" if hasattr(touch, "button") else False:
            self.unselect()
        else:
            if self.selected_piece_pos is None:
                self.select_piece(*touch.pos)
            else:
                if not self.piece_held:
                    self.place_piece(*touch.pos)
                else:
                    self._drag_pos = touch.pos
        self._full_refresh()
        return True

    def on_touch_move(self, touch: MotionEvent):
        if touch.grab_current is not self:
            return False
        if self.piece_held:
            self._drag_pos = touch.pos
            self._update_held_piece()
        return True

    def on_touch_up(self, touch: MotionEvent):
        if touch.grab_current is not self:
            return False
        touch.ungrab(self)
        if self.piece_held:
            self.place_piece(*touch.pos)
            self._full_refresh()
        return True

    def reset(self):
        self.chess_board        = Board()
        self.selected_piece_pos = None
        self.valid_moves        = []
        self.piece_held         = False
        self._full_refresh()


# ─────────────────────────────────────────────────────────────────────────────
#  StatusBar
# ─────────────────────────────────────────────────────────────────────────────
class StatusBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            padding=[dp(14), dp(6)],
            spacing=dp(10),
            **kwargs,
        )
        with self.canvas.before:
            Color(*C_PANEL)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)

        self._dot = Widget(size_hint=(None, None), size=(dp(14), dp(14)))
        self._dot_rgba = [1, 1, 1, 1]
        self._draw_dot()

        self.label = Label(
            text="Tour des Blancs",
            font_size=dp(16),
            color=C_TEXT,
            bold=True,
            halign="left",
            valign="middle",
        )
        self.label.bind(size=lambda *_: setattr(self.label, "text_size", self.label.size))

        self.flip_btn = Button(
            text="⇄ Flip",
            font_size=dp(13),
            size_hint=(None, 1),
            width=dp(72),
            background_normal="",
            background_color=(*C_ACCENT[:3], 0.15),
            color=C_ACCENT,
        )

        self.reset_btn = Button(
            text="↺ Reset",
            font_size=dp(13),
            size_hint=(None, 1),
            width=dp(72),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=C_ACCENT,
        )

        self.add_widget(self._dot)
        self.add_widget(self.label)
        self.add_widget(self.flip_btn)
        self.add_widget(self.reset_btn)

    def _draw_dot(self):
        self._dot.canvas.clear()
        with self._dot.canvas:
            Color(*self._dot_rgba)
            Ellipse(pos=self._dot.pos, size=self._dot.size)
        self._dot.bind(
            pos=lambda *_: self._repos_dot(),
            size=lambda *_: self._repos_dot(),
        )

    def _repos_dot(self):
        self._dot.canvas.clear()
        with self._dot.canvas:
            Color(*self._dot_rgba)
            Ellipse(pos=self._dot.pos, size=self._dot.size)

    def _upd(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def update(self, move_color):
        if move_color == PieceInfo.white:
            self.label.text = "Tour des Blancs"
            self._dot_rgba  = [0.96, 0.92, 0.84, 1]
        else:
            self.label.text = "Tour des Noirs"
            self._dot_rgba  = [0.10, 0.08, 0.06, 1]
        self._draw_dot()


# ─────────────────────────────────────────────────────────────────────────────
#  Application principale
# ─────────────────────────────────────────────────────────────────────────────
class ChessApp(App):
    title = "Échecs"

    def build(self):
        Window.clearcolor = C_BG

        root = BoxLayout(orientation="vertical", spacing=0, padding=0)

        status_bar = StatusBar()
        root.add_widget(status_bar)

        # Plateau carré centré
        container  = FloatLayout()
        board_widget = BoardWidget()

        def _keep_square(instance, _):
            side = min(instance.width, instance.height)
            board_widget.size_hint = (None, None)
            board_widget.size = (side, side)
            board_widget.pos  = (
                instance.x + (instance.width  - side) / 2,
                instance.y + (instance.height - side) / 2,
            )

        container.bind(size=_keep_square, pos=_keep_square)
        container.add_widget(board_widget)
        root.add_widget(container)

        # Brancher les boutons
        def _on_reset(*_):
            board_widget.reset()
            status_bar.update(board_widget.chess_board.position.move_color)

        def _on_flip(*_):
            board_widget.flip_side_mode = not board_widget.flip_side_mode
            status_bar.flip_btn.background_color = (
                (*C_ACCENT[:3], 0.30) if board_widget.flip_side_mode
                else (*C_ACCENT[:3], 0.10)
            )

        status_bar.reset_btn.bind(on_release=_on_reset)
        status_bar.flip_btn.bind(on_release=_on_flip)

        # Mettre à jour la barre après chaque coup
        def _after_touch(instance, touch):
            status_bar.update(board_widget.chess_board.position.move_color)

        board_widget.bind(on_touch_up=_after_touch)

        return root