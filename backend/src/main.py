import cv2
import base64
import numpy as np
import os
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 透過AVIファイルの読み込み
shutter_avi = "movie/avi/shutter_clear.avi"
shutter = cv2.VideoCapture(shutter_avi)

# tonoyon画像の読み込み
toyonon_img = cv2.imread("src/image/toyonon_flame01.png", cv2.IMREAD_UNCHANGED)

# 読み込み確認
if toyonon_img is None:
    print("画像の読み込みに失敗")
else:
    print(f"画像のサイズ: {toyonon_img.shape}")  # (高さ, 幅, チャンネル数)

#画像表示
def overlay_image(frame, overlay, position):
    """フレームの指定位置に透過PNGを重ねる"""
    if overlay is None:
        print("エラー: overlay が None")
        return frame

    h, w, _ = frame.shape
    oh, ow, oc = overlay.shape

    print(f"フレームサイズ: {h}x{w}, オーバーレイサイズ: {oh}x{ow}, チャンネル数: {oc}")

    if oc < 4:
        print("透過情報なし")
        return frame

    # ROI（対象領域）を取得
    x1, y1 = position
    x2, y2 = x1 + ow, y1 + oh

    # 画像サイズを超えないようにする
    x1, x2 = max(0, x1), min(w, x2)
    y1, y2 = max(0, y1), min(h, y2)

    print(f"貼り付け位置: ({x1}, {y1}) - ({x2}, {y2})")

    roi = frame[y1:y2, x1:x2]

    # アルファチャンネルを 0~1 に正規化
    alpha = overlay[:y2 - y1, :x2 - x1, 3].astype(np.float32) / 255.0
    overlay_rgb = overlay[:y2 - y1, :x2 - x1, :3].astype(np.float32)

    # 透過合成
    for c in range(3):  
        roi[:, :, c] = (1 - alpha) * roi[:, :, c].astype(np.float32) + alpha * overlay_rgb[:, :, c]

    # 合成結果を uint8 に変換
    frame[y1:y2, x1:x2] = roi.astype(np.uint8)

    return frame


# 手の形(ピース)検出関数
def detect_peace_sign(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in contours:
        if len(cnt) < 5:  # ConvexityDefectsの計算には5点以上が必要
            continue

        hull = cv2.convexHull(cnt, returnPoints=False)

        if hull.shape[0] < 4:
            continue  # hullの点が少なすぎる場合はスキップ
        
        defects = cv2.convexityDefects(cnt, hull)
        if defects is not None and len(defects) == 2:
            return True, cnt  # ピースサイン検出
    return False, None


@app.websocket("/video_feed")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection opened")

    try:
        while True:
            received_data = await websocket.receive_text()
            try:
                data = json.loads(received_data)
                if "image" not in data:
                    continue

                img_data = base64.b64decode(data["image"].split(',')[1])  
                np_array = np.frombuffer(img_data, dtype=np.uint8)
                frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                frame = cv2.resize(frame, (1920, 1080))

                if frame is not None:
                    detected, contour = detect_peace_sign(frame)

                    #透過toyononIMGを重ねる
                    frame = overlay_image(frame, toyonon_img, position=(frame.shape[1] - toyonon_img.shape[1] - 10, frame.shape[0] - toyonon_img.shape[0] - 10))

                    if detected:
                        cv2.putText(frame, "Peace Sign Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        print("ピースサイン検出！")
                    else:
                        cv2.putText(frame, "No Peace Sign", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    _, buffer = cv2.imencode('.jpg', frame)
                    processed_image = base64.b64encode(buffer).decode('utf-8')
                    response = json.dumps({"image": f"data:image/jpeg;base64,{processed_image}"})
                    await websocket.send_text(response)
            except Exception as e:
                print(f"エラー: {e}")
    finally:
        print("WebSocket connection closed")
        await websocket.close()

# @app.websocket("/video_gray")
# async def video_gray(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket connection opened")

#     try:
#         while True:
#             received_data = await websocket.receive_text()  

#             try:
#                 # JSONとして解析
#                 data = json.loads(received_data)
#                 if "image" not in data:
#                     print("受信データに 'image' キーがありません")
#                     continue

#                 # Base64データを抽出
#                 img_data = base64.b64decode(data["image"].split(',')[1])  
#                 np_array = np.frombuffer(img_data, dtype=np.uint8)
#                 frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

#                 if frame is not None:
#                     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#                     _, buffer = cv2.imencode('.jpg', gray)

#                     processed_image = base64.b64encode(buffer).decode('utf-8')
#                     response = json.dumps({"image": f"data:image/jpeg;base64,{processed_image}"})
#                     await websocket.send_text(response)

#             except json.JSONDecodeError:
#                 print("JSONデコードエラー: 受信データが正しくありません")
#             except Exception as e:
#                 print(f"画像処理エラー: {e}")

#     except Exception as e:
#         print(f"エラー: {e}")

#     finally:
#         print("WebSocket connection closed")
#         await websocket.close()



@app.get("/")
def read_root():
    return {"message": "Hello World"}