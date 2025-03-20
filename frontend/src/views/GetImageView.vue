<!-- 画像保存するのスマホ画面 -->
<template>
  <div>
    <h1>画像を保存する</h1>
    <div>
      <img :src="image" alt="image" />
    </div>
    <button @click="saveImage">保存</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import img from './../../captureImage/capture.png'

const image = ref<string>(img)
const saveImage = async () => {
    const a = document.createElement('a')
    a.href = image.value
    a.download = 'captureImage/capture.png'
    a.click()
}
</script>