# 文件名稱: train_yolo.py
import os
import torch
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from ultralytics import YOLO

# 找到一個可用的中文字體
# 在大多數 Linux 系統上，fonts-wqy-zenhei 安裝後，路徑為 /usr/share/fonts/
# 你也可以使用其他字體，例如 'SimHei' 或 'Arial Unicode MS'
font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
font_prop = FontProperties(fname=font_path, size=12)

# 在繪圖時使用這個字體
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Arial'] # 設置中文字體
plt.rcParams['axes.unicode_minus'] = False # 解決負號顯示問題
if __name__ == '__main__':
    # 檢查 CUDA 是否可用，並設定設備
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"訓練將在 {device.upper()} 上進行。")
    
    # 載入預訓練模型
    model = YOLO('yolov8n.pt') 
    
    # 開始訓練，並將訓練結果賦予 results 變數
    # 這裡的 results 物件將包含所有訓練過程的資訊
    results = model.train(
        data='yolo_dataset.yaml', 
        epochs=100, 
        imgsz=640, 
        device=device,
        project='runs/train',
        name='yolov8n_custom'
    )
    
    # 訓練完成後，模型會自動保存在 runs/train/yolov8n_custom/weights/best.pt
    # 訓練結果圖表也會自動生成在 runs/train/yolov8n_custom/ 資料夾中
    print("模型訓練完成！訓練結果儲存在 runs/train/yolov8n_custom/ 中。")
    
    # 如果需要，可以在訓練完成後單獨進行驗證
    # 例如：results = model.val()