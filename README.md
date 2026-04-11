
-----

# 📦 2D ConEx Pallet Optimization Solver


This repository contains an advanced algorithmic solution to the **2D ConEx Pallet Optimization Solver**, a heavily constrained variation of the classic 0/1 Knapsack problem. Developed for **IT5082 - Optimization Methods** assignment, this project benchmarks three distinct optimization strategies Exact Methods, Heuristics, and Metaheuristics to evaluate their performance, scalability, and physical feasibility in real-world logistics.

-----

## 📑 Table of Contents

1.  Problem Definition
2.  Data Description
3.  Mathematical Formulation
4.  Optimization Methods
5.  Comparative Evaluation & Results

-----

## 1\. Problem Definition

The objective is to maximize the total profit of loaded pallets inside a standard shipping container (e.g., 20ft or 40ft) while adhering to strict spatial physical, and weight constraints.

Unlike standard bin-packing, this real-world logistics model incorporates:

  * **Volumetric Constraints:** Pallets must not exceed container boundaries.
  * **Weight Capacity:** Total weight must stay within the container's safe working load.
  * **Physical Law Constraints:** \* **Fragility:** Non-stackable or fragile items cannot bear weight.
  * **Max Stack Weight:** The cumulative weight of pallets stacked on top of a base pallet cannot exceed its structural threshold.

-----

## 2\. Data Description

The optimization models are evaluated using a synthetic, logistics-oriented dataset designed to simulate complex loading scenarios. The data provides a stress test for algorithmic scalability.

**Key Pallet Attributes:**

  * `pallet_id`: Unique identifier.
  * `dimensions` (Length, Width, Height): Spatial footprint in feet.
  * `weight`: Physical mass in LBS.
  * `profit`: The economic value of successfully loading the item.
  * `cost`: The Logistics spending charges for the loading the item.
  * `fragile`: Boolean indicating if items can be stacked above it.
  * `stackable`: Boolean indicating if the item can be placed on top of others.
  * `max_stack_weight`: The maximum allowable weight pressure for the item.

-----

## 3\. Mathematical Formulation

To guarantee true optimality, the problem is formulated as a **Mixed-Integer Linear Programming (MILP)** model. The physical geometry is translated into algebraic equations using the "Big-M" method.

![img alt](https://github.com/manojitht/conex-pallet-optimization/blob/87a333e0ca8df6a18ad113a7fb68db320d2130b2/results/mathematic_formulation.png)

-----

## 4\. Optimization Methods

Three distinct approaches were implemented to demonstrate the trade-offs between computational speed and mathematical optimality.

  * **Greedy Heuristic (Baseline):** Sorts pallets by *Profit Density* (Profit/Volume) and sequentially packs them. Extremely fast ($O(n \log n)$), but prone to early local optima and the "Swiss Cheese" fragmentation effect.
  * **Exact Method (MILP via PuLP):** Utilizes the Branch & Bound algorithm to mathematically prove the highest possible profit. Subject to extreme exponential time complexity and memory limits due to $O(N^2)$ binary non-overlap variables.
  * **Genetic Algorithm (GA):** A metaheuristic evolutionary approach. Uses an **Order Crossover (OX1)** sequence optimizer and Swap Mutation. It simulates the physical packing to score "fitness," easily bypassing the RAM limitations of MILP while avoiding the local optima traps of the Greedy approach.

-----

## 5\. Comparative Evaluation & Results (20 datapoints)

The algorithms were tested against the dataset on a standard compute environment. Below is the comparative analysis highlighting the inherent trade-offs between Execution Time and Solution Quality (NP-Hardness).

| Algorithm | Total Profit | Space Utilized | Weight Utilized | Runtime |
| :--- | :--- | :--- | :--- | :--- |
| **Greedy Heuristic** | $14,007 | 53.29% | 16.39% | **0.001s** |
| **Genetic Algorithm (GA)** | $14,884 | 52.30% | 17.16% | 1.808s |
| **Exact Method (MILP)** | **$16,293** | **59.21%** | **20.05%** | 180.23s *(Timeout)* |

### Visualizations

#### 1\. Greedy Heuristic

*Fast execution, but leaves highly fragmented, unusable space due to lack of backtracking.*

![img alt](https://github.com/manojitht/conex-pallet-optimization/blob/fe1f0274d2618643da900fa53c1c1ba3015e389b/results/greedy_heuristic.png)

#### 2\. Genetic Algorithm (GA)

*Achieves higher profit than the heuristic in under 2 seconds by evolving the placement sequence.*

![img alt](https://github.com/manojitht/conex-pallet-optimization/blob/fe1f0274d2618643da900fa53c1c1ba3015e389b/results/genetic_algorithm.png)

#### 3\. Mixed-Integer Linear Programming (MILP)

*Terminated at the 180-second threshold. Found the highest profit layout before timeout, but demonstrates the computational impossibility of reaching true optimality for large $N$ datasets.*

![img alt](https://github.com/manojitht/conex-pallet-optimization/blob/fe1f0274d2618643da900fa53c1c1ba3015e389b/results/milp.png)

### Discussion

The results perfectly illustrate the curse of dimensionality in combinatorial optimization. While **MILP** found the most profitable configuration, its exponential runtime makes it unfeasible for real-time logistics. The **Greedy Heuristic** operates in near real-time but leaves significant revenue on the table. The **Genetic Algorithm** proves to be the most viable middle-ground for production systems, successfully balancing compute time with high-quality, physically feasible loading configurations.