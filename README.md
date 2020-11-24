# minesweeper

minesweeper is a solver for minesweeper games.

This code was written to solve the 'Mine Sweeper' Codewars kata: https://www.codewars.com/kata/57ff9d3b8f7dda23130015fa/. Input and output examples are taken from the kata's test cases.

## Input

* A string, with `?` indicating an unopened cell, and possibly some open `0,...,8` indicating the value of a cell (some open cells will be required for a solution in most cases). Columns should be separated by spaces, and rows by newlines. See example below.

* The number of mines contained in the board.

```
? ? ? ? ? ?
? ? ? ? ? ?
? ? ? 0 ? ?
? ? ? ? ? ?
? ? ? ? ? ?
0 0 0 ? ? ?
```

## Output

* If the board is solvable: a similar string, containing the solved minesweeper board. `x` is used to represent the position of a mine. See example below.
* If the board is not solvable: `'?'`.

```
1 x 1 1 x 1
2 2 2 1 2 2
2 x 2 0 1 x
2 x 2 1 2 2
1 1 1 1 x 1
0 0 0 1 1 1
```

## Strategies

We have 5 strategies, outlined below. Each iteration, we start at the most basic strategy, and attempt, in turn, more complex strategies. Whenever we mark a cell with a basic strategy or open a cell, we begin a new iteration.

### Basic strategies

Note: these could be replaced by Rules (see below).

#### 1. Trivial opening and flagging

For an open cell with value `n`, and `m` mines already around it:
* if `n = m`, we can open all neighbouring unopened cell
* if there are precisely `n - m` neighbouring unopened cells, we can mark these as mines.

#### 2. All mines identified/squares opened

* If there are no mines remaining, we can open all unopened cells.
* If there are as many mines remaining as unopened cells, we can mark everything as a mine.

#### 3. `1-n` patterns

For an open cell with value `1` and a neighbouring cell (parallel to the axis) with value `n`:
* of the cells marked `A` below, exactly `n - 1` or `n` of these must contain mines
* if we can deduce exactly `n - 1` of these cells contain mines, then the cells marked `B` can be opened.

```
B ? ? A
B 1 n A
B ? ? A
```

### Rule-based strategies

Rules are sets of `k` cells, exactly `n` of which must contain mines.

#### 4. Set generation

We first generate a set of rules from the open squares we have.

Suppose we have at least two Rules:
* Rule 1: set `A` contains exactly `n` mines
* Rule 2: set `B` contains exacrly `m` mines

We generate a larger set of rules by repeatedly applying the following operations:
* if `A` and `B` are disjoint, the union of `A` and `B` contains `n + m` mines
* if `A` is a subset of `B`, then `B\A` contains `m - n` mines.

If we find ourselves with a set containing `0` mines, we can open everything in it.
If we find ourselves with a set of `n` cells containing `n` mines, we can mark everything in it as a mine.

#### 5. Exhaustive search

We create Blocks of cells: i.e., cells that only ever appear together in the rules.

Each block can take an integer value between 0 and the size of the block, inclusive.

We iterate over all possible combinations of values, and check whether each combination satisfies the rules: this is a possible solution.

We look through the set of solutions: if there is a block that never contains a mine, then we can open everything in the block. Otherwise, any of the solutions could be possible, and we can't find out more without guessing another cell to open: the board is not solvable through purely logical methods.

