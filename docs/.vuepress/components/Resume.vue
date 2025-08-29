<template>
  <h1>몰입을 즐기는 개발자, 김호빈입니다.</h1>

  <h2>자기소개</h2>
  <div> 2년차 백엔드 개발자로 추천 서비스 스타트업인 아이겐코리아에서 대규모 로그 관리 및 추천 API 서버의 개발과 운영했습니다. 테스트
    코드 작성을 즐기며 실제 환경에 맞는 부하테스트를 통해 가능한 모든 경우를 대비하고자 노력합니다. 이를 통해 메인서버의 리소스를 효
    율화하고 비용을 56% 절감했습니다. 또한, 반복되는 작업을 자동화하는 것을 선호하여 데이터독을 활용해 API 호출 패턴을 시각화하고
    대시보드를 구축해 운영실의 분석 요청을 자동화한 경험이 있습니다.</div>
  <div>스스로 발전하는 것에 관심이 많습니다. 신기술에 관심이 많아 kubernetes, k6 test, Datadog 등 여러 기술을 배우고 실제로 업무에
    적용하고자 노력했습니다. 뿐만 아니라 LLM, 머신러닝과 같이 현재 직무와 직접 관련없더라도 흥미로운 기술을 공부하는 걸 좋아합니
    다. 이를 통해 문제가 발생했을 때 항상 더 나은 방법과 기술을 찾고자 노력합니다.</div>
    <div>대화와 협업이 개발자의 핵심 역량이라고 생각합니다. 비즈니스 가치를 높이기 위해 팀원들과 항상 소통하며 그 결과를 코드에 반영하
    기 위해 노력합니다. 애자일 프로세스에 익숙하고 다양한 구성원과 적극적인 커뮤니케이션으로 문제를 해결하여 보다 나은 결과를 만들
    어 내고자 합니다. interest-detection 프로젝트를 기획부터 서비스 단계까지 참여하며 기획의도를 개발언어로 옮기고 개발언어를 비개
    발자에게 설명하는 능력을 쌓았습니다.</div>

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
      <div class="work-list">
        <span class="work-name"></span>
        <span class="work-desc"></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Resume",
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