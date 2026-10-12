import json
from random import choices
from pieces import *

white = 0
black = 1

class Game:
    def __init__(self):
        self.practice = False
        self.gameover = False
        self.gagnant = None
        self.opening = []
        self.game = []

        self.side = white
        self.tour = white
        self.nb_move = 0
        self.error = 0
        self.piece_pos = {"p": [], "f": [], "c": [], "t": [], "d": [], "r": [],
                          "P": [], "F": [], "C": [], "T": [], "D": [], "R": []}
        self.arrows = []
        self.plateau = []
        self.init_plateau()
        if self.practice:
            self.pick_opening()

    def reset(self):
        self.practice = False
        self.gameover = False
        self.gagnant = None
        self.opening = []
        self.game = []

        self.side = black
        self.tour = white
        self.nb_move = 0
        self.error = 0
        self.piece_pos = {"p": [], "f": [], "c": [], "t": [], "d": [], "r": [],
                          "P": [], "F": [], "C": [], "T": [], "D": [], "R": []}
        self.arrows = []
        self.plateau = []
        self.init_plateau()
        if self.practice:
            self.pick_opening()

    def init_plateau(self):
        for y in range(8):
            self.plateau.append([Piece() for _ in range(8)])

            for x in range(8):

                if y == 1:
                    self.plateau[y][x] = Pion(black, "pion", x, y)
                    self.piece_pos["p"].append((y, x))

                elif y == 6:
                    self.plateau[y][x] = Pion(white, "pion", x, y)
                    self.piece_pos["P"].append((y, x))

                elif y == 0:
                    if x == 0 or x == 7:
                        self.plateau[y][x] = Tour(black, "tour", x, y)
                        self.piece_pos["t"].append((y, x))
                    elif x == 1 or x == 6:
                        self.plateau[y][x] = Cavalier(black, "cavalier", x, y)
                        self.piece_pos["c"].append((y, x))
                    elif x == 2 or x == 5:
                        self.plateau[y][x] = Fou(black, "fou", x, y)
                        self.piece_pos["f"].append((y, x))
                    elif x == 3:
                        self.plateau[y][x] = Dame(black, "dame", x, y)
                        self.piece_pos["d"].append((y, x))
                    elif x == 4:
                        self.plateau[y][x] = Roi(black, "roi", x, y)
                        self.piece_pos["r"].append((y, x))

                elif y == 7:
                    if x == 0 or x == 7:
                        self.plateau[y][x] = Tour(white, "tour", x, y)
                        self.piece_pos["T"].append((y, x))
                    elif x == 1 or x == 6:
                        self.plateau[y][x] = Cavalier(white, "cavalier", x, y)
                        self.piece_pos["C"].append((y, x))
                    elif x == 2 or x == 5:
                        self.plateau[y][x] = Fou(white, "fou", x, y)
                        self.piece_pos["F"].append((y, x))
                    elif x == 3:
                        self.plateau[y][x] = Dame(white, "dame", x, y)
                        self.piece_pos["D"].append((y, x))
                    elif x == 4:
                        self.plateau[y][x] = Roi(white, "roi", x, y)
                        self.piece_pos["R"].append((y, x))

                else:
                    self.plateau[y][x] = 0

    def pick_opening(self):
        with open("openings.json", "r", encoding="utf-8") as file:
            openings = json.load(file)
        if self.side == white:
            self.opening = choices(openings["white"], weights=openings["white_probability"], k=1)[0]
        else:
            self.opening = choices(openings["black"], weights=openings["black_probability"], k=1)[0]

    def changer_joueur(self):
        self.tour = black if self.tour == white else white

    def change_side(self):
        self.side = black if self.side == white else white

    def is_roque(self, piece, x):
        return piece.name == "roi" and abs(piece.x - x) == 2

    def play_move(self, piece, y, x):
        coups_valides = []
        if self.is_roque(piece, x):
            coups_valides = self.verif_roque(piece)

        if piece.name == "roi" and (piece.x - x == -2 or piece.x - x == 2):
            roque = self.verif_roque(piece)
            if (y, x) in roque: # and (not self.practice or self.check_move(piece, y, x)):
                self.valider_roque(piece, y, x)
        else:
            pass

    def verif_move(self, piece, y, x):
        if piece.name == "roi" and (piece.x - x == -2 or piece.x - x == 2):
            roque = self.verif_roque(piece)

            if (y, x) not in roque or (self.practice and not self.check_move(piece, y, x)):
                return False
            else:
                self.valider_roque(piece, y, x)
                return True
        else:
            coups_valides = piece.get_coups_valides(self.plateau)

            coups_valides = self.simulate_moves(coups_valides, piece)

            if (y, x) not in coups_valides or (self.practice and not self.check_move(piece, y, x)):
                return False
            else:
                self.valider_move(piece, y, x)
                return True

    def valider_move(self, piece, y, x):
        if self.plateau[y][x] != 0:
            captured_piece = self.plateau[y][x]
            if captured_piece.color == white:
                self.piece_pos[captured_piece.name[0].upper()].remove((captured_piece.y, captured_piece.x))
            else:
                self.piece_pos[captured_piece.name[0]].remove((captured_piece.y, captured_piece.x))

        if piece.name == "pion" or piece.name == "roi" or piece.name == "tour":
            piece.first_move = False

        if piece.name == "pion" and (y == 7 or y == 0):
            self.dame(piece, y, x)

        else:
            self.get_piece_pos(piece, y, x)
            self.game.append(self.write_move(piece, y, x))
            self.plateau[y][x], self.plateau[piece.y][piece.x] = piece, 0
            piece.y, piece.x = y, x

        self.nb_move += 1
        self.changer_joueur()
        if not self.practice:
            self.change_side()
        fin = self.verif_fin()
        if fin:
            self.get_gagnant()

    def get_piece_pos(self, piece, y, x):
        if piece.color == white:
            self.piece_pos[piece.name[0].upper()].remove((piece.y, piece.x))
            self.piece_pos[piece.name[0].upper()].append((y, x))
        else:
            self.piece_pos[piece.name[0]].remove((piece.y, piece.x))
            self.piece_pos[piece.name[0]].append((y, x))

    def dame(self, piece, y, x):
        if piece.color == white:
            self.piece_pos["P"].remove((piece.y, piece.x))
            self.plateau[y][x] = Dame(white, "dame", x, y)
            self.piece_pos["D"].append((y, x))
        else:
            self.piece_pos["p"].remove((piece.y, piece.x))
            self.plateau[y][x] = Dame(black, "dame", x, y)
            self.piece_pos["d"].append((y, x))

        self.plateau[piece.y][piece.x] = 0

    def simulate_moves(self, coups_valides, piece):
        coups_invalides = []
        for coup in coups_valides:
            y, x = coup[0], coup[1]
            save_piece = self.plateau[y][x]
            self.plateau[y][x], self.plateau[piece.y][piece.x] = piece, 0

            pos_roi = self.search_roi()

            coups_ennemis = self.get_enemy_moves()
            if pos_roi in coups_ennemis:
                coups_invalides.append(coup)

            self.plateau[y][x], self.plateau[piece.y][piece.x] = save_piece, piece

        coups_valides = list(set(coups_valides) - set(coups_invalides))
        return coups_valides

    def search_roi(self):
        for y in range(8):
            for x in range(8):
                piece = self.plateau[y][x]
                if piece != 0:
                    if piece.name == "roi" and piece.color == self.tour:
                        return y, x
        return False

    def get_enemy_moves(self):
        coups_ennemis = []
        for y in range(8):
            for x in range(8):
                piece = self.plateau[y][x]
                if piece != 0 and piece.color != self.tour:
                    coups_ennemis += piece.get_coups_valides(self.plateau)
        return coups_ennemis

    def get_gagnant(self):
        self.gameover = True

        pos_roi = self.search_roi()

        coups_ennemis = self.get_enemy_moves()

        if pos_roi in coups_ennemis:
            if self.tour == white:
                self.gagnant = black
            else:
                self.gagnant = white
        else:
            self.gagnant = False

    def verif_fin(self):
        for y in range(8):
            for x in range(8):
                piece = self.plateau[y][x]
                if piece != 0 and piece.color == self.tour:
                    coups_valides = self.simulate_moves(piece.get_coups_valides(self.plateau), piece)
                    if coups_valides:
                        return False
        return True

    def verif_roque(self, piece):
        roque = []
        coups_ennemis = self.get_enemy_moves()
        if piece.first_move:

            if (piece.y, piece.x) in coups_ennemis:
                return roque

            erreur = False
            for x in range(piece.x + 1, 7):
                if self.plateau[piece.y][x] != 0 or (piece.y, x) in coups_ennemis:
                    erreur = True
                    break

            if not erreur:
                if self.plateau[piece.y][7] != 0 and self.plateau[piece.y][7].name == "tour":
                    if self.plateau[piece.y][7].first_move:
                        roque.append((piece.y, 6))

            erreur = False
            for x in range(piece.x - 1, 0, -1):
                if self.plateau[piece.y][x] != 0 or (piece.y, x) in coups_ennemis:
                    erreur = True
                    break

            if not erreur:
                if self.plateau[piece.y][0] != 0 and self.plateau[piece.y][0].name == "tour":
                    if self.plateau[piece.y][0].first_move:
                        roque.append((piece.y, 2))

        return roque

    def valider_roque(self, piece, y, x):
        if x == 6:
            x_tour_i = 7
            x_tour_f = 5
            self.game.append("O-O")

        else:
            x_tour_i = 0
            x_tour_f = 3
            self.game.append("O-O-O")

        tour = self.plateau[y][x_tour_i]
        piece.first_move = False
        tour.first_move = False

        self.get_piece_pos(piece, y, x)
        self.get_piece_pos(tour, y, x_tour_f)
        self.plateau[y][x], self.plateau[piece.y][piece.x] = piece, 0
        self.plateau[y][x_tour_f], self.plateau[y][x_tour_i] = tour, 0
        piece.y, piece.x = y, x
        tour.y, tour.x = y, x_tour_f

        self.nb_move += 1
        self.changer_joueur()
        if not self.practice:
            self.change_side()
        fin = self.verif_fin()
        if fin:
            self.get_gagnant()

    def play_opening_move(self, move):
        convert = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7,
                   "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
        if move == "O-O":
            if self.tour == white:
                y, x = 7, 6
                pos = self.piece_pos["R"][0]
                piece = self.plateau[pos[0]][pos[1]]
            else:
                y, x = 0, 6
                pos = self.piece_pos["r"][0]
                piece = self.plateau[pos[0]][pos[1]]
            self.valider_roque(piece, y, x)
        elif move == "O-O-O":
            if self.tour == white:
                y, x = 7, 2
                pos = self.piece_pos["R"][0]
                piece = self.plateau[pos[0]][pos[1]]
            else:
                y, x = 0, 2
                pos = self.piece_pos["r"][0]
                piece = self.plateau[pos[0]][pos[1]]
            self.valider_roque(piece, y, x)
        else:
            move = list(move)
            if "x" in move:
                move.remove("x")
            if "=" in move:
                pass
            else:
                if move[0].isupper():
                    y, x = convert[move[-1]], convert[move[-2]]
                    if self.tour == black:
                        pieces = self.search_piece(move[0].lower(), y, x)
                    else:
                        pieces = self.search_piece(move[0], y, x)
                    if len(move) == 4:
                        piece = None
                        for p in pieces:
                            if convert[move[1]] == p.x:
                                piece = p
                    else:
                        piece = pieces[0]
                    self.valider_move(piece, y, x)
                else:
                    y, x = convert[move[-1]], convert[move[-2]]
                    if self.tour == black:
                        pieces = self.search_piece("p", y, x)
                    else:
                        pieces = self.search_piece("P", y, x)
                    if len(move) == 3:
                        piece = None
                        for p in pieces:
                            if convert[move[0]] == p.x:
                                piece = p
                    else:
                        piece = pieces[0]
                    self.valider_move(piece, y, x)

    def search_piece(self, name, y, x):
        pieces = []
        for piece_pos in self.piece_pos[name]:
            piece = self.plateau[piece_pos[0]][piece_pos[1]]
            if (y, x) in piece.get_coups_valides(self.plateau):
                pieces.append(piece)
        return pieces

    def write_move(self, piece, y, x):
        move = ""
        convert_x = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        convert_y = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
        if piece.name == "roi" and (piece.x - x == -2 or piece.x - x == 2):
            if x == 6:
                return "O-O"
            else:
                return "O-O-O"
        elif piece.name != "pion":
            move += piece.name[0].upper()

            if self.plateau[y][x] != 0:
                move += "x"
        elif self.plateau[y][x] != 0:
            move += convert_x[piece.x]
            move += "x"

        move += convert_x[x]
        move += convert_y[y]

        return move

    def pos_to_fen(self):
        n = 0
        fen = ""
        convert = {"pion": "p", "fou": "b", "cavalier": "n", "tour": "r", "dame": "q", "roi": "k"}
        for y, row in enumerate(self.plateau):
            if y != 0:
                if n != 0:
                    fen += str(n)
                    n = 0
                fen += "/"
            for x, piece in enumerate(row):
                if piece == 0:
                    n += 1
                else:
                    if n != 0:
                        fen += str(n)
                        n = 0

                    if piece.color == white:
                        fen += convert[piece.name].upper()
                    else:
                        fen += convert[piece.name]
        return fen

    def pick_move(self):
        if self.nb_move >= len(self.opening)-1:
            self.add_arrows(self.opening[self.nb_move])
            self.gameover = True
            self.gagnant = self.side
        else:
            self.play_opening_move(self.opening[self.nb_move])

    def check_move(self, piece, y, x):
        if self.opening[self.nb_move] == self.write_move(piece, y, x):
            return True
        else:
            self.error += 1
            return False

    def add_arrows(self, arrows):
        convert = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7,
                   "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
        for arrow in arrows:
            self.arrows.append((convert[arrow[0]], convert[arrow[1]], convert[arrow[2]], convert[arrow[3]]))
