import os
import cv2
from ultralytics import YOLO
import argparse
from dotenv import load_dotenv

# 確保載入環境變數
load_dotenv()

def predict_and_capture_frames(model_path, video_path, output_dir, conf_threshold=0.5):
    """
    使用 YOLO 模型對影片進行預測，自動截圖包含偵測到物件的畫面，
    並在截圖上繪製標記框和標籤。
    """
    if not os.path.exists(model_path) or not os.path.exists(video_path):
        print("錯誤：找不到模型或影片檔案。")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"已建立輸出資料夾: {output_dir}")

    print(f"正在載入模型: {model_path}")
    model = YOLO(model_path)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"錯誤：無法開啟影片: {video_path}")
        return

    frame_count = 0
    captured_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # 執行預測，設定置信度閾值
        results = model(frame, conf=conf_threshold, verbose=False)
        
        # 檢查是否有任何偵測結果
        if len(results[0].boxes) > 0:
            captured_count += 1
            
            # 從結果物件中繪製標記框到畫面上
            annotated_frame = results[0].plot()
            
            # 使用影片名稱、幀序號和偵測到的物件類別來命名
            detected_classes = [model.names[int(box.cls)] for box in results[0].boxes]
            detected_class_str = "_".join(sorted(list(set(detected_classes))))
            
            video_name_base = os.path.splitext(os.path.basename(video_path))[0]
            
            output_image_name = f"{video_name_base}_frame_{frame_count:05d}_{detected_class_str}.jpg"
            output_image_path = os.path.join(output_dir, output_image_name)
            
            # 儲存繪製好的圖片
            cv2.imwrite(output_image_path, annotated_frame)
            
            print(f"已截圖偵測到物件的影格 ({detected_class_str})：{output_image_path}")

    cap.release()
    print(f"\n影片處理完成。共檢查 {frame_count} 幀，截圖 {captured_count} 幀。")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='使用 YOLOv8 模型對影片進行預測，並截圖包含偵測結果的畫面。')
    
    DEFAULT_MODEL_PATH = os.getenv('DEFAULT_MODEL_PATH')
    DEFAULT_VIDEO_PATH = os.getenv('DEFAULT_VIDEO_PATH')
    DEFAULT_OUTPUT_DIR = os.getenv('PREDICTION_OUTPUT_DIR', 'runs/detect/detected_frames')

    parser.add_argument('--model', type=str, default=DEFAULT_MODEL_PATH, help='訓練好的 YOLOv8 模型路徑')
    parser.add_argument('--video', type=str, default=DEFAULT_VIDEO_PATH, help='待預測的影片路徑')
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT_DIR, help='儲存截圖的輸出資料夾')
    parser.add_argument('--conf', type=float, default=0.5, help='預測的最低置信度閾值')
    
    args = parser.parse_args()
    
    if not args.model or not args.video:
        print("錯誤：請透過 --model 和 --video 參數，或在 .env 檔案中指定預設路徑。")
        exit()

    predict_and_capture_frames(
        model_path=args.model,
        video_path=args.video,
        output_dir=args.output,
        conf_threshold=args.conf
    )