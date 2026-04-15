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

# PRECOMPUTE NEIGHBORS FOR SPEED
VARIABLES = [(r, c) for r in range(9) for c in range(9)]
NEIGHBORS = {}

for r, c in VARIABLES:
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
    neighbors.remove((r, c))
    NEIGHBORS[(r, c)] = neighbors

def get_neighbors(var):
    # Now it just does an instant dictionary lookup
    return NEIGHBORS[var]

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
    # For every x in xi's domain, is there a y in xj's domain such that x != y?
    for x in list(domains[xi]):
        # If the only possible value in xj is x, then x is impossible for xi
        if len(domains[xj]) == 1 and x in domains[xj]:
            domains[xi].remove(x)
            revised = True
    return revised

# Select unassigned variable (MRV)
def select_unassigned_variable(domains):
    unassigned = [v for v in domains if len(domains[v]) > 1]

    # Sort primarily by Minimum Remaining Values (MRV)
    # Sort secondarily by the Degree Heuristic (most constraints on unassigned neighbors)
    return min(unassigned, key=lambda var: (
        len(domains[var]),
        -sum(1 for n in get_neighbors(var) if len(domains[n]) > 1)
    ))

# Check consistency
def is_consistent(var, value, assignment):
    for neighbor in get_neighbors(var):
        if neighbor in assignment and assignment[neighbor] == value:
            return False
    return True


def forward_check(domains, var, value):
    # FAST COPY
    new_domains = {k: set(v) for k, v in domains.items()}
    new_domains[var] = {value}

    # Queue holds variables that have been assigned a single value
    # and need to propagate their constraints immediately.
    queue = deque([var])

    while queue:
        current = queue.popleft()
        # Since 'current' is in the queue, its domain size is exactly 1
        val = list(new_domains[current])[0]

        for neighbor in get_neighbors(current):
            if val in new_domains[neighbor]:
                new_domains[neighbor].remove(val)

                # If a neighbor's domain becomes empty, this path is a dead end
                if len(new_domains[neighbor]) == 0:
                    return None

                # CRITICAL FIX: If a neighbor was just reduced to a single value,
                # cascade the forced assignment immediately!
                if len(new_domains[neighbor]) == 1:
                    queue.append(neighbor)

    return new_domains

def backtrack(domains):
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    # Solved state: all variables have exactly one value
    if all(len(domains[v]) == 1 for v in domains):
        return domains

    # Minimum Remaining Values (MRV) heuristic
    var = select_unassigned_variable(domains)

    for value in domains[var]:
        new_domains = forward_check(domains, var, value)

        if new_domains is not None:
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

    # Run AC-3 ONCE at the start to narrow down the initial search space
    if not ac3(domains):
        return None, 0, 0

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
