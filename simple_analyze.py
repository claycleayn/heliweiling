import os
import glob
import csv
from collections import defaultdict

data_dir = "./data"
sampler_stats = {}

for sampler_dir in sorted(glob.glob(f"{data_dir}/sampler_*")):
    csv_file = os.path.join(sampler_dir, "sensor_data.csv")
    if not os.path.exists(csv_file):
        continue
    sampler_id = int(sampler_dir.split('_')[-1])
    temps = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            temps.append(float(row[1]))
    if not temps:
        continue
    sampler_stats[sampler_id] = temps
    print(f"Sampler {sampler_id}: {len(temps)} samples, final temp = {temps[-1]:.2f}")

# 总体统计
all_temps = [t for temps in sampler_stats.values() for t in temps]
if all_temps:
    mean = sum(all_temps) / len(all_temps)
    variance = sum((x - mean) ** 2 for x in all_temps) / len(all_temps)
    std = variance ** 0.5
    print(f"\n=== 总体统计 ===")
    print(f"总采样点数: {len(all_temps)}")
    print(f"平均温度: {mean:.2f} ± {std:.2f}")
    print(f"温度范围: {min(all_temps):.2f} ~ {max(all_temps):.2f}")

    # 按采样机统计
    print("\n各采样机统计：")
    print(f"{'采样机':<8} {'样本数':<8} {'均值':<8} {'标准差':<8} {'最小值':<8} {'最大值'}")
    for sid, temps in sorted(sampler_stats.items()):
        m = sum(temps)/len(temps)
        s = (sum((x-m)**2 for x in temps)/len(temps))**0.5
        print(f"{sid:<8} {len(temps):<8} {m:<8.2f} {s:<8.2f} {min(temps):<8.2f} {max(temps):<8.2f}")
else:
    print("没有找到数据文件")
