<script setup lang="ts">
import { ref, onMounted } from 'vue';

const videos = ref<{ text: string; value: string }[]>([]);
const selectedVideo = ref('');
const videoElement = ref<HTMLVideoElement | null>(null);

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
    const constraints = {
      video: { deviceId: { exact: selectedVideo.value } }
    };
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    
    if (videoElement.value) {
      videoElement.value.srcObject = stream;
    }
  } catch (error) {
    console.error("カメラ接続エラー: ", error);
  }
};

onMounted(getCameraDevices);
</script>

<template>
  <div  class="camera">
    <p>
      カメラ: 
      <select v-model="selectedVideo" @change="connectLocalCamera">
        <option disabled value="">Please select one</option>
        <option v-for="video in videos" :key="video.value" :value="video.value">
          {{ video.text }}
        </option>
      </select>
    </p>
    <video ref="videoElement" muted="true" width="1000" autoplay playsinline></video>
  </div>
</template>



<style scoped>
.camera {
  flex-direction: column;
}
</style>
