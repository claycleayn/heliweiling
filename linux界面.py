import threading
import time
import random
import queue
import csv
import logging
import os
from datetime import datetime

# ==========================================
# 1. 初始化设置：目录与日志
# ==========================================
if not os.path.exists('logs'):
    os.makedirs('logs')

# 获取环境变量（允许在Docker启动时动态传入比赛ID，方便区分不同容器的数据）
MATCH_ID = os.environ.get('MATCH_ID', 'MATCH_001')

log_filename = f"logs/{MATCH_ID}_simulator.log"
csv_filename = f"logs/{MATCH_ID}_player_data.csv"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler() # 同时也输出到控制台，方便 docker logs 查看
    ]
)

# 初始化 CSV 文件头
with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'MatchID', 'Team', 'PlayerID', 'State', 'HeartRate', 'Respiration', 'BlinkRate', 'SystolicBP', 'DiastolicBP', 'Temperature'])

# ==========================================
# 2. 多线程数据生成器 (复用之前验证过的核心逻辑)
# ==========================================
class PlayerDeviceThread(threading.Thread):
    def __init__(self, player_id, team, data_queue):
        super().__init__()
        self.player_id = player_id
        self.team = team
        self.data_queue = data_queue
        self.is_running = True
        self.state = "Normal" 
        self.stress_timer = 0  

    def run(self):
        logging.info(f"设备已连接: {self.team} - {self.player_id}")
        while self.is_running:
            # 状态跃迁逻辑 (模拟突发团战)
            if self.state == "Normal":
                if random.random() < 0.05:
                    self.state = "Stress"
                    self.stress_timer = random.randint(5, 15)
                    logging.warning(f"⚠️ {self.player_id} 突发高压状况！")
            else:
                self.stress_timer -= 1
                if self.stress_timer <= 0:
                    self.state = "Normal"
                    logging.info(f"✅ {self.player_id} 恢复平稳。")

            # 高斯分布生成生理数据
            if self.state == "Normal":
                hr = max(60, int(random.gauss(75, 5)))          
                resp = max(12, int(random.gauss(16, 2)))        
                blink = max(5, int(random.gauss(15, 3)))        
                sys_bp = max(90, int(random.gauss(115, 5)))     
                dia_bp = max(60, int(random.gauss(75, 4)))      
                temp = round(random.gauss(36.5, 0.1), 1)        
            else:
                hr = min(180, int(random.gauss(135, 10))) 
                resp = min(40, int(random.gauss(28, 4)))
                blink = max(1, int(random.gauss(5, 2)))         
                sys_bp = min(180, int(random.gauss(145, 8)))
                dia_bp = min(110, int(random.gauss(90, 6)))
                temp = round(random.gauss(37.0, 0.2), 1)

            data = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'match_id': MATCH_ID,
                'team': self.team,
                'player_id': self.player_id,
                'state': self.state,
                'hr': hr, 'resp': resp, 'blink': blink, 
                'sys_bp': sys_bp, 'dia_bp': dia_bp, 'temp': temp
            }

            self.data_queue.put(data)
            time.sleep(1)

    def stop(self):
        self.is_running = False

# ==========================================
# 3. 数据落盘消费者
# ==========================================
def data_writer_worker(data_queue):
    """独立的后台线程：专门负责从队列中取出数据并写入CSV"""
    logging.info("落盘服务已启动...")
    while True:
        try:
            data = data_queue.get(timeout=3)
            with open(csv_filename, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data['timestamp'], data['match_id'], data['team'], data['player_id'], data['state'],
                    data['hr'], data['resp'], data['blink'], data['sys_bp'], data['dia_bp'], data['temp']
                ])
        except queue.Empty:
            continue
        except Exception as e:
            logging.error(f"写入文件失败: {e}")

# ==========================================
# 4. 主程序入口 (无界面运行模式)
# ==========================================
if __name__ == "__main__":
    logging.info(f"=== 模拟器已启动 | 比赛场次: {MATCH_ID} ===")
    
    data_queue = queue.Queue()
    
    # 启动后台写入线程
    writer_thread = threading.Thread(target=data_writer_worker, args=(data_queue,), daemon=True)
    writer_thread.start()
    
    # 启动 10 个选手的设备线程
    threads = []
    for i in range(1, 6):
        threads.append(PlayerDeviceThread(f"R{i}", "Red", data_queue))
        threads.append(PlayerDeviceThread(f"B{i}", "Blue", data_queue))
        
    for t in threads:
        t.daemon = True
        t.start()
        
    logging.info("所有 10 个设备线程已全部拉起，正在持续产生数据...")
    
    # 保持主线程存活，阻断程序退出
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("接收到终止信号，正在关闭模拟器...")
        for t in threads:
            t.stop()
        logging.info("模拟器已安全退出。")