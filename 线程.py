import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random
import queue
import csv
import logging
import os
from datetime import datetime

# ==========================================
# 1. 初始化设置：目录、日志与CSV文件
# ==========================================
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志 (满足 PPT要求：将运行记录存入日志文件)
log_filename = f"logs/simulator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 准备 CSV 数据文件 (满足 PPT要求：产生的数据存入文件)
csv_filename = f"logs/player_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Team', 'PlayerID', 'State', 'HeartRate', 'Respiration', 'BlinkRate', 'SystolicBP', 'DiastolicBP', 'Temperature'])


# ==========================================
# 2. 多线程数据生成器 (核心逻辑)
# ==========================================
class PlayerDeviceThread(threading.Thread):
    """
    模拟单个电竞选手的穿戴设备线程
    满足 PPT要求：多线程模拟设备、让随机数符合统计规律(高斯分布)
    """
    def __init__(self, player_id, team, data_queue):
        super().__init__()
        self.player_id = player_id
        self.team = team
        self.data_queue = data_queue
        self.is_running = True
        
        # 状态机：Normal (平稳发育期), Stress (团战高压期)
        self.state = "Normal" 
        self.stress_timer = 0  # 记录高压状态剩余时间

    def run(self):
        logging.info(f"设备已启动: {self.team} - {self.player_id}")
        while self.is_running:
            # 1. 状态跃迁逻辑 (模拟突发团战事件)
            if self.state == "Normal":
                if random.random() < 0.05:  # 5%的概率突然爆发团战
                    self.state = "Stress"
                    self.stress_timer = random.randint(5, 15) # 团战持续 5-15 秒
                    logging.warning(f"⚠️ {self.player_id} 遭遇突发状况，进入高压状态！")
            else:
                self.stress_timer -= 1
                if self.stress_timer <= 0:
                    self.state = "Normal"
                    logging.info(f"✅ {self.player_id} 恢复平稳状态。")

            # 2. 生成符合统计规律的数据 (使用高斯分布 random.gauss)
            # 均值(mu), 标准差(sigma)
            if self.state == "Normal":
                hr = max(60, int(random.gauss(75, 5)))          # 心跳
                resp = max(12, int(random.gauss(16, 2)))        # 呼吸
                blink = max(5, int(random.gauss(15, 3)))        # 眨眼
                sys_bp = max(90, int(random.gauss(115, 5)))     # 收缩压
                dia_bp = max(60, int(random.gauss(75, 4)))      # 舒张压
                temp = round(random.gauss(36.5, 0.1), 1)        # 体温
            else:
                # 高压状态：心跳加速、呼吸急促、死盯屏幕不眨眼、血压升高、体温微升
                hr = min(180, int(random.gauss(135, 10))) 
                resp = min(40, int(random.gauss(28, 4)))
                blink = max(1, int(random.gauss(5, 2)))         
                sys_bp = min(180, int(random.gauss(145, 8)))
                dia_bp = min(110, int(random.gauss(90, 6)))
                temp = round(random.gauss(37.0, 0.2), 1)

            data = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'team': self.team,
                'player_id': self.player_id,
                'state': self.state,
                'hr': hr, 'resp': resp, 'blink': blink, 
                'sys_bp': sys_bp, 'dia_bp': dia_bp, 'temp': temp
            }

            # 将数据放入队列，交给主线程处理 (GUI更新和写入文件)
            self.data_queue.put(data)
            
            # 模拟设备每秒采集一次数据
            time.sleep(1)

    def stop(self):
        self.is_running = False


# ==========================================
# 3. GUI 可视化看板
# ==========================================
class SimulatorGUI:
    """
    教官端 5v5 数据监控看板
    满足 PPT要求：使用 GUI 窗口监控模拟器运行
    """
    def __init__(self, root):
        self.root = root
        self.root.title("电竞选手生理状态实时监控看板 (5v5)")
        self.root.geometry("1100x750")
        
        self.data_queue = queue.Queue()
        self.threads = []
        self.is_simulating = False
        
        self.setup_ui()
        
        # 启动定时器，从队列中拿取数据更新界面
        self.root.after(100, self.process_queue)

    def setup_ui(self):
        # 顶部控制栏
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(control_frame, text="数据生成频率: 1条/秒/设备", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        self.start_btn = tk.Button(control_frame, text="▶ 启动模拟器 (10线程)", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=20)
        
        self.stop_btn = tk.Button(control_frame, text="⏹ 停止模拟", bg="#F44336", fg="white", font=("Arial", 12, "bold"), command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # 中间看板区
        board_frame = ttk.Frame(self.root, padding=10)
        board_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 红队 (左)
        self.red_frame = tk.LabelFrame(board_frame, text="红队 (Red Team)", fg="red", font=("Arial", 14, "bold"), bg="#FFF0F0")
        self.red_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 蓝队 (右)
        self.blue_frame = tk.LabelFrame(board_frame, text="蓝队 (Blue Team)", fg="blue", font=("Arial", 14, "bold"), bg="#F0F0FF")
        self.blue_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # 生成 10 个选手的 UI 卡片
        self.player_cards = {}
        for i in range(1, 6):
            self.player_cards[f"R{i}"] = self.create_player_card(self.red_frame, f"R{i}", "red")
            self.player_cards[f"B{i}"] = self.create_player_card(self.blue_frame, f"B{i}", "blue")

        # 底部日志区 (修复了 padding 报错问题)
        log_frame = tk.LabelFrame(self.root, text="系统实时日志", padx=5, pady=5)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state='disabled', bg="black", fg="lime", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_player_card(self, parent, player_id, team_color):
        """创建一个选手的状态数据显示卡片"""
        card = tk.Frame(parent, bd=2, relief=tk.GROOVE, bg="white")
        card.pack(fill=tk.X, pady=5, padx=5)
        
        header_color = "#FFCCCC" if team_color == "red" else "#CCCCFF"
        header = tk.Label(card, text=f"Player {player_id}", bg=header_color, font=("Arial", 12, "bold"))
        header.pack(fill=tk.X)
        
        content = tk.Frame(card, bg="white")
        content.pack(fill=tk.X, padx=5, pady=2)
        
        # 数据显示标签
        labels = {}
        fields = [("状态", "state"), ("心跳", "hr"), ("呼吸", "resp"), ("血压", "bp"), ("体温", "temp"), ("眨眼", "blink")]
        
        for idx, (label_text, key) in enumerate(fields):
            tk.Label(content, text=f"{label_text}:", bg="white", font=("Arial", 9)).grid(row=0, column=idx*2, sticky=tk.E)
            val_label = tk.Label(content, text="--", bg="white", font=("Arial", 9, "bold"), width=7, anchor=tk.W)
            val_label.grid(row=0, column=idx*2+1, sticky=tk.W)
            labels[key] = val_label
            
        return labels

    def log_message(self, message):
        """将信息打印到 GUI 的控制台"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def start_simulation(self):
        self.is_simulating = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_message("系统指令: 启动多线程模拟器...")
        
        # 启动 10 个线程 (5个红队，5个蓝队)
        self.threads = []
        for i in range(1, 6):
            t_red = PlayerDeviceThread(f"R{i}", "Red", self.data_queue)
            t_blue = PlayerDeviceThread(f"B{i}", "Blue", self.data_queue)
            self.threads.extend([t_red, t_blue])
            
        for t in self.threads:
            t.daemon = True # 设置为守护线程，主程序关闭时自动退出
            t.start()

    def stop_simulation(self):
        self.is_simulating = False
        self.log_message("系统指令: 正在停止所有设备线程...")
        for t in self.threads:
            t.stop()
            
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def process_queue(self):
        """消费者：处理队列中的数据，更新UI并写入CSV (保证线程安全)"""
        try:
            while True:
                # 非阻塞方式获取队列数据，如果队列为空会抛出 Empty 异常退出循环
                data = self.data_queue.get_nowait()
                pid = data['player_id']
                card = self.player_cards[pid]
                
                # 1. 更新 UI 数值
                card['state'].config(text="高压" if data['state'] == "Stress" else "平稳", fg="red" if data['state'] == "Stress" else "green")
                card['hr'].config(text=f"{data['hr']} bpm")
                card['resp'].config(text=f"{data['resp']} 次/分")
                card['bp'].config(text=f"{data['sys_bp']}/{data['dia_bp']}")
                card['temp'].config(text=f"{data['temp']} ℃")
                card['blink'].config(text=f"{data['blink']} 次/分")
                
                # 如果数值异常（高压状态），背景变红提醒
                bg_color = "#FFE0E0" if data['state'] == "Stress" else "white"
                for label in card.values():
                    label.config(bg=bg_color)
                
                # 同步日志如果进入高压
                if data['state'] == "Stress" and data['hr'] > 130:
                    self.log_message(f"🚨 [警报] {pid} 心跳飙升至 {data['hr']}! 处于极度紧张状态。")

                # 2. 写入 CSV 文件 (满足 PPT要求)
                with open(csv_filename, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        data['timestamp'], data['team'], data['player_id'], data['state'],
                        data['hr'], data['resp'], data['blink'], data['sys_bp'], data['dia_bp'], data['temp']
                    ])
                    
        except queue.Empty:
            pass
        finally:
            # 循环调用自身，达到持续刷新的目的
            self.root.after(100, self.process_queue)


# ==========================================
# 4. 主程序入口
# ==========================================
if __name__ == "__main__":
    logging.info("主程序启动，初始化 GUI 面板...")
    root = tk.Tk()
    
    # 设置全局字体抗锯齿（在部分系统中让字体更好看）
    root.option_add('*Font', 'Arial 10')
    
    app = SimulatorGUI(root)
    root.mainloop()
    
    # 退出程序时的清理工作
    app.stop_simulation()
    logging.info("程序已退出。")