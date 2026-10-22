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
            <div class="responsibility-title">방제기 IoT 플랫폼</div>
            <div class="period">2026.10 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> &#8226; 방제기 원격 관제·조종을 위한 IoT 백엔드, AWS 리소스, 디바이스 인터페이스 설계·구축</span></div>
            <div class="responsibility-detail"> &#8226; 디바이스–클라우드 인터페이스 정의 — MQTT 토픽, Device Shadow 상태 모델, cmd/ack 명령 프로토콜, 공장 프로비저닝 흐름</div>
            <div class="responsibility-detail"> &#8226; Kotlin Spring 백엔드 — IoT Rule → SQS 이벤트 처리, 앱용 MQTT Custom Authorizer Lambda, Amazon KVS WebRTC 영상·DataChannel 원격 조종 연동</div>
            <div class="responsibility-detail"> &#8226; AWS 리소스 Terraform IaC — IoT Core(mTLS 인증서·정책), VPC·ALB·EC2·RDS·Redis·SQS, Firehose 텔레메트리 S3 아카이브</div>
            <div class="responsibility-detail"> &#8226; Python 디바이스 시뮬레이터로 로컬 E2E 검증 환경 구성</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">NISHIBE 택시 운행관리 플랫폼</div>
            <div class="period">2026.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> &#8226; 일본 택시 7만 대 이상의 단말 데이터를 수집·통제하는 운행관리 서비스 백엔드와 클라우드 인프라 구축</span></div>
            <div class="responsibility-detail"> &#8226; 미터기·DTG(디지털 운행기록계) 로그 sync API 를 sequence 기반 멱등 처리로 설계</div>
            <div class="responsibility-detail"> &#8226; SD카드 일계 데이터 일괄 수신과 운행기록 CSV 처리 개발</div>
            <div class="responsibility-detail"> &#8226; 도쿄 리전 EKS·Aurora·Redis·ArgoCD 인프라 신규 구축, Terraform 모듈화와 GitHub OIDC CI 인증, ApplicationSet 배포 전환</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">자율주행 앱 데이터 수집 &amp; 앱 관리</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> &#8226; 자율주행 농기계 앱의 주행 데이터를 수집·집계·관제하는 파이프라인과 앱 운영 관리</span></div>
            <div class="responsibility-detail"> &#8226; Protobuf 이벤트 수집 서버에서 Kafka 전송 + 위치정보 AWS KMS 암호화, Kafka Streams 로 실시간 위치·작업량·경고 집계와 DLQ 설계</div>
            <div class="responsibility-detail"> &#8226; Spring Batch 일배치로 history S3 적재·통계 산출, 청크·메모리 튜닝으로 OOM 해소</div>
            <div class="responsibility-detail"> &#8226; LiveLocation WebSocket 송출 소켓 서버와 주행기록·장비 가동 통계 관제 API 개발</div>
            <div class="responsibility-detail"> &#8226; 자율주행 서비스(log-server·stream·batch·monitor) GitHub Actions CI/CD 와 Lambda SAM 배포 파이프라인 구축</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">SDM 플랫폼 인프라 · IoT · 기기 관리</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> &#8226; ISOBUS 장비에 앱을 배포·관리하는 SEAMOS 디바이스 관리(SDM) 플랫폼의 인프라·IoT·기기 관리 백엔드</span></div>
            <div class="responsibility-detail"> &#8226; AWS IoT Core 토픽·정책·인증서 설계, Device Shadow 상태 SQS 적재 + Redis 캐싱, 디바이스 상태 전이 엔진 구현</div>
            <div class="responsibility-detail"> &#8226; OTA 캠페인·업데이트·취소·retry 와 idempotency·timeout·rollback 정책, Redis 분산 락으로 멱등한 OTA 처리</div>
            <div class="responsibility-detail"> &#8226; AWS IoT Job 상태 기반 잔류 배포 확정, presigned URL 만료 재발송, 재설치 루프 차단, 최소 BSP·런타임 버전 검사로 현장 OTA 실패 경로 정리</div>
            <div class="responsibility-detail"> &#8226; EKS·Terraform·ArgoCD(Helm) GitOps 로 dev/prod 운영, Karpenter·HPA 오토스케일링, Grafana·Prometheus·Loki·Tempo 관측성 구축</div>
            <div class="responsibility-detail"> &#8226; 위치정보사업자 인증 2건 획득 — KMS 암호화, IAM·RBAC 최소권한, 접근 로그 감사, Prowler 보안 점검 자동화</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">SeamOS World SIL 검증 플랫폼</div>
            <div class="period">2026.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> &#8226; ISOBUS 기반 농기계 소프트웨어를 개발·검증하는 SIL(Software-in-the-Loop) 디지털 트윈 플랫폼 구축</span></div>
            <div class="responsibility-detail"> &#8226; QEMU 로 Bosch CCU 하드웨어 에뮬레이션 — CAN FD·IMU 칩 모델을 직접 제작해 실 디바이스와 동일한 SDK 스택 구동</div>
            <div class="responsibility-detail"> &#8226; 3D 시뮬레이터가 GPS·CAN·ISOBUS 신호를 실시간 공급, Rust 신호 허브·브리지로 앱까지 전달</div>
            <div class="responsibility-detail"> &#8226; ISO 11783-6 VT·ISO 11783-10 TC 서버, Lidar·Radar·초음파 센서, 흙 역학·ISO 8608 노면 모델, 스프레이어·균평기·이앙기 작업기 ECU 모델 구현</div>
            <div class="responsibility-detail"> &#8226; 시크릿 키 하나로 시뮬레이터 EC2 를 생성·접속·삭제하는 온디맨드 클라우드(API Gateway·Lambda·DynamoDB·ALB, Keycloak device flow, Terraform)</div>
            <div class="responsibility-detail"> &#8226; 엣지 디바이스 상태 Electron 대시보드(텔레메트리·로그·MQTT), Homebrew·APT·S3 크로스 플랫폼 릴리스 자동화</div>
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
            <div class="responsibility-detail"> &#8226; LLM 기반 ETL 파이프라인과 langchain FastAPI 서버 개발, 비동기 전환으로 응답 200~300ms 로 개선</div>
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
            <div class="responsibility-detail"> &#8226; 구독자 이벤트 ETL 파이프라인과 주기별 추천 배치 프로세스 구축, 대시보드 API 개발</div>
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
            <div class="responsibility-detail"> • 데이터독 PoC·도입·고도화로 전사 실시간 모니터링 시스템 구축</div>
            <div class="responsibility-detail"> • 자사 6개 서비스 기능/부하 테스트 진행 및 비용감소 프로젝트로 AWS 비용 월 56% 감축</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProjectDevice"
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
