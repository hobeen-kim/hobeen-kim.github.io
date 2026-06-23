import{_ as s,c as a,e,o as t}from"./app-Bgkt9_QX.js";const l={};function p(i,n){return t(),a("div",null,n[0]||(n[0]=[e(`<h1 id="컨테이너-네트워크와-볼륨" tabindex="-1"><a class="header-anchor" href="#컨테이너-네트워크와-볼륨"><span>컨테이너 네트워크와 볼륨</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>bridge·host·none·overlay 네트워크 드라이버가 각각 어떤 격리·연결 모델인지 설명할 수 있다.</li><li>포트 매핑(-p)이 호스트와 컨테이너를 어떻게 연결하는지 이해한다.</li><li>사용자 정의 네트워크에서 컨테이너 이름으로 통신하는 내장 DNS의 동작을 안다.</li><li>볼륨과 바인드 마운트의 차이, 그리고 컨테이너 데이터 영속성 전략을 익힌다.</li><li>Docker Compose로 여러 컨테이너를 선언적으로 묶어 띄울 수 있다.</li></ul></div><h2 id="_1-네트워크-드라이버-—-bridge-host-none-overlay" tabindex="-1"><a class="header-anchor" href="#_1-네트워크-드라이버-—-bridge-host-none-overlay"><span>1. 네트워크 드라이버 — bridge, host, none, overlay</span></a></h2><p>컨테이너는 <a href="/study/kubernetes/01-container-basics">네트워크 namespace</a> 덕에 자기만의 네트워크 스택을 가진다. 이 스택을 호스트·외부와 어떻게 연결할지 결정하는 것이 <strong>네트워크 드라이버</strong>다. 전체 설명은 <a href="https://docs.docker.com/engine/network/" target="_blank" rel="noopener noreferrer">Docker networking</a>에 있다.</p><table><thead><tr><th>드라이버</th><th>동작</th><th>용도</th></tr></thead><tbody><tr><td><code>bridge</code></td><td>가상 브리지(docker0)에 연결, NAT로 외부 접속</td><td>단일 호스트 기본값</td></tr><tr><td><code>host</code></td><td>호스트의 네트워크 스택을 그대로 공유 (격리 없음)</td><td>최고 성능이 필요할 때</td></tr><tr><td><code>none</code></td><td>네트워크 인터페이스 없음 (loopback만)</td><td>완전 격리</td></tr><tr><td><code>overlay</code></td><td>여러 호스트의 컨테이너를 한 가상 네트워크로 연결</td><td>Swarm·멀티 호스트</td></tr></tbody></table><p><strong>bridge</strong>가 기본이자 가장 중요하다. 도커는 <code>docker0</code>라는 가상 브리지를 만들고, 각 컨테이너에 가상 이더넷 쌍(veth pair)을 꽂아 사설 IP를 준다. 외부로 나갈 때는 호스트가 NAT(masquerade)로 변환한다.</p><pre class="mermaid">flowchart TB
    Internet[&quot;외부 네트워크&quot;]
    Host[&quot;호스트 (eth0, NAT)&quot;]
    Internet &lt;--&gt; Host
    Host --&gt; Bridge[&quot;docker0 브리지 (172.17.0.1)&quot;]
    Bridge --&gt; C1[&quot;컨테이너 A&lt;br&gt;172.17.0.2&quot;]
    Bridge --&gt; C2[&quot;컨테이너 B&lt;br&gt;172.17.0.3&quot;]
    Bridge --&gt; C3[&quot;컨테이너 C&lt;br&gt;172.17.0.4&quot;]
</pre><p><strong>host</strong> 모드는 NAT·veth를 거치지 않고 호스트 스택을 직접 쓴다. 포트 매핑이 없어 컨테이너가 80번을 열면 호스트 80번이 곧 그것이다. 빠르지만 포트 충돌과 격리 상실이라는 대가가 따른다. <strong>none</strong>은 외부 연결이 전혀 없는 완전 격리 환경이다. <strong>overlay</strong>는 여러 호스트에 걸친 컨테이너를 하나의 L2 네트워크처럼 묶으며, 쿠버네티스의 CNI 오버레이 개념의 선조 격이다.</p><h2 id="_2-포트-매핑-—-컨테이너를-외부에-노출하기" tabindex="-1"><a class="header-anchor" href="#_2-포트-매핑-—-컨테이너를-외부에-노출하기"><span>2. 포트 매핑 — 컨테이너를 외부에 노출하기</span></a></h2><p>bridge 네트워크의 컨테이너는 사설 IP를 가지므로 호스트 바깥에서 직접 닿을 수 없다. 외부에서 접속하려면 <strong>포트 매핑(port publishing)</strong>으로 호스트의 포트를 컨테이너 포트에 연결한다.</p><div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre><code><span class="line"><span class="token comment"># 호스트 8080 → 컨테이너 80 으로 매핑</span></span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-d</span> <span class="token parameter variable">-p</span> <span class="token number">8080</span>:80 nginx</span>
<span class="line"></span>
<span class="line"><span class="token comment"># 특정 인터페이스에만 바인딩 (보안상 권장)</span></span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-d</span> <span class="token parameter variable">-p</span> <span class="token number">127.0</span>.0.1:8080:80 nginx</span>
<span class="line"></span>
<span class="line"><span class="token comment"># 호스트 포트를 자동 할당</span></span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-d</span> <span class="token parameter variable">-P</span> nginx</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>-p 8080:80</code>은 &quot;호스트의 8080으로 들어온 트래픽을 컨테이너의 80으로 전달하라&quot;는 뜻이며, 내부적으로 iptables DNAT 규칙으로 구현된다. Dockerfile의 <code>EXPOSE</code>는 문서화일 뿐 실제 매핑이 아니라는 점을 다시 확인해 둔다.</p><pre class="mermaid">sequenceDiagram
    participant U as 외부 클라이언트
    participant H as 호스트 :8080
    participant IPT as iptables (DNAT)
    participant C as 컨테이너 :80
    U-&gt;&gt;H: GET http://host:8080
    H-&gt;&gt;IPT: 8080 도착
    IPT-&gt;&gt;C: 172.17.0.2:80 으로 전달
    C--&gt;&gt;U: 응답
</pre><h2 id="_3-컨테이너-간-통신과-dns" tabindex="-1"><a class="header-anchor" href="#_3-컨테이너-간-통신과-dns"><span>3. 컨테이너 간 통신과 DNS</span></a></h2><p>같은 호스트의 컨테이너끼리 통신할 때, 기본 bridge 네트워크는 IP로만 통신할 수 있어 불편하다. 반면 <strong>사용자 정의 네트워크(user-defined bridge)</strong>를 만들면 도커의 <strong>내장 DNS</strong>가 동작해 <strong>컨테이너 이름으로 서로를 찾을 수 있다</strong>. 이것이 실무에서 사용자 정의 네트워크를 쓰는 가장 큰 이유다.</p><div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre><code><span class="line"><span class="token comment"># 사용자 정의 네트워크 생성</span></span>
<span class="line"><span class="token function">docker</span> network create appnet</span>
<span class="line"></span>
<span class="line"><span class="token comment"># 두 컨테이너를 같은 네트워크에 연결</span></span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-d</span> <span class="token parameter variable">--name</span> db <span class="token parameter variable">--network</span> appnet postgres:16</span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-d</span> <span class="token parameter variable">--name</span> api <span class="token parameter variable">--network</span> appnet myapp:1.0</span>
<span class="line"></span>
<span class="line"><span class="token comment"># api 컨테이너 안에서 &quot;db&quot;라는 이름으로 DB에 접속 가능</span></span>
<span class="line"><span class="token function">docker</span> <span class="token builtin class-name">exec</span> api <span class="token function">ping</span> db        <span class="token comment"># 이름이 IP로 해석된다</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>api 컨테이너의 코드에서 DB 호스트를 <code>db:5432</code>로 적으면 된다. IP가 바뀌어도 이름은 그대로이므로 설정이 견고해진다. 이 &quot;이름 기반 서비스 디스커버리&quot;는 쿠버네티스의 <a href="/study/kubernetes/28-dns-discovery">Service·DNS</a>에서 훨씬 정교하게 확장된다.</p><div class="hint-container tip"><p class="hint-container-title">기본 bridge vs 사용자 정의 bridge</p><p>도커가 자동으로 만드는 기본 <code>bridge</code> 네트워크는 DNS 이름 해석을 제공하지 않는다(레거시 <code>--link</code>만 가능). 컨테이너 간 통신이 필요하면 항상 <code>docker network create</code>로 사용자 정의 네트워크를 만들어 쓴다.</p></div><h2 id="_4-볼륨과-바인드-마운트-—-데이터-영속성" tabindex="-1"><a class="header-anchor" href="#_4-볼륨과-바인드-마운트-—-데이터-영속성"><span>4. 볼륨과 바인드 마운트 — 데이터 영속성</span></a></h2><p>컨테이너의 쓰기 레이어에 저장한 데이터는 컨테이너를 지우면 사라진다. 데이터베이스·업로드 파일처럼 살아남아야 하는 데이터는 컨테이너 바깥에 저장해야 한다. 도커는 두 가지 방식을 제공한다. 자세한 비교는 <a href="https://docs.docker.com/engine/storage/" target="_blank" rel="noopener noreferrer">Manage data in Docker</a>에 있다.</p><ul><li><strong>볼륨(volume)</strong>: 도커가 관리하는 저장소(<code>/var/lib/docker/volumes/</code>). 호스트 경로를 신경 쓸 필요 없고, 이식성·백업·드라이버 확장이 좋다. <strong>운영 데이터의 표준</strong>.</li><li><strong>바인드 마운트(bind mount)</strong>: 호스트의 특정 경로를 컨테이너에 직접 연결. 호스트 파일을 즉시 반영하므로 개발 중 소스 코드 공유에 적합하다.</li></ul><pre class="mermaid">flowchart LR
    subgraph Host[&quot;호스트&quot;]
        VolDir[&quot;/var/lib/docker/volumes/dbdata&lt;br&gt;(도커 관리 볼륨)&quot;]
        SrcDir[&quot;/home/dev/project&lt;br&gt;(임의 호스트 경로)&quot;]
    end
    subgraph C[&quot;컨테이너&quot;]
        Mnt1[&quot;/var/lib/postgresql/data&quot;]
        Mnt2[&quot;/app&quot;]
    end
    VolDir -- &quot;named volume&quot; --&gt; Mnt1
    SrcDir -- &quot;bind mount&quot; --&gt; Mnt2
</pre><div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre><code><span class="line"><span class="token comment"># 명명된 볼륨 생성 후 DB 데이터를 영속화</span></span>
<span class="line"><span class="token function">docker</span> volume create dbdata</span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-d</span> <span class="token parameter variable">--name</span> db <span class="token parameter variable">-v</span> dbdata:/var/lib/postgresql/data postgres:16</span>
<span class="line"></span>
<span class="line"><span class="token comment"># 바인드 마운트: 호스트 소스를 컨테이너에 직접 연결 (개발용)</span></span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-d</span> <span class="token parameter variable">-v</span> <span class="token variable"><span class="token variable">$(</span><span class="token builtin class-name">pwd</span><span class="token variable">)</span></span>:/app <span class="token parameter variable">-w</span> /app node:20 <span class="token function">npm</span> run dev</span>
<span class="line"></span>
<span class="line"><span class="token comment"># 읽기 전용 마운트</span></span>
<span class="line"><span class="token function">docker</span> run <span class="token parameter variable">-v</span> dbdata:/data:ro alpine</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>이제 <code>db</code> 컨테이너를 삭제했다 다시 만들어도, <code>dbdata</code> 볼륨을 같은 경로에 마운트하면 데이터가 그대로 남아 있다. <strong>컨테이너는 일회용, 데이터는 볼륨에</strong> — 이 원칙이 컨테이너 운영의 기본이며 쿠버네티스의 <a href="/study/kubernetes/30-volume-pv-pvc">PV/PVC</a>로 그대로 이어진다.</p><div class="hint-container warning"><p class="hint-container-title">바인드 마운트의 함정</p><p>바인드 마운트는 호스트의 실제 파일을 노출하므로, 컨테이너가 그 경로를 변조할 수 있고 호스트 보안에 영향을 준다. 운영에서 영속 데이터는 볼륨을 쓰고, 바인드 마운트는 개발 환경의 소스 핫리로드 정도로 한정하는 것이 안전하다.</p></div><h2 id="_5-docker-compose-기초" tabindex="-1"><a class="header-anchor" href="#_5-docker-compose-기초"><span>5. Docker Compose 기초</span></a></h2><p>실제 애플리케이션은 앱·DB·캐시 등 여러 컨테이너로 구성된다. 이를 매번 <code>docker run</code>으로 띄우면 옵션이 길어지고 재현이 어렵다. <strong>Docker Compose</strong>는 여러 컨테이너·네트워크·볼륨을 하나의 YAML 파일로 <strong>선언적으로</strong> 정의하고 한 번에 띄운다. 자세한 내용은 <a href="https://docs.docker.com/compose/" target="_blank" rel="noopener noreferrer">Compose 문서</a>를 참고한다.</p><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token comment"># compose.yaml</span></span>
<span class="line"><span class="token key atrule">services</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">api</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">build</span><span class="token punctuation">:</span> .                 <span class="token comment"># 현재 디렉터리의 Dockerfile로 빌드</span></span>
<span class="line">    <span class="token key atrule">ports</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token string">&quot;8080:8080&quot;</span></span>
<span class="line">    <span class="token key atrule">environment</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token key atrule">DB_HOST</span><span class="token punctuation">:</span> db            <span class="token comment"># 서비스 이름으로 DB에 접속</span></span>
<span class="line">      <span class="token key atrule">DB_PORT</span><span class="token punctuation">:</span> <span class="token string">&quot;5432&quot;</span></span>
<span class="line">    <span class="token key atrule">depends_on</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token punctuation">-</span> db</span>
<span class="line">    <span class="token key atrule">networks</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token punctuation">-</span> appnet</span>
<span class="line"></span>
<span class="line">  <span class="token key atrule">db</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">image</span><span class="token punctuation">:</span> postgres<span class="token punctuation">:</span><span class="token number">16</span></span>
<span class="line">    <span class="token key atrule">environment</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token key atrule">POSTGRES_PASSWORD</span><span class="token punctuation">:</span> secret</span>
<span class="line">    <span class="token key atrule">volumes</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token punctuation">-</span> dbdata<span class="token punctuation">:</span>/var/lib/postgresql/data   <span class="token comment"># 명명된 볼륨으로 영속화</span></span>
<span class="line">    <span class="token key atrule">networks</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token punctuation">-</span> appnet</span>
<span class="line"></span>
<span class="line"><span class="token key atrule">volumes</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">dbdata</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line"><span class="token key atrule">networks</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">appnet</span><span class="token punctuation">:</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre><code><span class="line"><span class="token comment"># 전체 스택을 백그라운드로 기동</span></span>
<span class="line"><span class="token function">docker</span> compose up <span class="token parameter variable">-d</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># 로그 확인 / 상태 확인</span></span>
<span class="line"><span class="token function">docker</span> compose logs <span class="token parameter variable">-f</span></span>
<span class="line"><span class="token function">docker</span> compose <span class="token function">ps</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># 전체 정리 (볼륨까지 지우려면 -v)</span></span>
<span class="line"><span class="token function">docker</span> compose down</span>
<span class="line"><span class="token function">docker</span> compose down <span class="token parameter variable">-v</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Compose는 정의된 서비스를 위한 네트워크를 자동으로 만들어 주므로, <code>api</code>에서 DB 호스트를 그냥 <code>db</code>로 적으면 내장 DNS로 해석된다. 별도 <code>docker network create</code>가 필요 없다.</p><pre class="mermaid">flowchart TB
    Compose[&quot;compose.yaml&lt;br&gt;(선언)&quot;] --&gt; Up[&quot;docker compose up&quot;]
    Up --&gt; Net[&quot;자동 생성 네트워크 appnet&quot;]
    Up --&gt; Vol[&quot;자동 생성 볼륨 dbdata&quot;]
    Net --&gt; S1[&quot;api 서비스&quot;]
    Net --&gt; S2[&quot;db 서비스&quot;]
    Vol --&gt; S2
    S1 -. &quot;db:5432 (DNS)&quot; .-&gt; S2
</pre><p>Compose의 &quot;여러 컨테이너를 선언적으로 묶는다&quot;는 발상은 쿠버네티스의 매니페스트와 곧장 연결된다. 다만 Compose는 단일 호스트 중심이고, 쿠버네티스는 다중 노드 클러스터에서 스케줄링·자가치유·확장까지 책임진다는 점이 다르다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li><strong>bridge</strong>가 단일 호스트 기본 네트워크이며 NAT로 외부와 연결된다. host는 격리를 버린 고성능, none은 완전 격리, overlay는 멀티 호스트용이다.</li><li><strong>포트 매핑(-p)</strong>은 iptables DNAT로 호스트 포트를 컨테이너 포트에 연결한다. EXPOSE는 문서일 뿐 실제 매핑이 아니다.</li><li><strong>사용자 정의 네트워크</strong>에서는 내장 DNS로 컨테이너 이름 통신이 가능하다. 기본 bridge에는 이 기능이 없다.</li><li>영속 데이터는 <strong>볼륨</strong>에 둔다(컨테이너는 일회용). 바인드 마운트는 개발용 소스 공유에 한정한다.</li><li><strong>Docker Compose</strong>는 다중 컨테이너 앱을 YAML로 선언해 한 번에 띄우며, 쿠버네티스 매니페스트의 사고방식으로 이어진다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p>도커 위에서 컨테이너를 다뤄봤으니, 이제 그 아래에서 컨테이너를 실제로 실행하는 엔진을 들여다본다. <a href="/study/kubernetes/05-container-runtime">컨테이너 런타임 심화</a>에서 OCI 표준·runc·containerd·CRI와 샌드박스 런타임을 다룬다.</p>`,35)]))}const r=s(l,[["render",p],["__file","04-container-network-volume.html.vue"]]),c=JSON.parse('{"path":"/study/kubernetes/04-container-network-volume.html","title":"컨테이너 네트워크와 볼륨","lang":"en-US","frontmatter":{"title":"컨테이너 네트워크와 볼륨","description":"bridge·host·none·overlay 네트워크 드라이버와 포트 매핑·DNS, 볼륨과 바인드 마운트로 데이터를 영속화하는 법, Docker Compose 기초를 다룬다.","date":"2026-06-15T00:00:00.000Z","tags":["Docker","Network","Volume","bridge","Compose"],"prev":"/study/kubernetes/03-dockerfile-image","next":"/study/kubernetes/05-container-runtime"},"headers":[{"level":1,"title":"컨테이너 네트워크와 볼륨","slug":"컨테이너-네트워크와-볼륨","link":"#컨테이너-네트워크와-볼륨","children":[{"level":2,"title":"1. 네트워크 드라이버 — bridge, host, none, overlay","slug":"_1-네트워크-드라이버-—-bridge-host-none-overlay","link":"#_1-네트워크-드라이버-—-bridge-host-none-overlay","children":[]},{"level":2,"title":"2. 포트 매핑 — 컨테이너를 외부에 노출하기","slug":"_2-포트-매핑-—-컨테이너를-외부에-노출하기","link":"#_2-포트-매핑-—-컨테이너를-외부에-노출하기","children":[]},{"level":2,"title":"3. 컨테이너 간 통신과 DNS","slug":"_3-컨테이너-간-통신과-dns","link":"#_3-컨테이너-간-통신과-dns","children":[]},{"level":2,"title":"4. 볼륨과 바인드 마운트 — 데이터 영속성","slug":"_4-볼륨과-바인드-마운트-—-데이터-영속성","link":"#_4-볼륨과-바인드-마운트-—-데이터-영속성","children":[]},{"level":2,"title":"5. Docker Compose 기초","slug":"_5-docker-compose-기초","link":"#_5-docker-compose-기초","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/kubernetes/04-container-network-volume.md"}');export{r as comp,c as data};
