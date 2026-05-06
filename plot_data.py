import json
import matplotlib.pyplot as plt
from datetime import datetime

def plot_robot_data(log_file):
    results = {}

    # 1. 读取并解析数据
    with open(log_file, 'r') as f:
        for line in f:
            try:
                # 提取 JSON 部分
                content = line[line.find('{'):]
                d = json.loads(content)
                
                device_id = d['device_id']
                if device_id not in results:
                    results[device_id] = {'x': [], 'y': []}
                
                # 使用系统记录的时间戳作为 X 轴
                results[device_id]['y'].append(d['temperature'])
                # 简单记录序号作为 X 轴
                results[device_id]['x'].append(len(results[device_id]['y']))
            except:
                continue

    # 2. 开始绘图
    plt.figure(figsize=(12, 6))
    for device_id, data in results.items():
        if device_id == "test": continue # 跳过测试数据
        plt.plot(data['x'], data['y'], label=device_id, linewidth=1.5)

    plt.title('Multi-Robot Sensor Temperature Trend', fontsize=14)
    plt.xlabel('Sample Point', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    # 3. 关键步骤：保存为文件而不是 plt.show()
    output_file = 'trend_analysis.png'
    plt.savefig(output_file)
    print(f"📊 图像已生成并保存为: {output_file}")

if __name__ == "__main__":
    plot_robot_data('received_data.log')