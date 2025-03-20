<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';

const videoRef = ref<HTMLVideoElement | null>(null);
const isPlaying = ref(false);

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !isPlaying.value) {
    isPlaying.value = true;
    nextTick(() => {
      if (videoRef.value) {
        videoRef.value.requestFullscreen?.(); // オプショナルチェーンで安全に呼び出す
        videoRef.value.play();
      }
    });
  } else if (event.key === 'Escape' && isPlaying.value) {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
    isPlaying.value = false;
  }
};

// 動画終了時に全画面を閉じる
const handleVideoEnded = () => {
  exitFullscreen();
};

// 全画面を解除する関数
const exitFullscreen = () => {
  if (document.fullscreenElement) {
    document.exitFullscreen();
  }
  isPlaying.value = false;
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<template>
  <div id="app">
    <router-view/>
  </div>
  <div v-if="isPlaying">
    <video ref="videoRef" class="fullscreen-video" @ended="handleVideoEnded">
      <source src="../src/movie/mp4/shutter_unClear.mp4" type="video/mp4">
      お使いのブラウザは動画タグをサポートしていません。
    </video>
  </div>
</template>

<style scoped>
.fullscreen-video {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  object-fit: cover;
  background: black;
}
</style>
