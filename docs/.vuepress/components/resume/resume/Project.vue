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
            <div class="responsibility-title">SEAMOS 마켓플레이스 &amp; 디바이스 OTA</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • ISOBUS 기반 장비에 앱을 제공하는 마켓플레이스 및 디바이스 OTA 관리 서비스</span></div>
            <div class="responsibility-detail"> • 마켓플레이스 백엔드 API 개발 (앱 설치/다운로드/검색, 디바이스·회원·조직 관리)를 멀티모듈 아키텍처로 설계</div>
            <div class="responsibility-detail"> • AWS IoT(MQTT)/HTTPS 디바이스 상태 수집 + 상태 전이 엔진, OTA 캠페인·업데이트·취소·retry 구현</div>
            <div class="responsibility-detail"> • idempotency·retry·timeout·rollback 정책과 Redis 분산 락으로 멱등하고 회귀에 강한 OTA 처리 구현</div>
            <div class="responsibility-detail"> • 디바이스 Shadow 상태 SQS Consumer 적재 + Redis 캐싱으로 인증·가드 경로의 반복 DB 조회 제거</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Kotlin/Spring</span>
                <span class="tag">AWS IoT</span>
                <span class="tag">SQS</span>
                <span class="tag">Postgres</span>
                <span class="tag">Redis</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">Keycloak OIDC 인증 &amp; 보안</div>
            <div class="period">2025.05 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 통합 Keycloak 인증 서버 구축 및 OIDC 인증 전환, 디바이스 단위 인증 체계 구축</span></div>
            <div class="responsibility-detail"> • Keycloak 커스텀 SPI 개발 — 기존 사용자 BCrypt 마이그레이션, email OTP 2-step 회원가입, device direct grant, user CUD 이벤트 SNS 발행</div>
            <div class="responsibility-detail"> • BFF 패턴 Keycloak 콜백/로그인/로그아웃/refresh 엔드포인트 구현, SQS로 KC user 이벤트 수신 후 로컬 DB 동기화</div>
            <div class="responsibility-detail"> • deviceId+pin → per-device client JWT 발급, device-scoped 권한 및 토큰 role/userId claim 정합화</div>
            <div class="responsibility-detail"> • @PreAuthorize 세분화 권한, IDOR 방어, OWASP 기반 보안 점검(평문 로깅 마스킹·시크릿 외부화) 수행</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Kotlin/Spring</span>
                <span class="tag">Keycloak SPI</span>
                <span class="tag">Spring Security</span>
                <span class="tag">SNS/SQS</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">자율주행 로그 데이터 파이프라인</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 차량 이벤트 로그를 수집·집계·적재·시각화하는 E2E 데이터 파이프라인 개발</span></div>
            <div class="responsibility-detail"> • Protobuf 차량 이벤트 수집 서버(log-server)에서 Kafka 전송 + 위치정보 AWS KMS 암호화 적용</div>
            <div class="responsibility-detail"> • Kafka Streams(stream-processors) 실시간 집계 — 실시간 위치·작업량(workunit)·경고·동시접속자, structured-log 전환, DLQ 설계</div>
            <div class="responsibility-detail"> • Spring Batch(log-batch) 일배치로 history S3 적재·통계 산출, 청크·메모리 튜닝으로 OOM 해소</div>
            <div class="responsibility-detail"> • 실시간 위치 소켓 서버(socket-consumer) — LiveLocation WebSocket 송출 + KMS 좌표 복호화</div>
            <div class="responsibility-detail"> • 모니터링 API(monitor-server) — 주행기록 CSV 조회, 사용자 통계 대시보드, Envers 변경 이력 관리</div>
            <div class="responsibility-skills">
                <div class="tech-stack">
                  <span class="tag">Kotlin/Spring</span>
                  <span class="tag">Kafka Streams</span>
                  <span class="tag">Spring Batch</span>
                  <span class="tag">MongoDB</span>
                  <span class="tag">Protobuf</span>
                  <span class="tag">AWS KMS</span>
                </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">NISHIBE 택시 운행관리 플랫폼</div>
            <div class="period">2026.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 일본 택시 운행관리 서비스 백엔드를 신규 설계·구축</span></div>
            <div class="responsibility-detail"> • User/Vehicle 2종 인증 주체를 추상화한 JWT subjectType 분기 인증 + 조직 계층 권한 상속(CTE) 설계</div>
            <div class="responsibility-detail"> • 경량 ReBAC(Zanzibar 모델) 기반 권한 시스템 설계 및 구축</div>
            <div class="responsibility-detail"> • 운행일보/월보 — DTG CSV 파싱·집계·매핑 배치 + presigned 업로드, 기간 집계 대시보드 API 개발</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Kotlin/Spring</span>
                <span class="tag">ReBAC</span>
                <span class="tag">Postgres</span>
                <span class="tag">Redis</span>
                <span class="tag">AWS SES</span>
                <span class="tag">S3</span>
              </div>
            </div>
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
            <div class="responsibility-detail"> • 상품/리뷰 데이터로 추천문구를 추출하는 LLM 기반 ETL 파이프라인 개발</div>
            <div class="responsibility-detail"> • 추천문구와 추천결과를 조합하는 Spring 서버와 langchain 을 활용하는 fast api 서버 개발</div>
            <div class="responsibility-detail"> • 수 초 이상 걸리는 gpt 요청으로 인한 지연을 비동기로 구조를 변경하여 200ms ~ 300ms 로 개선</div>
            <div class="responsibility-detail"> • EKS 와 Lambda, SNS 를 활용한 서버리스 이벤트 기반 아키텍처로 일 100만 건의 상품과 1만 건의 리뷰에서 키워드 및 추천문구 출력 처리</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Kotlin/Spring</span>
                <span class="tag">Python</span>
                <span class="tag">AWS EKS</span>
                <span class="tag">MongoDB</span>
                <span class="tag">OPENAI API</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">연합뉴스 추천 시스템 파이프라인 설계</div>
            <div class="period">2024.03 ~ 2024.10</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 연합뉴스 피드의 추천 시스템 개발</span></div>
            <div class="responsibility-detail"> • 구독자의 이벤트를 수집하고 적재하는 ETL 파이프라인 개발</div>
            <div class="responsibility-detail"> • 주기(일/시간)별 추천 로직을 추출하는 배치 프로세스 구축 및 관리</div>
            <div class="responsibility-detail"> • 추천 결과 및 사용자 이벤트를 대시보드로 보여주는 API 개발</div>
            <div class="responsibility-detail"> • 반정규화 및 파티셔닝으로 수 백만 row 의 DB 조회시간을 초 단위에서 500ms 이하로 단축</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Kotlin/Spring</span>
                <span class="tag">Postgres(AWS Aurora)</span>
                <span class="tag">Kinesis</span>
                <span class="tag">Redshift</span>
              </div>
            </div>
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
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Java/Spring</span>
                <span class="tag">Kotlin</span>
                <span class="tag">Postgres(AWS Aurora)</span>
                <span class="tag">Kinesis</span>
                <span class="tag">Datadog</span>
                <span class="tag">S3</span>
              </div>
            </div>
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
