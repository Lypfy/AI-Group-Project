# AI-Group-Project: Maze Solver AI Engine

<img width="200" height="200" alt="Maze" src="https://github.com/user-attachments/assets/471dbea0-c3bb-44d5-9d83-17ff9376a5fc" />

Đây là dự án AI giải quyết bài toán tìm đường trong mê cung (Maze) sử dụng đa dạng các thuật toán tìm kiếm từ cơ bản đến nâng cao. Ứng dụng cung cấp giao diện trực quan (GUI) được xây dựng bằng Tkinter, cho phép người dùng quan sát quá trình chạy của từng thuật toán trên nhiều bản đồ khác nhau.

## Các thuật toán được hỗ trợ (Algorithms Showcase)

Dưới đây là danh sách các thuật toán đã được cài đặt và template để thêm ảnh động minh họa (GIF) cho từng thuật toán trong tương lai.

### 1. Breadth-First Search (BFS)
Thuật toán tìm kiếm theo chiều rộng, luôn đảm bảo tìm được đường đi ngắn nhất trong đồ thị không trọng số.
<!-- Thêm link ảnh động GIF cho BFS vào src dưới đây -->
<img width="500" alt="BFS Demo" src="TODO_ADD_GIF_LINK_HERE" />

### 2. Depth-First Search (DFS)
Thuật toán tìm kiếm theo chiều sâu, ưu tiên đi sâu vào một nhánh trước khi quay lui.
<!-- Thêm link ảnh động GIF cho DFS vào src dưới đây -->
<img width="500" alt="DFS Demo" src="TODO_ADD_GIF_LINK_HERE" />

### 3. A* Search (A-Star)
Thuật toán tìm kiếm có thông tin (Heuristic), kết hợp giữa ưu điểm của BFS và Greedy để tìm đường đi tối ưu một cách hiệu quả.
<!-- Thêm link ảnh động GIF cho A* vào src dưới đây -->
<img width="500" alt="A-Star Demo" src="TODO_ADD_GIF_LINK_HERE" />

### 4. Greedy Best-First Search (GBFS)
Thuật toán tìm kiếm tham lam, luôn ưu tiên chọn đỉnh có khoảng cách heuristic gần đích nhất.
<!-- Thêm link ảnh động GIF cho GBFS vào src dưới đây -->
<img width="500" alt="GBFS Demo" src="TODO_ADD_GIF_LINK_HERE" />

### 5. Simulated Annealing (SA)
Thuật toán tôi luyện mô phỏng (Local Search), cho phép chấp nhận các bước đi tồi hơn với xác suất giảm dần để thoát khỏi cực đại cục bộ.
<!-- Thêm link ảnh động GIF cho SA vào src dưới đây -->
<img width="500" alt="SA Demo" src="TODO_ADD_GIF_LINK_HERE" />

### 6. Steepest Ascent Hill Climbing (SAHC)
Thuật toán leo đồi dốc nhất (Local Search), luôn chọn nước đi tốt nhất trong số các trạng thái kề.
<!-- Thêm link ảnh động GIF cho SAHC vào src dưới đây -->
<img width="500" alt="SAHC Demo" src="TODO_ADD_GIF_LINK_HERE" />

### 7. Sensorless Search (Belief State)
Thuật toán tìm kiếm không cảm biến (Môi trường phức tạp), xử lý trường hợp agent không biết chính xác vị trí ban đầu của mình.
<!-- Thêm link ảnh động GIF cho Belief State vào src dưới đây -->
<img width="500" alt="Belief State Demo" src="TODO_ADD_GIF_LINK_HERE" />

## Hướng dẫn phát triển

### Thêm thuật toán mới (Add new algorithm)
1. Thêm file chứa thuật toán mới vào trong thư mục `Maze/algorithms/` tương ứng (Ví dụ: `Maze/algorithms/uninformed/dfs.py`).
2. Thêm dòng import ở đầu file `Maze/ui/app_window.py`:
   ```python
   from algorithms.uninformed.dfs import DFS
   ```
3. Cập nhật dictionary `self.algorithms` trong file `Maze/ui/app_window.py`:
   ```python
   self.algorithms = { 
       "Breadth-First Search (BFS)": BFS, 
       "A* Search (A-Star)": AStar, 
       "Depth-First Search (DFS)": DFS # <--- THÊM DÒNG NÀY LÀ XONG 
   }
   ```

### Thêm bản đồ mới (Add new map)
Vào trong file `Maze/core/map.py` để thêm mảng (matrix) level mới cho màn mới và câu gợi ý (hint), sau đó cập nhật dictionary `MAPS`.
