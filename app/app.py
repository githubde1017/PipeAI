# 文件名稱: app/app.py
import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ANNOTATION_FILE'] = 'annotations.json'
app.config['CLASS_CONFIG_FILE'] = 'class_config.json'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/class_config')
def get_class_config():
    try:
        with open(app.config['CLASS_CONFIG_FILE'], 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/list_videos')
def list_videos():
    video_files = []
    # 使用 os.listdir() 列出 uploads 資料夾中的所有檔案
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        # 篩選出符合影片副檔名的檔案
        if filename.lower().endswith(('.mp4', '.mov', '.avi')):
            video_files.append(filename)
    return jsonify(video_files)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 使用 secure_filename() 處理檔名
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # 將處理後的安全檔名返回給前端
    return jsonify({'message': 'Video uploaded successfully', 'filename': filename}), 200

@app.route('/annotations', methods=['POST'])
def save_annotation():
    """
    接收來自前端的單一標註資料，並安全地追加到 annotations.json 檔案。
    """
    new_annotation_data = request.json
    
    annotations_list = []
    
    # 1. 檢查並讀取現有的標註資料
    if os.path.exists(app.config['ANNOTATION_FILE']) and os.path.getsize(app.config['ANNOTATION_FILE']) > 0:
        with open(app.config['ANNOTATION_FILE'], 'r', encoding='utf-8') as f:
            try:
                annotations_list = json.load(f)
            except json.JSONDecodeError as e:
                # 如果檔案損壞，提示並從空列表開始
                print(f"警告：annotations.json 檔案損壞，無法載入。詳細錯誤: {e}")
                # 這裡可以選擇備份或忽略舊檔案
                # 例如：shutil.copyfile(...)
                pass
    
    # 2. 將新資料添加到列表中
    annotations_list.append(new_annotation_data)
    
    # 3. 將整個列表覆寫回檔案
    try:
        with open(app.config['ANNOTATION_FILE'], 'w', encoding='utf-8') as f:
            json.dump(annotations_list, f, indent=4, ensure_ascii=False)
        return jsonify({"message": "標註資料已成功儲存。"}), 200
    except Exception as e:
        return jsonify({"error": f"儲存檔案時發生錯誤: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)