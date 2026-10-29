# Snake · 贪吃蛇

一个用 **Python + tkinter** 写的贪吃蛇，单文件、零第三方依赖。

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

## 运行

```bash
python snake.py
```

不需要 `pip install` —— tkinter 是 Python 标准库的一部分（Windows / macOS 官方安装包自带）。

## 操作

| 按键 | 作用 |
|---|---|
| `↑` `↓` `←` `→` 或 `W` `A` `S` `D` | 移动 |
| `空格` | 暂停 / 继续 |
| `R` | 重新开始 |

## 规则

- 吃到红色食物得 **10 分**，蛇身变长一节
- 每吃一个食物，速度提升一点（间隔从 130 ms 逐步降到 60 ms）
- 撞墙或撞到自己 → 游戏结束
- 最高分只记录在本次运行的内存里，关掉窗口就清空

## 实现要点

- **单文件 200 行**，没有第三方库，方便直接读懂和改
- 蛇用 `list` 存格子坐标，头在 `snake[0]`；移动 = 头插一节 + 尾删一节，吃到食物时省略删尾
- 自撞判断会排除尾巴那一格——否则会误判"追着自己的尾尖跑"为碰撞
- 转向进入一个最多两项的队列，防止一帧内连按两次导致 180 度掉头
- 用 `root.after()` 驱动帧循环，不做忙等

## 想改点什么

| 想法 | 改哪里 |
|---|---|
| 棋盘更大 | `COLS, ROWS` |
| 整体更大/更小 | `CELL` |
| 更快 | `START_DELAY` 调小 |
| 颜色 | 文件顶部的颜色常量 |
| 加分更多 | `POINTS` |

## 许可

MIT
