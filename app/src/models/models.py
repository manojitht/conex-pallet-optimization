import time
import io
import base64
import pulp
import random
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class ContainerOptimizer:
    def __init__(self, length=40, width=8, height=8, weight_limit=29000):
        self.length = length
        self.width = width
        self.height = height
        self.weight_limit = weight_limit
        self.remaining_weight = weight_limit
        self.total_profit = 0
        self.loaded_pallets = []
        
        # 2D Grid representing the floor plan. Stores lists of pallets (stacks)
        self.grid = [[[] for _ in range(self.width)] for _ in range(self.length)]
        self.color_palette = ["#8B4513", "#9932CC", "#00CED1", "#FFA500", "#228B22", "#4169E1", "#DC143C"]

    def greedy_heuristic(self, pallets):
        start_time = time.time()
        
        # OBJECTIVE FUNCTION: Maximize Profit. 
        # Strategy: Sort by Profit Density (Profit / Floor Area)
        pallets.sort(key=lambda p: p['profit'] / (p['length'] * p['width']), reverse=True)

        for index, pallet in enumerate(pallets):
            if self.remaining_weight < pallet['weight']:
                continue # Violates container weight limit

            placed = self._try_place_on_floor(pallet, index)
            if not placed:
                self._try_stack(pallet, index)

        runtime = round(time.time() - start_time, 4)
        
        # Calculate Metrics
        space_utilized = self._calculate_space_utilization()
        weight_utilized = ((self.weight_limit - self.remaining_weight) / self.weight_limit) * 100

        return {
            "algorithm": "Greedy Heuristic",
            "profit": self.total_profit,
            "pallets_loaded": len(self.loaded_pallets),
            "space_utilization": round(space_utilized, 2),
            "weight_utilization": round(weight_utilized, 2),
            "runtime": f"{runtime}s",
            "image_base64": self.visualize()
        }
    
    def milp(self, pallets, time_limit_seconds=180):
        start_time = time.time()
        
        # Initialize the MILP Problem
        prob = pulp.LpProblem("Container_Optimization", pulp.LpMaximize)
        
        N = len(pallets)
        
        # 1. DECISION VARIABLES
        # s_i: 1 if pallet i is selected, 0 otherwise
        s = pulp.LpVariable.dicts("selected", range(N), cat=pulp.LpBinary)
        
        # x, y, z coordinates for the bottom-left corner of each pallet
        x = pulp.LpVariable.dicts("x", range(N), lowBound=0, upBound=self.length, cat=pulp.LpContinuous)
        y = pulp.LpVariable.dicts("y", range(N), lowBound=0, upBound=self.width, cat=pulp.LpContinuous)
        z = pulp.LpVariable.dicts("z", range(N), lowBound=0, upBound=self.height, cat=pulp.LpContinuous)
        
        # Relative positioning variables to prevent overlapping
        l = pulp.LpVariable.dicts("left", [(i, j) for i in range(N) for j in range(N) if i < j], cat=pulp.LpBinary)
        r = pulp.LpVariable.dicts("right", [(i, j) for i in range(N) for j in range(N) if i < j], cat=pulp.LpBinary)
        f = pulp.LpVariable.dicts("front", [(i, j) for i in range(N) for j in range(N) if i < j], cat=pulp.LpBinary)
        b = pulp.LpVariable.dicts("back", [(i, j) for i in range(N) for j in range(N) if i < j], cat=pulp.LpBinary)
        u = pulp.LpVariable.dicts("under", [(i, j) for i in range(N) for j in range(N) if i < j], cat=pulp.LpBinary)
        d = pulp.LpVariable.dicts("above", [(i, j) for i in range(N) for j in range(N) if i < j], cat=pulp.LpBinary)

        # 2. OBJECTIVE FUNCTION
        prob += pulp.lpSum([float(pallets[i]['profit']) * s[i] for i in range(N)]), "Total_Profit"

        # 3. CONSTRAINTS
        # Total Weight Constraint
        prob += pulp.lpSum([float(pallets[i]['weight']) * s[i] for i in range(N)]) <= self.weight_limit, "Weight_Limit"

        # Big M constants (Large enough to deactivate constraints when items aren't selected)
        Mx = self.length
        My = self.width
        Mz = self.height

        for i in range(N):
            # Boundary constraints: Items must fit inside the container if selected
            prob += x[i] + float(pallets[i]['length']) <= self.length + Mx * (1 - s[i])
            prob += y[i] + float(pallets[i]['width']) <= self.width + My * (1 - s[i])
            prob += z[i] + float(pallets[i]['height']) <= self.height + Mz * (1 - s[i])

            # Non-overlapping constraints (Only active if BOTH i and j are selected)
            for j in range(i + 1, N):
                # If both are selected, they must be separated in at least one spatial dimension
                prob += x[i] + float(pallets[i]['length']) <= x[j] + Mx * (1 - l[(i, j)]) + Mx * (2 - s[i] - s[j])
                prob += x[j] + float(pallets[j]['length']) <= x[i] + Mx * (1 - r[(i, j)]) + Mx * (2 - s[i] - s[j])
                
                prob += y[i] + float(pallets[i]['width']) <= y[j] + My * (1 - f[(i, j)]) + My * (2 - s[i] - s[j])
                prob += y[j] + float(pallets[j]['width']) <= y[i] + My * (1 - b[(i, j)]) + My * (2 - s[i] - s[j])
                
                prob += z[i] + float(pallets[i]['height']) <= z[j] + Mz * (1 - u[(i, j)]) + Mz * (2 - s[i] - s[j])
                prob += z[j] + float(pallets[j]['height']) <= z[i] + Mz * (1 - d[(i, j)]) + Mz * (2 - s[i] - s[j])

                # At least one separation direction must be true
                prob += l[(i, j)] + r[(i, j)] + f[(i, j)] + b[(i, j)] + u[(i, j)] + d[(i, j)] >= s[i] + s[j] - 1

        # 4. SOLVE (With Time Limit to prevent infinite hanging)
        solver = pulp.PULP_CBC_CMD(timeLimit=time_limit_seconds, msg=False)
        prob.solve(solver)

        runtime = round(time.time() - start_time, 4)

        # 5. PROCESS RESULTS
        self.total_profit = 0
        self.loaded_pallets = []
        
        if prob.status == pulp.LpStatusOptimal or prob.status == pulp.LpStatusNotSolved: # Might hit time limit but have partial solution
            for i in range(N):
                if pulp.value(s[i]) == 1.0:
                    px = round(pulp.value(x[i]))
                    py = round(pulp.value(y[i]))
                    pz = round(pulp.value(z[i]))
                    
                    pallet = pallets[i]
                    self.loaded_pallets.append({
                        "id": pallet['id'],
                        "position": (px, py, pz),
                        "dimensions": (pallet['length'], pallet['width'], pallet['height']),
                        "color": self.color_palette[i % len(self.color_palette)]
                    })
                    self.remaining_weight -= float(pallet['weight'])
                    self.total_profit += float(pallet['profit'])

        space_utilized = self._calculate_space_utilization()
        weight_utilized = ((self.weight_limit - self.remaining_weight) / self.weight_limit) * 100

        return {
            "algorithm": "Exact Method (MILP)",
            "profit": self.total_profit,
            "pallets_loaded": len(self.loaded_pallets),
            "space_utilization": round(space_utilized, 2),
            "weight_utilization": round(weight_utilized, 2),
            "runtime": f"{runtime}s (Max {time_limit_seconds}s)",
            "image_base64": self.visualize()
        }
    
    def genetic_algorithm(self, pallets, pop_size=40, generations=50, mutation_rate=0.15):
        start_time = time.time()
        N = len(pallets)
        
        def calculate_fitness(chromosome):
            temp_grid = [[[] for _ in range(self.width)] for _ in range(self.length)]
            temp_weight = self.weight_limit
            temp_profit = 0

            for idx in chromosome:
                pallet = pallets[idx]
                if temp_weight < float(pallet['weight']):
                    continue # Skip if too heavy
                
                # Simulated Floor Placement
                placed = False
                for x in range(self.length - int(pallet['length']) + 1):
                    for y in range(self.width - int(pallet['width']) + 1):
                        can_place = True
                        for i in range(int(pallet['length'])):
                            for j in range(int(pallet['width'])):
                                if len(temp_grid[x + i][y + j]) > 0:
                                    can_place = False
                                    break
                            if not can_place: break
                            
                        if can_place:
                            for i in range(int(pallet['length'])):
                                for j in range(int(pallet['width'])):
                                    temp_grid[x + i][y + j].append(pallet)
                            temp_weight -= float(pallet['weight'])
                            temp_profit += float(pallet['profit'])
                            placed = True
                            break
                    if placed: break
                
                if not placed:
                    for x in range(self.length - int(pallet['length']) + 1):
                        for y in range(self.width - int(pallet['width']) + 1):
                            current_height = sum(int(p['height']) for p in temp_grid[x][y])
                            if current_height + int(pallet['height']) > self.height:
                                continue
                                
                            can_stack = True
                            for i in range(int(pallet['length'])):
                                for j in range(int(pallet['width'])):
                                    stack = temp_grid[x + i][y + j]
                                    if not stack:
                                        can_stack = False; break
                                    top = stack[-1]
                                    
                                    if str(top['fragile']).upper() == 'TRUE' or str(top['stackable']).upper() == 'FALSE':
                                        can_stack = False; break
                                        
                                    top_weight = sum(float(p['weight']) for p in stack[1:])
                                    if (top_weight + float(pallet['weight'])) > float(top['max_stack_weight']):
                                        can_stack = False; break
                                if not can_stack: break
                                
                            if can_stack:
                                for i in range(int(pallet['length'])):
                                    for j in range(int(pallet['width'])):
                                        temp_grid[x + i][y + j].append(pallet)
                                temp_weight -= float(pallet['weight'])
                                temp_profit += float(pallet['profit'])
                                placed = True
                                break
                        if placed: break

            return temp_profit

        population = [random.sample(range(N), N) for _ in range(pop_size)]
        
        best_overall_chromosome = None
        best_overall_profit = -1

        for gen in range(generations):
            # Score the population
            fitness_scores = [calculate_fitness(chrom) for chrom in population]
            
            # Track the absolute best layout found so far
            max_fitness_idx = fitness_scores.index(max(fitness_scores))
            if fitness_scores[max_fitness_idx] > best_overall_profit:
                best_overall_profit = fitness_scores[max_fitness_idx]
                best_overall_chromosome = population[max_fitness_idx]

            new_population = []
            
            # Selection (Tournament Selection)
            # Pick 2 random layouts, the one with higher profit gets to breed
            for _ in range(pop_size):
                t1, t2 = random.sample(range(pop_size), 2)
                winner = population[t1] if fitness_scores[t1] > fitness_scores[t2] else population[t2]
                new_population.append(winner)

            # Crossover (Order Crossover - OX1)
            # Combines two parent sequences without duplicating pallets
            for i in range(0, pop_size, 2):
                if i + 1 < pop_size:
                    p1, p2 = new_population[i], new_population[i+1]
                    start, end = sorted(random.sample(range(N), 2))
                    
                    c1 = [-1] * N
                    c1[start:end] = p1[start:end]
                    
                    p2_filtered = [x for x in p2 if x not in c1]
                    idx = 0
                    for j in range(N):
                        if c1[j] == -1:
                            c1[j] = p2_filtered[idx]
                            idx += 1
                            
                    new_population[i] = c1

            # Mutation (Swap Mutation)
            # Randomly swap two pallets in the sequence to explore new layouts
            for i in range(pop_size):
                if random.random() < mutation_rate:
                    idx1, idx2 = random.sample(range(N), 2)
                    new_population[i][idx1], new_population[i][idx2] = new_population[i][idx2], new_population[i][idx1]

            population = new_population

        # Apply the mathematically evolved sequence to the real container
        ordered_pallets = [pallets[i] for i in best_overall_chromosome]
        
        # Ensure container is empty before final pack
        self.remaining_weight = self.weight_limit
        self.total_profit = 0
        self.loaded_pallets = []
        self.grid = [[[] for _ in range(self.width)] for _ in range(self.length)]
        
        for index, pallet in enumerate(ordered_pallets):
            if self.remaining_weight < float(pallet['weight']):
                continue
            
            # We reuse the exact same layout functions you wrote for the Greedy approach
            placed = self._try_place_on_floor(pallet, index)
            if not placed:
                self._try_stack(pallet, index)

        runtime = round(time.time() - start_time, 4)
        space_utilized = self._calculate_space_utilization()
        weight_utilized = ((self.weight_limit - self.remaining_weight) / self.weight_limit) * 100

        return {
            "algorithm": "Genetic Algorithm (GA)",
            "profit": self.total_profit,
            "pallets_loaded": len(self.loaded_pallets),
            "space_utilization": round(space_utilized, 2),
            "weight_utilization": round(weight_utilized, 2),
            "runtime": f"{runtime}s",
            "image_base64": self.visualize()
        }

    def _try_place_on_floor(self, pallet, index):
        for x in range(self.length - pallet['length'] + 1):
            for y in range(self.width - pallet['width'] + 1):
                # Check if space is completely empty
                can_place = True
                for i in range(pallet['length']):
                    for j in range(pallet['width']):
                        if len(self.grid[x + i][y + j]) > 0:
                            can_place = False
                            break
                    if not can_place: break
                
                if can_place:
                    self._register_placement(x, y, 0, pallet, index)
                    return True
        return False

    def _try_stack(self, pallet, index):
        for x in range(self.length - pallet['length'] + 1):
            for y in range(self.width - pallet['width'] + 1):
                # Check stacking constraints across the required footprint
                current_stack_height = sum(p['height'] for p in self.grid[x][y])
                
                # Constraint 1: Height limit
                if current_stack_height + pallet['height'] > self.height:
                    continue

                can_stack = True
                for i in range(pallet['length']):
                    for j in range(pallet['width']):
                        stack = self.grid[x + i][y + j]
                        if not stack:
                            can_stack = False
                            break
                        
                        top_pallet = stack[-1]
                        
                        # Constraint 2 & 3: Fragile & Stackable
                        if str(top_pallet['fragile']).upper() == 'TRUE' or str(top_pallet['stackable']).upper() == 'FALSE':
                            can_stack = False
                            break
                            
                        # Constraint 4: Max Stack Weight
                        current_weight_on_top = sum(p['weight'] for p in stack[1:]) # Weight excluding bottom
                        if (current_weight_on_top + pallet['weight']) > float(top_pallet['max_stack_weight']):
                            can_stack = False
                            break
                            
                if can_stack:
                    self._register_placement(x, y, current_stack_height, pallet, index)
                    return True
        return False

    def _register_placement(self, x, y, z, pallet, index):
        for i in range(pallet['length']):
            for j in range(pallet['width']):
                self.grid[x + i][y + j].append(pallet)
                
        self.loaded_pallets.append({
            "id": pallet['id'],
            "position": (x, y, z),
            "dimensions": (pallet['length'], pallet['width'], pallet['height']),
            "color": self.color_palette[index % len(self.color_palette)]
        })
        self.remaining_weight -= pallet['weight']
        self.total_profit += float(pallet['profit'])

    def _calculate_space_utilization(self):
        total_volume = self.length * self.width * self.height
        used_volume = sum(p['dimensions'][0] * p['dimensions'][1] * p['dimensions'][2] for p in self.loaded_pallets)
        return (used_volume / total_volume) * 100

    def visualize(self):
        # Increased the width of the figure to accommodate two plots
        fig = plt.figure(figsize=(14, 6))
        
        # --- View 1: Rear to Front Perspective ---
        ax1 = fig.add_subplot(121, projection='3d')
        ax1.set_title("Rear to Front Perspective")
        ax1.set_box_aspect((self.length, self.width, self.height))
        
        # --- View 2: Front to Rear Perspective ---
        ax2 = fig.add_subplot(122, projection='3d')
        ax2.set_title("Front to Rear Perspective")
        ax2.set_box_aspect((self.length, self.width, self.height))

        # Apply limits and labels to both axes
        for ax in [ax1, ax2]:
            ax.set_xlim([0, self.length])
            ax.set_ylim([0, self.width])
            ax.set_zlim([0, self.height])
            ax.set_xlabel("Length")
            ax.set_ylabel("Width")
            ax.set_zlabel("Height")

        # Draw the pallets on both axes
        for pallet in self.loaded_pallets:
            x, y, z = pallet["position"]
            dx, dy, dz = pallet["dimensions"]
            color = pallet["color"]
            vertices = [
                [x, y, z], [x + dx, y, z], [x + dx, y + dy, z], [x, y + dy, z],
                [x, y, z + dz], [x + dx, y, z + dz], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]
            ]
            edges = [[vertices[i] for i in face] for face in [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [4, 7, 3, 0]]]
            
            for ax in [ax1, ax2]:
                ax.add_collection3d(Poly3DCollection(edges, facecolors=color, edgecolors='k', alpha=0.8))

        # Set the viewing angles (azim 45 is front-right, azim 225 is back-left)
        ax1.view_init(elev=30, azim=45)
        ax2.view_init(elev=30, azim=225)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    
