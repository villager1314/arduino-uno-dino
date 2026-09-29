# Arduino Uno 小恐龙

这是一个由 **Arduino Uno（ATmega328P）负责游戏逻辑**、Windows 电脑上的 **Python/Pygame 负责画面与输入**的横版跑酷游戏。Uno 与电脑通过 CH340 USB 串口通信。

## 硬件要求

- Arduino Uno 或兼容的 ATmega328P 开发板
- CH340 USB 转串口芯片
- 一根连接开发板和 Windows 电脑的 USB 数据线

## 游戏特色

- Uno 负责跳跃、重力、碰撞、计分和难度控制
- 包含仙人掌、飞鸟、火柴人、坦克、毒水坑、飞机和陨石
- 火柴人会发射子弹，坦克会发射炮弹
- 火柴人和坦克可以从上方踩死或踩爆
- 冰红茶提供可叠加护盾，最多储存 9 层
- 分数越高，游戏速度越快
- 每 300 分自动切换白天和夜晚
- 跳跃时 Uno 板载 `L` 灯常亮，死亡后快速闪烁
- 支持暂停、断线提示及 CH340 自动重连
- 动态安全间距可避免无法躲避的障碍组合

## 安装与运行

### 1. 上传 Arduino 固件

使用 Arduino IDE 打开：

```text
uno_platform_game/uno_platform_game.ino
```

选择 **Arduino Uno** 和对应的 CH340 串口，然后上传程序。通信波特率为 `115200`。

上传完成后，请关闭 Arduino IDE 的串口监视器，否则 Python 无法打开同一个串口。

### 2. 安装 Python 依赖

项目支持 Python 3.14，使用 `pygame-ce` 和 `pyserial`：

```powershell
python -m pip install pygame-ce pyserial
```

`pygame-ce` 在代码中仍然通过 `import pygame` 导入。

### 3. 启动游戏

程序通常可以自动识别 CH340 串口：

```powershell
python uno_game.py
```

也可以手动指定端口，例如：

```powershell
python uno_game.py --port COM32
```

## 操作方式

- `空格`、`W`、`↑` 或鼠标左键：跳跃
- `P`：暂停或继续
- `R`：重新开始
- `Esc`：退出游戏

小恐龙本身不会发射武器。面对火柴人和坦克时，可以跳过敌方弹药，或者从敌人上方落下将其踩死。

## Uno 与电脑的分工

Arduino Uno 负责：

- 恐龙的跳跃、重力和落地
- 障碍物与敌人的生成和移动
- 火柴人子弹、坦克炮弹、飞机和陨石
- 碰撞检测、护盾层数和死亡判断
- 分数、最高分、昼夜状态和速度
- 板载 LED 状态

电脑上的 Python/Pygame 负责：

- 获取键盘和鼠标输入
- 通过 USB 串口把输入发送给 Uno
- 接收 Uno 返回的游戏状态
- 绘制恐龙、敌人、障碍物、天气和界面

数据流程：

```text
键盘 / 鼠标
     ↓
Python 发送输入
     ↓ USB 串口
Arduino Uno 计算游戏
     ↓ USB 串口
Python/Pygame 绘制画面
```

拔掉 Uno 后，游戏画面会冻结并显示 `ARDUINO DISCONNECTED`。重新插入开发板后，程序会自动寻找 CH340 串口并恢复连接。
