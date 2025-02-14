<template>
  <div class="img-box-wrapper">
    <div class="img-box"
         @touchstart="touchStart"
         @touchmove="touchMove"
         @touchend="touchEnd">
      <span @click="showPrevImage" class="arrow left" v-if="images.length > 1 && currentShowedImage !== 0"></span>
      <div class="slider" :style="sliderStyle">
        <div v-for="(image, i) in images"
             :key="image"
             class="slide">
          <img :src="path + image.name"
               alt="image"
               @load="setImageDimensions" />
        </div>
      </div>
      <span @click="showNextImage" class="arrow right" v-if="images.length > 1 && currentShowedImage !== images.length - 1"></span>
    </div>
  </div>
</template>


<script>
export default {
  name: 'ImgBox',
  props: {
    images: {
      type: Array,
      required: true
    },
    path: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      currentShowedImage: 0,
      touchStartX: 0,
      touchEndX: 0,
      slideTransition: 'transform 0.3s ease',
      slideOffset: 0
    }
  },
  computed: {
    sliderStyle() {
      return {
        transform: `translateX(${-100 * this.currentShowedImage + this.slideOffset}%)`,
        transition: this.slideTransition
      }
    }
  },
  methods: {
    showNextImage() {
      if (this.currentShowedImage < this.images.length - 1) {
        this.currentShowedImage++
      }
    },
    showPrevImage() {
      if (this.currentShowedImage > 0) {
        this.currentShowedImage--
      }
    },
    setImageDimensions(event) {
      const img = event.target
      const container = img.parentElement
      const containerRatio = container.clientWidth / container.clientHeight
      const imgRatio = img.naturalWidth / img.naturalHeight

      if (imgRatio > containerRatio) {
        // 이미지가 더 넓은 경우
        img.style.width = '100%'
        img.style.height = 'auto'
        const heightDiff = (container.clientHeight - img.clientHeight) / 2
        img.style.marginTop = `${heightDiff}px`
      } else {
        // 이미지가 더 높은 경우
        img.style.height = '100%'
        img.style.width = 'auto'
        const widthDiff = (container.clientWidth - img.clientWidth) / 2
        img.style.marginLeft = `${widthDiff}px`
      }
    },
    touchStart(e) {
      this.touchStartX = e.touches[0].clientX
      this.slideTransition = 'none'
    },
    touchMove(e) {
      const currentX = e.touches[0].clientX
      const diff = currentX - this.touchStartX
      this.slideOffset = (diff / this.boxWidth) * 100
    },
    touchEnd() {
      this.slideTransition = 'transform 0.3s ease'
      if (Math.abs(this.slideOffset) > 20) {
        if (this.slideOffset > 0) {
          this.showPrevImage()
        } else {
          this.showNextImage()
        }
      }
      this.slideOffset = 0
    }
  },
}
</script>

<style scoped>
.img-box-wrapper {
  max-width: 800px;
  height: 15rem;
  display: flex;
  justify-content: center;
}

.img-box {
  width: 65%;
  height: 15rem;
  position: relative;
  overflow: hidden;
  background: var(--vp-c-bg);
}

.slider {
  display: flex;
  width: 100%;
  height: 100%;
}

.slide {
  flex: 0 0 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

img {
  object-fit: contain;
  margin: 0 !important;
}

.arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 2em;
  height: 2em;
  background-color: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s;
}

.arrow.left {
  left: 10px;
  transform: rotate(-90deg);
}

.arrow.right {
  right: 10px;
  transform: rotate(90deg);
}

.arrow:hover {
  background-color: rgba(255, 255, 255, 0.6);
}

/* 다크모드 화살표 스타일 */
[data-theme='dark'] .arrow {
  background-color: rgba(0, 0, 0, 0.4);
}

[data-theme='dark'] .arrow:hover {
  background-color: rgba(0, 0, 0, 0.6);
}
</style>