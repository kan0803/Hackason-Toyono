<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const video = ref(null);
const canvas = ref(null);
const handShape = ref("undefined");
let stream = null;

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (video.value) {
      video.value.srcObject = stream;
      video.value.play();
      video.value.addEventListener("loadeddata", () => {
        console.log("カメラ映像の取得開始");
        detectHandShape();
      });
    }
  } catch (err) {
    console.error("カメラの取得に失敗しました:", err);
  }
};

const detectHandShape = async () => {
  if (!video.value || !canvas.value) return;

  const ctx = canvas.value.getContext("2d");
  const width = video.value.videoWidth;
  const height = video.value.videoHeight;

  if (width === 0 || height === 0) {
    console.warn("カメラ映像のサイズが取得できません。再試行します。");
    setTimeout(detectHandShape, 100);
    return;
  }

  canvas.value.width = width;
  canvas.value.height = height;

  ctx.clearRect(0, 0, width, height);
  ctx.drawImage(video.value, 0, 0, width, height);

  let src = cv.imread(canvas.value);
  if (src.empty()) {
    console.error("cv.imread() に失敗しました。");
    setTimeout(detectHandShape, 100);
    return;
  }

  let gray = new cv.Mat();
  let blur = new cv.Mat();
  let thresh = new cv.Mat();

  cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY);
  cv.GaussianBlur(gray, blur, new cv.Size(5, 5), 0);
  cv.threshold(blur, thresh, 100, 255, cv.THRESH_BINARY_INV);

  let contours = new cv.MatVector();
  let hierarchy = new cv.Mat();
  cv.findContours(thresh, contours, hierarchy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);

  if (contours.size() === 0) {
    console.warn("手の輪郭が検出されませんでした。");
    handShape.value = "不明";
    setTimeout(detectHandShape, 100);
    return;
  }

  let maxContour = contours.get(0);
  let maxSize = cv.contourArea(maxContour);

  for (let i = 1; i < contours.size(); i++) {
    let contour = contours.get(i);
    let size = cv.contourArea(contour);
    if (size > maxSize) {
      maxSize = size;
      maxContour = contour;
    }
  }

  let detectedShape = "不明";

  if (maxContour.total() >= 5) {
    let hull = new cv.Mat();
    let defects = new cv.Mat();

    //console.log(hull);
    //console.log(defects);

    cv.convexHull(maxContour, hull, false, true);
    console.log(cv.convexHull(maxContour, hull, false, true));

    if (hull.rows >= 4) {
      try {
        // convexityDefectsが正しく動作するかチェック
        if (!defects.empty()) {
          defects.delete();
        }
        cv.convexityDefects(maxContour, hull, defects);
      } catch (err) {
        //console.error("cv.convexityDefects() でエラーが発生しました:", err);
        hull.delete();
        defects.delete();
        setTimeout(detectHandShape, 100);
        return;
      }

      if (!defects.empty() && defects.rows > 0) {
        let defectCount = defects.rows;

        if (defectCount === 0) {
          detectedShape = "GU"; // グー
        } else if (defectCount === 2) {
          detectedShape = "TYOKI"; // チョキ
        } else if (defectCount >= 4) {
          detectedShape = "PA"; // パー
        }
      }
    } else {
      console.warn("凸包の点が少なすぎるため、判定をスキップしました。");
    }

    hull.delete();
    defects.delete();
  }

  handShape.value = detectedShape;
  console.log("判定結果:", detectedShape);

  // 後処理
  src.delete();
  gray.delete();
  blur.delete();
  thresh.delete();
  contours.delete();
  hierarchy.delete();

  setTimeout(detectHandShape, 100);
};

onMounted(async () => {
  try {
    if (typeof cv === "undefined") {
      console.log("OpenCV.js のロード開始");
      const script = document.createElement("script");
      script.src = "https://docs.opencv.org/4.5.5/opencv.js";
      script.onload = async () => {
        cv.onRuntimeInitialized = async () => {
          console.log("OpenCV.js の初期化完了");
          await startCamera();
        };
      };
      script.onerror = () => console.error("OpenCV.js の読み込みに失敗しました");
      document.body.appendChild(script);
    } else {
      await startCamera();
    }
  } catch (error) {
    console.error(error.message);
  }
});

onUnmounted(() => {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
});
</script>


<template>
  <div class="container">
    <video ref="video" autoplay class="video"></video>
    <canvas ref="canvas"></canvas>
    <p class="result">判定結果: {{ handShape }}</p>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100vh;
  background-color: #f0f0f0;
}

.video {
  width: 640px;
  height: 480px;
  border: 2px solid #333;
  background-color: black;
}

.canvas {
  display: none;
}

.result {
  margin-top: 10px;
  font-size: 20px;
  font-weight: bold;
  color: #333;
}
</style>
