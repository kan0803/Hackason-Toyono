import cv2
import numpy as np
import os
import json
import base64
import time
from fastapi import FastAPI, WebSocket, UploadFile, File, responses
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ディレクトリが存在しない場合は作成
if not os.path.exists("/app/captureImage"):
    print("Create directory: /app/captureImage")
    os.makedirs("/app/captureImage")


@app.get("/get_image")
def get_image():
    image_path = "/app/captureImage/capture.png"
    if not os.path.exists(image_path):
        return {"error": "File not found"}
    with open(image_path, "rb") as f:
        image = f.read()
    return {"image": base64.b64encode(image).decode('utf-8')}

@app.get('/download-image')
async def download():
    return responses.FileResponse('./captureImage/capture.png',filename='toyonon-pickture.png')

@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    image_path = "/app/captureImage/capture.png"
    with open(image_path, "wb") as f:
        f.write(await file.read())
    return {"message": "success"}

@app.websocket("/video_feed")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket接続成功")

    last_sent_time = time.time()
    frame_buffer = None  

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

                if frame is not None:
                    frame_buffer = frame  

                # 5秒ごとに判定
                if time.time() - last_sent_time >= 1 and frame_buffer is not None:
                    skin_mask = get_skin_mask(frame_buffer)
                    hand_contours = find_hand_contours(skin_mask)

                    if len(hand_contours) == 0:
                        hand_shape = "Unknown"
                    elif len(hand_contours) == 1:
                        hand_shape = detect_fingers(frame_buffer, hand_contours[0])
                    else:
                        # 複数の手がある場合、すべての手の形状を取得
                        detected_shapes = [detect_fingers(frame_buffer, c) for c in hand_contours]
                        if all(shape == detected_shapes[0] for shape in detected_shapes):
                            hand_shape = detected_shapes[0]  
                        else:
                            hand_shape = "Unknown"  

                    # 判定結果を送信
                    response = json.dumps({"hand_sign": hand_shape})
                    await websocket.send_text(response)
                    last_sent_time = time.time()

            except Exception as e:
                print(f"エラー: {e}")

    finally:
        print("WebSocket接続終了")
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

# 手の肌色部分を抽出
def get_skin_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    return mask

# すべての手の輪郭を取得
def find_hand_contours(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) > 2000]  # 小さすぎる領域は無視

# 指の本数から形状を判断（ピースの精度を向上）
def detect_fingers(frame, contour):
    hull = cv2.convexHull(contour, returnPoints=False)
    if len(hull) < 3:
        return "Unknown"

    try:
        defects = cv2.convexityDefects(contour, hull)
        if defects is None:
            return "Rock"

        finger_count = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            far = tuple(contour[f][0])

            # 距離が一定以上の凹みを指と判定（閾値調整）
            if d > 8000:  
                finger_count += 1
                cv2.circle(frame, far, 5, [0, 0, 255], -1)  

        if finger_count >= 4:
            return "Paper"
        elif 1 <= finger_count <= 2:  # Scissors の判定を緩和
            return "Scissors"
        else:
            return "Rock"
    except cv2.error as e:
        print(f"OpenCV Error: {e}")
        return "Unknown"
