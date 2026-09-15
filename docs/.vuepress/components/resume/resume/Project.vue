<template>
  <div class="project-section">
    <div class="header2">프로젝트 경험</div>
    <div class="project-item">
      <div class="project-header">
        <div class="company-name">아그모</div>
        <div class="position-period">
          <span class="position">백엔드 엔지니어</span><span class="period"> / 2025.02 ~ 현재</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">SeamOS World 시뮬레이터</div>
            <div class="period">2026.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> &#8226; ISOBUS 기반 농기계 소프트웨어를 개발·검증하는 디지털 트윈 플랫폼 구축</span></div>
            <div class="responsibility-detail"> &#8226; QEMU 로 Bosch CCU 하드웨어 에뮬레이션 — CAN FD·IMU 칩 모델을 직접 제작해 실 디바이스와 동일한 SDK 스택 구동</div>
            <div class="responsibility-detail"> &#8226; 3D 시뮬레이터가 GPS·CAN·ISOBUS 신호를 실시간 공급, Rust 신호 허브·브리지로 앱까지 전달</div>
            <div class="responsibility-detail"> &#8226; Electron 대시보드(텔레메트리·로그·MQTT) 개발, Homebrew·APT·S3 로 릴리스 자동화</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">SEAMOS 마켓플레이스</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • ISOBUS 기반 장비에 앱을 제공하는 마켓플레이스 서비스</span></div>
            <div class="responsibility-detail"> &#8226; 마켓플레이스 백엔드 API(앱 설치/다운로드/검색, 디바이스·회원·조직 관리)를 멀티모듈 아키텍처로 설계</div>
            <div class="responsibility-detail"> &#8226; AWS IoT(MQTT)/HTTPS 디바이스 상태 수집 + 상태 전이 엔진 구현, idempotency·retry·rollback 정책과 Redis 분산 락으로 멱등성 확보</div>
            <div class="responsibility-detail"> &#8226; 디바이스 Shadow 상태 SQS Consumer 적재 + Redis 캐싱으로 인증·가드 경로의 반복 DB 조회 제거</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">자율주행 로그 데이터 파이프라인</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 차량 이벤트 로그를 수집·집계·적재·시각화하는 E2E 데이터 파이프라인 개발</span></div>
            <div class="responsibility-detail"> &#8226; Protobuf 이벤트 수집 서버에서 Kafka 전송 + 위치정보 AWS KMS 암호화, Kafka Streams 로 실시간 위치·작업량·경고 집계와 DLQ 설계</div>
            <div class="responsibility-detail"> &#8226; Spring Batch 일배치로 history S3 적재·통계 산출, 청크·메모리 튜닝으로 OOM 해소</div>
            <div class="responsibility-detail"> &#8226; LiveLocation WebSocket 송출 소켓 서버와 주행기록·사용자 통계 모니터링 API 개발</div>
          </div>
        </div>
      </div>
    </div>
    <div class="project-item">
      <div class="project-header">
        <div class="company-name">테크랩스</div>
        <div class="position-period">
          <span class="position">AI 사업부 백엔드 엔지니어</span><span class="period"> / 2023.11 ~ 2025.02</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">Interest detection</div>
            <div class="period">2024.04 ~ 2025.02</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 사용자가 선택한 상품을 통해 GPT 로 관심사 키워드를 추출하고 상품을 추천하는 서비스</span></div>
            <div class="responsibility-detail"> &#8226; 상품/리뷰 데이터로 추천문구를 추출하는 LLM 기반 ETL 파이프라인과 langchain FastAPI 서버 개발</div>
            <div class="responsibility-detail"> &#8226; 수 초 이상 걸리던 GPT 요청을 비동기 구조로 전환해 응답 200~300ms 로 개선</div>
            <div class="responsibility-detail"> &#8226; EKS·Lambda·SNS 서버리스 이벤트 아키텍처로 일 100만 건 상품·1만 건 리뷰의 키워드 추출 처리</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">연합뉴스 추천 시스템 파이프라인 설계</div>
            <div class="period">2024.03 ~ 2024.10</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 연합뉴스 피드의 추천 시스템 개발</span></div>
            <div class="responsibility-detail"> &#8226; 구독자 이벤트를 수집·적재하는 ETL 파이프라인과 주기(일/시간)별 추천 배치 프로세스 구축</div>
            <div class="responsibility-detail"> &#8226; 추천 결과 및 사용자 이벤트 대시보드 API 개발</div>
            <div class="responsibility-detail"> &#8226; 반정규화·파티셔닝으로 수백만 row DB 조회를 초 단위에서 500ms 이하로 단축</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">추천 시스템 관리</div>
            <div class="period">주요 업무</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 하루 8000만 건 로그, API 호출 4000만 회의 Spring 기반 추천 API 및 배치 시스템 관리</span></div>
            <div class="responsibility-detail"> • 데이터독 PoC 및 도입 및 고도화로 실시간 모니터링 시스템 구축</div>
            <div class="responsibility-detail"> • 자사 6개 모든 서비스에 대한 기능/부하 테스트 진행 및 비용감소 프로젝트로 AWS 비용 월 56% 감축</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Experience"
}
</script>

<style scoped>

.project-section {
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}
.project-item {
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 4px;
}

.project-header {
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.company-name {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
  font-weight: 600;
  margin-right: 0.5rem;
  color: var(--vp-c-text-1);
}

.position-period {
  margin-top: 0.25rem;
}

.period {
  margin-top: 0.25rem;
  font-weight: 300;
  font-size: 0.8rem;
  color: var(--vp-c-text-2, #6c757d);
}

.position {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.responsibilities {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.responsibility-item {
  margin-bottom: 1rem;
  display: flex;
}

.responsibility-header {
  font-weight: 700;
  margin-right: 0.5rem;
  min-width: 140px;
  color: var(--vp-c-text-1);
}

.responsibility-title {
  font-size: 1rem;
  font-weight: 700;
  max-width: 130px;
  color: var(--vp-c-text-1);
}

.responsibility-description {
}

.responsibility-detail-main {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  font-weight: 600;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  padding-left: 1rem;
  text-indent: -1rem;
}

.responsibility-detail-main span {
  border-bottom: 1px solid var(--vp-c-border);
}

.responsibility-detail {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;
  line-height: 1.3;
  padding-left: 1rem;
  text-indent: -1rem;
}

.responsibility-skills {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;

}

.responsibility-skills span {
}


</style>
