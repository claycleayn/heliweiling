#!/bin/bash

# ==========================================
# 电竞选手模拟器 - 批量部署脚本
# ==========================================

# 1. 编译 Docker 镜像 (标记为 esports-simulator:v1)
echo ">>> [1/3] 正在构建 Docker 镜像..."
docker build -t esports-simulator:v1 .

# 2. 创建宿主机的数据挂载目录 (用于把容器里产生的数据映射到外部)
echo ">>> [2/3] 准备挂载目录 ./sim_logs"
mkdir -p ./sim_logs

# 3. 批量启动模拟器实例 (对标PPT要求："批量启动大量的模拟器实例")
INSTANCE_COUNT=5 # 这里我们启动 5 个实例，相当于模拟 5 场比赛同时进行，共并发 50 个选手线程

echo ">>> [3/3] 准备一键拉起 $INSTANCE_COUNT 个模拟器实例..."

for i in $(seq 1 $INSTANCE_COUNT)
do
    # 动态生成比赛 ID，如 MATCH_01, MATCH_02
    CURRENT_MATCH=$(printf "MATCH_%02d" $i)
    
    echo "正在启动实例: $CURRENT_MATCH"
    
    # docker run 解析：
    # -d: 后台运行
    # --name: 给容器命名
    # -e MATCH_ID: 传入环境变量，让脚本知道自己是哪一场比赛
    # -v: 将宿主机的 ./sim_logs 挂载到容器的 /app/logs 目录，这样容器销毁后数据还在
    docker run -d \
        --name "esports_sim_$CURRENT_MATCH" \
        -e MATCH_ID="$CURRENT_MATCH" \
        -v $(pwd)/sim_logs:/app/logs \
        esports-simulator:v1
done

echo ">>> 全部启动完毕！"
echo "你可以使用 'docker ps' 查看运行中的容器。"
echo "生成的并发测试数据将保存在当前目录的 ./sim_logs 文件夹中。"