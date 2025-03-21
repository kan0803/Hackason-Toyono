<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
// 効果音ファイルのインポート
import sound0 from '@/assets/soundeffect/effect01.mp3';
import sound1 from '@/assets/soundeffect/effect02.mp3';
import sound2 from '@/assets/soundeffect/effect03.mp3';


const videos = ref<{ text: string; value: string }[]>([]);
const selectedVideo = ref('');
const videoElement = ref<HTMLVideoElement | null>(null);
const canvasElement = ref<HTMLCanvasElement | null>(null);
const processedImage = ref<HTMLImageElement | null>(null);
const handSignText = ref('');
const faceDetectedNum = ref('');
const ws = ref<WebSocket | null>(null);

// 効果音の再生関数
const playSound = (sound: string) => {
  const audio = new Audio(sound);
  audio.play();
};

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
      // 手の形（hand_sign）を受け取る
      if (data.hand_sign) {
        console.log(`検出された手の形: ${data.hand_sign}`);
        // 例えば、手の形を表示するUIに反映させる
        handSignText.value = data.hand_sign; // 手の形を表示するための変数
      }
      // 顔検出の結果取得
      faceDetectedNum.value = parseInt(data.face_detected).toString();
      console.log(`顔検出: ${data.face_detected}`);
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

// 効果音再生のためのウォッチャー
watch([faceDetectedNum, handSignText], ([newFaceDetectedNum, newHandSignText]) => {
  if (faceDetectedNum.value === '1' && handSignText.value === 'Unknown') {
    playSound(sound0);
  } else if (faceDetectedNum.value >= '2' && handSignText.value === 'Unknown') {
    playSound(sound1);
  } else if ((handSignText.value === 'Rock' || handSignText.value === 'Paper' || handSignText.value === 'Scissors') && faceDetectedNum.value !== '0') {
    playSound(sound2);
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
    <div style="display: flex; justify-content: center; position: relative;">
      <video ref="videoElement" muted autoplay playsinline style="width: 100vw; height: 100vh;">
      </video>

      <!-- 顔検出・手の形状の状態に応じて表示する画像を変更 -->
      <img v-if="faceDetectedNum === '0'" src="@/assets/image/TynnWithFrame/toyonon_frame05.png" alt="顔未検出" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
      <img v-else-if="faceDetectedNum === '1' && handSignText === 'Unknown'" src="@/assets/image/TynnWithFrame/toyonon_frame04.png" alt="顔検出" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
      <img v-else-if="faceDetectedNum >= '2' && handSignText === 'Unknown'" src="@/assets/image/TynnWithFrame/toyonon_frame03.png" alt="顔複数検出" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
      <img v-else-if="(handSignText === 'Rock' || handSignText === 'Paper' || handSignText === 'Scissors') && faceDetectedNum !== '0'" src="@/assets/image/TynnWithFrame/toyonon_frame02.png" alt="手の形: rock" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
      <img v-else src="@/assets/image/TynnWithFrame/toyonon_frame00.png" alt="初期画像" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">

    </div>
    <canvas ref="canvasElement" width="640" height="480" style="display: none"></canvas>
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