import cv2
import base64
import numpy as np
import os
import json
from fastapi import FastAPI, WebSocket
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

@app.post("/post_image")
def post_image(image: str):
    image_path = "/app/captureImage/capture.png"
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image.split(',')[1]))
    return {"message": "success"}

@app.websocket("/video_feed")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection opened")

    try:
        while True:
            received_data = await websocket.receive_text()  

            try:
                # JSONとして解析
                data = json.loads(received_data)
                if "image" not in data:
                    print("受信データに 'image' キーがありません")
                    continue

                # Base64データを抽出
                img_data = base64.b64decode(data["image"].split(',')[1])  
                np_array = np.frombuffer(img_data, dtype=np.uint8)
                frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                if frame is not None:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    _, buffer = cv2.imencode('.jpg', gray)

                    processed_image = base64.b64encode(buffer).decode('utf-8')
                    response = json.dumps({"image": f"data:image/jpeg;base64,{processed_image}"})
                    await websocket.send_text(response)

            except json.JSONDecodeError:
                print("JSONデコードエラー: 受信データが正しくありません")
            except Exception as e:
                print(f"画像処理エラー: {e}")

    except Exception as e:
        print(f"エラー: {e}")

    finally:
        print("WebSocket connection closed")
        await websocket.close()



@app.get("/")
def read_root():
    return {"message": "Hello World"}
