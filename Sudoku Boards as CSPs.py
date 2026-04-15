from collections import deque
import copy
backtrack_calls = 0
backtrack_failures = 0

# Read Sudoku from file
def read_board(filename):
    board = []
    with open(filename, 'r') as f:
        for line in f:
            board.append([int(x) for x in line.strip()])
    return board

# Get all variables (cells)
def get_variables():
    return [(r, c) for r in range(9) for c in range(9)]

# Domain initialization
def init_domains(board):
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                domains[(r, c)] = set(range(1, 10))
            else:
                domains[(r, c)] = {board[r][c]}
    return domains

# Get neighbors (row, col, box)
def get_neighbors(var):
    r, c = var
    neighbors = set()

    # Row + Column
    for i in range(9):
        neighbors.add((r, i))
        neighbors.add((i, c))

    # Box
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            neighbors.add((i, j))

    neighbors.remove(var)
    return neighbors

# AC-3 Algorithm
def ac3(domains):
    queue = deque()

    for xi in domains:
        for xj in get_neighbors(xi):
            queue.append((xi, xj))

    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False
            for xk in get_neighbors(xi):
                if xk != xj:
                    queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    revised = False
    
    if len(domains[xj]) == 1:
        val = next(iter(domains[xj]))
        if val in domains[xi]:
            domains[xi].remove(val)
            revised = True

    return revised

# Select unassigned variable (MRV)
def select_unassigned_variable(domains):
    unassigned = [v for v in domains if len(domains[v]) > 1]
    return min(unassigned, key=lambda var: len(domains[var]))

# Check consistency
def is_consistent(var, value, assignment):
    for neighbor in get_neighbors(var):
        if neighbor in assignment and assignment[neighbor] == value:
            return False
    return True

# Forward Checking
def forward_check(domains, var, value):
    new_domains = copy.deepcopy(domains)
    new_domains[var] = {value}

    for neighbor in get_neighbors(var):
        if value in new_domains[neighbor]:
            new_domains[neighbor].remove(value)
            if len(new_domains[neighbor]) == 0:
                return None

    return new_domains

# Backtracking Search
def backtrack(domains):
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    # Check if solved
    if all(len(domains[v]) == 1 for v in domains):
        return domains

    var = select_unassigned_variable(domains)

    for value in domains[var]:
        if is_consistent(var, value, {v: list(domains[v])[0] for v in domains if len(domains[v]) == 1}):

            new_domains = forward_check(domains, var, value)
            if new_domains is not None:

                if ac3(new_domains):
                    result = backtrack(new_domains)
                    if result is not None:
                        return result

    backtrack_failures += 1
    return None

# Solve function
def solve_sudoku(board):
    global backtrack_calls, backtrack_failures
    backtrack_calls = 0
    backtrack_failures = 0

    domains = init_domains(board)

    if not ac3(domains):
        return None, backtrack_calls, backtrack_failures

    result = backtrack(domains)

    return result, backtrack_calls, backtrack_failures

# Print Board
def print_solution(domains):
    for r in range(9):
        row = []
        for c in range(9):
            row.append(str(list(domains[(r, c)])[0]))
        print(" ".join(row))

files = ["easy.txt", "medium.txt", "hard.txt", "veryhard.txt"]

for f in files:
    print(f"\n===== Solving {f} =====\n")

    board = read_board(f)
    result = solve_sudoku(board)

    if result is None:
        print("No solution found")
    else:
        solution, calls, fails = result
        if solution:
            print_solution(solution)
            print("\nBacktrack Calls:", calls)
            print("Backtrack Failures:", fails)
        else:
            print("No solution found")

# Easy Board
# AC-3 + Forward Checking solved most constraints early
# Very few backtracking steps required
# Medium Board
# More ambiguity then more branching
# Backtracking increased but still manageable
# Hard Board
# Many variables had multiple values
# AC-3 alone insufficient → deeper search needed
# Very Hard Board
# Maximum branching
# Backtracking dominates solving process
# Shows exponential nature of CSP