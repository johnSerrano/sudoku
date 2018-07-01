import argparse
import math

from collections import defaultdict


class Square(object):
    def __init__(self, digit=None):
        assert digit is None or isinstance(digit, int), "digit is type {}".format(type(digit))
        self.digit = digit
        self.mutable = not digit
        self.potentials = []

    def __str__(self):
        return str(self.digit or '.')


class SudokuBoard(object):
    def __init__(self, raw_board, length=9):
        self.length = length
        self.root = math.sqrt(self.length)
        assert not self.root - int(self.root) # possible float equality bug
        self.root = int(self.root)

        self.load_board(raw_board)

    def __str__(self):
        lines = []
        for line in self.squares:
            lines.append(' '.join([str(s) for s in line]))
        return '\n'.join(lines)
            
    def get_comparable_hash(self):
        strings = []
        for line in self.squares:
            for square in line:
                strings.append(str(square) + '-' + str(sorted(square.potentials)))

        return hash('/'.join(strings))
        
    def load_board(self, raw_board):
        '''
        Loads string data as a sudoku board. The board is a series of lines 
        equal to self.length. Each line is comprised of whitespace separated 
        integers or the characheter '.', used to indicate a blank square. lines 
        are also expected to contain exactly self.length values.
        '''

        lines = raw_board.strip().split('\n')
        assert len(lines) == self.length, 'expected {} lines, got {}'.format(self.length, len(lines))

        squares = [[None] * self.length for _ in range(self.length)]

        for i, line in enumerate(lines):
            chars = line.split()
            assert len(chars) == self.length

            for j, char in enumerate(chars):
                if char == '.':
                    squares[i][j] = Square()
                    continue

                digit = int(char)
                assert 0 < digit <= self.length, 'digit: {}'.format(digit)
                squares[i][j] = Square(digit)

        self.squares = squares

    def get_cell_starts(self):
        return [self.root * i for i in range(self.root)]

    def rule_set_if_one_potential(self):
        for line in self.squares:
            for square in line:
                if not square.digit and len(square.potentials) == 1:
                    square.digit = square.potentials[0]

    def rule_already_exists_in_cell(self):
        # Only one of each digit can exist in a cell
        cell_starts = self.get_cell_starts()

        for start_x in cell_starts:
            for start_y in cell_starts:
                digits_in_cell = []

                # Collect all digits in the cell
                for i in range(self.root):
                    for j in range(self.root):
                        coord_x = start_x + i
                        coord_y = start_y + j
                        square = self.squares[coord_x][coord_y]
                        if square.digit:
                            digits_in_cell.append(square.digit)

                # Remove the digits from each square's potentials
                for i in range(self.root):
                    for j in range(self.root):
                        coord_x = start_x + i
                        coord_y = start_y + j
                        square = self.squares[coord_x][coord_y]
                        if len(square.potentials) != 1:
                            square.potentials = list(set(square.potentials) - set(digits_in_cell))

    def rule_already_exists_in_line(self):
        # get the list of values in each row/column and remove from potentials in that line
        for i in range(self.length):
            digits_in_row = []
            digits_in_col = []

            for j in range(self.length):
                square_row = self.squares[i][j]
                if square_row.digit:
                    digits_in_row.append(square_row.digit)

                square_col = self.squares[j][i]
                if square_col.digit:
                    digits_in_col.append(square_col.digit)

            for j in range(self.length):
                square_row = self.squares[i][j]
                square_row.potentials = list(set(square_row.potentials) - set(digits_in_row))

                square_col = self.squares[j][i]
                square_col.potentials = list(set(square_col.potentials) - set(digits_in_col))
           

    def rule_only_potential_in_cell(self):
        # if a cell is the only one in its cell with a given potential, make that its only potential
        cell_starts = self.get_cell_starts()

        for start_x in cell_starts:
            for start_y in cell_starts:
                potential_count = defaultdict(int)

                # count the number of occurences of a potential value in the cell
                for i in range(self.root):
                    for j in range(self.root):
                        coord_x = start_x + i
                        coord_y = start_y + j
                        square = self.squares[coord_x][coord_y]
                        for potential in square.potentials:
                            potential_count[potential] += 1

                # look for unique potentials
                for i in range(self.root):
                    for j in range(self.root):
                        coord_x = start_x + i
                        coord_y = start_y + j
                        square = self.squares[coord_x][coord_y]
                        for potential in square.potentials:
                            if potential_count[potential] == 1:
                                square.potentials = [potential]
                                break

    def rule_only_potential_in_line(self):
        # if a cell is the only one in a row or column with a given potential, make that its only potential
        for i in range(self.length):
            potential_count_row = defaultdict(int)
            potential_count_col = defaultdict(int)

            for j in range(self.length):
                square_row = self.squares[i][j]
                for potential in square_row.potentials:
                    potential_count_row[potential] += 1

                square_col = self.squares[j][i]
                for potential in square_col.potentials:
                    potential_count_col[potential] += 1

            for j in range(self.length):
                square_row = self.squares[i][j]
                for potential in square_row.potentials:
                    if potential_count_row[potential] == 1:
                        square_row.potentials = [potential]
                        break

                square_col = self.squares[j][i]
                for potential in square_col.potentials:
                    if potential_count_col[potential] == 1:
                        square_col.potentials = [potential]
                        break

    def rule_potentials_in_a_line(self):
        # if all the potentials in a cell for one digit are in a 
        # line, remove all other potentials in a line
        cell_starts = self.get_cell_starts()

        for start_x in cell_starts:
            for start_y in cell_starts:
                potential_x = defaultdict(list)
                potential_y = defaultdict(list)

                for i in range(self.root):
                    for j in range(self.root):
                        coord_x = start_x + i
                        coord_y = start_y + j
                        square = self.squares[coord_x][coord_y]
                        for potential in square.potentials:
                            potential_x[potential].append(coord_x)
                            potential_y[potential].append(coord_y)

                for potential, positions_x in potential_x.iteritems():
                    positions_y = potential_y[potential]

                    if len(set(positions_x)) == 1 and len(set(positions_y)) > 1:
                        coord_x = positions_x[0] 
                        # iterate over every square _not_ in this cell and remove it from potentials
                        for coord_y in range(self.length):
                            if coord_y >= start_x and coord_y < start_x + self.root:
                                continue

                            square = self.squares[coord_x][coord_y]
                            square.potentials = list(set(square.potentials) - set([potential]))

                    if len(set(positions_y)) == 1 and len(set(positions_x)) > 1:
                        coord_y = positions_y[0]

                        for coord_y in range(self.length):
                            if coord_y >= start_y and coord_y < start_y + self.root:
                                continue

                            square = self.squares[coord_x][coord_y]
                            square.potentials = list(set(square.potentials) - set([potential]))

    def apply_rules(self):
        while True:
            before_hash = self.get_comparable_hash()
            
            for name in dir(self):
                if name.startswith('rule_'):
                    getattr(self, name)()

            after_hash = self.get_comparable_hash()
            if after_hash == before_hash:
                break

    def solve(self):
        '''
        Attempt to solve the sudoku board. Fills in as many squares as possible.
        '''
        # set initial potential values
        for line in self.squares:
            for square in line:
                if square.mutable:
                    square.potentials = [i+1 for i in range(self.length)]
                else:
                    square.potentials = [square.digit]

        self.apply_rules()
                

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.file) as f:
        raw_data = f.read()
    board = SudokuBoard(raw_data)

    board.solve()

    print board
    

if __name__ == '__main__':
    main()
