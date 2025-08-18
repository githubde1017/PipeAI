#!/bin/bash

# ====================================================================
# PipeAI - 啟動資料處理與模型訓練
# ====================================================================

# 啟動虛擬環境
. venv/bin/activate

echo "--- 1. 檢查並建立必要的訓練檔案 ---"

# 檢查與創建訓練相關檔案
if [ ! -f "yolo_dataset.yaml" ]; then
    echo "建立 yolo_dataset.yaml 檔案..."
    echo -e "path: ./yolo_dataset\ntrain: images\nval: images\nnc: 3\nnames: ['裂縫', '積水線段', '異物']" > yolo_dataset.yaml
fi

if [ ! -f "train_yolo.py" ]; then
    echo "建立 train_yolo.py 檔案..."
    echo -e "from ultralytics import YOLO\n\nif __name__ == '__main__':\n    model = YOLO('yolov8n.pt')\n    results = model.train(data='yolo_dataset.yaml', epochs=100, imgsz=640)\n    results = model.val()" > train_yolo.py
fi

if [ ! -f "convert_annotations.py" ]; then
    echo "錯誤：找不到 convert_annotations.py 檔案。請確保該檔案已存在。"
    exit 1
fi

echo "--- 2. 開始資料轉換 ---"
python3 convert_annotations.py

echo "--- 3. 開始模型訓練 ---"
python3 train_yolo.py

echo ""
echo "--- 4. 流程結束 ---"
echo "模型訓練已完成。訓練好的模型權重檔案通常保存在 runs/detect/train/weights/best.pt"