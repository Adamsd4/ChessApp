from board import Board
from pieces import PieceInfo
from move import Move
from utility import get_notation_from_move, get_move_from_notation

from game_ui import Game
# from game_ui_kivy import ChessApp


def get_transpose(plt):
    new_plt = [[0 for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(8):
            new_plt[i][j] = plt[j][i]
    return new_plt

def draw(plt, moves = None):
    for x in range(8):
        for y in range(8):
            piece = plt[y][x]
            if moves is not None and (y, x) in moves:
                print(".", end=" ")
            else:
                print(PieceInfo.get_symbol(piece), end=" ")
        print("")

def test2():
    game_test = Board("2R3R1/6b1/r6k/8/7K/2b2Q1Q/r7/7Q b - - 0 1")

    while True:
        draw(game_test.position.board)

        move_notation = input("move notation: ")
        move = get_move_from_notation(game_test, move_notation)
        while move is None:
            move_notation = input("move notation: ")
            move = get_move_from_notation(game_test, move_notation)

        print(get_notation_from_move(game_test.position, move))
        game_test.update_board(move)


def test():
    game_test = Board()

    while True:
        draw(game_test.position.board)

        x1 = int(input("start_pos x : "))
        y1 = int(input("start_pos y : "))
        while PieceInfo.get_color(game_test.position.board[x1][y1]) != game_test.position.move_color:
            x1 = int(input("start_pos x : "))
            y1 = int(input("start_pos y : "))

        valid_moves = game_test.get_piece_moves(x1, y1)

        draw(game_test.position.board, valid_moves)

        x2 = int(input("target_pos x : "))
        y2 = int(input("target_pos y : "))
        while (x2, y2) not in valid_moves:
            x2 = int(input("target_pos x : "))
            y2 = int(input("target_pos y : "))

        game_test.update_board(Move((x1, y1), (x2, y2), game_test.position.board))

if __name__ == "__main__":
    test2()
    # Game().run()
    # ChessApp().run()
