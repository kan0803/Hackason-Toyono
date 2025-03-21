<!-- アプリの画面全体のキャプチャとバックエンドへのアップロード -->
<template></template>

<script lang="ts">
import html2canvas from 'html2canvas';
import axios from 'axios';

// 画面全体のキャプチャを取得する関数
export const takeEntireCapture = async () => {
  console.log("takeEntireCapture");
  try {
    const canvas = await html2canvas(document.body, {
      ignoreElements: (element: Element) => {
        // 特定の要素を無視する
        return element.tagName === 'SCRIPT' || element.tagName === 'LINK';
      }
    });
    const dataUrl = canvas.toDataURL("image/png");
    const blob = await (await fetch(dataUrl)).blob();
    const formData = new FormData();
    formData.append('file', blob, 'capture.png');
    console.log("Image has been captured");
    // バックエンドに画像をアップロード
    await axios.post('/upload_image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log("Image has been saved on the server");
  } catch (error) {
    console.error("Screen capture error: ", error);
  }
};

export default {
  name: 'TakeEntireCapture'
};
</script>