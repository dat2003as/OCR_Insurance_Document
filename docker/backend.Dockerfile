FROM python:3.11-slim

WORKDIR /app

# Cài hệ thống dependencies cho OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và install
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy source code
COPY src ./src
COPY .env.example .env

# Create directories
RUN mkdir -p uploads temp
CMD ["python", "src/main.py"]



