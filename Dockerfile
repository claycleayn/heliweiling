FROM python:3.9-slim
WORKDIR /app
COPY emitter.py .
RUN pip install requests
CMD ["python", "-u", "emitter.py"]
