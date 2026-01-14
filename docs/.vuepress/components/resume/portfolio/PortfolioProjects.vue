<template>
  <section class="projects-section">
    <div class="header2">Projects</div>

    <!-- 프로젝트 1: SEAMOS 마켓플레이스 -->
    <div class="project-item">
      <div class="project-header">
        <h3>SEAMOS 마켓플레이스</h3>
        <span class="period">2025.04 - 현재</span>
      </div>

      <div class="project-overview">
        <p><strong>개요:</strong> ISOBUS 기반 농기계/건설기계 장비에 대한 앱을 제공하는 마켓플레이스 서비스 개발</p>
        <p><strong>수행 인원:</strong> 3명 (BE 1, FE 1, PM 1)</p>
        <p><strong>역할:</strong> Backend 개발, 인프라 구축, 모니터링 시스템 설계</p>
      </div>

      <div class="project-details">
        <h4>수행 업무</h4>
        <ul>
          <li>마켓 플레이스 백엔드 API 개발 (앱 관리, 디바이스 관리, 회원 관리 등)</li>
          <li>AWS IoT Core를 활용한 디바이스와 MQTT 통신 시스템 구축</li>
          <li>Grafana, Prometheus, Loki, Pyroscope를 활용한 통합 모니터링 시스템 구축</li>
          <li>ArgoCD를 이용한 GitOps 기반 배포 파이프라인 구축</li>
        </ul>

        <h4>성과</h4>
        <ul>
          <li>안정적인 앱 배포 및 업데이트 시스템 구축</li>
          <li>실시간 디바이스 상태 모니터링 및 원격 제어 기능 구현</li>
        </ul>

        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Kotlin</span>
          <span class="tech-tag">Spring Boot</span>
          <span class="tech-tag">PostgreSQL</span>
          <span class="tech-tag">AWS IoT</span>
          <span class="tech-tag">EKS</span>
          <span class="tech-tag">ArgoCD</span>
        </div>
      </div>
    </div>

    <!-- 프로젝트 2: 자율주행 모니터링 앱 -->
    <div class="project-item">
      <div class="project-header">
        <h3>자율주행 모니터링 시스템</h3>
        <span class="period">2025.02 - 현재</span>
      </div>

      <div class="project-overview">
        <p><strong>개요:</strong> 농기계 자율주행 중 생성되는 대용량 로그 수집 및 분석 파이프라인 구축</p>
        <p><strong>수행 인원:</strong> 2명 (BE 1, FE 1)</p>
        <p><strong>역할:</strong> 데이터 파이프라인 설계 및 개발, 백엔드 API 개발</p>
      </div>

      <div class="project-details">
        <h4>수행 업무</h4>
        <ul>
          <li>실시간 자율주행 로그 수집을 위한 ETL 파이프라인 개발</li>
          <li>Kafka Streams를 활용한 실시간 로그 집계 및 통계 분석 로직 구현</li>
          <li>에러 처리를 위한 DLT(Dead Letter Topic) 설계 및 재처리 프로세스 구축</li>
          <li>MongoDB를 활용한 비정형 로그 데이터 저장 및 조회 최적화</li>
        </ul>

        <h4>성과</h4>
        <ul>
          <li>실시간 자율주행 현황 모니터링 대시보드 제공</li>
          <li>로그 분석을 통한 자율주행 알고리즘 개선 데이터 제공</li>
        </ul>

        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Java</span>
          <span class="tech-tag">Spring Boot</span>
          <span class="tech-tag">Kafka</span>
          <span class="tech-tag">MongoDB</span>
          <span class="tech-tag">AWS ECS</span>
        </div>
      </div>
    </div>

    <!-- 프로젝트 3: Interest detection -->
    <div class="project-item">
      <div class="project-header">
        <h3>Interest detection (관심사 추출 및 추천)</h3>
        <span class="period">2024.04 - 2025.02</span>
      </div>

      <div class="project-overview">
        <p><strong>개요:</strong> 사용자 행동 기반 관심사 키워드 추출 및 상품 추천 LLM 서비스</p>
        <p><strong>수행 인원:</strong> 4명 (BE 2, AI 2)</p>
        <p><strong>역할:</strong> 백엔드 시스템 설계 및 개발, LLM 파이프라인 구축</p>
      </div>

      <div class="project-details">
        <h4>수행 업무</h4>
        <ul>
          <li>상품/리뷰 데이터 기반 추천 문구 추출 LLM ETL 파이프라인 개발</li>
          <li>Spring Boot와 FastAPI(LangChain)를 연동한 하이브리드 아키텍처 설계</li>
          <li>비동기 처리를 통한 GPT 응답 지연 시간 개선 (수 초 -> 200~300ms 체감)</li>
          <li>AWS EKS, Lambda, SNS를 활용한 서버리스 이벤트 기반 아키텍처 구축</li>
        </ul>

        <h4>성과</h4>
        <ul>
          <li>일 100만 건 이상의 상품 데이터 및 1만 건 이상의 리뷰 데이터 처리</li>
          <li>개인화 추천을 통한 클릭률(CTR) 및 구매 전환율 상승 기여</li>
        </ul>

        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Kotlin</span>
          <span class="tech-tag">Spring Boot</span>
          <span class="tech-tag">Python</span>
          <span class="tech-tag">FastAPI</span>
          <span class="tech-tag">AWS EKS</span>
          <span class="tech-tag">MongoDB</span>
          <span class="tech-tag">OpenAI API</span>
        </div>

         <h4>트러블 슈팅</h4>
          <div class="troubleshooting">
            <div class="ts-item">
              <p class="ts-problem"><strong>Problem:</strong> GPT API 호출 시 응답 지연으로 인한 사용자 경험 저하</p>
              <p class="ts-solution"><strong>Solution:</strong> 요청을 비동기 큐(SQS)에 적재하고, 별도 워커 프로세스에서 처리 후 결과를 저장, 클라이언트는 폴링 또는 웹소켓으로 결과 수신하도록 구조 변경하여 체감 대기 시간 단축</p>
            </div>
          </div>
      </div>
    </div>

     <!-- 프로젝트 4: 연합뉴스 추천 시스템 -->
    <div class="project-item">
      <div class="project-header">
        <h3>연합뉴스 추천 시스템</h3>
        <span class="period">2024.03 - 2024.10</span>
      </div>

      <div class="project-overview">
        <p><strong>개요:</strong> 연합뉴스 독자를 위한 개인화 뉴스 추천 시스템 구축</p>
        <p><strong>수행 인원:</strong> 3명 (BE 1, AI 2)</p>
        <p><strong>역할:</strong> 데이터 파이프라인 구축, 추천 API 개발</p>
      </div>

      <div class="project-details">
        <h4>수행 업무</h4>
        <ul>
          <li>사용자 이벤트 수집 및 적재를 위한 ETL 파이프라인 개발 (Kinesis -> Redshift)</li>
          <li>주기별 추천 로직 실행을 위한 배치 프로세스 구축</li>
          <li>추천 결과 서빙을 위한 고성능 API 개발</li>
          <li>DB 반정규화 및 파티셔닝을 통한 조회 성능 최적화</li>
        </ul>

        <h4>성과</h4>
        <ul>
          <li>수백만 건의 데이터 조회 시간을 초 단위에서 500ms 이하로 단축</li>
          <li>안정적인 뉴스 추천 서비스 운영</li>
        </ul>

        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Kotlin</span>
          <span class="tech-tag">Spring Boot</span>
          <span class="tech-tag">PostgreSQL</span>
          <span class="tech-tag">AWS Kinesis</span>
          <span class="tech-tag">Redshift</span>
        </div>
      </div>
    </div>

  </section>
</template>

<script>
export default {
  name: 'PortfolioProjects'
}
</script>

<style scoped>
.projects-section {
  margin-bottom: 3rem;
}

.project-item {
  margin-bottom: 3rem;
  padding: 1.5rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px solid var(--vp-c-border);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--vp-c-border);
  padding-bottom: 0.5rem;
}

.project-header h3 {
  font-size: 1.5rem;
  margin: 0;
  color: var(--vp-c-brand);
  font-weight: 700;
}

.period {
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.project-overview {
  background-color: var(--vp-c-bg-alt);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.project-overview p {
  margin: 0.3rem 0;
  color: var(--vp-c-text-1);
}

h4 {
  font-size: 1.1rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: var(--vp-c-brand);
  font-weight: 600;
}

ul {
  padding-left: 1.2rem;
  margin-bottom: 1rem;
}

li {
  margin-bottom: 0.4rem;
  color: var(--vp-c-text-1);
  font-size: 0.95rem;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tech-tag {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  background-color: var(--vp-c-brand-dimm);
  color: var(--vp-c-brand);
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.troubleshooting {
  background-color: var(--vp-c-bg-alt);
  border-left: 4px solid var(--vp-c-warning);
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.ts-item {
  margin-bottom: 0.5rem;
}

.ts-problem {
  color: var(--vp-c-text-1);
  margin-bottom: 0.3rem;
}

.ts-solution {
  color: var(--vp-c-text-1);
}
</style>
