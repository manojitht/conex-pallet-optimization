from pydantic import BaseModel
from typing import List
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import io
import base64
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class Pallet(BaseModel):
    pallet_id: str
    length: int
    width: int
    height: int
    weight: int
    quantity: int

class ContainerRequest(BaseModel):
    length: int
    width: int
    height: int
    weight_limit: int
    pallets: List[Pallet]

class Container:
    def __init__(self, length, width, height, weight_limit):
        self.length = length
        self.width = width
        self.height = height
        self.weight_limit = weight_limit
        self.remaining_weight = weight_limit
        self.loaded_pallets = []
        self.unloaded_pallets = []
        self.floor_plan = [[None] * self.width for _ in range(self.length)]
        self.stack_columns = {}
        self.color_palette = ["peru", "brown", "darkviolet", "cyan", "orange", "green", "blue", "red", "purple", "yellow", "lime", "gray"]

    def load_pallets(self, pallets):
        pallets.sort(key=lambda p: p.weight, reverse=True)
        for index, pallet in enumerate(pallets):
            for _ in range(pallet.quantity):
                if self.remaining_weight < pallet.weight:
                    self.unloaded_pallets.append(pallet)
                    continue
                placed = False
                for x in range(self.length):
                    for y in range(self.width):
                        if self._can_place_pallet_on_floor(x, y, pallet):
                            self._place_pallet_on_floor(x, y, pallet, index)
                            placed = True
                            break
                    if placed:
                        break
                if not placed:
                    stacked = self._stack_pallet(pallet, index)
                    if not stacked:
                        self.unloaded_pallets.append(pallet)

    def _can_place_pallet_on_floor(self, x, y, pallet):
        if x + pallet.length > self.length or y + pallet.width > self.width:
            return False
        for i in range(pallet.length):
            for j in range(pallet.width):
                if self.floor_plan[x + i][y + j] is not None:
                    return False
        return True

    def _place_pallet_on_floor(self, x, y, pallet, index):
        for i in range(pallet.length):
            for j in range(pallet.width):
                self.floor_plan[x + i][y + j] = pallet
        self.loaded_pallets.append({
            "pallet_id": pallet.pallet_id,
            "position": (x, y, 0),
            "dimensions": (pallet.length, pallet.width, pallet.height),
            "weight": pallet.weight,
            "color": self.color_palette[index % len(self.color_palette)]
        })
        self.remaining_weight -= pallet.weight
        self.stack_columns[(x, y)] = pallet.height

    def _stack_pallet(self, pallet, index):
        for (x, y), height in self.stack_columns.items():
            if height + pallet.height <= self.height:
                self.loaded_pallets.append({
                    "pallet_id": pallet.pallet_id,
                    "position": (x, y, height),
                    "dimensions": (pallet.length, pallet.width, pallet.height),
                    "weight": pallet.weight,
                    "color": self.color_palette[index % len(self.color_palette)]
                })
                self.remaining_weight -= pallet.weight
                self.stack_columns[(x, y)] += pallet.height
                return True
        return False

    def visualize(self):
        fig = plt.figure(figsize=(14, 8))

        # Front View
        ax_front = fig.add_subplot(121, projection='3d')
        ax_front.set_title("Front Perspective")
        ax_front.set_box_aspect((self.length, self.width, self.height))

        # Opposite Side View
        ax_opposite = fig.add_subplot(122, projection='3d')
        ax_opposite.set_title("Opposite Perspective")
        ax_opposite.set_box_aspect((self.length, self.width, self.height))

        # Set limits for both views
        for ax in [ax_front, ax_opposite]:
            ax.set_xlim([0, self.length])
            ax.set_ylim([0, self.width])
            ax.set_zlim([0, self.height])
            ax.set_xlabel("Length (ft)")
            ax.set_ylabel("Width (ft)")
            ax.set_zlabel("Height (ft)")

        for pallet in self.loaded_pallets:
            x, y, z = pallet["position"]
            dx, dy, dz = pallet["dimensions"]
            color = pallet["color"]
            vertices = [
                [x, y, z], [x + dx, y, z], [x + dx, y + dy, z], [x, y + dy, z],
                [x, y, z + dz], [x + dx, y, z + dz], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]
            ]
            edges = [[vertices[i] for i in face] for face in [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [4, 7, 3, 0]]]
            for ax in [ax_front, ax_opposite]:
                ax.add_collection3d(Poly3DCollection(edges, facecolors=color, edgecolors='k', alpha=0.7))

        ax_front.view_init(elev=20, azim=30)
        ax_opposite.view_init(elev=20, azim=-30)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    