#!/bin/bash

# =========================================================
# PipeAI 全自動訓練腳本
# 這個腳本將自動執行從資料擷取到模型訓練的所有步驟
# =========================================================

echo "--- 1. 啟動虛擬環境 ---"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "錯誤：無法啟動虛擬環境。請確認 'venv' 資料夾存在。"
    exit 1
fi
echo "虛擬環境已啟動。"

# --- 2. 檢查必要的檔案和資料夾 ---
echo "--- 2. 檢查必要檔案 ---"
if [ ! -f .env ]; then
    echo "錯誤：找不到 .env 檔案。請確保它存在於專案根目錄。"
    exit 1
fi
if [ ! -f class_config.json ]; then
    echo "錯誤：找不到 class_config.json 檔案。請確保它存在於專案根目錄。"
    exit 1
fi
echo "必要檔案檢查通過。"

# --- 3. 執行畫格擷取 (正常影片) ---
echo "--- 3. 擷取正常影片畫格 ---"
python3 extract/extract_normal.py
if [ $? -ne 0 ]; then
    echo "錯誤：擷取正常影片畫格失敗。請檢查影片路徑和檔名。"
    exit 1
fi
echo "正常影片畫格擷取完成。"

# --- 4. 執行畫格擷取 (異常影片) ---
echo "--- 4. 擷取異常影片畫格 ---"
python3 extract/extract_abnormal.py
if [ $? -ne 0 ]; then
    echo "警告：擷取異常影片畫格失敗。可能是因為 annotations.json 為空。繼續..."
fi
echo "異常影片畫格擷取完成。"

# --- 5. 執行資料集整合 ---
echo "--- 5. 整合資料集並備份標註 ---"
python3 convert_annotations.py
if [ $? -ne 0 ]; then
    echo "錯誤：資料集整合失敗。請檢查 convert_annotations.py 腳本和輸入檔案。"
    exit 1
fi
echo "資料集整合完成。"

# --- 6. 執行模型訓練 ---
echo "--- 6. 啟動 YOLOv8 模型訓練 ---"
python3 train_yolo.py
if [ $? -ne 0 ]; then
    echo "錯誤：模型訓練失敗。請檢查 train_yolo.py 腳本或訓練資料。"
    exit 1
fi
echo "模型訓練完成！"

echo "--- 7. 整個工作流程已完成 ---"