<template>
  <div class="skill">
    <span class="title">기술</span>
    <div class="resume-body">
      <div class="skill-list"><strong>백엔드</strong> - Java, Kotlin, Spring, Spring Data JPA</div>
      <div class="skill-list"><strong>데이터베이스</strong> - Postgres, Redis, MongoDB</div>
      <div class="skill-list"><strong>데브옵스</strong> - AWS, Kubenetes, Kafka</div>
    </div>
  </div>
  <div class="work-ex">
    <span class="title">직무 경험</span>
    <div class="resume-body">
      <div class="work-list">
        <div class="work-name">아그모</div>
        <div class="work-desc">백엔드 엔지니어 | 자율주행 데이터 파이프라인 구성 및 관리 | 2025.02 ~</div>
      </div>
      <div class="work-list">
        <span class="work-name">아이겐 코리아</span>
        <span class="work-desc">백엔드 엔지니어 | 초개인화 추천서비스를 위한 유저 행동 로그 수집 및 데이터 파이프라인 구성 | 2023.11 ~ 2025.02</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
name: "Resume"
}
</script>

<style scoped>

.title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--vp-c-accent);
}

.resume-body {
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.skill-list {
  margin-top: 0.5rem;
  margin-left: 1rem;

  strong {
    font-weight: 700;
  }
}

.work-list {
  margin-top: 0.4rem;
  padding-top: 0.6rem;
  margin-left: 1rem;
  display: flex;
  border-top : 1px solid var(--vp-c-control-hover);

  strong {
    font-weight: 700;
  }
}

.work-name {
  font-weight: 700;
  font-size: 1.1rem;
  margin-right: 0.5rem;
  width: 8rem;
}

.work-desc {
  margin-top: 0.05rem;
}

</style>