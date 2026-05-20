"""
================================================================================
RESCUE MISSION ORDER - AI COURSE PROJECT
--------------------------------------------------------------------------------
Yossef Ahmed Abd Elkareem
================================================================================
"""

import numpy as np
import random
import matplotlib.pyplot as plt
from time import time
from collections import deque

# --- 1. Environment & Setup ---
def create_env(size=20):
    grid = np.zeros((size, size))
    # Creating a complex 20x20 maze to demonstrate GA optimization power 
    for _ in range(120): 
        grid[random.randint(0,19), random.randint(0,19)] = 1
    
    # Ensuring entities are placed on non-wall cells
    free_cells = [(r, c) for r in range(size) for c in range(size) if grid[r,c] == 0]
    pts = random.sample(free_cells, 6)
    return grid, pts[0], pts[1:]

# --- 2. BFS Pathfinding (Search Task) ---
def get_bfs(grid, start, end):
    """Calculates actual shortest distance ignoring straight-line paths """
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end: return len(path)-1, path
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<20 and 0<=nc<20 and grid[nr,nc]==0 and (nr,nc) not in visited:
                visited.add((nr,nc))
                queue.append(((nr,nc), path + [(nr,nc)]))
    # Return infinity if path is blocked (Edge Case Handling)
    return float('inf'), []

# --- 3. Genetic Algorithm Components ---
def fitness(chrom, dist_matrix):
    """
    LOGIC: Fitness = 1/Total_Distance. 
    Since GA maximizes fitness, this forces the minimization of distance.
    If distance is infinity (trapped victim), fitness is 0 (Penalty).
    """
    dist = dist_matrix[0, chrom[0]] + sum(dist_matrix[chrom[i], chrom[i+1]] for i in range(4)) + dist_matrix[chrom[4], 0]
    if dist == float('inf') or dist == 0: return 0
    return 1.0 / dist

def ox_crossover(p1, p2):
    """
    LOGIC: Ordered Crossover (OX1) is used because chromosomes are permutations.
    Standard crossover causes duplicate victims; OX1 preserves unique visit order.
    """
    c = [None]*5
    a, b = sorted(random.sample(range(5), 2))
    c[a:b+1] = p1[a:b+1]
    p2_rem = [x for x in p2 if x not in c]
    idx = 0
    for i in range(5):
        if c[i] is None:
            c[i] = p2_rem[idx]; idx += 1
    return c

# --- 4. Main Execution ---
def main():
    print("-" * 50)
    print("RESCUE MISSION OPTIMIZATION START")
    print("-" * 50)
    
    grid, robot, victims = create_env()
    all_pts = [robot] + victims
    
    # BFS Phase: Building the 6x6 Distance Matrix 
    t0 = time()
    dist_matrix = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            if i != j: 
                dist_matrix[i,j], _ = get_bfs(grid, all_pts[i], all_pts[j])
    
    bfs_t = (time() - t0) * 1000
    print(f"\n[Requirement] Distance Matrix (6x6):\n{dist_matrix.astype(float)}")
    print(f"\nBFS Construction Time: {bfs_t:.2f}ms")

    # GA Phase: Finding the optimal visit sequence
    t0 = time()
    pop = [random.sample([1,2,3,4,5], 5) for _ in range(50)]
    for _ in range(100):
        fits = [fitness(ind, dist_matrix) for ind in pop]
        best_chrom = pop[np.argmax(fits)]
        new_pop = [best_chrom] # Elitism (keep best)
        while len(new_pop) < 50:
            # Tournament Selection (Selection Task) 
            p1 = max(random.sample(list(zip(pop, fits)), 3), key=lambda x: x[1])[0]
            p2 = random.choice(pop)
            child = ox_crossover(p1, p2)
            if random.random() < 0.1: # Swap Mutation
                i, j = random.sample(range(5), 2)
                child[i], child[j] = child[j], child[i]
            new_pop.append(child)
        pop = new_pop
    
    ga_t = (time() - t0) * 1000
    
    # Final Result Output
    final_fit = max(fits)
    best_dist = 1.0/final_fit if final_fit > 0 else float('inf')
    print(f"GA Optimization Time: {ga_t:.2f}ms")
    print(f"Best Rescue Order: Robot -> {best_chrom} -> Robot")
    print(f"Total Path Distance: {best_dist} units")

    # Visualization: Plotting Grid and Winding Path
    plt.imshow(grid, cmap='gray', alpha=0.5)
    plt.grid(which='both', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    plt.plot(robot[1], robot[0], 'bs', markersize=12, label="Robot")
    for i, v in enumerate(victims): 
        plt.plot(v[1], v[0], 'ro')
        plt.text(v[1], v[0]-0.5, f"V{i+1}", color='red', weight='bold')
    
    # Draw actual walking paths (Avoiding Walls)
    seq = [0] + best_chrom + [0]
    for i in range(len(seq)-1):
        _, path = get_bfs(grid, all_pts[seq[i]], all_pts[seq[i+1]])
        if path: plt.plot([p[1] for p in path], [p[0] for p in path], 'g--', linewidth=2)
    
    plt.title(f"20x20 Rescue Mission | Best Distance: {best_dist:.1f}\nBFS: {bfs_t:.1f}ms | GA: {ga_t:.1f}ms\nBest Rescue Order: | Robot -> {best_chrom} -> Robot |")
    plt.show()


if __name__ == "__main__": 
    main()
