<template>
  <div class="study-container">
    <span class="study-list-title">스터디</span>
    <div class="study-list-description">함께 공부하고 성장합니다.</div>
    <div class="study-list">
      <div v-if="studies.length === 0" class="no-studies">등록된 스터디가 없습니다.</div>
      <div v-for="study in studies" :key="study.slug">
        <StudyCard :study="study"/>
      </div>
    </div>
  </div>
</template>

<script>
import StudyCard from "./StudyCard.vue";

export default {
  name: "StudyList",
  components: { StudyCard },
  data() {
    return {
      studies: __STUDIES__ || [],
    }
  },
  mounted() {
    document.body.classList.remove('page-has-title')
  }
}
</script>

<style scoped>

.study-container {
  width: 1000px;
  position: relative;
  left: -20%;
  margin: 0 auto;
  padding: 20px;
}

.study-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
}

.study-list-title {
  font-size: 1.875rem;
  font-weight: 700;
  position: relative;
  left: 12%;
  padding-left: 2rem;
  margin-bottom: 1rem;
  margin-top: 1rem;
}

.study-list-description {
  font-size: 1rem;
  color: var(--vp-c-text-mute);
  position: relative;
  left: 12.3%;
  padding-left: 2rem;
  margin-top: 1rem;
  margin-bottom: 3rem;
}

.no-studies {
  grid-column: 1 / -1;
  text-align: center;
  color: var(--vp-c-text-mute);
  font-size: 1rem;
  padding: 2rem 0;
}
</style>
