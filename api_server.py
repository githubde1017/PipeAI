import os
import json
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# 獲取腳本的絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# 影片資料夾路徑
VIDEO_FOLDER = os.path.join(BASE_DIR, os.getenv('UPLOAD_FOLDER', 'uploads'))
# 標註檔案路徑
ANNOTATIONS_FILE = os.path.join(BASE_DIR, os.getenv('ANNOTATIONS_FILE', 'annotations.json'))

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def serve_annotator():
    """提供前端標註頁面，並動態載入影片列表"""
    mp4_videos = []
    try:
        with os.scandir(VIDEO_FOLDER) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith('.mp4'):
                    mp4_videos.append(entry.name)
    except FileNotFoundError:
        print(f"警告：找不到影片資料夾 {VIDEO_FOLDER}")
    
    return render_template('annotator.html', videos=mp4_videos)

@app.route('/annotations', methods=['GET'])
def get_annotations():
    """提供標註資料"""
    if os.path.exists(ANNOTATIONS_FILE):
        with open(ANNOTATIONS_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # 如果檔案存在但內容損壞，回傳空陣列
                return jsonify([])
            return jsonify(data)
    else:
        # 如果檔案不存在，回傳空陣列
        return jsonify([])

@app.route('/annotations', methods=['POST'])
def save_annotations():
    """儲存標註資料"""
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "無效的輸入格式，預期為 JSON 陣列。"}), 400
    
    try:
        with open(ANNOTATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return jsonify({"message": "標註資料已成功儲存。"})
    except Exception as e:
        return jsonify({"error": f"儲存檔案時發生錯誤: {str(e)}"}), 500

@app.route('/videos/<path:filename>')
def serve_video(filename):
    """提供影片檔案"""
    return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == '__main__':
    # 在啟動前，確保 annotations.json 檔案存在且格式正確
    if not os.path.exists(ANNOTATIONS_FILE):
        with open(ANNOTATIONS_FILE, 'w') as f:
            f.write('[]')
    
    app.run(host='0.0.0.0', port=5000)