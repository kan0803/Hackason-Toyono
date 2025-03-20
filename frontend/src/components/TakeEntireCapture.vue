<!-- アプリの画面全体のキャプチャとバックエンドへのアップロード -->
<template>
  <div>
    <button @click="takeEntireCapture">Take Entire Capture</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import html2canvas from 'html2canvas';
import axios from 'axios';

const takeEntireCapture = async () => {
  try {
    const canvas = await html2canvas(document.body, {
      ignoreElements: (element) => {
        // 特定の要素を無視する
        return element.tagName === 'SCRIPT' || element.tagName === 'LINK';
      }
    });
    const dataUrl = canvas.toDataURL("image/png");
    const blob = await (await fetch(dataUrl)).blob();
    const formData = new FormData();
    formData.append('file', blob, 'capture.png');
    // バックエンドに画像をアップロード
    await axios.post('http://localhost:8000/upload_image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log("Image has been saved on the server");
  } catch (error) {
    console.error("Screen capture error: ", error);
  }
};
</script>