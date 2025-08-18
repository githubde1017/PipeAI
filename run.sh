#!/bin/bash

# ====================================================================
# PipeAI 專案執行腳本
# 這個腳本將引導您完成整個標註與模型訓練流程
# ====================================================================

# 1. 檢查與創建必要的資料夾及檔案
echo "--- 1. 檢查並建立必要的資料夾與檔案 ---"

# 檢查 venv 虛擬環境
if [ ! -d "venv" ]; then
    echo "找不到虛擬環境 venv，正在建立..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# 檢查資料夾
if [ ! -d "uploads" ]; then
    echo "建立 uploads 資料夾..."
    mkdir uploads
fi
if [ ! -d "yolo_dataset" ]; then
    echo "建立 yolo_dataset 資料夾..."
    mkdir yolo_dataset
fi

# 檢查檔案
if [ ! -f "annotations.json" ]; then
    echo "建立空白的 annotations.json 檔案..."
    touch annotations.json
fi
if [ ! -f "yolo_dataset.yaml" ]; then
    echo "建立空白的 yolo_dataset.yaml 檔案..."
    touch yolo_dataset.yaml
    echo -e "path: ./yolo_dataset\ntrain: images\nval: images\nnc: 3\nnames: ['裂縫', '積水線段', '異物']" > yolo_dataset.yaml
    echo "已自動填入 yolo_dataset.yaml 內容。"
fi
if [ ! -f "train_yolo.py" ]; then
    echo "建立 train_yolo.py 檔案..."
    echo -e "from ultralytics import YOLO\n\nif __name__ == '__main__':\n    model = YOLO('yolov8n.pt')\n    results = model.train(data='yolo_dataset.yaml', epochs=100, imgsz=640)\n    results = model.val()" > train_yolo.py
    echo "已自動填入 train_yolo.py 內容。"
fi
if [ ! -f "convert_annotations.py" ]; then
    echo "建立 convert_annotations.py 檔案..."
    # 這裡需要您手動貼上 convert_annotations.py 的內容，因為它比較長
    echo "請將 convert_annotations.py 的程式碼貼到此檔案中。"
fi

echo "--- 步驟 1 完成。所有必要檔案已就緒。---"
echo ""

# 2. 標註階段
echo "--- 2. 啟動標註伺服器 ---"
echo "請在瀏覽器中開啟 http://localhost:5001"
echo "上傳影片並進行標註。完成後，回到此終端機，按 Ctrl + C 停止伺服器。"
echo ""
read -p "準備好開始標註了嗎？按 Enter 繼續..."

docker-compose up --build

echo ""
echo "--- 3. 執行資料處理與模型訓練 ---"

# 3.1. 資料轉換
read -p "標註完成並停止伺服器了嗎？按 Enter 開始資料轉換..."
python3 convert_annotations.py

# 3.2. 模型訓練
read -p "資料轉換完成。按 Enter 開始模型訓練..."
python3 train_yolo.py

echo ""
echo "--- 4. 流程結束 ---"
echo "模型訓練已完成。訓練好的模型權重檔案會保存在 runs/detect/train/weights/best.pt"