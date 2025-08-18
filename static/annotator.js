// 文件名稱: annotator.js (最終修正版，新增按鈕)

const API_URL = 'http://localhost:5000';

const videoSelect = document.getElementById('video-select');
const labelSelect = document.getElementById('label-select');
const videoElement = document.getElementById('video');
const canvasElement = document.getElementById('video-canvas');
const saveBtn = document.getElementById('save-btn');
const annotateBtn = document.getElementById('annotate-btn');
const statusMessage = document.getElementById('status-message');
const annotationsUl = document.getElementById('annotations-ul'); // 新增清單元素
const ctx = canvasElement.getContext('2d');

let allAnnotations = [];
let currentVideoAnnotations = [];
let isDrawing = false;
let startX, startY;
let currentRect = null;
let isAnnotatingMode = false; // 新增的狀態變數

// 載入所有標註資料
async function loadAnnotations() {
    try {
        const response = await fetch(`${API_URL}/annotations`);
        if (!response.ok) throw new Error('無法載入標註');
        allAnnotations = await response.json();
        statusMessage.textContent = '已成功載入舊標註資料。';
        populateLabelList(); // 成功載入後，填充標籤列表
    } catch (error) {
        statusMessage.textContent = `載入標註失敗: ${error.message}`;
        allAnnotations = [];
    }
}

// 載入所有標註資料
async function loadAnnotations() {
    try {
        const response = await fetch(`${API_URL}/annotations`);
        if (!response.ok) throw new Error('無法載入標註');
        allAnnotations = await response.json();
        statusMessage.textContent = '已成功載入舊標註資料。';
        populateLabelList(); // 成功載入後，填充標籤列表
    } catch (error) {
        statusMessage.textContent = `載入標註失敗: ${error.message}`;
        allAnnotations = [];
    }
}

// 根據所有標註，填充標籤下拉選單
function populateLabelList() {
    const labels = new Set();
    allAnnotations.forEach(ann => {
        ann.annotations.forEach(box => {
            if (box.label) {
                labels.add(box.label);
            }
        });
    });

    labelSelect.innerHTML = '';
    
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- 選擇或輸入標籤 --';
    labelSelect.appendChild(defaultOption);

    labels.forEach(label => {
        const option = document.createElement('option');
        option.value = label;
        option.textContent = label;
        labelSelect.appendChild(option);
    });
}

// 根據伺服器提供的影片列表，填充下拉選單
async function populateVideoList() {
    try {
        const response = await fetch(`${API_URL}/videos`);
        if (!response.ok) throw new Error('無法載入影片列表');
        const videos = await response.json();

        if (videos.length === 0) {
            statusMessage.textContent = '警告：未找到影片檔案。請上傳影片至 /uploads 資料夾。';
            return;
        }

        videoSelect.innerHTML = '';
        videos.forEach(video => {
            const option = document.createElement('option');
            option.value = video;
            option.textContent = video;
            videoSelect.appendChild(option);
        });

        loadVideo(videos[0]);
    } catch (error) {
        statusMessage.textContent = `載入影片列表失敗: ${error.message}`;
    }
}

// 根據選定的影片載入並顯示標註
function loadVideo(videoName) {
    videoElement.src = `${API_URL}/videos/${videoName}`;
    currentVideoAnnotations = allAnnotations.filter(ann => ann.video === videoName);
    videoElement.onloadeddata = () => {
        canvasElement.width = videoElement.clientWidth;
        canvasElement.height = videoElement.clientHeight;
        drawAnnotations();
        renderAnnotationsList();
    };
    videoElement.ontimeupdate = drawAnnotations;
}

// 繪製標註框到 Canvas 上
function drawAnnotations() {
    ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    const currentTime = videoElement.currentTime;

    const scaleX = videoElement.videoWidth / videoElement.clientWidth;
    const scaleY = videoElement.videoHeight / videoElement.clientHeight;

    currentVideoAnnotations.forEach(ann => {
        if (Math.abs(ann.timestamp - currentTime) < 0.1) {
            ann.annotations.forEach(box => {
                if (box.type === 'bbox') {
                    const displayX = box.x / scaleX;
                    const displayY = box.y / scaleY;
                    const displayWidth = box.width / scaleX;
                    const displayHeight = box.height / scaleY;
                    
                    ctx.beginPath();
                    ctx.rect(displayX, displayY, displayWidth, displayHeight);
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = '#007bff';
                    ctx.stroke();
                    ctx.fillStyle = '#fff';
                    ctx.fillRect(displayX, displayY - 20, ctx.measureText(box.label).width + 10, 20);
                    ctx.fillStyle = '#007bff';
                    ctx.fillText(box.label, displayX + 5, displayY - 5);
                }
            });
        }
    });

    if (isDrawing && currentRect) {
        ctx.beginPath();
        ctx.rect(currentRect.x, currentRect.y, currentRect.width, currentRect.height);
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#28a745';
        ctx.stroke();
    }
}

// 儲存標註
async function saveAnnotations() {
    const otherAnnotations = allAnnotations.filter(ann => ann.video !== videoSelect.value);
    const mergedAnnotations = [...otherAnnotations, ...currentVideoAnnotations];
    try {
        const response = await fetch(`${API_URL}/annotations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mergedAnnotations),
        });
        if (!response.ok) throw new Error('儲存失敗');
        const data = await response.json();
        statusMessage.textContent = data.message;
        await loadAnnotations();
    } catch (error) {
        statusMessage.textContent = `儲存標註失敗: ${error.message}`;
    }
}

// 渲染標註清單
function renderAnnotationsList() {
    annotationsUl.innerHTML = '';
    currentVideoAnnotations.sort((a, b) => a.timestamp - b.timestamp);
    currentVideoAnnotations.forEach((ann, index) => {
        ann.annotations.forEach((box, boxIndex) => {
            const listItem = document.createElement('li');
            listItem.className = 'annotation-item';

            const time = ann.timestamp.toFixed(2);
            const label = box.label;
            const textContent = `時間: ${time}s, 標籤: ${label}`;
            
            const textSpan = document.createElement('span');
            textSpan.textContent = textContent;
            textSpan.onclick = () => {
                videoElement.currentTime = ann.timestamp;
                videoElement.play();
            };

            const deleteButton = document.createElement('button');
            deleteButton.textContent = '刪除';
            deleteButton.className = 'delete-btn';
            deleteButton.onclick = (e) => {
                e.stopPropagation();
                deleteAnnotation(index, boxIndex);
            };

            listItem.appendChild(textSpan);
            listItem.appendChild(deleteButton);
            annotationsUl.appendChild(listItem);
        });
    });
}

// 刪除標註
function deleteAnnotation(annIndex, boxIndex) {
    if (confirm('確定要刪除這個標註嗎？')) {
        const annotationEntry = currentVideoAnnotations[annIndex];
        annotationEntry.annotations.splice(boxIndex, 1);
        if (annotationEntry.annotations.length === 0) {
            currentVideoAnnotations.splice(annIndex, 1);
        }
        drawAnnotations();
        renderAnnotationsList();
    }
}

// 切換標註模式
function toggleAnnotateMode() {
    isAnnotatingMode = !isAnnotatingMode;
    if (isAnnotatingMode) {
        // 進入標註模式
        annotateBtn.textContent = '結束標註';
        canvasElement.style.pointerEvents = 'auto';
        canvasElement.style.cursor = 'crosshair';
        statusMessage.textContent = '已進入標註模式，請在影片上拖曳滑鼠來創建標註。';
    } else {
        // 結束標註模式
        annotateBtn.textContent = '開始標註';
        canvasElement.style.pointerEvents = 'none';
        canvasElement.style.cursor = 'default';
        statusMessage.textContent = '已退出標註模式，可以正常操作影片播放器。';
    }
}

// 監聽畫布事件以創建新標註
canvasElement.addEventListener('mousedown', (e) => {
    if (!isAnnotatingMode) return;
    isDrawing = true;
    const rect = canvasElement.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
});

canvasElement.addEventListener('mousemove', (e) => {
    if (!isDrawing || !isAnnotatingMode) return;
    const rect = canvasElement.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    const boxX = Math.min(startX, endX);
    const boxY = Math.min(startY, endY);
    const boxWidth = Math.abs(startX - endX);
    const boxHeight = Math.abs(startY - endY);

    currentRect = { x: boxX, y: boxY, width: boxWidth, height: boxHeight };
    drawAnnotations();
});

canvasElement.addEventListener('mouseup', (e) => {
    if (!isDrawing || !isAnnotatingMode) return;
    isDrawing = false;
    currentRect = null;

    const rect = canvasElement.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    const boxX = Math.min(startX, endX);
    const boxY = Math.min(startY, endY);
    const boxWidth = Math.abs(startX - endX);
    const boxHeight = Math.abs(startY - endY);

    if (boxWidth > 5 && boxHeight > 5) {
        const label = prompt('請輸入標籤名稱:');
        if (label) {
            const scaleX = videoElement.videoWidth / videoElement.clientWidth;
            const scaleY = videoElement.videoHeight / videoElement.clientHeight;
            
            const originalX = boxX * scaleX;
            const originalY = boxY * scaleY;
            const originalWidth = boxWidth * scaleX;
            const originalHeight = boxHeight * scaleY;

            const newBox = {
                type: 'bbox',
                x: originalX,
                y: originalY,
                width: originalWidth,
                height: originalHeight,
                label: label
            };

            const currentTime = videoElement.currentTime;
            let annotationEntry = currentVideoAnnotations.find(ann => Math.abs(ann.timestamp - currentTime) < 0.1);

            if (!annotationEntry) {
                annotationEntry = {
                    video: videoSelect.value,
                    timestamp: currentTime,
                    annotations: []
                };
                currentVideoAnnotations.push(annotationEntry);
            }
            annotationEntry.annotations.push(newBox);
            drawAnnotations();
        }
    }
    // 繪製完成後自動退出標註模式
    toggleAnnotateMode();
});

// 事件監聽
videoSelect.onchange = (e) => loadVideo(e.target.value);
saveBtn.onclick = saveAnnotations;
annotateBtn.onclick = toggleAnnotateMode; // 綁定新的按鈕事件

// 初始化函式
async function initialize() {
    // 確保畫布在初始時是不可點擊的
    canvasElement.style.pointerEvents = 'none';
    canvasElement.style.cursor = 'default';

    await loadAnnotations();
    if (videoSelect.options.length > 0) {
        const firstVideo = videoSelect.options[0].value;
        loadVideo(firstVideo);
    } else {
        statusMessage.textContent = '警告：未找到影片檔案。請上傳影片至 /uploads 資料夾。';
    }
}

// 使用 DOMContentLoaded 事件
document.addEventListener('DOMContentLoaded', initialize);