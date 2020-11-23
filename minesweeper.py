from copy import deepcopy
from collections import defaultdict
from itertools import product

class Minesweeper:
    
    def __init__(self, map, n):
        # initialise board and do some basic solving
        self.DIRECTIONS = ((-1,-1), (-1, 0), (-1, 1),
                           ( 0,-1), ( 0, 0), ( 0, 1),
                           ( 1,-1), ( 1, 0), ( 1, 1))
        self.CARDINAL_DIRECTIONS = ((-1,0), (1,0), (0,-1), (0,1))
        self.NON_NUMERICS = ('?','x')
        self.NON_ZERO_NUMERICS = (0,'?','x')
        self.updated = True
        self.finished = False
        self.opened = set()
        self.mines, self.mines_remaining, self.mines_found = n, n, 0
        zeros, others = self.make_board(map)
        self.open_surroundings(zeros)
        self.check_neighbours(self.opened.union(others))
        
        
    def solve(self):
        # overall solving method
        # each loop, attempts easier methods
        #     before moving to 'harder' ones
        while not self.finished:
            self.updated = False
            print('Basic opening and marking.')
            self.opened.intersection_update(self.unexhausted)
            self.check_neighbours(self.opened)
            if not self.updated:
                print('Checking if grid is already solved.')
                self.grid_finished_check()
                if not self.updated:
                    print('Finding 1-n patterns.')
                    self.basic_patterns(self.opened)
                    if not self.updated:
                        print('Using rule-based approach.')
                        rules = self.create_rules()
                        old_rules = []
                        self.rule_found = False
                        while rules and not self.updated:
                            rules, old_rules = self.combine_rules(rules, old_rules)
                            self.check_rules(rules)
                        if not self.updated:
                            print('Attempting to solve rules.')
                            rules, block_list = self.create_blocks(old_rules)
                            self.solve_rules(rules, block_list)
                            if not self.updated:
                                print('Grid is not solvable.')
                                return '?'
        return self.__str__(False)
                                
    
    
    def __str__(self, extras=True):
        # used for printing the board or returning the solution
        if extras:
            print('\nThe current board is:\n')
        return '\n'.join([' '.join(map(str, row)) for row in self.board])
    
    def print_reduced(self):
        # prints the 'reduced' board
        print('\nThe reduced board is:\n')
        print('\n'.join([' '.join(map(str, row)) for row in self.reduced_board]))
    
    def make_board(self, map):
        # sets up the board
        zeros = []
        others = []
        self.unexhausted = set()
        self.board = [i.split() for i in map.splitlines()]
        self.len_x = len(self.board)
        self.len_y = len(self.board[0])
        self.free_cells_remaining = self.len_x * self.len_y
        for x in range(self.len_x):
            for y in range(self.len_y):
                self.unexhausted.add((x,y))
                if self.board[x][y] == '0':
                    self.board[x][y] = 0
                    zeros.append((x,y))
                    self.free_cells_remaining -= 1
                elif self.board[x][y] not in self.NON_NUMERICS:
                    self.board[x][y] = int(self.board[x][y])
                    others.append((x,y))
                    self.free_cells_remaining -= 1
        self.reduced_board = deepcopy(self.board)
        return zeros, others
            
    def open_surroundings(self, clear_cells):
        # opens everything around a given cell
        to_open = set()
        for x,y in clear_cells:
            self.unexhausted.remove((x,y))
            for dx,dy in self.DIRECTIONS:
                if self.on_board(x+dx,y+dy):
                    if self.board[x+dx][y+dy] == '?':
                        to_open.add((x+dx, y+dy))
        for cell in to_open:
            self.open_cell(cell)
        return to_open
    
    def open_cell(self, pos):
        # opens a cell (plus does some housekeeping)
        x,y = pos
        self.board[x][y] = open(x,y)
        self.reduced_board[x][y] = open(x,y) - self.count_mines(x,y)
        self.free_cells_remaining -= 1
        self.opened.add(pos)
    
    def mark_surroundings(self, bad_cells):
        # marks everything around a given cell
        to_mark = set()
        for x,y in bad_cells:
            self.unexhausted.remove((x,y))
            for dx,dy in self.DIRECTIONS:
                if self.on_board(x+dx,y+dy):
                    if self.board[x+dx][y+dy] == '?':
                        to_mark.add((x+dx, y+dy))
        for cell in to_mark:
            self.mark_cell(cell)
        return to_mark
    
    def mark_cell(self, pos):
        # marks a cell (plus does some housekeeping)
        x,y = pos
        self.mines_found += 1
        self.mines_remaining -= 1
        self.board[x][y] = self.reduced_board[x][y] = 'x'
        self.free_cells_remaining -= 1
        for dx,dy in self.DIRECTIONS:
            a,b = x+dx,y+dy
            if self.on_board(a,b):
                    if self.reduced_board[a][b] not in self.NON_NUMERICS:
                        self.reduced_board[a][b] -= 1

    def on_board(self, x, y):
        # check to ensure coordinates are on the board
        return 0<=x<=self.len_x - 1 and 0<=y<=self.len_y - 1
    
    def check_neighbours(self, cells):
        # checks neighbouring cells to see if
        #     we can mark or clear everything
        can_open_around = []
        can_mark_around = []
        for x,y in cells:
            mines = self.count_mines(x, y)
            if self.reduced_board[x][y] == 0:
                can_open_around.append((x,y))
            if self.reduced_board[x][y] == self.count_frees(x, y) != 0:
                can_mark_around.append((x,y))
        if can_open_around or can_mark_around:
            self.updated = True
            self.open_surroundings(can_open_around)
            self.mark_surroundings(can_mark_around)
                
    def count_mines(self, x, y):
        # counts the number of mines already around a cell
        mines = 0
        for dx, dy in self.DIRECTIONS:
            a, b=x+dx, y+dy
            if self.on_board(a, b):
                mines += self.board[a][b] == 'x'
        return mines
    
    def count_frees(self, x, y):
        # counts the number of free cells around a cell
        frees = 0
        for dx, dy in self.DIRECTIONS:
            a, b=x+dx, y+dy
            if self.on_board(a, b):
                frees += self.board[a][b] == '?'
        return frees

    def grid_finished_check(self):
        # checks if remaining cells must be all mines
        #     or all clear
        if self.mines_remaining == 0:
            print('No mines remaining. Opening everything.')
            for x in range(self.len_x):
                for y in range(self.len_y):
                    if self.reduced_board[x][y] == '?':
                        self.open_cell((x,y))
            self.finished = self.updated = True
        elif self.mines_remaining == self.free_cells_remaining:
            print('Remaining squares are all mines. Marking everything.')
            for x in range(self.len_x):
                for y in range(self.len_y):
                    if self.reduced_board[x][y] == '?':
                        self.mark_cell((x,y))
            self.finished = self.updated = True
    
    def basic_patterns(self, cells):
        # looks for 1-n patterns
        # this could be done through rules
        #     but it's so common it's clearer what's
        #     happening if we explicitly search for it
        to_open = set()
        to_mark = set()
        for x in range(self.len_x):
            for y in range(self.len_y):
                if self.reduced_board[x][y] == 1:
                    for dx, dy in self.CARDINAL_DIRECTIONS:
                        a,b = x+dx,y+dy
                        if self.on_board(a, b):
                            if self.reduced_board[a][b] not in self.NON_ZERO_NUMERICS:
                                safes, mines = self.one_by_n(x,y,dx,dy)
                                to_open = to_open.union(safes)
                                to_mark = to_mark.union(mines)
        if to_open or to_mark:
            self.updated = True
            for cell in to_open:
                self.open_cell(cell)
            for cell in to_mark:
                self.mark_cell(cell)
        
    def one_by_n(self, x, y, dx, dy):
        # (   x,    y) has 1 in
        # (x+dx, y+dy) has n in
        # need to check for empties in squares past n
        # if n - 1 empties, these are mines and squares past 1 are safe
        n = self.reduced_board[x+dx][y+dy]
        free_squares = []
        test_squares = [(x+2*dx, y+2*dy),
                        (x+2*dx+dy, y+2*dy+dx),
                        (x+2*dx-dy, y+2*dy-dx)]
        for a,b in test_squares:
            if self.on_board(a, b):
                if self.reduced_board[a][b] == '?':
                    free_squares.append((a,b))
        if len(free_squares) == n - 1:
            potential_safe_squares = [(x-dx, y-dy),
                                      (x-dx+dy, y-dy+dx),
                                      (x-dx-dy, y-dy-dx)]
            safe_squares = []
            for a,b in potential_safe_squares:
                if self.on_board(a, b):
                    if self.reduced_board[a][b] == '?':
                        safe_squares.append((a, b))
            return safe_squares, free_squares
        return [], []
    
    def create_rules(self):
        # makes list of rules
        # creates rule for each cell
        #     if we have a (non-zero) number for it
        rules = []
        unknowns = []
        for x in range(self.len_x):
            for y in range(self.len_y):
                if self.reduced_board[x][y] == '?':
                    unknowns.append((x,y))
                elif self.reduced_board[x][y] not in self.NON_ZERO_NUMERICS:
                    possibles = []
                    for dx, dy in self.DIRECTIONS:
                        pos = a, b = x+dx, y+dy
                        if self.on_board(a,b):
                            if self.reduced_board[a][b] == '?':
                                possibles.append(pos)
                    new_rule = Rule(self.reduced_board[x][y], possibles)
                    append = True
                    for other_rule in rules:
                        if new_rule.equals(other_rule):
                            append = False
                            break
                    if append:
                        rules.append(new_rule)
        # adds rule for 'empty cells must contain remaining mines'
        new_rule = Rule(self.mines_remaining, unknowns)
        self.unknowns = unknowns
        append = True
        for other_rule in rules:
            if new_rule.equals(other_rule):
                append = False
                break
        if append:
            rules.append(new_rule)
        return rules
    
    def combine_rules(self, rules, old_rules):
        # loop over rules and combine
        new_rules = []
        # first check pairs within rules
        #    later check across old_rules and rules
        for i in range(len(rules) - 1):
            for j in range(i+1, len(rules)):
                new_rule = rules[i].combine(rules[j])
                if new_rule:
                    append = True
                    # make sure rule is actually new
                    for other_rule in old_rules:
                        if new_rule.equals(other_rule):
                            append = False
                            break
                    for other_rule in rules:
                        if new_rule.equals(other_rule):
                            append = False
                            break
                    for other_rule in new_rules:
                        if new_rule.equals(other_rule):
                            append = False
                            break
                    if append:
                        new_rules.append(new_rule)
        # checks combinations of old rules with rules
        for old_rule in old_rules:
            for rule in rules:
                new_rule = rule.combine(old_rule)
                if new_rule:
                    append = True
                    # make sure rule is actually new
                    for other_rule in old_rules:
                        if new_rule.equals(other_rule):
                            append = False
                            break
                    if append:
                        for other_rule in rules:
                            if new_rule.equals(other_rule):
                                append = False
                                break
                    if append:
                        for other_rule in new_rules:
                            if new_rule.equals(other_rule):
                                append = False
                                break
                    if append:
                        new_rules.append(new_rule)
        return new_rules, old_rules + rules
    
    def check_rules(self, rules):
        # checks if rules have trivial solutions; i.e,
        #     if everything in a rule is safe, or
        #     if everything in a rule is a mine
        to_open = set()
        to_mark = set()
        for rule in rules:
            if rule.mines == 0:
                # open everything in rule
                to_open.update(rule.possibles)
                self.updated = True
            elif rule.mines == rule.len:
                # mark everything in rule
                to_mark.update(rule.possibles)
                self.updated = True
        for cell in to_open:
            self.open_cell(cell)
        for cell in to_mark:
            self.mark_cell(cell)
    
    def create_blocks(self, rules):
        # creates blocks of cells that always occur in rules together
        blocks = defaultdict(list)
        for cell in self.unknowns:
            binary = []
            for rule in rules:
                if cell in rule.possibles:
                    binary.append('1')
                else:
                    binary.append('0')
            key = ''.join(binary)
            blocks[key].append(cell)
        block_list = []
        for block in blocks.values():
            block_list.append(Block(block, min(self.mines_remaining, len(block))))
        for rule in rules:
            rule.block_it(block_list)
        return rules, block_list
    
    def solve_rules(self, rules, block_list):
        # searches for solutions to rules
        # sort list by max_mines
        #     this isn't needed but helps visualising
        block_list.sort(key=lambda x: x.max_mines, reverse=True)
        # max values for blocks in solution
        lengths_list = [x.max_mines for x in block_list]
        # loops over all possible values for blocks
        solutions = []
        for values in product(*[range(length + 1) for length in lengths_list]):
            # avoids checking rules if obviously not a solution
            if sum(values) == self.mines_remaining:
                self.set_block_values(values, block_list)
                is_solution = self.test_rules(rules)
                if is_solution:
                    solutions.append(values)
        # finds max number of mines for each of the blocks
        #     if max is 0, then mine is free
        #     if no block has max of 0, then solution is not unique
        empty_blocks = []
        max_mines = [max(column) for column in zip(*solutions)]
        for i in range(len(max_mines)):
            if not max_mines[i]:
                empty_blocks.append(block_list[i])
        if empty_blocks:
            self.updated = True
            for block in empty_blocks:
                for cell in block.possibles:
                    self.open_cell(cell)

    def set_block_values(self, values, block_list):
        # sets values for blocks
        for i in range(len(block_list)):
            block_list[i].set_value(values[i])
    
    def test_rules(self, rules):
        # checks if block values are a solution
        # a lot of this checking is unnecessary
        #     we could actually just use the original rules
        for rule in rules:
            if not rule.test_rule():
                return False
        return True


class Rule:
    # class for creating rules:
    #     sets in which we know there must be a specific number of mines
    
    def __init__(self, mines, possibles):
        self.mines = mines
        self.possibles = set(possibles)
        self.len = len(possibles)
    
    def equals(self, other):
        # don't need to check mines as sets same => mines same
        return self.possibles == other.possibles
    
    def combine(self, other):
        # checks if rules can be used to infer a new rule
        if self.possibles.isdisjoint(other.possibles):
            return Rule(self.mines + other.mines, self.possibles.union(other.possibles))
        elif self.possibles.issubset(other.possibles):
            return Rule(other.mines - self.mines, other.possibles.difference(self.possibles))
        elif  other.possibles.issubset(self.possibles):
            return Rule(self.mines - other.mines, self.possibles.difference(other.possibles))
        else:
            return False
    
    def block_it(self, block_list):
        # converts set of cells into list of blocks
        new_possibles = []
        for block in block_list:
            if block.possibles[0] in self.possibles:
                new_possibles.append(block)
        self.possibles = new_possibles
    
    def test_rule(self):
        # checks if values for blocks satisfy the rule
        total = sum([block.value for block in self.possibles])
        if total == self.mines:
            return True
        else:
            return False


class Block:
    # class for grouping together sets that always occur together in rules
    
    def __init__(self, possibles, max_mines):
        self.max_mines = max_mines
        self.possibles = possibles
    
    def set_value(self, n):
        # easy helper function for setting values to test
        self.value = n


def solve_mine(map, n):
    # runs everything
    game = Minesweeper(map, n)
    solution = game.solve()
    game.print_reduced()
    print(game)
    print("\nTotal mines:", game.mines)
    print("Found:", game.mines_found)
    print("Remaining:", game.mines_remaining)
    return solution
