# 🤖 AI Maze Search Algorithms

A Python-based graphical application to visualize and compare various Artificial Intelligence search algorithms in a maze environment. This project demonstrates how different AI algorithms explore and find paths, including Uninformed Search, Informed Search, Local Search, Adversarial Search, and Constraint Satisfaction Problems (CSP).

## ✨ Features

- **Interactive GUI**: Built with Pygame and Pygame GUI, allowing users to watch the algorithms step-by-step.
- **Multiple Levels**: Different maze configurations and environments to test algorithms.
- **Algorithm Comparison**: Observe how algorithms like BFS, DFS, A*, and Minimax behave in real-time.
- **Auto-Move**: Watch the agent follow the final computed path.

## 🛠️ Requirements

- Python 3.8+
- Pygame
- Pygame GUI

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/AI-Group-Project.git
   cd AI-Group-Project/Maze
   ```
2. Install the required dependencies:
   ```bash
   pip install pygame pygame_gui
   ```

## 🚀 Usage

Run the main application file from the `Maze` directory:

```bash
python main.py
```

- **Select Level**: Choose different maze levels from the UI.
- **Run Skill**: Select an algorithm and click "Run Skill" to see it in action.
- **Pause/Resume**: Pause the visualization at any time.
- **Auto Move**: Once the path is found, click to see the character move along the path.

## 📁 Project Structure

```text
Maze/
├── algorithms/   # Core implementations of all AI search algorithms
├── asset/        # Images, spritesheets, and fonts
├── core/         # Main application loop, settings, and game state
├── entities/     # Game objects (Player, Monsters, etc.)
├── levels/       # Maze maps and level loaders
├── ui/           # GUI components and theme configurations
└── main.py       # Entry point of the application
```

---

# 🎬 Algorithm Demonstrations

The following GIFs demonstrate the execution process of each implemented search algorithm.

---

## 📚 Uninformed Search

<table align="center">
<tr>
<td align="center">

### Breadth-First Search (BFS)

<img src="./gif/uninform/bfs.gif" width="420">

</td>

<td align="center">

### Depth-First Search (DFS)

<img src="./gif/uninform/dfs.gif" width="420">

</td>
</tr>
</table>

---

## 🎯 Informed Search

<table align="center">
<tr>
<td align="center">

### Greedy Best-First Search

<img src="./gif/inform/greedy.gif" width="420">

</td>

<td align="center">

### A* Search

<img src="./gif/inform/a_star.gif" width="420">

</td>
</tr>
</table>

---

## 🏔️ Local Search

<table align="center">
<tr>
<td align="center">

### Hill Climbing

<img src="./gif/local/hill_climb.gif" width="420">

</td>

<td align="center">

### Simulated Annealing

<img src="./gif/local/annealing.gif" width="420">

</td>
</tr>
</table>

---

## 🌍 Complex Environment Search

<table align="center">
<tr>
<td align="center">

### Belief State DFS

<img src="./gif/complex_environment/belief_state.gif" width="420">

</td>

<td align="center">

### Partially Observable BFS

<img src="./gif/complex_environment/partially.gif" width="420">

</td>
</tr>
</table>

---

## 🧩 Constraint Satisfaction Problems (CSP)

<table align="center">
<tr>
<td align="center">

### Forward Checking

<img src="./gif/csp/forward_checking.gif" width="420">

</td>

<td align="center">

### Min-Conflict

<img src="./gif/csp/min_conflict.gif" width="420">

</td>
</tr>
</table>

---

## ♟️ Adversarial Search

<table align="center">
<tr>
<td align="center">

### Alpha-Beta Pruning

<img src="./gif/adversarial/alpha_beta.gif" width="420">

</td>

<td align="center">

### Minimax

<img src="./gif/adversarial/minimax.gif" width="420">

</td>
</tr>
</table>

# 🎬 Algorithm Demonstrations

Các ảnh GIF dưới đây minh họa quá trình thực thi của từng thuật toán tìm kiếm đã được cài đặt.

---

## 📚 Uninformed Search

<table align="center">
<tr>
<td align="center">

### Breadth-First Search (BFS)

<img src="./gif/uninform/bfs.gif" width="420">

</td>

<td align="center">

### Depth-First Search (DFS)

<img src="./gif/uninform/dfs.gif" width="420">

</td>
</tr>
</table>

---

## 🎯 Informed Search

<table align="center">
<tr>
<td align="center">

### Greedy Best-First Search

<img src="./gif/inform/greedy.gif" width="420">

</td>

<td align="center">

### A* Search

<img src="./gif/inform/a_star.gif" width="420">

</td>
</tr>
</table>

---

## 🏔️ Local Search

<table align="center">
<tr>
<td align="center">

### Hill Climbing

<img src="./gif/local/hill_climb.gif" width="420">

</td>

<td align="center">

### Simulated Annealing

<img src="./gif/local/annealing.gif" width="420">

</td>
</tr>
</table>

---

## 🌍 Complex Environment Search

<table align="center">
<tr>
<td align="center">

### Belief State DFS

<img src="./gif/complex_environment/belief_state.gif" width="420">

</td>

<td align="center">

### Partially Observable BFS

<img src="./gif/complex_environment/partially.gif" width="420">

</td>
</tr>
</table>

---

## 🧩 Constraint Satisfaction Problems (CSP)

<table align="center">
<tr>
<td align="center">

### Forward Checking

<img src="./gif/csp/forward_checking.gif" width="420">

</td>

<td align="center">

### Min-Conflict

<img src="./gif/csp/min_conflict.gif" width="420">

</td>
</tr>
</table>

---

## ♟️ Adversarial Search

<table align="center">
<tr>
<td align="center">

### Alpha-Beta Pruning

<img src="./gif/adversarial/alpha_beta.gif" width="420">

</td>

<td align="center">

### Minimax

<img src="./gif/adversarial/minimax.gif" width="420">

</td>
</tr>
</table>
