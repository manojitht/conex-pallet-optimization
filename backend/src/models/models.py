import time
import io
import base64
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
    
