#!/bin/bash

# ====================================================================
# PipeAI - 啟動標註伺服器
# ====================================================================

echo "--- 1. 檢查並建立必要的資料夾與檔案 ---"

# 檢查與創建資料夾
if [ ! -d "uploads" ]; then
    echo "建立 uploads 資料夾..."
    mkdir uploads
fi
if [ ! -d "yolo_dataset" ]; then
    echo "建立 yolo_dataset 資料夾..."
    mkdir yolo_dataset
fi

# 檢查與創建檔案
if [ ! -f "annotations.json" ]; then
    echo "建立空白的 annotations.json 檔案..."
    touch annotations.json
fi

echo "--- 2. 啟動標註伺服器 ---"
echo "請在瀏覽器中開啟 http://localhost:5000"
echo "請完成所有影片的標註。完成後，回到此終端機，按 Ctrl + C 停止伺服器。"
echo ""

# 啟動 Docker 服務，並在終端機中顯示日誌
docker-compose up --build

echo ""
echo "標註服務已停止。請執行 ./start_training.sh 繼續下一步。"