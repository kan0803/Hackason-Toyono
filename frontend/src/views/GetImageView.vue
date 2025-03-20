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
import { ref, onMounted } from 'vue'
import axios from 'axios'

const image = ref<string>('')

// 画像をデバイスにダウンロードさせる
const saveImage = async () => {
  // imageの値が空の場合は処理を中断
  if (!image.value){
    console.error('画像がありません')
    return
  } 
  return new Promise((resolve, reject) => {
    const a = document.createElement('a')
    a.href = image.value
    a.download = 'image.png'
    a.click()
    resolve('画像保存成功')
  })
}

const getImage = async () => {
  try {
    const response = await axios.get('http://localhost:8000/get_image/')
    image.value = `data:image/png;base64,${response.data.image}`
    console.log('画像取得成功')
  } catch (error) {
    console.error('画像取得エラー: ', error)
  }
}

// ページが読み込まれたときにgetImage関数を実行
onMounted(() => {
  getImage()
})
</script>