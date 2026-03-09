from typing import List
from app.schemas.board_schema import BingoCell


def has_bingo(board: List[List[BingoCell]]) -> bool:
    size = len(board)

    # check rows
    for row in board:
        if all(cell.completed for cell in row):
            return True

    # check columns
    for col in range(size):
        if all(board[row][col].completed for row in range(size)):
            return True

    # check main diagonal
    if all(board[i][i].completed for i in range(size)):
        return True

    # check anti-diagonal
    if all(board[i][size - 1 - i].completed for i in range(size)):
        return True

    return False
