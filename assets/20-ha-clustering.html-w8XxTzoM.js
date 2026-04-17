import{_ as n,c as t,e as i,o as a}from"./app-BprzU0vx.js";const s={};function l(d,e){return a(),t("div",null,e[0]||(e[0]=[i(`<h1 id="infinispan-ha-클러스터링" tabindex="-1"><a class="header-anchor" href="#infinispan-ha-클러스터링"><span>Infinispan HA 클러스터링</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>Infinispan이 무엇이고 Keycloak이 어디에 어떻게 쓰는지 설명할 수 있다.</li><li>Keycloak이 관리하는 5가지 캐시(sessions, authenticationSessions, offlineSessions, loginFailures, actionTokens)를 구분할 수 있다.</li><li>Embedded Infinispan과 External Infinispan의 차이를 이해하고, v26 이후 권장 구조를 설명할 수 있다.</li><li>SYNC/ASYNC 동기화 모드 선택이 성능과 정합성에 미치는 영향을 판단할 수 있다.</li><li>Multi-site(Active/Passive) 배포 구조와 XSite 복제 개념을 파악한다.</li></ul></div><hr><h2 id="_1-infinispan이란-무엇인가" tabindex="-1"><a class="header-anchor" href="#_1-infinispan이란-무엇인가"><span>1. Infinispan이란 무엇인가</span></a></h2><p><strong>Infinispan</strong>은 Red Hat이 개발·유지보수하는 오픈소스 <strong>인메모리 분산 데이터 그리드(In-Memory Data Grid)</strong>다. 가장 가까운 용도로 보면 &quot;여러 JVM에 걸쳐 공유되는 분산 캐시&quot;지만, 트랜잭션·이벤트 리스너·쿼리·영속화까지 지원해 단순 캐시 이상의 기능을 갖춘다. 대중적인 Redis·Memcached와 달리 Java 위에서 돌며, Keycloak처럼 JVM에 내장(Embedded)할 수도, 별도 서버로 분리(Remote/Server)할 수도 있다.</p><table><thead><tr><th>비교 대상</th><th>포지션</th><th>언어</th><th>Keycloak과의 관계</th></tr></thead><tbody><tr><td>Infinispan</td><td>In-Memory Data Grid</td><td>Java</td><td><strong>Keycloak 내장 기본</strong></td></tr><tr><td>Hazelcast</td><td>In-Memory Data Grid</td><td>Java</td><td>대안 (직접 지원은 아님)</td></tr><tr><td>Redis</td><td>In-Memory KV Store</td><td>C</td><td>Keycloak이 직접 사용하지 않음</td></tr><tr><td>Ehcache</td><td>단일 프로세스 캐시</td><td>Java</td><td>분산 시나리오에 부적합</td></tr></tbody></table><h3 id="keycloak이-infinispan을-쓰는-이유" tabindex="-1"><a class="header-anchor" href="#keycloak이-infinispan을-쓰는-이유"><span>Keycloak이 Infinispan을 쓰는 이유</span></a></h3><p>Keycloak은 로그인 세션·진행 중인 인증 상태·Brute Force 카운터 같은 자주 바뀌는 데이터를 DB에 매번 쓰지 않는다. 만약 모든 토큰 발급 요청마다 DB 왕복을 하면 발급 TPS가 금방 DB에 병목이 걸린다. Infinispan은 이 데이터를 <strong>메모리</strong>에 두고, 여러 Keycloak 노드가 <strong>같은 뷰</strong>를 공유하도록 한다.</p><pre class="mermaid">flowchart LR
    U[사용자] --&gt;|로그인 요청| LB[로드밸런서]
    LB --&gt; N1[Keycloak Node 1]
    LB --&gt; N2[Keycloak Node 2]
    LB --&gt; N3[Keycloak Node 3]
    N1 &lt;--&gt;|Infinispan 세션 공유| N2
    N2 &lt;--&gt;|Infinispan 세션 공유| N3
    N1 &lt;--&gt;|Infinispan 세션 공유| N3
    N1 --&gt; DB[(PostgreSQL)]
    N2 --&gt; DB
    N3 --&gt; DB
</pre><p>로드밸런서가 어느 노드로 라우팅해도 같은 세션을 볼 수 있는 이유가 여기에 있다. 세션이 없다면 &quot;로그인은 Node 1에서 했는데 다음 요청이 Node 2로 가서 다시 로그인을 요구받는&quot; sticky-session 의존 구조가 된다.</p><h3 id="단일-노드에서도-infinispan이-쓰인다" tabindex="-1"><a class="header-anchor" href="#단일-노드에서도-infinispan이-쓰인다"><span>단일 노드에서도 Infinispan이 쓰인다</span></a></h3><p>Keycloak 노드가 1개뿐이어도 Infinispan은 항상 동작한다. 이 경우에는 &quot;분산&quot; 기능은 비활성이고 <strong>로컬 메모리 캐시</strong>로만 작동한다. 즉 Infinispan은 Keycloak의 선택적 부가 기능이 아니라 <strong>필수 내부 구성요소</strong>다. 클러스터를 구성할 때만 노드 간 복제(JGroups)가 추가로 켜진다.</p><h3 id="언제-infinispan을-의식해야-하는가" tabindex="-1"><a class="header-anchor" href="#언제-infinispan을-의식해야-하는가"><span>언제 Infinispan을 의식해야 하는가</span></a></h3><p>평소에는 Keycloak 운영자가 Infinispan 내부를 몰라도 된다. 하지만 다음 상황에서는 반드시 이해가 필요하다.</p><ul><li><strong>클러스터 확장</strong> — 노드를 2개 이상으로 늘리면 JGroups 디스커버리·복제 모드·동기화 모드 결정이 필요하다.</li><li><strong>롤링 업그레이드</strong> — 메모리 전용 캐시가 어떤 캐시인지 모르면 재시작 중 전원 로그아웃이 발생할 수 있다.</li><li><strong>Multi-site 재해 복구</strong> — Site 간 복제(XSite) 설정에서 Infinispan 구조 이해가 전제된다.</li><li><strong>대규모 세션</strong> — 수백만 세션 환경에서 분산(distributed) 캐시의 <code>owners</code> 파라미터 선택이 메모리 비용에 직결된다.</li></ul><p>이 챕터 이후부터는 Infinispan을 &quot;Keycloak이 세션 공유에 쓰는 엔진&quot;으로 전제하고 진행한다.</p><hr><h2 id="_2-keycloak-캐시-5종" tabindex="-1"><a class="header-anchor" href="#_2-keycloak-캐시-5종"><span>2. Keycloak 캐시 5종</span></a></h2><p>Keycloak은 로그인 상태와 임시 데이터를 DB가 아닌 메모리(Infinispan)에 보관한다. 모든 토큰 발급 요청마다 DB를 치면 처리량이 금방 한계에 부딪히기 때문이다. 클러스터 구성을 이해하려면 먼저 &quot;Keycloak이 어떤 캐시를 들고 있느냐&quot;부터 정리해야 한다.</p><table><thead><tr><th>캐시 이름</th><th>용도</th><th>영속성</th><th>TTL</th></tr></thead><tbody><tr><td><code>sessions</code></td><td>로그인한 사용자 세션 (SSO 세션)</td><td>메모리 전용</td><td>SSO Session Idle/Max</td></tr><tr><td><code>authenticationSessions</code></td><td>로그인 진행 중인 임시 상태</td><td>메모리 전용</td><td>5~30분</td></tr><tr><td><code>offlineSessions</code></td><td>Refresh Token 기반 오프라인 세션</td><td>DB + 메모리</td><td>Offline Session Idle/Max</td></tr><tr><td><code>loginFailures</code></td><td>Brute Force 카운터</td><td>메모리 전용</td><td>실패 카운터 리셋 주기</td></tr><tr><td><code>actionTokens</code></td><td>Email 검증·비밀번호 초기화 토큰</td><td>메모리 전용</td><td>토큰 만료 시간</td></tr></tbody></table><p>핵심은 &quot;오프라인 세션만 DB에 영구 저장된다&quot;는 점이다. 나머지 네 캐시는 모두 메모리 전용이라, Keycloak 노드가 전부 재시작되면 전원 로그아웃된다. 운영 중에 &quot;왜 롤링 업그레이드 한 번에 전체 로그아웃이 됐나&quot; 같은 사고가 터지는 이유가 대부분 이 구분을 몰라서다.</p><pre class="mermaid">flowchart LR
    subgraph Node1[Keycloak Node 1]
        C1[sessions]
        C2[authSessions]
        C3[offlineSessions]
        C4[loginFailures]
        C5[actionTokens]
    end
    subgraph Node2[Keycloak Node 2]
        D1[sessions]
        D2[authSessions]
        D3[offlineSessions]
        D4[loginFailures]
        D5[actionTokens]
    end
    subgraph Node3[Keycloak Node 3]
        E1[sessions]
        E2[authSessions]
        E3[offlineSessions]
        E4[loginFailures]
        E5[actionTokens]
    end
    Node1 &lt;--&gt;|JGroups 복제| Node2
    Node2 &lt;--&gt;|JGroups 복제| Node3
    Node1 &lt;--&gt;|JGroups 복제| Node3
    Node1 --&gt; DB[(PostgreSQL)]
    Node2 --&gt; DB
    Node3 --&gt; DB
    DB -.영속 저장.-&gt; C3
</pre><h3 id="분산-distributed-vs-복제-replicated" tabindex="-1"><a class="header-anchor" href="#분산-distributed-vs-복제-replicated"><span>분산(distributed) vs 복제(replicated)</span></a></h3><p>Infinispan은 두 가지 캐시 모드를 지원한다.</p><ul><li><strong>Distributed</strong>: 각 엔트리를 N개 노드에만 복제. 예를 들어 <code>owners=2</code>면 3개 노드 중 2곳만 특정 세션을 들고 있다. 메모리 효율이 높지만, 원래 노드가 전부 죽으면 그 세션은 사라진다.</li><li><strong>Replicated</strong>: 모든 노드가 같은 데이터를 복제. 조회가 항상 로컬에서 끝나지만, 쓰기가 전 노드로 전파되어 부하가 크다.</li></ul><p>Keycloak 기본은 대부분 <code>owners=2</code>인 분산 캐시다. 세션 수가 수백만 단위로 커지는 환경에서 모든 노드가 전량 복제하면 메모리가 버티지 못한다.</p><hr><h2 id="_3-embedded-infinispan" tabindex="-1"><a class="header-anchor" href="#_3-embedded-infinispan"><span>3. Embedded Infinispan</span></a></h2><p>v25까지(그리고 v26의 기본 설정에서도) Keycloak은 Infinispan을 JVM 내부에 품고 돈다. 이를 <strong>Embedded Infinispan</strong> 모드라고 한다. 별도의 Infinispan 서버를 띄우지 않고, Keycloak 프로세스끼리 JGroups로 직접 클러스터를 이룬다.</p><h3 id="기동-구조" tabindex="-1"><a class="header-anchor" href="#기동-구조"><span>기동 구조</span></a></h3><pre class="mermaid">flowchart TB
    LB[Load Balancer] --&gt; KC1[Keycloak + Infinispan]
    LB --&gt; KC2[Keycloak + Infinispan]
    LB --&gt; KC3[Keycloak + Infinispan]
    KC1 &lt;--&gt;|JGroups TCP/MPING| KC2
    KC2 &lt;--&gt;|JGroups TCP/MPING| KC3
    KC1 &lt;--&gt;|JGroups TCP/MPING| KC3
    KC1 --&gt; DB[(PostgreSQL)]
    KC2 --&gt; DB
    KC3 --&gt; DB
</pre><p>각 Keycloak 프로세스가 Infinispan을 동시에 호스팅한다. JVM 하나가 애플리케이션 서버와 분산 캐시를 같이 수행하는 구조다.</p><h3 id="jgroups-디스커버리" tabindex="-1"><a class="header-anchor" href="#jgroups-디스커버리"><span>JGroups 디스커버리</span></a></h3><p>클러스터에 새 노드가 참여하려면 먼저 &quot;이미 떠 있는 노드가 누구인지&quot;를 찾아야 한다. 이 과정을 디스커버리(discovery)라고 하며, Keycloak은 JGroups의 여러 프로토콜 중 환경에 맞는 것을 고를 수 있다.</p><table><thead><tr><th>프로토콜</th><th>용도</th><th>전형적인 환경</th></tr></thead><tbody><tr><td><code>MPING</code></td><td>IP 멀티캐스트</td><td>온프레미스 단일 네트워크</td></tr><tr><td><code>TCPPING</code></td><td>고정된 노드 목록</td><td>정적 클러스터</td></tr><tr><td><code>DNS_PING</code></td><td>DNS SRV/A 레코드 조회</td><td>Kubernetes (Headless Service)</td></tr><tr><td><code>JDBC_PING</code></td><td>공유 DB 테이블에 멤버 기록</td><td>클라우드</td></tr></tbody></table><p>Kubernetes에서는 <code>DNS_PING</code>이 사실상 표준이다. Headless Service가 Pod IP 목록을 DNS A 레코드로 뿌려 주면, JGroups가 그 리스트를 읽어 클러스터를 구성한다.</p><div class="language-conf line-numbers-mode" data-highlighter="prismjs" data-ext="conf" data-title="conf"><pre><code><span class="line"># cache-ispn.xml 스니펫 — DNS_PING 예시</span>
<span class="line">&lt;stack name=&quot;tcp-dns-ping&quot;&gt;</span>
<span class="line">    &lt;TCP bind_addr=&quot;\${jgroups.bind.address:SITE_LOCAL}&quot; bind_port=&quot;\${jgroups.bind.port:7800}&quot;/&gt;</span>
<span class="line">    &lt;dns.DNS_PING dns_query=&quot;keycloak-discovery.keycloak.svc.cluster.local&quot;/&gt;</span>
<span class="line">    &lt;MERGE3/&gt;</span>
<span class="line">    &lt;FD_SOCK/&gt;</span>
<span class="line">    &lt;FD_ALL/&gt;</span>
<span class="line">    &lt;VERIFY_SUSPECT/&gt;</span>
<span class="line">    &lt;pbcast.NAKACK2/&gt;</span>
<span class="line">    &lt;UNICAST3/&gt;</span>
<span class="line">    &lt;pbcast.STABLE/&gt;</span>
<span class="line">    &lt;pbcast.GMS/&gt;</span>
<span class="line">    &lt;MFC/&gt;</span>
<span class="line">    &lt;FRAG3/&gt;</span>
<span class="line">&lt;/stack&gt;</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="embedded-모드의-한계" tabindex="-1"><a class="header-anchor" href="#embedded-모드의-한계"><span>Embedded 모드의 한계</span></a></h3><p>Embedded는 설정이 단순하지만 두 가지 구조적 문제가 있다.</p><ul><li><strong>스케일링 결합</strong>: Keycloak 인스턴스를 늘리면 Infinispan 노드도 같이 늘어난다. 세션 캐시만 키우고 싶을 때도 Keycloak 전체가 증설된다.</li><li><strong>롤링 업그레이드 위험</strong>: 모든 노드를 순차 재시작하면 캐시가 재분배되는 중에 부하가 몰린다. 메이저 업그레이드 때 캐시 프로토콜이 바뀌면 아예 호환성 문제가 터진다.</li></ul><p>이 한계를 해결하려고 v26부터 External Infinispan을 권장하기 시작했다.</p><hr><h2 id="_4-external-infinispan" tabindex="-1"><a class="header-anchor" href="#_4-external-infinispan"><span>4. External Infinispan</span></a></h2><p><strong>External Infinispan</strong>(Infinispan Remote Store)은 Keycloak 외부에 전용 Infinispan 서버 클러스터를 두고, Keycloak은 Hot Rod 프로토콜로 그 서버를 원격 캐시로 사용하는 구조다. v26부터 Multi-site 공식 가이드가 이 구성을 전제로 작성된다.</p><pre class="mermaid">flowchart TB
    subgraph App[Keycloak 레이어]
        KC1[Keycloak 1]
        KC2[Keycloak 2]
        KC3[Keycloak 3]
    end
    subgraph Cache[Infinispan 클러스터]
        I1[Infinispan 1]
        I2[Infinispan 2]
        I3[Infinispan 3]
    end
    KC1 --&gt;|Hot Rod| I1
    KC2 --&gt;|Hot Rod| I2
    KC3 --&gt;|Hot Rod| I3
    I1 &lt;--&gt; I2
    I2 &lt;--&gt; I3
    I1 &lt;--&gt; I3
    App --&gt; DB[(PostgreSQL)]
</pre><h3 id="embedded와-비교" tabindex="-1"><a class="header-anchor" href="#embedded와-비교"><span>Embedded와 비교</span></a></h3><table><thead><tr><th>항목</th><th>Embedded</th><th>External</th></tr></thead><tbody><tr><td>배포 복잡도</td><td>낮음 (단일 컴포넌트)</td><td>높음 (Infinispan 별도 운영)</td></tr><tr><td>독립 스케일링</td><td>불가</td><td>가능 (Keycloak vs Infinispan 분리)</td></tr><tr><td>롤링 업그레이드</td><td>캐시 재분배 발생</td><td>Keycloak만 재기동, 캐시 그대로</td></tr><tr><td>Multi-site</td><td>제한적</td><td>XSite 복제 공식 지원</td></tr><tr><td>추천 상황</td><td>소규모/단일 리전</td><td>대규모/Multi-site</td></tr></tbody></table><p>External 구성은 운영 컴포넌트가 하나 더 늘어나지만, 그 대가로 Keycloak을 무정지로 재기동할 수 있고 Multi-site 복제를 제대로 설계할 수 있다.</p><h3 id="keycloak-측-설정" tabindex="-1"><a class="header-anchor" href="#keycloak-측-설정"><span>Keycloak 측 설정</span></a></h3><p>Keycloak이 외부 Infinispan을 원격 캐시로 쓰려면 <code>cache-remote-*</code> 옵션을 지정한다.</p><div class="language-conf line-numbers-mode" data-highlighter="prismjs" data-ext="conf" data-title="conf"><pre><code><span class="line"># keycloak.conf</span>
<span class="line">cache=ispn</span>
<span class="line">cache-remote-host=infinispan.keycloak.svc.cluster.local</span>
<span class="line">cache-remote-port=11222</span>
<span class="line">cache-remote-username=keycloak</span>
<span class="line">cache-remote-password=&lt;secret&gt;</span>
<span class="line">cache-remote-tls-enabled=true</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>v26의 &quot;Persistent user sessions&quot; 기능과 맞물리면 Keycloak 재기동 시에도 세션이 살아남는다. 이제 세션이 Infinispan 클러스터에 모여 있으므로, Keycloak Pod 하나가 죽어도 사용자는 재로그인할 필요가 없다.</p><hr><h2 id="_5-캐시-동기화-모드" tabindex="-1"><a class="header-anchor" href="#_5-캐시-동기화-모드"><span>5. 캐시 동기화 모드</span></a></h2><p>Infinispan 캐시의 쓰기 전파 방식은 <strong>SYNC</strong>와 <strong>ASYNC</strong> 두 가지다. 선택에 따라 처리량과 정합성이 크게 달라진다.</p><h3 id="sync-모드" tabindex="-1"><a class="header-anchor" href="#sync-모드"><span>SYNC 모드</span></a></h3><pre class="mermaid">sequenceDiagram
    participant C as Client
    participant N1 as Node 1
    participant N2 as Node 2
    C-&gt;&gt;N1: PUT session-xyz
    N1-&gt;&gt;N2: Replicate
    N2--&gt;&gt;N1: ACK
    N1--&gt;&gt;C: 200 OK
</pre><ul><li>쓰기 요청이 다른 노드의 ACK를 받고 나서야 응답한다.</li><li>모든 노드가 같은 상태를 본다. Read-after-write 정합성 보장.</li><li>응답 지연이 노드 수에 비례해 늘어난다.</li></ul><h3 id="async-모드" tabindex="-1"><a class="header-anchor" href="#async-모드"><span>ASYNC 모드</span></a></h3><pre class="mermaid">sequenceDiagram
    participant C as Client
    participant N1 as Node 1
    participant N2 as Node 2
    C-&gt;&gt;N1: PUT session-xyz
    N1--&gt;&gt;C: 200 OK
    N1-&gt;&gt;N2: Replicate (비동기)
</pre><ul><li>로컬에 쓰고 바로 응답. 복제는 뒤에서 진행.</li><li>응답이 빠르지만, 복제 전에 노드가 죽으면 데이터 유실 가능.</li><li>사용자가 Node 1에 로그인하고 다음 요청이 Node 2로 가면 &quot;세션 없음&quot; 에러가 날 수 있다.</li></ul><h3 id="keycloak-권장-설정" tabindex="-1"><a class="header-anchor" href="#keycloak-권장-설정"><span>Keycloak 권장 설정</span></a></h3><table><thead><tr><th>캐시</th><th>권장 모드</th><th>이유</th></tr></thead><tbody><tr><td><code>sessions</code></td><td>SYNC</td><td>SSO 세션이 누락되면 곧바로 재로그인</td></tr><tr><td><code>authenticationSessions</code></td><td>SYNC</td><td>로그인 진행 중 상태가 사라지면 플로우 실패</td></tr><tr><td><code>offlineSessions</code></td><td>SYNC</td><td>Refresh 토큰 일관성 필요</td></tr><tr><td><code>loginFailures</code></td><td>ASYNC</td><td>카운터 약간 부정확해도 무방</td></tr><tr><td><code>actionTokens</code></td><td>SYNC</td><td>한 번 쓰고 버리는 토큰, 정확도가 보안</td></tr></tbody></table><p>로그인 실패 카운터만 ASYNC를 쓰면 약간의 성능 이득이 있지만, 대부분 실무에서는 전부 SYNC로 통일한다. Brute Force 카운터가 노드 간 불일치면 공격자가 노드를 바꿔가며 시도 횟수를 우회할 수 있기 때문이다.</p><hr><h2 id="_6-multi-site-배포" tabindex="-1"><a class="header-anchor" href="#_6-multi-site-배포"><span>6. Multi-site 배포</span></a></h2><p><strong>Multi-site</strong>는 지리적으로 떨어진 두 데이터센터에 Keycloak을 동시에 운영하는 구조다. 단일 DC 장애에도 서비스를 유지하려는 목적이 크다. Keycloak은 v26부터 공식 Multi-site 가이드를 제공하며, 권장 형태는 <strong>Active/Passive</strong>다.</p><h3 id="active-passive-구조" tabindex="-1"><a class="header-anchor" href="#active-passive-구조"><span>Active/Passive 구조</span></a></h3><pre class="mermaid">flowchart LR
    subgraph Site1[Site A - Active]
        KC_A[Keycloak]
        INF_A[Infinispan]
        DB_A[(PostgreSQL Primary)]
    end
    subgraph Site2[Site B - Passive]
        KC_B[Keycloak - standby]
        INF_B[Infinispan]
        DB_B[(PostgreSQL Replica)]
    end
    LB[Global Load Balancer] --&gt;|traffic| KC_A
    LB -.failover.-&gt; KC_B
    INF_A &lt;--&gt;|XSite 비동기 복제| INF_B
    DB_A --&gt;|논리 복제| DB_B
</pre><ul><li>Site A가 트래픽을 받고, Site B는 standby로 대기한다.</li><li>Infinispan은 <strong>XSite Replication</strong>으로 세션을 비동기 복제한다.</li><li>PostgreSQL은 별도의 스트리밍 복제로 DB 상태를 맞춘다.</li><li>Site A 장애 시 Global LB가 Site B로 페일오버한다.</li></ul><h3 id="왜-active-active가-아닌가" tabindex="-1"><a class="header-anchor" href="#왜-active-active가-아닌가"><span>왜 Active/Active가 아닌가</span></a></h3><p>Active/Active(양쪽 DC에서 동시에 트래픽을 받는 구조)는 이론적으로는 가능하지만, Keycloak 운영팀이 공식적으로 권장하지 않는다. 이유는 세 가지다.</p><ul><li><strong>로그인 레이스 컨디션</strong>: 같은 사용자의 인증이 동시에 두 DC에서 시작되면 <code>authenticationSessions</code> 상태가 충돌한다.</li><li><strong>토큰 발급 중복</strong>: Client Credentials Grant가 두 사이트에서 동시에 들어오면 동일한 세션 ID가 생길 수 있다.</li><li><strong>Sticky 세션 요구</strong>: 한 사용자의 요청은 같은 사이트로 지속적으로 라우팅되어야 하는데, 이는 일반적인 Global LB로는 까다롭다.</li></ul><p>대신 Keycloak v26의 XSite 비동기 복제는 RPO(Recovery Point Objective)가 수 초 단위로 좁아져서, Active/Passive도 실질적으로 &quot;거의 무중단&quot;에 가까운 가용성을 제공한다.</p><h3 id="rto-rpo-목표" tabindex="-1"><a class="header-anchor" href="#rto-rpo-목표"><span>RTO/RPO 목표</span></a></h3><table><thead><tr><th>지표</th><th>단일 DC + HA</th><th>Multi-site Active/Passive</th></tr></thead><tbody><tr><td>RTO (복구 시간)</td><td>5~30분 (Pod 재기동)</td><td>1~5분 (DNS 페일오버)</td></tr><tr><td>RPO (복구 시점)</td><td>0 (같은 DB)</td><td>수 초 (XSite 지연)</td></tr><tr><td>DC 전체 장애 대응</td><td>불가능</td><td>가능</td></tr></tbody></table><hr><h2 id="_7-장애-시나리오" tabindex="-1"><a class="header-anchor" href="#_7-장애-시나리오"><span>7. 장애 시나리오</span></a></h2><p>클러스터는 평소에는 순탄해도 네트워크 분할이나 DB 장애에서 예상치 못한 동작을 보인다. 대표 사례를 정리한다.</p><h3 id="split-brain" tabindex="-1"><a class="header-anchor" href="#split-brain"><span>Split-brain</span></a></h3><p><strong>Split-brain</strong>은 네트워크 분할로 노드 그룹이 서로를 못 보게 되는 상황이다. Node 1·2는 &quot;Node 3이 죽었다&quot;고 판단하고, Node 3은 &quot;Node 1·2가 죽었다&quot;고 판단한다. 각자 독립적으로 쓰기를 계속하면 데이터가 갈라진다.</p><pre class="mermaid">flowchart LR
    subgraph Partition1[Partition A]
        N1[Node 1]
        N2[Node 2]
    end
    subgraph Partition2[Partition B]
        N3[Node 3]
    end
    N1 &lt;--&gt; N2
    N1 -.단절.- N3
    N2 -.단절.- N3
</pre><p>Infinispan은 기본적으로 다수파(majority) 파티션만 쓰기를 허용한다. 3노드 중 2:1로 갈라지면 2 노드 쪽만 살아 있고 1 노드 쪽은 DENY_READ_WRITES 상태로 격리된다. 설정으로 이 동작을 바꿀 수 있지만 운영상 기본값이 안전하다.</p><div class="language-conf line-numbers-mode" data-highlighter="prismjs" data-ext="conf" data-title="conf"><pre><code><span class="line"># cache-ispn.xml</span>
<span class="line">&lt;distributed-cache name=&quot;sessions&quot;&gt;</span>
<span class="line">    &lt;partition-handling when-split=&quot;DENY_READ_WRITES&quot; merge-policy=&quot;PREFERRED_ALWAYS&quot;/&gt;</span>
<span class="line">&lt;/distributed-cache&gt;</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="노드-완전-소실" tabindex="-1"><a class="header-anchor" href="#노드-완전-소실"><span>노드 완전 소실</span></a></h3><p>전체 Keycloak 노드가 동시에 재시작되면 Embedded 모드에서는 메모리 캐시 4종(sessions/authSessions/loginFailures/actionTokens)이 모두 날아간다.</p><ul><li>영향: 전체 사용자 재로그인, 로그인 진행 중이던 플로우 실패, Brute Force 카운터 리셋.</li><li>완화: External Infinispan으로 캐시를 분리하면, Keycloak 전체 재기동에도 세션은 남는다.</li><li>완화: v26 Persistent user sessions로 DB에 세션을 영속화.</li></ul><h3 id="db-장애" tabindex="-1"><a class="header-anchor" href="#db-장애"><span>DB 장애</span></a></h3><p>PostgreSQL이 다운되면 토큰 발급은 멈추지만, 기존 세션 검증은 캐시에 있는 동안 계속 동작할 수 있다. 다만 <code>offlineSessions</code>처럼 DB와 싱크되는 캐시는 쓰기 실패로 에러를 던진다.</p><ul><li>영향: 신규 로그인 차단, Refresh Token 저장 실패.</li><li>완화: PostgreSQL HA(Patroni, Crunchy) 구성, Connection Pool 재시도 설정.</li></ul><h3 id="운영-체크리스트" tabindex="-1"><a class="header-anchor" href="#운영-체크리스트"><span>운영 체크리스트</span></a></h3><table><thead><tr><th>항목</th><th>확인</th></tr></thead><tbody><tr><td><code>cache-remote-*</code> 설정이 환경변수로 주입되는가</td><td>Secret/ConfigMap 활용</td></tr><tr><td>JGroups 디스커버리가 DNS_PING인가</td><td>K8s Headless Service 검증</td></tr><tr><td>Partition handling 기본값(DENY_READ_WRITES) 유지</td><td>Split-brain 시 데이터 안전</td></tr><tr><td><code>sessions</code>·<code>actionTokens</code> 모드가 SYNC인가</td><td>Replicated/Distributed 모드 점검</td></tr><tr><td>Multi-site XSite 복제 지연 모니터링</td><td>Infinispan Prometheus 지표</td></tr></tbody></table><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>Keycloak은 5가지 캐시(sessions/authSessions/offlineSessions/loginFailures/actionTokens)를 Infinispan으로 관리하며, offlineSessions만 DB에 영속된다.</li><li>Embedded는 구성 단순하지만 스케일링 결합 문제가 있다. v26+는 External Infinispan + Persistent sessions 조합을 권장한다.</li><li>SYNC는 정합성, ASYNC는 성능. 대부분의 Keycloak 캐시는 SYNC가 안전한 기본이다.</li><li>Multi-site는 Active/Passive + XSite 비동기 복제가 표준. Active/Active는 로그인 레이스 컨디션으로 권장되지 않는다.</li><li>Split-brain에는 partition-handling DENY_READ_WRITES가 기본이고, 이는 데이터 무결성을 위해 유지한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p>클러스터 기본 구조를 이해했다면 이제 실제 배포 형태를 다룬다. <a href="/study/keycloak/21-k8s-operator">CH21. Kubernetes + Operator 배포</a>에서 Keycloak Operator로 프로덕션급 Keycloak을 쿠버네티스에 올리는 방법과, Realm을 GitOps로 선언 관리하는 패턴을 살펴본다.</p><ul><li>이전: <a href="/study/keycloak/19-theme">CH19. Theme 커스터마이징</a></li><li>다음: <a href="/study/keycloak/21-k8s-operator">CH21. Kubernetes + Operator 배포</a></li></ul>`,97)]))}const o=n(s,[["render",l],["__file","20-ha-clustering.html.vue"]]),c=JSON.parse('{"path":"/study/keycloak/20-ha-clustering.html","title":"Infinispan HA 클러스터링","lang":"en-US","frontmatter":{"title":"Infinispan HA 클러스터링","description":"Keycloak의 Infinispan 기반 세션 분산 캐시와 Multi-site 배포 구조를 다룬다.","date":"2026-04-17T00:00:00.000Z","tags":["Keycloak","Infinispan","HA","클러스터"],"prev":"/study/keycloak/19-theme","next":"/study/keycloak/21-k8s-operator"},"headers":[{"level":1,"title":"Infinispan HA 클러스터링","slug":"infinispan-ha-클러스터링","link":"#infinispan-ha-클러스터링","children":[{"level":2,"title":"1. Infinispan이란 무엇인가","slug":"_1-infinispan이란-무엇인가","link":"#_1-infinispan이란-무엇인가","children":[{"level":3,"title":"Keycloak이 Infinispan을 쓰는 이유","slug":"keycloak이-infinispan을-쓰는-이유","link":"#keycloak이-infinispan을-쓰는-이유","children":[]},{"level":3,"title":"단일 노드에서도 Infinispan이 쓰인다","slug":"단일-노드에서도-infinispan이-쓰인다","link":"#단일-노드에서도-infinispan이-쓰인다","children":[]},{"level":3,"title":"언제 Infinispan을 의식해야 하는가","slug":"언제-infinispan을-의식해야-하는가","link":"#언제-infinispan을-의식해야-하는가","children":[]}]},{"level":2,"title":"2. Keycloak 캐시 5종","slug":"_2-keycloak-캐시-5종","link":"#_2-keycloak-캐시-5종","children":[{"level":3,"title":"분산(distributed) vs 복제(replicated)","slug":"분산-distributed-vs-복제-replicated","link":"#분산-distributed-vs-복제-replicated","children":[]}]},{"level":2,"title":"3. Embedded Infinispan","slug":"_3-embedded-infinispan","link":"#_3-embedded-infinispan","children":[{"level":3,"title":"기동 구조","slug":"기동-구조","link":"#기동-구조","children":[]},{"level":3,"title":"JGroups 디스커버리","slug":"jgroups-디스커버리","link":"#jgroups-디스커버리","children":[]},{"level":3,"title":"Embedded 모드의 한계","slug":"embedded-모드의-한계","link":"#embedded-모드의-한계","children":[]}]},{"level":2,"title":"4. External Infinispan","slug":"_4-external-infinispan","link":"#_4-external-infinispan","children":[{"level":3,"title":"Embedded와 비교","slug":"embedded와-비교","link":"#embedded와-비교","children":[]},{"level":3,"title":"Keycloak 측 설정","slug":"keycloak-측-설정","link":"#keycloak-측-설정","children":[]}]},{"level":2,"title":"5. 캐시 동기화 모드","slug":"_5-캐시-동기화-모드","link":"#_5-캐시-동기화-모드","children":[{"level":3,"title":"SYNC 모드","slug":"sync-모드","link":"#sync-모드","children":[]},{"level":3,"title":"ASYNC 모드","slug":"async-모드","link":"#async-모드","children":[]},{"level":3,"title":"Keycloak 권장 설정","slug":"keycloak-권장-설정","link":"#keycloak-권장-설정","children":[]}]},{"level":2,"title":"6. Multi-site 배포","slug":"_6-multi-site-배포","link":"#_6-multi-site-배포","children":[{"level":3,"title":"Active/Passive 구조","slug":"active-passive-구조","link":"#active-passive-구조","children":[]},{"level":3,"title":"왜 Active/Active가 아닌가","slug":"왜-active-active가-아닌가","link":"#왜-active-active가-아닌가","children":[]},{"level":3,"title":"RTO/RPO 목표","slug":"rto-rpo-목표","link":"#rto-rpo-목표","children":[]}]},{"level":2,"title":"7. 장애 시나리오","slug":"_7-장애-시나리오","link":"#_7-장애-시나리오","children":[{"level":3,"title":"Split-brain","slug":"split-brain","link":"#split-brain","children":[]},{"level":3,"title":"노드 완전 소실","slug":"노드-완전-소실","link":"#노드-완전-소실","children":[]},{"level":3,"title":"DB 장애","slug":"db-장애","link":"#db-장애","children":[]},{"level":3,"title":"운영 체크리스트","slug":"운영-체크리스트","link":"#운영-체크리스트","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/keycloak/20-ha-clustering.md"}');export{o as comp,c as data};
