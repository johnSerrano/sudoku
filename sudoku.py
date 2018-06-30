import argparse
import math


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

    def rule_set_if_one_potential(self):
        for line in self.squares:
            for square in line:
                if not square.digit and len(square.potentials) == 1:
                    square.digit = square.potentials[0]

    def rule_already_exists_in_cell(self):
        # get list of values in cell and remove from potentials of all in cell
        number_of_cells = self.root
        cell_starts = [number_of_cells * i for i in range(number_of_cells)]

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
                        assert len(square.potentials) != 0

    def rule_already_exists_in_line(self):
        # get the list of values in each row/column and remove from potentials in that line
        pass

    def rule_only_potential_in_cell(self):
        # if a cell is the only one in its cell with a given potential, make that its only potential
        pass

    def rule_only_potential_in_line(self):
        # if a cell is the only one in a row or column with a given potential, make that its only potential
        pass

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
