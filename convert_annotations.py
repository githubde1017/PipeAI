# 文件名稱: convert_annotations.py
import json
import os
import cv2
import shutil
import datetime

def convert_to_yolo_format(annotations_file, video_folder, output_folder, class_mapping):
    """
    從 annotations.json 讀取資料，並轉換為 YOLO 格式的標註檔案 (.txt)。
    同時從影片中擷取對應的畫面。
    """
    # 確保所有輸出資料夾存在
    images_folder = os.path.join(output_folder, 'images')
    labels_folder = os.path.join(output_folder, 'labels')
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(labels_folder, exist_ok=True)

    print(f"正在讀取 {annotations_file}...")

    # 正確的 JSON 讀取邏輯
    try:
        with open(annotations_file, 'r', encoding='utf-8') as f:
            # 您的前端程式碼產生的是單一完整的 JSON 陣列，因此應使用 json.load()
            annotations_list = json.load(f)
    except FileNotFoundError:
        print(f"錯誤：找不到標註檔案 {annotations_file}。")
        return
    except json.JSONDecodeError as e:
        print(f"錯誤：標註檔案 {annotations_file} 格式不正確。請檢查檔案內容。")
        print(f"詳細錯誤訊息：{e}")
        return

    processed_frames = {}
    
    for annotation_data in annotations_list:
        video_name = annotation_data['video']
        timestamp = annotation_data['timestamp']
        annotations = annotation_data['annotations']

        # 去重
        if (video_name, timestamp) in processed_frames:
            continue
        processed_frames[(video_name, timestamp)] = True

        video_path = os.path.join(video_folder, video_name)
        if not os.path.exists(video_path):
            print(f"錯誤：找不到影片檔案 {video_path}，已跳過。")
            continue

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"錯誤：無法開啟影片 {video_path}，已跳過。")
            continue

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = cap.read()
        if not ret:
            print(f"警告：無法擷取影片 {video_path} 第 {timestamp} 秒的畫面，已跳過。")
            cap.release()
            continue

        img_height, img_width, _ = frame.shape
        cap.release()

        image_name_base = f"{os.path.splitext(video_name)[0]}_{int(timestamp)}_{int((timestamp-int(timestamp))*100)}"
        
        # 儲存擷取的圖片
        image_path = os.path.join(images_folder, f"{image_name_base}.jpg")
        cv2.imwrite(image_path, frame)
        
        yolo_annotations = []
        for ann in annotations:
            class_name = ann['label']
            if class_name not in class_mapping:
                print(f"警告：類別 {class_name} 未在 class_config.json 中定義，已跳過。")
                continue
            
            class_id = class_mapping[class_name]
            
            if ann['type'] == 'bbox':
                x, y, width, height = ann['x'], ann['y'], ann['width'], ann['height']
                
                x_center = (x + width / 2) / img_width
                y_center = (y + height / 2) / img_height
                norm_width = width / img_width
                norm_height = height / img_height
                
                yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}")
            
            elif ann['type'] == 'water_level':
                y = ann['y']
                
                x_center = 0.5
                y_center = y / img_height
                norm_width = 1.0
                norm_height = 0.001 # 使用一個固定的微小值
                
                yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}")

        if yolo_annotations:
            label_file_path = os.path.join(labels_folder, f"{image_name_base}.txt")
            with open(label_file_path, 'w') as out_f:
                out_f.write('\n'.join(yolo_annotations))
            print(f"已儲存 {video_name} 於 {timestamp} 秒的圖片與標註檔案。")

    print("\n所有標註的畫格已轉換完成。")
    pass

if __name__ == '__main__':
    annotations_file = 'annotations.json'
    video_directory = 'uploads'
    output_directory = 'yolo_dataset'
    
    # --- 備份 annotations.json 檔案 ---
    source_path = annotations_file
    if os.path.exists(annotations_file):
        backup_dir = 'backups/annotations'
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        destination_path = os.path.join(backup_dir, f'annotations_{timestamp}.json')
        shutil.copyfile(source_path, destination_path)
        print(f"已成功備份 annotations.json 到 {destination_path}")
    else:
        print(f"警告：找不到 {annotations_file} 檔案，跳過備份。")

    # 從設定檔讀取類別映射
    class_map = {}
    try:
        with open('class_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 使用 'names' 鍵來獲取類別列表
            if 'names' in config and isinstance(config['names'], list):
                for i, class_name in enumerate(config['names']):
                    class_map[class_name] = i
            else:
                print("錯誤：class_config.json 格式不正確。請確認有 'names' 鍵且其值為列表。")
                exit()
    except FileNotFoundError:
        print("錯誤：找不到 class_config.json 檔案，無法進行轉換。")
        exit()
    
    if os.path.exists(annotations_file):
        convert_to_yolo_format(annotations_file, video_directory, output_directory, class_map)
    else:
        print(f"錯誤：找不到標註檔案 {annotations_file}，無法進行轉換。")