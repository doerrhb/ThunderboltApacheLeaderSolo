from engine.config import *

def get_hex_positions(board_x, board_y, layout):

    positions = []

    start_x = board_x + FIRST_HEX_TOP_VERTEX[0] - (HEX_WIDTH // 2)
    start_y = board_y + FIRST_HEX_TOP_VERTEX[1]

    for row_index, count in enumerate(layout):

        if row_index == 1:
            row_x = start_x - (HEX_WIDTH // 2)
        else:
            row_x = start_x

        row_y = start_y + row_index * VERTICAL_STEP

        for col_index in range(count):
            x = row_x + col_index * HORIZONTAL_STEP
            y = row_y
            positions.append((x, y))

    return positions