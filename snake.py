"""贪吃蛇 —— 单文件 tkinter 实现，零第三方依赖。

运行：python snake.py
操作：方向键 / WASD 控制，空格暂停，R 重开。
"""

import random
import tkinter as tk

# ---------- 外观参数 ----------
CELL = 26                 # 每格像素
COLS, ROWS = 20, 20       # 棋盘格数
W, H = COLS * CELL, ROWS * CELL

BG = "#0d1117"            # 背景（深色）
GRID = "#161b22"          # 网格线
HEAD = "#56d364"          # 蛇头
BODY = "#2ea043"          # 蛇身
FOOD = "#f85149"          # 食物
FG = "#c9d1d9"            # 主文字
MUTED = "#8b949e"         # 次要文字

# ---------- 玩法参数 ----------
START_DELAY = 130         # 初始每步间隔（毫秒），越小越快
MIN_DELAY = 60            # 最快速度
SPEED_UP = 4              # 每吃一个食物提速的毫秒数
POINTS = 10               # 每个食物的分数

DIRS = {
    "Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0),
    "w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0),
    "W": (0, -1), "S": (0, 1), "A": (-1, 0), "D": (1, 0),
}


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Snake · 贪吃蛇")
        root.configure(bg=BG)
        root.resizable(False, False)

        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", padx=14, pady=(12, 6))
        self.score_label = tk.Label(bar, text="分数 0", bg=BG, fg=FG,
                                    font=("Consolas", 13, "bold"))
        self.score_label.pack(side="left")
        self.best_label = tk.Label(bar, text="最高 0", bg=BG, fg=MUTED,
                                   font=("Consolas", 13))
        self.best_label.pack(side="right")

        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG,
                                highlightthickness=0)
        self.canvas.pack(padx=14, pady=(0, 14))

        root.bind("<Key>", self.on_key)

        self.best = 0
        self.after_id = None
        self.reset()
        self.draw()

    # ---------------- 状态 ----------------

    def reset(self) -> None:
        """把局面恢复到开局状态（不动最高分）。"""
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]  # 头在列表首位
        self.dir = (1, 0)
        self.queue = []          # 缓存最多两个转弯，避免一帧内连按丢输入
        self.score = 0
        self.delay = START_DELAY
        self.state = "ready"     # ready / playing / paused / over
        self.food = self.spawn_food()
        self.update_labels()

    def spawn_food(self):
        blocked = set(self.snake)
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in blocked]
        return random.choice(free) if free else None

    def update_labels(self) -> None:
        self.score_label.config(text=f"分数 {self.score}")
        self.best_label.config(text=f"最高 {max(self.best, self.score)}")

    # ---------------- 循环 ----------------

    def start(self) -> None:
        self.state = "playing"
        self.schedule()

    def schedule(self) -> None:
        self.after_id = self.root.after(self.delay, self.tick)

    def tick(self) -> None:
        if self.state != "playing":
            return
        self.step()
        self.draw()
        if self.state == "playing":
            self.schedule()

    def step(self) -> None:
        # 取一个待执行的转向，忽略 180 度掉头
        if self.queue:
            d = self.queue.pop(0)
            if d != (-self.dir[0], -self.dir[1]):
                self.dir = d

        hx, hy = self.snake[0]
        nx, ny = hx + self.dir[0], hy + self.dir[1]

        # 撞墙
        if not (0 <= nx < COLS and 0 <= ny < ROWS):
            self.game_over()
            return

        eating = (nx, ny) == self.food
        # 不吃食物时尾巴会移走，所以判断自撞要排除尾巴那一格
        body = set(self.snake if eating else self.snake[:-1])
        if (nx, ny) in body:
            self.game_over()
            return

        self.snake.insert(0, (nx, ny))
        if eating:
            self.score += POINTS
            self.delay = max(MIN_DELAY, self.delay - SPEED_UP)
            self.food = self.spawn_food()
            self.update_labels()
            if self.food is None:      # 铺满棋盘
                self.finish("通关！", "按 R 再来一局")
                return
        else:
            self.snake.pop()

    def game_over(self) -> None:
        self.best = max(self.best, self.score)
        self.finish("游戏结束", "按 R 重新开始")
        self.update_labels()

    def finish(self, title: str, hint: str) -> None:
        self.state = "over"
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.draw(title, hint)

    # ---------------- 输入 ----------------

    def on_key(self, event) -> None:
        key = event.keysym

        if key in DIRS:
            if self.state == "ready":
                self.start()
            elif self.state == "over":
                self.reset()
                self.start()
            elif self.state == "paused":
                self.state = "playing"
                self.schedule()
            d = DIRS[key]
            if d != (-self.dir[0], -self.dir[1]) and len(self.queue) < 2:
                self.queue.append(d)
            return

        if key in ("r", "R"):
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.reset()
            self.draw()
            return

        if key in ("space", "Space"):
            if self.state == "playing":
                self.state = "paused"
                if self.after_id:
                    self.root.after_cancel(self.after_id)
                    self.after_id = None
                self.draw("已暂停", "按空格继续")
            elif self.state == "paused":
                self.state = "playing"
                self.schedule()
                self.draw()

    # ---------------- 绘制 ----------------

    def draw(self, title: str = "", hint: str = "") -> None:
        c = self.canvas
        c.delete("all")

        # 网格
        for i in range(COLS + 1):
            c.create_line(i * CELL, 0, i * CELL, H, fill=GRID)
        for j in range(ROWS + 1):
            c.create_line(0, j * CELL, W, j * CELL, fill=GRID)

        # 食物
        if self.food:
            fx, fy = self.food
            c.create_oval(fx * CELL + 5, fy * CELL + 5,
                          (fx + 1) * CELL - 5, (fy + 1) * CELL - 5,
                          fill=FOOD, outline="")

        # 蛇（倒序画，让蛇头压在最上面）
        for i in range(len(self.snake) - 1, -1, -1):
            x, y = self.snake[i]
            pad = 2 if i == 0 else 3
            c.create_rectangle(x * CELL + pad, y * CELL + pad,
                               (x + 1) * CELL - pad, (y + 1) * CELL - pad,
                               fill=HEAD if i == 0 else BODY, outline="")

        if self.state == "ready":
            self.overlay("准备开始", "按方向键出发")
        elif self.state == "paused":
            self.overlay(title or "已暂停", hint or "按空格继续")
        elif self.state == "over":
            self.overlay(title or "游戏结束", hint or "按 R 重新开始")

    def overlay(self, title: str, hint: str) -> None:
        c = self.canvas
        c.create_rectangle(0, 0, W, H, fill=BG, outline="", stipple="gray50")
        c.create_text(W / 2, H / 2 - 16, text=title, fill=FG,
                      font=("Microsoft YaHei", 22, "bold"))
        c.create_text(W / 2, H / 2 + 22, text=hint, fill=MUTED,
                      font=("Microsoft YaHei", 12))
        if self.state == "over":
            c.create_text(W / 2, H / 2 + 52, text=f"本局 {self.score} 分",
                          fill=FG, font=("Consolas", 12))


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
