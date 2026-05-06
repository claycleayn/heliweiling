import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

data_dir = "./data"
all_data = []

for sampler_dir in sorted(glob.glob(f"{data_dir}/sampler_*")):
    csv_file = os.path.join(sampler_dir, "sensor_data.csv")
    if not os.path.exists(csv_file):
        continue
    df = pd.read_csv(csv_file)
    df['sampler_id'] = int(sampler_dir.split('_')[-1])
    all_data.append(df)
    print(f"Sampler {sampler_dir.split('_')[-1]}: {len(df)} samples, final temp = {df['temperature'].iloc[-1]:.2f}")

# 合并所有数据
combined = pd.concat(all_data, ignore_index=True)

print("\n=== 总体统计 ===")
print(f"总采样点数: {len(combined)}")
print(f"平均温度: {combined['temperature'].mean():.2f} ± {combined['temperature'].std():.2f}")
print(f"温度范围: {combined['temperature'].min():.2f} ~ {combined['temperature'].max():.2f}")

# 按采样机分组统计
grouped = combined.groupby('sampler_id')['temperature'].agg(['mean', 'std', 'min', 'max'])
print("\n各采样机统计：")
print(grouped)

# 画图：所有采样机的时间序列
plt.figure(figsize=(12, 6))
for sampler_id, group in combined.groupby('sampler_id'):
    plt.plot(group['sample_id'], group['temperature'], label=f'Sampler {sampler_id}', alpha=0.6)
plt.xlabel('Sample ID')
plt.ylabel('Temperature (°C)')
plt.title('Random Temperature Readings from Multiple Samplers')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('temperature_curves.png')
plt.show()