import random
import pandas as pd

PALLET_BASE = {
    "NA": {"length": 1219, "width": 1016},
    "EU": {"length": 1200, "width": 800}
}

PALLET_TYPES = ["FULL", "HALF", "QUARTER"]

GOODS_TYPES = ["Electronics", "Food", "Chemicals", "Furniture", "Pharmaceuticals"]

COST_TABLE = {
    100: {200: 181, 400: 210, 600: 261, 800: 324, 1000: 387},
    300: {200: 351, 400: 411, 600: 495, 800: 579, 1000: 677},
    900: {200: 471, 400: 520, 600: 612, 800: 704, 1000: 754}
}

WEIGHT_BUCKETS = [200, 400, 600, 800, 1000]
DISTANCE_BUCKETS = [100, 300, 900]

MM_TO_FT = 0.00328084

def mm_to_ft(value):
    return int(round(value * MM_TO_FT))

def get_closest_bucket(value, buckets):
    return min(buckets, key=lambda x: abs(x - value))


def compute_cost(weight, distance):
    w = get_closest_bucket(weight, WEIGHT_BUCKETS)
    d = get_closest_bucket(distance, DISTANCE_BUCKETS)
    return COST_TABLE[d][w]


def get_dimensions(base, pallet_size):
    l = base["length"]
    w = base["width"]

    if pallet_size == "FULL":
        return l, w
    elif pallet_size == "HALF":
        return l // 2, w
    else:  # QUARTER
        return l // 2, w // 2


def assign_goods_properties(goods):
    if goods == "Electronics":
        return True, False
    elif goods == "Food":
        return False, True
    elif goods == "Chemicals":
        return random.choice([True, False]), False
    elif goods == "Furniture":
        return False, True
    elif goods == "Pharmaceuticals":
        return True, False


def generate_dataset(n=100):
    data = []

    for i in range(n):
        pallet_origin = random.choice(["NA", "EU"])
        pallet_size = random.choice(PALLET_TYPES)

        base = PALLET_BASE[pallet_origin]
        length_mm, width_mm = get_dimensions(base, pallet_size)

        length = mm_to_ft(length_mm)
        width = mm_to_ft(width_mm)
        height = mm_to_ft(random.randint(800, 1800))
        weight = random.randint(150, 1000)
        distance = random.choice(DISTANCE_BUCKETS)

        goods = random.choice(GOODS_TYPES)
        fragile, stackable = assign_goods_properties(goods)

        cost = compute_cost(weight, distance)
        profit = int(weight * random.uniform(1.5, 3.0))

        max_stack_weight = (
            random.randint(0, 100) if fragile else random.randint(300, 1000)
        )

        data.append({
            "id": f"P{i+1}",
            "origin": pallet_origin,
            "pallet_size": pallet_size,
            "length": length,
            "width": width,
            "height": height,
            "weight": weight,
            "distance": distance,
            "goods": goods,
            "fragile": fragile,
            "stackable": stackable,
            "max_stack_weight": max_stack_weight,
            "cost": cost,
            "profit": profit
        })

    return pd.DataFrame(data)


# Generate dataset
df = generate_dataset(100)

print(df.head())
df.to_csv("pallet_dataset.csv", index=False)

