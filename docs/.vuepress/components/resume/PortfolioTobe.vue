<template>
  <section class="projects-section">
    <div class="header2">포트폴리오</div>

    <!-- 01 보안 -->
    <div class="project-item">
      <div class="project-header">
        <h3>ISMS-P 보안 점검 자동화와 취약점 0건 달성</h3>
        <span class="period">아그모 | Prowler · Airflow · ESO · Kyverno · Trivy</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> AWS 계정이 늘면서 보안 점검이 수작업에 의존했고, 점검 결과가 수백 건이라 무엇부터 조치할지 판단하기 어려웠음.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>상용 CSPM 대신 오픈소스 Prowler 채택 — ISMS-P·CIS 체크 기본 제공, 결과 후처리 자유로움. Airflow로 매주 동일 조건 자동 실행</li>
          <li>수백 건의 우선순위 판단은 AI 에이전트가 심각도·서비스별로 분류해 조치안 제시 → 사람은 조치에 집중</li>
          <li>비중이 가장 큰 ECS/Lambda 평문 시크릿 134건을 External Secrets Operator로 이관, IAM 과대권한·혼동 대리 정리</li>
          <li>재발 방지를 위해 Kyverno admission, Trivy 이미지 스캔, gitleaks를 CI 게이트로 추가</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>Critical 180건·High 690건 → 0 (2계정 합산)</li>
          <li>시크릿 노출 134건 → 0 (ESO 이관)</li>
          <li>점검 주기 수동·비정기 → 매주 자동</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Prowler</span>
          <span class="tech-tag">Apache Airflow</span>
          <span class="tech-tag">External Secrets Operator</span>
          <span class="tech-tag">Kyverno</span>
          <span class="tech-tag">Trivy</span>
          <span class="tech-tag">gitleaks</span>
          <span class="tech-tag">AWS Secrets Manager</span>
        </div>
      </div>
    </div>

    <!-- 02 비용 -->
    <div class="project-item">
      <div class="project-header">
        <h3>AWS 비용 최적화 (-56% / -30%)</h3>
        <span class="period">테크랩스 / 아그모 | Karpenter · Spot/Graviton · VPC Endpoint · Infracost</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> 테크랩스는 6개 서비스가 트래픽 대비 과할당돼 비용이 높았고, 아그모는 컴퓨팅·네트워크 비용을 줄이면서 다시 오르지 않게 관리할 체계가 없었음.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>테크랩스 — 6개 서비스에 부하·기능 테스트를 돌려 실제 필요 리소스를 측정하고 과할당분을 단계적으로 축소</li>
          <li>아그모 — Karpenter로 노드 프로비저닝 자동화(분→초), Graviton(arm64)·Spot 확대로 컴퓨팅 단가 절감</li>
          <li>네트워크 — Cross-AZ 전송·NAT Gateway 비용을 경로 분석 후 Topology Aware Routing·VPC Endpoint로 절감</li>
          <li>거버넌스 — Infracost PR 비용 코멘트, Grafana 대시보드·Cost Anomaly Detection으로 이상 지출 자동 알림</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>테크랩스 6개 서비스 월 비용 -56%</li>
          <li>아그모 2계정 월 3,800 → 2,660달러 (-30%)</li>
          <li>노드 프로비저닝 분 → 초</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Karpenter</span>
          <span class="tech-tag">AWS Spot</span>
          <span class="tech-tag">Graviton(arm64)</span>
          <span class="tech-tag">Topology Aware Routing</span>
          <span class="tech-tag">VPC Endpoint</span>
          <span class="tech-tag">Infracost</span>
          <span class="tech-tag">Cost Anomaly Detection</span>
        </div>
      </div>
    </div>

    <!-- 03 플랫폼 -->
    <div class="project-item">
      <div class="project-header">
        <h3>Terraform CI·GitOps 표준화와 ECS→EKS 무중단 마이그레이션</h3>
        <span class="period">아그모 | Terraform · GitHub OIDC · ArgoCD · Argo Rollouts · Checkov</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> 인프라 변경이 수동 <code>terraform apply</code>에 의존했고, 레포마다 같은 모듈이 복제돼 있었음. 일부 레거시 워크로드는 ECS(EC2)로 남아 EKS와 운영 스택이 이원화돼 있었음.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>Terraform CI — GitHub Actions OIDC(키리스)로 PR plan / merge apply 파이프라인 구성. Checkov 게이트로 잘못된 보안그룹·퍼블릭 버킷을 머지 전 차단</li>
          <li>모듈 공용화 — 레포마다 복제된 eks·aurora·redis 모듈을 private module로 추출</li>
          <li>배포 안정성 — ArgoCD App-of-Apps 위에 Argo Rollouts 카나리/블루-그린 도입</li>
          <li>마이그레이션 — 레거시 ECS 워크로드를 헬스체크 기반 트래픽 컷오버로 무중단 EKS 전환</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>인프라 변경 리드타임 -70%, 수동 apply 0</li>
          <li>신규 환경 셋업 약 1일 → 2시간</li>
          <li>운영 스택 ECS+EKS 이원화 → EKS 일원화</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Terraform</span>
          <span class="tech-tag">GitHub Actions OIDC</span>
          <span class="tech-tag">ArgoCD</span>
          <span class="tech-tag">Argo Rollouts</span>
          <span class="tech-tag">Checkov</span>
          <span class="tech-tag">Helm</span>
        </div>
      </div>
    </div>

    <!-- 04 위치정보 -->
    <div class="project-item">
      <div class="project-header">
        <h3>위치정보사업자 인증 2건 — 보안 컴플라이언스</h3>
        <span class="period">아그모 | KMS · IAM/RBAC · 감사 로그 · 위치정보보호법</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> 농기계 위치 데이터를 다루는 서비스라 위치정보사업자 인증이 필요했고, 법적 보호조치를 인프라 차원에서 충족해야 했음.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>법적 요구사항을 암호화·접근통제·감사 세 축으로 나눠 인프라 설계에 매핑</li>
          <li>암호화 — KMS로 저장 구간을, TLS로 전송 구간을 암호화</li>
          <li>접근통제 — IAM/RBAC 최소 권한, DB 유저 분리</li>
          <li>감사 추적 — 위치정보 접근 로그를 법정 기간 적재·추적, 망 분리·보안그룹·Secrets 관리</li>
          <li>각 보호조치의 증빙(설정·로그)을 인증 평가에 제출 가능한 형태로 준비</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>위치정보사업자 인증 2건 획득</li>
          <li>인프라 보안 요건 설계·이행</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">AWS KMS</span>
          <span class="tech-tag">IAM</span>
          <span class="tech-tag">Aurora 접근 로깅</span>
          <span class="tech-tag">CloudTrail</span>
          <span class="tech-tag">VPC 망 분리</span>
        </div>
      </div>
    </div>

    <!-- 05 NISHIBE -->
    <div class="project-item">
      <div class="project-header">
        <h3>NISHIBE 택시 클라우드 인프라 신규 구축</h3>
        <span class="period">아그모 | EKS · Aurora · Redis · ArgoCD · Terraform · GitHub OIDC</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> 일본 택시 운행관리 서비스의 클라우드 인프라를 처음부터 설계·구축해야 했음. 사내 패턴을 참고하되 네트워크부터 배포 파이프라인까지 직접 설계.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>EKS + Aurora + Redis + ArgoCD로 풀스택 dev 환경 구성 및 서비스 배포</li>
          <li>global 네트워크 레이어와 환경 골격을 Terraform 모듈로 분리해 환경 확장에 대비</li>
          <li>GitHub OIDC 기반 CI 인증으로 장기 액세스키 없이 배포</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>신규 서비스 인프라 구축·배포 완료</li>
          <li>네트워크부터 배포 파이프라인까지 전 구간 단독 설계·구축</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">EKS</span>
          <span class="tech-tag">Aurora</span>
          <span class="tech-tag">Redis</span>
          <span class="tech-tag">ArgoCD</span>
          <span class="tech-tag">Terraform</span>
          <span class="tech-tag">GitHub Actions OIDC</span>
        </div>
      </div>
    </div>

    <!-- 06 관측성 -->
    <div class="project-item">
      <div class="project-header">
        <h3>관측성 통합 + SLO + AI 온콜 보조</h3>
        <span class="period">아그모 | Grafana · Prometheus · Loki · Tempo · Pyroscope · k6</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> 지표·로그·트레이스가 따로 흩어져 있고 알림은 오탐이 많아, 정작 중요한 신호가 묻혔음.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>Grafana·Prometheus·Loki·Tempo·Pyroscope로 메트릭·로그·트레이스·프로파일을 한 스택에 통합</li>
          <li>핵심 서비스에 SLO를 정의하고 그에 맞춰 모니터를 재설계, 행동으로 이어지지 않는 오탐 알림 정리</li>
          <li>AI 온콜 보조 — Alertmanager 알림·에러 로그를 Slack으로 받으면, 이를 트리거로 AI 에이전트가 Grafana 메트릭·로그를 직접 조회·분석해 원인과 조치를 제안하고 담당자에게 메일 발송</li>
          <li>기존에는 담당자가 알림 확인 → 메트릭 확인 → 로그 확인을 수동으로 거쳤지만, 그 과정을 에이전트가 대신하면서 원인 파악·조치 착수 시간 단축</li>
          <li>k6 부하테스트로 SLO가 실제 부하에서 지켜지는지 검증</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>오탐 알림 일 10여 회 → 0 수준</li>
          <li>MTTD 주요 알림 기준 5분 이내</li>
          <li>원인 파악 수동(알림→메트릭→로그) → 에이전트 자동</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Grafana</span>
          <span class="tech-tag">Prometheus</span>
          <span class="tech-tag">Loki</span>
          <span class="tech-tag">Tempo</span>
          <span class="tech-tag">Pyroscope</span>
          <span class="tech-tag">Alertmanager</span>
          <span class="tech-tag">k6</span>
        </div>
      </div>
    </div>

    <!-- 07 Keycloak -->
    <div class="project-item">
      <div class="project-header">
        <h3>Keycloak 기반 공통 인증·인가 (HA)</h3>
        <span class="period">아그모 | Keycloak · OIDC/OAuth2 · RBAC · Aurora</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> 서비스마다 인증을 따로 구현하면서 권한 모델이 제각각이었고, 인증 서버가 단일 인스턴스라 장애에 취약했음.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>여러 서비스가 함께 쓰는 공통 인증 기반을 Keycloak으로 구축, OIDC/OAuth2 SSO 연동</li>
          <li>Realm·Role·Group 권한 상속 모델을 설계해 권한 체계 표준화</li>
          <li>dev/prod 인증 서버를 Aurora 백엔드로 분리, 단일 인스턴스 → HA 클러스터링·백업 자동화</li>
          <li>user events를 SNS→SQS fanout으로 외부 시스템과 계정 변경 동기화</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>인증 기반 서비스별 개별 → 공통화</li>
          <li>가용성 단일 인스턴스 → HA (SPOF 제거)</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Keycloak</span>
          <span class="tech-tag">OIDC</span>
          <span class="tech-tag">OAuth2</span>
          <span class="tech-tag">Aurora</span>
          <span class="tech-tag">SNS</span>
          <span class="tech-tag">SQS</span>
        </div>
      </div>
    </div>

    <!-- 08 멀티리전 -->
    <div class="project-item">
      <div class="project-header">
        <h3>멀티리전 Active-Standby 페일오버</h3>
        <span class="period">아그모 | Aurora Global DB · Route53 · EKS Pilot Light · Karpenter</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> 단일 리전(서울) 운영이라 리전 장애 시 복구 수단이 없었음. Active-Active는 비용이 두 배라, 비용을 최소화하면서 리전 장애에 대응하는 Pilot Light 방식을 택함.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>Aurora Global DB — 서울(Primary) → 도쿄(Replica) 비동기 복제, 페일오버 시 Replica를 Primary로 승격</li>
          <li>Pilot Light EKS — 도쿄에 최소 노드(Spot)로 클러스터를 상시 유지, 페일오버 시 Karpenter가 필요 노드를 즉시 확장</li>
          <li>Route53 Health Check — 서울 엔드포인트 실패 시 도쿄로 DNS 자동 전환, TTL 최소화로 전파 지연 단축</li>
          <li>Standby는 실 트래픽이 없어 Active 대비 ~7% 비용 수준 유지</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>리전 장애 RTO 복구 수단 없음 → &lt;15분</li>
          <li>Standby 유휴 비용 Active 대비 ~7% 수준</li>
          <li>페일오버 수동 → Route53 자동 DNS 전환</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Aurora Global DB</span>
          <span class="tech-tag">Route53 Health Check</span>
          <span class="tech-tag">EKS</span>
          <span class="tech-tag">Karpenter</span>
          <span class="tech-tag">AWS Spot</span>
        </div>
      </div>
    </div>

    <!-- 09 온프렘 GPU -->
    <div class="project-item">
      <div class="project-header">
        <h3>온프렘 GPU 서버 구축 — SeamOS 개발 AI Agent</h3>
        <span class="period">아그모 | vLLM · Ubuntu Server · Tailscale VPN · Nginx · Keycloak</span>
      </div>
      <div class="project-overview">
        <p><strong>배경:</strong> SeamOS 개발 보조 AI를 외부 SaaS에 의존하면 사내 코드가 외부로 전송됨. 상시 사용 시 온프렘이 클라우드 대비 손익분기가 빨라, 물리 GPU 서버를 직접 구성해 사내망에서 추론 서버를 운영하기로 함.</p>
      </div>
      <div class="project-details">
        <h4>의사결정 · 구현</h4>
        <ul>
          <li>물리 GPU 서버(RTX 4090, VRAM 24GB) 구성, NVMe SSD로 모델 로딩 시간 단축</li>
          <li>vLLM을 Docker로 실행해 OpenAI 호환 API 노출, continuous batching·Flash Attention 2·KV cache 튜닝으로 throughput 최적화, AWQ INT4 양자화로 VRAM 사용량 ~50% 절감</li>
          <li>Tailscale VPN으로 사무실 밖 개발자도 사내망과 동일 조건으로 접근</li>
          <li>Nginx reverse proxy + Keycloak API 키 인증·rate limit, 외부 인터넷에 직접 노출하지 않고 VPN 경유만 허용</li>
          <li>systemd로 재부팅 시 자동 기동, Grafana + node_exporter로 GPU 온도·VRAM 사용률·throughput 모니터링</li>
        </ul>
        <h4>성과</h4>
        <ul>
          <li>코드 보안 외부 SaaS 전송 → 사내망 완결</li>
          <li>VRAM FP16 대비 ~50% 절감 (AWQ INT4, 70B 단일 GPU 서빙)</li>
          <li>비용 사용량 비례 API 과금 → 하드웨어 초기 투자 후 전기세만</li>
          <li>전 개발자 공용 AI Agent — 사내 직접·원격 VPN 접근</li>
        </ul>
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">vLLM</span>
          <span class="tech-tag">Docker</span>
          <span class="tech-tag">Ubuntu Server</span>
          <span class="tech-tag">NVIDIA GPU</span>
          <span class="tech-tag">Tailscale VPN</span>
          <span class="tech-tag">Nginx</span>
          <span class="tech-tag">Keycloak</span>
          <span class="tech-tag">Grafana</span>
          <span class="tech-tag">node_exporter</span>
        </div>
      </div>
    </div>

  </section>
</template>

<script>
export default {
  name: 'PortfolioTobe'
}
</script>

<style scoped>
.projects-section {
  margin-bottom: 3rem;
}

.header2 {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--vp-c-brand);
  border-bottom: 2px solid var(--vp-c-brand);
  padding-bottom: 0.25rem;
  margin-bottom: 1rem;
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
  font-size: 1.3rem;
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
  font-size: 1.05rem;
  margin-top: 1.2rem;
  margin-bottom: 0.6rem;
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
</style>
