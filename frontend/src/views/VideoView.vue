<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const videos = ref<{ text: string; value: string }[]>([]);
const selectedVideo = ref('');
const videoElement = ref<HTMLVideoElement | null>(null);
const canvasElement = ref<HTMLCanvasElement | null>(null);
const processedImage = ref<HTMLImageElement | null>(null);
const handSignText = ref('');
const ws = ref<WebSocket | null>(null);

const getCameraDevices = async () => {
  try {
    const deviceInfos = await navigator.mediaDevices.enumerateDevices();
    videos.value = deviceInfos
      .filter(deviceInfo => deviceInfo.kind === 'videoinput')
      .map((video, index) => ({
        text: video.label || `Camera ${index + 1}`,
        value: video.deviceId
      }));
  } catch (error) {
    console.error("カメラデバイスの取得に失敗しました: ", error);
  }
};

const connectLocalCamera = async () => {
  if (!selectedVideo.value) return;

  try {
    const constraints = { video: { deviceId: { exact: selectedVideo.value } } };
    const stream = await navigator.mediaDevices.getUserMedia(constraints);

    if (videoElement.value) {
      videoElement.value.srcObject = stream;
    }

    startWebSocket();
  } catch (error) {
    console.error("カメラ接続エラー: ", error);
  }
};

const startWebSocket = () => {
  if (ws.value) {
    ws.value.close();
  }

  ws.value = new WebSocket("ws://localhost:8000/video_feed");

  ws.value.onopen = () => {
    console.log("WebSocket接続成功");
    startStreaming();
  };

  ws.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      // 画像データを受け取る場合
      //if (data.image && processedImage.value) {
      //  processedImage.value.src = data.image; // `<img>` に表示
      //}

      // 手の形（hand_sign）を受け取る場合
      if (data.hand_sign) {
        console.log(`検出された手の形: ${data.hand_sign}`);
        // 例えば、手の形を表示するUIに反映させる
        handSignText.value = data.hand_sign; // 手の形を表示するための変数
      }
    } catch (error) {
      console.error("受信データの解析エラー: ", error);
    }
  };

  ws.value.onerror = (error) => {
    console.error("WebSocketエラー: ", error);
  };

  ws.value.onclose = () => {
    console.log("WebSocket接続終了");
  };
};

const startStreaming = () => {
  if (!canvasElement.value || !videoElement.value || !ws.value) return;

  const ctx = canvasElement.value.getContext('2d');
  if (!ctx) return;

  const sendFrame = () => {
    if (!videoElement.value || !canvasElement.value || !ws.value || ws.value.readyState !== WebSocket.OPEN) return;

    ctx.drawImage(videoElement.value, 0, 0, canvasElement.value.width, canvasElement.value.height);
    const imageData = canvasElement.value.toDataURL("image/jpeg"); // Base64エンコード

    ws.value.send(JSON.stringify({ image: imageData })); // JSON形式で送信

    requestAnimationFrame(sendFrame);
  };

  sendFrame();
};

onMounted(() => {
  getCameraDevices();
});

onUnmounted(() => {
  if (ws.value) {
    ws.value.close();
  }
});
</script>

<template>
  <div class="camera" tabindex="0">
    <p>
      カメラ:
      <select v-model="selectedVideo" @change="connectLocalCamera">
        <option disabled value="">Please select one</option>
        <option v-for="video in videos" :key="video.value" :value="video.value">
          {{ video.text }}
        </option>
      </select>
    </p>
    <div style="position: relative;">
      <video ref="videoElement" muted autoplay playsinline style="width: 1920px; height: 1080px;">
      </video>
      <img v-if="handSignText === 'Unknown'" src="../../image/toyonon_flame01.png" alt="Overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.5;">
      <img v-else-if="handSignText === 'Scissors'" src="../../image/toyonon_01.png" alt="Overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.5;">
      <img v-else-if="handSignText === 'Rock'" src="../../image/toyonon_02.png" alt="Overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.5;">
      <img v-else-if="handSignText === 'Paper'" src="../../image/toyonon_03.png" alt="Overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.5;">
    </div>
    <canvas ref="canvasElement" width="640" height="480" style="display: none"></canvas>
    <p>現在の手の形: {{ handSignText }}</p>
  </div>
</template>

<style scoped>
.camera {
  display: flex;
  flex-direction: column;
  align-items: center;
}
video {
  width: 1920px;
  height: 1080px;
}
</style>