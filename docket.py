# 使用轻量级的 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将无界面版的核心代码拷贝进容器内
COPY headless_simulator.py /app/

# 设置默认的环境变量（可以在 docker run 时覆盖）
ENV MATCH_ID="DEFAULT_MATCH"

# 容器启动时默认执行的命令
CMD ["python", "headless_simulator.py"]