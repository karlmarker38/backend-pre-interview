from typing import List, Optional

import attr


@attr.s(auto_attribs=True)
class Cell:
    row: Optional['Row'] = attr.ib(init=False)
    x: int = attr.ib(validator=attr.validators.instance_of(int))
    y: int = attr.ib(validator=attr.validators.instance_of(int))
    value: str = attr.ib(
        converter=int,
        validator=attr.validators.instance_of(int),
    )

    @x.validator
    def x_range(self, _, value):
        if not 0 <= value < 9:
            raise ValueError(f'Position received an invalid x {x}')

    @y.validator
    def y_range(self, _, value):
        if not 0 <= value < 9:
            raise ValueError(f'Position received an invalid y {y}')

    @value.validator
    def value_range(self, attribute, v):
        if not 0 <= v <= 9:
            raise ValueError(f'Cell received an invalid value `{v}`')

    @classmethod
    def from_str_value(cls, x: int, y: int, str_value: str):
        return cls(
            x=x,
            y=y,
            value=str_value,
        )

    @property
    def is_empty(self):
        return self.value == 0

    @property
    def column(self) -> List['Cell']:
        return self.row.board.get_column(self.x)


@attr.s(auto_attribs=True)
class Row:
    ix: int = attr.ib(validator=attr.validators.instance_of(int))
    cells: List[Cell] = attr.ib()

    @ix.validator
    def validate_ix(self, _, v):
        if not 0 <= v < 9:
            raise ValueError(f'Row received invalid ix `{v}`')

    @cells.validator
    def validate_cells(self, _, v):
        if len(v) != 9:
            raise ValueError(f'Row expected 9 cells, but got {len(v)}')

    def __attrs_post_init__(self):
        # reversed relationship
        for cell in self.cells:
            cell.row = self

    def __str__(self):
        return self.ix

    @classmethod
    def from_array(cls, y, array: List[str]) -> 'Row':
        return cls(
            ix=y,
            cells=[Cell.from_str_value(x, y, v) for x, v in enumerate(array)]
        )


@attr.s(auto_attribs=True)
class Grid:
    cells: List['Cell'] = attr.ib()


@attr.s(auto_attribs=True)
class Board:
    rows: List[Row] = attr.ib()

    @rows.validator
    def validate_rows(self, _, v):
        if len(v) != 9:
            raise ValueError(f'Board expected 9 rows, but got {len(v)}')

    def __attrs_post_init__(self):
        # reversed relationship
        for row in self.rows:
            row.board = self
        # assigning cell <-> grid
        grid_length = 3
        for x in range(0, 9, grid_length):
            for y in range(0, 9, grid_length):
                grid_cells = [
                    cell
                    for row in self.rows[y: y + grid_length]
                    for cell in row.cells[x: x + grid_length]
                ]
                grid = Grid(cells=grid_cells)
                for cell in grid_cells:
                    cell.grid = grid

    def __str__(self):
        string = ''
        for row in self.rows:
            for cell in row.cells:
                string += f'{cell.value} '
            string += '\n'
        return string

    @classmethod
    def from_array_of_strings(cls, array: List[str]) -> 'Board':
        return cls(
            rows=[Row.from_array(y, list(row)) for y, row in enumerate(array)]
        )

    def get_column(self, i) -> List['Cell']:
        return [
            row.cells[i]
            for row in self.rows
        ]

    def get_empty_cell(self) -> 'Cell':
        for row in self.rows:
            for cell in row.cells:
                if cell.is_empty:
                    return cell

    def is_valid(self, test_num, cell):
        if any(c.value == test_num for c in cell.row.cells):
            return False
        if any(c.value == test_num for c in cell.column):
            return False
        if any(c.value == test_num for c in cell.grid.cells):
            return False
        return True

    def solve(self):
        cell = self.get_empty_cell()
        # no empty cells = solved
        if not cell:
            return True

        for test_num in range(1, 10):
            if self.is_valid(test_num, cell):
                cell.value = test_num
                if self.solve():
                    return True
                cell.value = 0

        return False


def generate_board_from_file_path(path):
    rows = []
    with open(path) as file:
        file.readline()  # skip first line
        for line in file:
            if line.startswith('G'):
                yield Board.from_array_of_strings(rows)
                rows = []
            else:
                rows.append(line.strip())
    yield Board.from_array_of_strings(rows)


FILE_PATH = './sudoku.txt'
if __name__ == '__main__':
    summed = 0
    for i, board in enumerate(generate_board_from_file_path(FILE_PATH)):
        result = board.solve()
        assert result is True, f'Board \n\n {board}\n\n cannot be solved'
        summed += sum(cell.value for cell in board.rows[0].cells[0:3])
    print(summed)
