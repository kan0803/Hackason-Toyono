<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { takeEntireCapture } from '@/components/TakeEntireCapture.vue';

const videoRef = ref<HTMLVideoElement | null>(null);
const isPlaying = ref(false);

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !isPlaying.value) {
    isPlaying.value = true;
    nextTick(() => {
      if (videoRef.value) {
        videoRef.value.play();
      }
    });
  } else if (event.key === 'Escape' && isPlaying.value) {
    exitVideo();
  }
};

// 動画終了時に再生状態を解除
const handleVideoEnded = () => {
  exitVideo();
  takeEntireCapture();
};

// 再生状態を解除する関数
const exitVideo = () => {
  isPlaying.value = false;
  // 取得した要素を HTMLElement 型にキャスト
const videoContainer = document.querySelector('.video-container') as HTMLElement;

// キャプチャ前に video-container を隠す
if (videoContainer) {
  videoContainer.style.display = 'none';
}
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<template>
  <div>
    <router-view/>
  </div>
  <div v-if="isPlaying" class="video-container">
    <video ref="videoRef" class="window-video" @ended="handleVideoEnded" >
      <source src="../src/movie/mp4/shutter_unClear.mp4" type="video/mp4">
      お使いのブラウザは動画タグをサポートしていません。
    </video>
  </div>
</template>

<style scoped>
.video-container {
  position: absolute; /* 全画面ではなくウィンドウサイズに配置 */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* クリックをブロックしない */
}

.window-video {
  width: 100%;
  height: 100%;
  object-fit: cover; /* アスペクト比を維持しつつフィット */
  opacity: 0.5; /* 透過度調整（0.0〜1.0） */
  background: transparent;
}
</style>
