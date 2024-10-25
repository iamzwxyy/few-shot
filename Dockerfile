FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# 创建模型存储目录
RUN mkdir -p models

# 安装Python依赖
# 注意：实际使用时请替换为具体的requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建执行脚本
RUN echo '#!/bin/bash' > /app/run_training.sh && \
    echo 'set -e' >> /app/run_training.sh && \
    # 1. 数据预处理
    echo 'echo "Step 1: Data Preprocessing"' >> /app/run_training.sh && \
    echo 'python3 parse_data.py' >> /app/run_training.sh && \
    # 2. 生成训练数据
    echo 'for i in {1..6}; do' >> /app/run_training.sh && \
    echo '  python3 doccano.py -d "./data/${i}_ner_train_data.json" -save_p "trains${i}.txt"' >> /app/run_training.sh && \
    echo 'done' >> /app/run_training.sh && \
    # 3. 基线模型训练
    echo 'echo "Step 2: Baseline Model Training"' >> /app/run_training.sh && \
    echo 'python model_training.py' >> /app/run_training.sh && \
    # 4. LSTM生成合成数据
    echo 'echo "Step 3: LSTM Synthetic Data Generation"' >> /app/run_training.sh && \
    echo 'python data_process.py' >> /app/run_training.sh && \
    echo 'python LSTM_model.py' >> /app/run_training.sh && \
    # 5. 数据扩充
    echo 'echo "Step 4: Data Augmentation"' >> /app/run_training.sh && \
    echo 'python data_process1.py' >> /app/run_training.sh && \
    echo 'python model_training.py' >> /app/run_training.sh && \
    # 6. L&R训练
    echo 'echo "Step 5: L&R Training"' >> /app/run_training.sh && \
    echo 'for i in {1..6}; do' >> /app/run_training.sh && \
    echo '  python stack_finetune1.py -t "dataset/trains${i}.txt" -s "models/model${i}"' >> /app/run_training.sh && \
    echo '  python stack_finetune.py -t "dataset/train${i}.txt" -s "models/model${i}-mid"' >> /app/run_training.sh && \
    echo '  python stack_finetune.py -t "dataset/train${i}.txt" -s "models/model${i}-end" -m "models/model${i}/model_best"' >> /app/run_training.sh && \
    echo 'done' >> /app/run_training.sh && \
    # 7. 伪标签处理
    echo 'echo "Step 6: Pseudo-labeling"' >> /app/run_training.sh && \
    echo 'python data_process2.py' >> /app/run_training.sh && \
    echo 'for i in {1..6}; do' >> /app/run_training.sh && \
    echo '  python predict.py -f "dataset/predict.json" -t $i -w "dataset/result${i}.json" -m "models/model${i}/model_best"' >> /app/run_training.sh && \
    echo 'done' >> /app/run_training.sh && \
    echo 'python3 parse_data.py' >> /app/run_training.sh && \
    echo 'python model_training.py' >> /app/run_training.sh && \
    chmod +x /app/run_training.sh

# 设置执行命令
CMD ["/app/run_training.sh"]