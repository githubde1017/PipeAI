# 文件名稱: detect_video.py
from ultralytics import YOLO
import cv2
import os
import json

def detect_on_video(model_path, input_video_path, output_video_path, class_names):
    """
    載入訓練好的 YOLOv8 模型，對影片進行物件偵測，並將結果儲存為新影片。
    """
    if not os.path.exists(model_path):
        print(f"錯誤：找不到模型檔案 {model_path}。請確認路徑是否正確。")
        return
    
    if not os.path.exists(input_video_path):
        print(f"錯誤：找不到輸入影片檔案 {input_video_path}。請確認路徑是否正確。")
        return

    # 載入訓練好的模型
    model = YOLO(model_path)
    
    # 讀取輸入影片
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"錯誤：無法開啟影片檔案 {input_video_path}。")
        return
        
    # 獲取影片屬性
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 設定輸出影片格式
    # 建議使用 'mp4v' 或 'XVID'，前者支援更多播放器，後者在 Windows 上較常見
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    
    print(f"開始處理影片：{input_video_path}...")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 使用模型進行預測
        results = model(frame, verbose=False)
        
        # 在畫面上繪製預測結果
        # results[0].plot() 方法會自動將偵測框和標籤畫在影格上
        annotated_frame = results[0].plot()
        
        # 寫入處理後的影格到輸出影片
        out.write(annotated_frame)
        
        frame_count += 1
        print(f"\r已處理 {frame_count} 幀...", end='', flush=True)

    print("\n影片處理完成！")
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"結果已儲存到：{output_video_path}")


if __name__ == '__main__':
    # 從 class_config.json 讀取類別名稱，實現自動同步
    try:
        with open('class_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            class_names = config['names']
    except FileNotFoundError:
        print("錯誤：找不到 class_config.json 檔案。請確認檔案是否存在。")
        exit()

    # 您訓練好的模型路徑，通常在 runs/detect/train/weights/best.pt
    # 如果您重新訓練了模型，請確認路徑是否正確
    model_file_path = 'runs/detect/train/weights/best.pt'
    
    # 要進行辨識的影片路徑
    # 請將 'your_new_video.mp4' 替換為您實際的影片檔名
    input_video_path = 'uploads/your_new_video.mp4'
    
    # 處理後輸出的影片路徑
    output_video_path = 'output_video.mp4'
    
    detect_on_video(model_file_path, input_video_path, output_video_path, class_names)