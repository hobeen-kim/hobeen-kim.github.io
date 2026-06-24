import{_ as n,c as a,e as i,o as s}from"./app-CC7cIlbq.js";const t={};function l(r,e){return s(),a("div",null,e[0]||(e[0]=[i(`<h1 id="ch5-모델링-패턴" tabindex="-1"><a class="header-anchor" href="#ch5-모델링-패턴"><span>CH5. 모델링 패턴</span></a></h1><h2 id="학습-목표" tabindex="-1"><a class="header-anchor" href="#학습-목표"><span>학습 목표</span></a></h2><ul><li>Schema를 설계할 때 relation과 permission을 나누는 기준을 세운다.</li><li>Google Drive 스타일의 폴더 상속·공유 링크 모델을 SpiceDB Schema로 옮긴다.</li><li>GitHub 스타일의 조직·팀·저장소 계층을 subject relation과 arrow로 표현한다.</li><li>SaaS 멀티테넌시 3가지 전략(relation 필터 / prefix / 인스턴스 분리)을 비교하고 선택 기준을 잡는다.</li><li>assertions/validation YAML로 schema 회귀 테스트를 돌리는 감각을 익힌다.</li></ul><h2 id="모델링의-일반-원칙" tabindex="-1"><a class="header-anchor" href="#모델링의-일반-원칙"><span>모델링의 일반 원칙</span></a></h2><p>Schema 설계가 처음이라면 세 문장만 머리에 박아 두면 된다. &quot;관계를 먼저 찾고, permission은 그 조합으로&quot;, &quot;저장 가능한 건 <code>relation</code>, 계산되는 건 <code>permission</code>&quot;, &quot;상속은 arrow(<code>-&gt;</code>)와 parent 관계로 표현한다&quot;.</p><p>제품 요구사항을 받았을 때 가장 먼저 할 일은 &quot;어떤 객체가 있고, 누가 누구와 어떤 이름으로 엮이는지&quot;를 나열하는 것이다. 이 단계에서 나오는 단어가 전부 relation 후보다. 예를 들어 &quot;폴더 소유자&quot;, &quot;저장소 관리자&quot;, &quot;팀 멤버&quot;는 모두 relation이다.</p><p>그다음 &quot;이 관계가 있으면 할 수 있는 행동&quot;을 정리하면 그게 permission이다. <code>edit</code>·<code>view</code>·<code>push</code>·<code>admin</code> 같은 동사 중심 이름이 자연스럽다. 여기서 실수하기 쉬운 게 &quot;relation도 permission도 가능한 경우&quot;인데, 규칙은 단순하다. 사람이 직접 쓰기(writeRelationship) 가능한 건 relation, 스키마가 스스로 계산하는 건 permission이다.</p><p>상속은 거의 항상 arrow로 푼다. 폴더 안의 파일이 폴더의 뷰어를 자동 상속한다면, 파일 쪽에 <code>parent</code> relation을 두고 <code>permission view = viewer + parent-&gt;view</code>로 적는다. <code>parent-&gt;view</code>는 &quot;parent(folder)의 view permission을 소환해서 합친다&quot;는 뜻이다.</p><p>조직·팀·그룹처럼 &quot;주체 쪽이 집합&quot;인 경우는 subject relation으로 표현한다. <code>relation member: user | team#member</code>라고 쓰면, member에는 사용자 개인이 들어갈 수도 있고 &quot;다른 팀의 member 전체&quot;가 들어갈 수도 있다. 이 <code>team#member</code> 문법이 Zanzibar의 userset rewrite를 그대로 물려받은 부분이다.</p><div class="hint-container info"><p class="hint-container-title">relation 이름은 역할이 아니라 관계로</p><p><code>admin</code> 같은 역할 이름과 <code>owner</code>·<code>editor</code> 같은 관계 이름이 섞이기 쉽다. 일관성을 위해 &quot;소유/관리/편집&quot; 같이 관계로 읽을 수 있는 명사를 쓰고, &quot;할 수 있는 것&quot;은 permission 이름으로 분리한다. 예컨대 <code>relation admin</code>은 관계, <code>permission manage</code>는 행동.</p></div><h2 id="패턴-1-google-drive-스타일" tabindex="-1"><a class="header-anchor" href="#패턴-1-google-drive-스타일"><span>패턴 1: Google Drive 스타일</span></a></h2><p>Google Drive는 &quot;폴더 안에 폴더, 폴더 안에 파일&quot;이라는 계층과 상속이 핵심이다. 요구사항을 조금 더 구체적으로 풀어 보자.</p><ul><li>폴더는 다른 폴더의 자식이 될 수 있다(폴더 트리).</li><li>폴더의 viewer·editor 권한은 그 안의 파일·하위 폴더에 상속된다.</li><li>&quot;링크 있는 누구나 보기&quot; 같은 공개 공유가 가능해야 한다.</li><li>개별 사용자에게 폴더·파일 단위로 직접 공유할 수 있어야 한다.</li></ul><p>이걸 스키마로 옮기면 다음과 같다.</p><div class="language-zed line-numbers-mode" data-highlighter="prismjs" data-ext="zed" data-title="zed"><pre><code><span class="line">definition user {}</span>
<span class="line"></span>
<span class="line">definition folder {</span>
<span class="line">  relation parent: folder</span>
<span class="line">  relation owner: user</span>
<span class="line">  relation editor: user | folder#editor</span>
<span class="line">  relation viewer: user | folder#viewer</span>
<span class="line">  relation public_viewer: user:*</span>
<span class="line">  permission edit = owner + editor + parent-&gt;edit</span>
<span class="line">  permission view = viewer + edit + public_viewer + parent-&gt;view</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">definition file {</span>
<span class="line">  relation parent: folder</span>
<span class="line">  relation owner: user</span>
<span class="line">  relation editor: user</span>
<span class="line">  relation viewer: user</span>
<span class="line">  permission edit = owner + editor + parent-&gt;edit</span>
<span class="line">  permission view = viewer + edit + parent-&gt;view</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>핵심 포인트를 짚어 보자.</p><p>첫째, <code>parent: folder</code>가 폴더 트리를 만든다. <code>permission edit = ... + parent-&gt;edit</code>는 &quot;내 부모 폴더의 edit 권한이 있으면 나도 edit 가능&quot;이라는 재귀적 정의다. SpiceDB는 이걸 arrow 재귀로 풀어내면서 순환이 없도록 탐색한다.</p><p>둘째, <code>editor: user | folder#editor</code>에서 <code>folder#editor</code> 부분은 &quot;다른 폴더의 editor 전원&quot;을 subject로 받는 문법이다. &quot;이 공유 폴더의 editor는 팀 공용 폴더의 editor와 동일&quot; 같은 위임 관계를 만들 때 쓴다.</p><p>셋째, <code>public_viewer: user:*</code>가 바로 &quot;링크 있는 누구나&quot;를 표현하는 wildcard다. 공개용 relation을 <code>viewer</code>와 분리해 두면 <code>folder:shared#public_viewer@user:*</code>처럼 공개 공유 의도가 이름에서 드러나고, 스키마 리뷰·감사 단계에서 실수로 전원 공개가 되는 사고를 줄인다.</p><p>넷째, 파일의 <code>permission view = viewer + edit + parent-&gt;view</code> 순서가 중요하다. <code>edit</code>이 먼저 들어가면, 개별 파일 edit 권한이 있는 사람은 자동으로 view도 받는다. <code>parent-&gt;view</code>는 폴더의 뷰어 상속이다.</p><div class="hint-container warning"><p class="hint-container-title">user:* wildcard는 검토가 두 번 필요하다</p><p><code>user:*</code>는 편하지만 실수로 공개 공유가 되기 쉽다. Schema 리뷰와 relationship 쓰기 양쪽에서 공개 의도가 맞는지 반드시 확인한다. 가능하면 공개용 relation은 별도 이름(예: <code>public_viewer</code>)으로 분리해서 눈에 띄게 만드는 편이 안전하다.</p></div><pre class="mermaid">flowchart TB
  U[user:alice]
  F1[folder:root]
  F2[folder:project]
  FIL[file:spec.md]
  U --&gt;|owner| F1
  F2 --&gt;|parent| F1
  FIL --&gt;|parent| F2
  U2[user:bob]
  U2 --&gt;|viewer| F2
  W[user:*]
  W --&gt;|public_viewer| F1
  subgraph derived[상속된 권한]
    F2 -. parent-&gt;view .-&gt; F1
    FIL -. parent-&gt;view .-&gt; F2
  end
</pre><p>이 그래프로 보면 &quot;root의 owner인 alice는 parent 체인을 타고 spec.md의 edit까지 얻고, root의 <code>public_viewer</code>에 들어간 누구나도 view로 접근&quot;되는 흐름이 한눈에 들어온다.</p><h2 id="패턴-2-github-스타일-조직·팀·저장소" tabindex="-1"><a class="header-anchor" href="#패턴-2-github-스타일-조직·팀·저장소"><span>패턴 2: GitHub 스타일 조직·팀·저장소</span></a></h2><p>GitHub의 권한 모델은 세 계층이다. organization 아래 team이 있고, team은 다시 상위 팀을 가질 수 있다. repository는 organization에 속하면서 개별 사용자나 팀에 권한을 부여한다. 팀에 권한을 주면 그 팀의 모든 멤버가 권한을 받는다.</p><div class="language-zed line-numbers-mode" data-highlighter="prismjs" data-ext="zed" data-title="zed"><pre><code><span class="line">definition user {}</span>
<span class="line"></span>
<span class="line">definition organization {</span>
<span class="line">  relation admin: user</span>
<span class="line">  relation member: user</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">definition team {</span>
<span class="line">  relation organization: organization</span>
<span class="line">  relation parent_team: team</span>
<span class="line">  relation member: user | team#member</span>
<span class="line">  permission join = member + parent_team-&gt;member + organization-&gt;admin</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">definition repository {</span>
<span class="line">  relation organization: organization</span>
<span class="line">  relation admin: user | team#member</span>
<span class="line">  relation maintainer: user | team#member</span>
<span class="line">  relation reader: user | team#member</span>
<span class="line">  permission push = admin + maintainer</span>
<span class="line">  permission read = reader + push + organization-&gt;admin</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>여기서 <code>team#member</code>가 다시 등장한다. repository의 <code>admin: user | team#member</code>는 &quot;이 저장소 admin에 사용자 개인도 들어가지만, 팀 자체를 넣어도 된다&quot;는 뜻이다. 팀을 넣으면 해당 팀의 member 전원이 repository admin이 된다.</p><p><code>team</code> 쪽의 <code>permission join = member + parent_team-&gt;member + organization-&gt;admin</code>이 계층 상속을 보여준다. 조직의 admin은 자동으로 모든 팀에 join 가능하고, 상위 팀의 멤버는 하위 팀에도 속한다. GitHub가 실제로 &quot;nested team은 상위 팀 권한을 상속한다&quot;고 문서화한 규칙 그대로다.</p><p>repository의 <code>permission read = reader + push + organization-&gt;admin</code>에서 <code>organization-&gt;admin</code>도 같은 패턴이다. 조직 admin이면 모든 저장소에 자동 read 권한이 붙는다. &quot;slash-and-burn admin&quot; 같은 실수 방지를 위해 조직 admin은 최소 인원만 부여하는 운영 규칙이 별도로 필요하다.</p><pre class="mermaid">flowchart TB
  ORG[organization:acme]
  T1[team:platform]
  T2[team:platform-backend]
  R1[repository:api]
  T1 --&gt;|organization| ORG
  T2 --&gt;|organization| ORG
  T2 --&gt;|parent_team| T1
  R1 --&gt;|organization| ORG
  U1[user:admin-alice]
  U1 --&gt;|admin| ORG
  U2[user:dev-bob]
  U2 --&gt;|member| T2
  T1 -. team#member .-&gt; R1
  R1 -. maintainer .-&gt; T1
</pre><p>alice는 조직 admin이라 모든 repository의 read를 자동 획득하고, bob은 platform-backend 멤버이자 그 상위 팀 platform을 통해 repository:api의 maintainer가 된다. 스키마 한 장이 이 흐름 전부를 표현한다.</p><h2 id="패턴-3-saas-멀티테넌시" tabindex="-1"><a class="header-anchor" href="#패턴-3-saas-멀티테넌시"><span>패턴 3: SaaS 멀티테넌시</span></a></h2><p>하나의 SpiceDB 인스턴스가 여러 테넌트(고객사)의 데이터를 담아야 할 때 격리 전략을 잘못 잡으면 &quot;A사 사용자가 B사 프로젝트를 조회&quot;하는 사고가 난다. 실전에서 쓰는 방법은 크게 세 가지다.</p><p><strong>방법 A</strong> — 모든 object에 <code>tenant</code> relation을 포함하고, 권한 규칙에 tenant 소속을 필수 조건으로 건다.</p><div class="language-zed line-numbers-mode" data-highlighter="prismjs" data-ext="zed" data-title="zed"><pre><code><span class="line">definition tenant {</span>
<span class="line">  relation admin: user</span>
<span class="line">  relation member: user</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">definition project {</span>
<span class="line">  relation tenant: tenant</span>
<span class="line">  relation owner: user</span>
<span class="line">  permission view = owner + tenant-&gt;member</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>이 방식은 &quot;project:123은 tenant:acme에 속한다&quot;는 관계를 명시적으로 두고, <code>permission view</code>가 <code>tenant-&gt;member</code>를 통해 테넌트 소속을 검증한다. 한 인스턴스·한 스키마·한 DB로 운영 가능하지만, 관계를 쓸 때 tenant 연결을 빠뜨리면 격리가 뚫린다.</p><p><strong>방법 B</strong> — object id에 prefix를 붙여 namespacing한다. 예: <code>project:acme-123</code>, <code>project:beta-456</code>. 스키마는 그대로, id 규칙만 테넌트별로 구분한다.</p><p>구현은 가장 가볍지만 격리는 가장 느슨하다. id prefix는 관례일 뿐 엔진이 강제하지 못하므로 운영 실수가 곧 격리 사고다. 내부 관리 도구처럼 신뢰 경계가 느슨한 상황에서만 고려할 만하다.</p><p><strong>방법 C</strong> — 테넌트별로 SpiceDB 인스턴스(또는 datastore schema)를 분리한다. 완전한 물리적 격리이고 감사·규제 대응도 쉽지만, 운영 비용·배포 복잡도가 크게 는다.</p><p>선택 기준을 표로 정리하면 이렇다.</p><table><thead><tr><th>기준</th><th>방법 A (tenant relation)</th><th>방법 B (id prefix)</th><th>방법 C (인스턴스 분리)</th></tr></thead><tbody><tr><td>격리 강도</td><td>논리적 (스키마 규칙)</td><td>관례적 (id 규칙)</td><td>물리적 (별도 인프라)</td></tr><tr><td>운영 비용</td><td>낮음</td><td>가장 낮음</td><td>가장 높음</td></tr><tr><td>테넌트 수</td><td>많음 가능</td><td>많음 가능</td><td>수십~수백 제한적</td></tr><tr><td>규제 대응</td><td>중간 (설계로 입증)</td><td>어려움</td><td>쉬움 (물리 격리)</td></tr><tr><td>크로스 테넌트 공유</td><td>쉬움</td><td>쉬움</td><td>어려움 (instance 간 호출 필요)</td></tr></tbody></table><div class="hint-container tip"><p class="hint-container-title">실전 선택</p><p>대부분의 SaaS는 <strong>방법 A</strong>에서 시작하고, 규제가 강한 특정 고객 전용 배포가 필요해지면 그 고객만 <strong>방법 C</strong>로 옮긴다. <strong>방법 B</strong>는 권장하지 않는다.</p></div><h2 id="schema-리팩토링-팁" tabindex="-1"><a class="header-anchor" href="#schema-리팩토링-팁"><span>Schema 리팩토링 팁</span></a></h2><p>Schema는 코드처럼 자란다. 초기엔 깔끔하지만 요구사항이 늘면 지저분해지기 마련이다. 몇 가지 규칙만 지켜도 관리 비용이 확 줄어든다.</p><ul><li>permission 이름은 제품 전역에서 일관되게 쓴다. 한쪽은 <code>view</code>인데 다른 definition은 <code>read</code>라고 쓰면 application 코드에서 매번 분기해야 한다.</li><li>relation 이름은 소문자 단수형을 쓴다. <code>members</code>·<code>Admins</code>가 섞이면 schema diff가 지저분해진다.</li><li>공개용 relation과 내부용 relation을 이름으로 구분한다. <code>viewer</code>와 <code>public_viewer</code>처럼.</li><li><code>user:*</code> 사용 지점에는 주석으로 의도를 남긴다. 스키마 리뷰 때 눈에 띄어야 한다.</li><li>사용하지 않는 relation을 오래 방치하지 않는다. CH10에서 다루는 마이그레이션 절차를 밟아 제거한다.</li></ul><h2 id="테스트-—-assertions-validation-yaml" tabindex="-1"><a class="header-anchor" href="#테스트-—-assertions-validation-yaml"><span>테스트 — assertions / validation YAML</span></a></h2><p>SpiceDB는 스키마 회귀 테스트를 위한 YAML 포맷을 제공한다. 스키마 변경 PR에 이 파일을 함께 수정·실행하는 게 사실상 표준이다. 간단 예시.</p><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token key atrule">schema</span><span class="token punctuation">:</span> <span class="token punctuation">|</span><span class="token punctuation">-</span></span>
<span class="line">  definition user <span class="token punctuation">{</span><span class="token punctuation">}</span></span>
<span class="line">  definition document <span class="token punctuation">{</span></span>
<span class="line">    <span class="token key atrule">relation viewer</span><span class="token punctuation">:</span> user</span>
<span class="line">    permission view = viewer</span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token key atrule">relationships</span><span class="token punctuation">:</span> <span class="token punctuation">|</span><span class="token punctuation">-</span></span>
<span class="line">  document<span class="token punctuation">:</span>readme<span class="token comment">#viewer@user:alice</span></span>
<span class="line"></span>
<span class="line"><span class="token key atrule">assertions</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">assertTrue</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token punctuation">-</span> <span class="token string">&quot;document:readme#view@user:alice&quot;</span></span>
<span class="line">  <span class="token key atrule">assertFalse</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token punctuation">-</span> <span class="token string">&quot;document:readme#view@user:bob&quot;</span></span>
<span class="line"></span>
<span class="line"><span class="token key atrule">validation</span><span class="token punctuation">:</span></span>
<span class="line">  document<span class="token punctuation">:</span>readme<span class="token comment">#view:</span></span>
<span class="line">    <span class="token punctuation">-</span> <span class="token string">&quot;[user:alice] is &lt;document:readme#viewer&gt;&quot;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>zed validate schema.yaml</code> 한 줄로 검증한다. <code>assertions</code>는 &quot;참이어야 한다/거짓이어야 한다&quot;는 단언, <code>validation</code>은 &quot;이 권한이 왜 성립하는지 풀어서 표시&quot;한다. CI에 붙여 두면 스키마 회귀를 자동으로 잡는다.</p><div class="hint-container info"><p class="hint-container-title">실전 워크플로우</p><p>스키마를 바꿀 땐 보통 ① validation YAML에 &quot;지금 시나리오&quot;를 먼저 박고 → ② 스키마 수정 → ③ 테스트 돌려 기존이 깨지지 않는지 확인 → ④ 새 시나리오 assertion 추가 순으로 간다. 애플리케이션 테스트 전에 이 단계에서 실수 대부분이 걸린다.</p></div><h2 id="핵심-정리" tabindex="-1"><a class="header-anchor" href="#핵심-정리"><span>핵심 정리</span></a></h2><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li><strong>relation은 저장되는 관계, permission은 계산되는 규칙</strong>. 상속은 arrow(<code>-&gt;</code>)와 parent relation으로 표현한다.</li><li><strong>Google Drive 모델</strong>: folder trees는 <code>parent: folder</code>, 파일의 상속은 <code>parent-&gt;view</code>, 공개 링크는 <code>user:*</code> wildcard.</li><li><strong>GitHub 모델</strong>: <code>team#member</code> subject relation으로 &quot;팀 단위 권한 부여&quot;를 구현한다. 부모 팀 상속·조직 admin 자동 권한도 arrow 한 줄.</li><li><strong>멀티테넌시 3가지</strong>: tenant relation(기본) · id prefix(비권장) · 인스턴스 분리(규제 대응). 시작은 A, 필요시 C로.</li><li><strong>테스트는 YAML</strong>: assertions·validation으로 스키마 회귀를 CI에서 자동 검증한다.</li><li><strong>리팩토링 원칙</strong>: 이름 일관성, 공개/내부 relation 구분, <code>user:*</code> 주석, 사용하지 않는 relation은 제거.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p>CH6에서는 Caveats를 본격적으로 다룬다. &quot;관계가 있고 + 업무시간이고 + 회사 네트워크 안이면&quot;처럼 관계 그래프만으로는 표현하지 못하는 조건부 권한을 CEL 표현식과 partial evaluation으로 풀어낸다.</p>`,54)]))}const d=n(t,[["render",l],["__file","05-modeling-patterns.html.vue"]]),c=JSON.parse('{"path":"/study/spicedb/05-modeling-patterns.html","title":"CH5. 모델링 패턴","lang":"en-US","frontmatter":{"title":"CH5. 모델링 패턴","description":"Google Drive의 폴더 상속, GitHub의 조직·팀·저장소, SaaS의 멀티테넌시까지 실전 시나리오를 SpiceDB Schema로 번역하는 법.","date":"2026-04-20T00:00:00.000Z","tags":["SpiceDB","Modeling","Schema","Multi-tenancy","Google Drive","GitHub"]},"headers":[{"level":1,"title":"CH5. 모델링 패턴","slug":"ch5-모델링-패턴","link":"#ch5-모델링-패턴","children":[{"level":2,"title":"학습 목표","slug":"학습-목표","link":"#학습-목표","children":[]},{"level":2,"title":"모델링의 일반 원칙","slug":"모델링의-일반-원칙","link":"#모델링의-일반-원칙","children":[]},{"level":2,"title":"패턴 1: Google Drive 스타일","slug":"패턴-1-google-drive-스타일","link":"#패턴-1-google-drive-스타일","children":[]},{"level":2,"title":"패턴 2: GitHub 스타일 조직·팀·저장소","slug":"패턴-2-github-스타일-조직·팀·저장소","link":"#패턴-2-github-스타일-조직·팀·저장소","children":[]},{"level":2,"title":"패턴 3: SaaS 멀티테넌시","slug":"패턴-3-saas-멀티테넌시","link":"#패턴-3-saas-멀티테넌시","children":[]},{"level":2,"title":"Schema 리팩토링 팁","slug":"schema-리팩토링-팁","link":"#schema-리팩토링-팁","children":[]},{"level":2,"title":"테스트 — assertions / validation YAML","slug":"테스트-—-assertions-validation-yaml","link":"#테스트-—-assertions-validation-yaml","children":[]},{"level":2,"title":"핵심 정리","slug":"핵심-정리","link":"#핵심-정리","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/spicedb/05-modeling-patterns.md"}');export{d as comp,c as data};
