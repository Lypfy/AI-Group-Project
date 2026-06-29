# Escape the maze

Một ứng dụng giao diện đồ họa viết bằng Python giúp mô phỏng và so sánh các thuật toán Tìm kiếm trong Trí tuệ Nhân tạo. Dự án này trực quan hóa cách các thuật toán AI khám phá và tìm đường trong mê cung, bao gồm: Tìm kiếm mù (Uninformed Search), Tìm kiếm có kinh nghiệm (Informed Search), Tìm kiếm cục bộ (Local Search), Tìm kiếm đối kháng (Adversarial Search) và Bài toán thỏa mãn ràng buộc (CSP).

## ✨ Các tính năng chính

- **Giao diện tương tác (GUI)**: Xây dựng bằng Pygame và Pygame GUI, cho phép người dùng quan sát từng bước chạy của thuật toán.
- **Nhiều màn chơi (Levels)**: Các cấu hình mê cung và môi trường khác nhau để thử nghiệm thuật toán.
- **So sánh thuật toán**: Quan sát sự khác biệt về thời gian và cách hoạt động của BFS, DFS, A*, Minimax... trong thời gian thực.
- **Di chuyển tự động (Auto-Move)**: Xem nhân vật tự động di chuyển dọc theo đường đi ngắn nhất đã tìm được.

## 🛠️ Yêu cầu hệ thống

- Python 3.8+
- Pygame
- Pygame GUI

## ⚙️ Cài đặt

1. Clone repository về máy:
   ```bash
   git clone https://github.com/your-username/AI-Group-Project.git
   cd AI-Group-Project/Maze
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install pygame pygame_gui
   ```

## 🚀 Hướng dẫn sử dụng

Chạy file chương trình chính bên trong thư mục `Maze`:

```bash
python main.py
```

- **Select Level (Chọn Màn chơi)**: Thay đổi các mê cung khác nhau từ thanh UI.
- **Run Skill (Chạy thuật toán)**: Chọn một thuật toán từ danh sách và nhấn "Run Skill" để bắt đầu quá trình mô phỏng.
- **Pause/Resume (Tạm dừng/Tiếp tục)**: Tạm dừng hoặc tiếp tục quá trình mô phỏng bất cứ lúc nào.
- **Auto Move (Tự động di chuyển)**: Sau khi tìm được đường đi, nhấn nút này để xem nhân vật di chuyển tới đích.

## 📁 Cấu trúc thư mục

```text
Maze/
├── algorithms/   # Chứa mã nguồn của tất cả các thuật toán AI
├── asset/        # Hình ảnh nhân vật, tileset và font chữ
├── core/         # Vòng lặp game chính, cài đặt và trạng thái game
├── entities/     # Các đối tượng game (Người chơi, Quái vật, v.v.)
├── levels/       # Cấu hình bản đồ mê cung
├── ui/           # Component của giao diện UI
└── main.py       # File chạy chính của chương trình
```

---

# 🎬 Demo Thuật toán

Dưới đây là các hình ảnh GIF minh họa quá trình thực thi của từng thuật toán tìm kiếm.

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
