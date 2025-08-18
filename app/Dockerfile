# 文件名稱: app/Dockerfile
FROM python:3.10-slim
WORKDIR /app
# 將專案根目錄下的 requirements.txt 複製進來
COPY requirements.txt .
RUN pip install --no-cache-dir -v -r requirements.txt
# 將 app/ 資料夾下的所有檔案複製進來
COPY app .
# 設定 Flask 啟動指令
CMD ["python", "app.py"]