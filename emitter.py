#!/usr/bin/env python3
import time
import os
import requests
import sys

CLOUD_API = "http://101.37.231.199:8080/data"    # 确保有双斜杠
WATCH_FILE = "/data/sensor_data.csv"

def send_data(line):
    line = line.strip()
    if not line:
        return
    parts = line.split(',')
    if len(parts) != 2:
        return
    # 跳过 CSV 表头行
    if parts[0] == 'sample_id':
        return
    try:
        sample_id = int(parts[0])
        temp = float(parts[1])
    except ValueError:
        # 忽略不是数字的行
        return

    payload = {
        "device_id": os.environ.get("DEVICE_ID", "unknown"),
        "sample_id": sample_id,
        "temperature": temp,
        "timestamp": time.time()
    }
    try:
        resp = requests.post(CLOUD_API, json=payload, timeout=2)
        if resp.status_code == 200:
            print(f"发送成功: {payload['device_id']} sample {sample_id}")
        else:
            print(f"发送失败 HTTP {resp.status_code}: {resp.text}", file=sys.stderr)
    except Exception as e:
        print(f"发送异常: {e}", file=sys.stderr)

def main():
    print("Emitter 已启动，等待数据文件...")
    while not os.path.exists(WATCH_FILE):
        time.sleep(1)
    print(f"数据文件 {WATCH_FILE} 已就绪，开始监控...")
    last_line_count = 0
    with open(WATCH_FILE, 'r') as f:
        while True:
            lines = f.readlines()
            if len(lines) > last_line_count:
                for line in lines[last_line_count:]:
                    send_data(line)
                last_line_count = len(lines)
            time.sleep(0.5)

if __name__ == "__main__":
    main()