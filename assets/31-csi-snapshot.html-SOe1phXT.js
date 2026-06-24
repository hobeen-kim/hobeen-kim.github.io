import{_ as n,c as a,e,o as t}from"./app-dO2BZptS.js";const l={};function p(i,s){return t(),a("div",null,s[0]||(s[0]=[e(`<h1 id="csi와-동적-프로비저닝" tabindex="-1"><a class="header-anchor" href="#csi와-동적-프로비저닝"><span>CSI와 동적 프로비저닝</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>CSI가 왜 등장했는지, 그리고 그 아키텍처가 어떤 컴포넌트로 구성되는지 이해한다.</li><li>PVC 하나로 PV·실제 디스크가 자동 생성되는 동적 프로비저닝의 단계별 흐름을 익힌다.</li><li>VolumeSnapshot으로 스냅샷을 만들고 그것으로부터 새 볼륨을 복원하는 방법을 다룬다.</li><li>운영 중인 볼륨을 무중단으로 확장(expansion)하는 조건과 절차를 안다.</li></ul></div><h2 id="_1-csi는-왜-등장했나" tabindex="-1"><a class="header-anchor" href="#_1-csi는-왜-등장했나"><span>1. CSI는 왜 등장했나</span></a></h2><p>초기 쿠버네티스는 스토리지 벤더 코드를 자기 본체(in-tree)에 직접 담았다. AWS EBS, GCE PD, Cinder 같은 드라이버가 쿠버네티스 소스 안에 들어 있었다. 이 방식은 문제가 많았다. 새 스토리지를 지원하려면 쿠버네티스 자체를 고쳐 릴리스해야 했고, 벤더 코드의 버그가 핵심 컴포넌트(kubelet, controller-manager)를 위협했다.</p><p><strong>CSI(Container Storage Interface)</strong>는 이 결합을 끊는 표준 인터페이스다. 스토리지 제공자가 쿠버네티스 밖에서 독립적으로 드라이버를 개발·배포할 수 있게 하고, 쿠버네티스는 표준 gRPC 인터페이스로 그 드라이버와 통신한다. 같은 인터페이스를 Kubernetes 외 다른 오케스트레이터(Nomad 등)도 쓸 수 있어, 한 번 만든 드라이버를 여러 플랫폼에서 재사용한다.</p><p>CSI 드라이버는 보통 세 종류의 gRPC 서비스를 구현한다.</p><ul><li><strong>Identity</strong>: 드라이버 이름·능력 보고</li><li><strong>Controller</strong>: 볼륨 생성·삭제·스냅샷 등 클러스터 수준 작업</li><li><strong>Node</strong>: 노드에서 볼륨을 stage/publish(실제 마운트)하는 작업</li></ul><pre class="mermaid">flowchart TB
    subgraph &quot;쿠버네티스 측 (sidecar)&quot;
        prov[&quot;external-provisioner&quot;]
        att[&quot;external-attacher&quot;]
        snap[&quot;external-snapshotter&quot;]
        resz[&quot;external-resizer&quot;]
    end
    subgraph &quot;벤더 측 (CSI Driver)&quot;
        ctrl[&quot;Controller Service&quot;]
        node[&quot;Node Service&quot;]
    end
    prov &amp; att &amp; snap &amp; resz -- &quot;gRPC&quot; --&gt; ctrl
    kubelet[&quot;kubelet&quot;] -- &quot;gRPC&quot; --&gt; node
    ctrl &amp; node -. &quot;벤더 API&quot; .-&gt; storage[(&quot;실제 스토리지&lt;br&gt;(클라우드 API/SAN)&quot;)]
</pre><p>위에서 <code>external-provisioner</code>, <code>external-attacher</code> 같은 <strong>사이드카</strong>들은 쿠버네티스 SIG가 제공하는 공용 컴포넌트로, 쿠버네티스 API 오브젝트(PVC, VolumeAttachment 등)를 감시하다가 적절한 시점에 벤더의 CSI 드라이버 gRPC를 호출한다. 벤더는 Controller·Node 서비스만 구현하면 된다. 전체 개요는 <a href="https://kubernetes.io/docs/concepts/storage/volumes/#csi" target="_blank" rel="noopener noreferrer">CSI 개념 문서</a>에 있다.</p><h2 id="_2-동적-프로비저닝의-흐름" tabindex="-1"><a class="header-anchor" href="#_2-동적-프로비저닝의-흐름"><span>2. 동적 프로비저닝의 흐름</span></a></h2><p>앞 챕터에서 본 정적 프로비저닝은 관리자가 PV를 미리 만들어둬야 했다. <strong>동적 프로비저닝</strong>은 PVC가 들어오면 StorageClass의 지시에 따라 PV와 실제 디스크가 그 자리에서 자동 생성된다. 사용자는 PVC 한 장만 내면 된다.</p><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token key atrule">apiVersion</span><span class="token punctuation">:</span> v1</span>
<span class="line"><span class="token key atrule">kind</span><span class="token punctuation">:</span> PersistentVolumeClaim</span>
<span class="line"><span class="token key atrule">metadata</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">name</span><span class="token punctuation">:</span> db<span class="token punctuation">-</span>data</span>
<span class="line"><span class="token key atrule">spec</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">accessModes</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token punctuation">-</span> ReadWriteOnce</span>
<span class="line">  <span class="token key atrule">storageClassName</span><span class="token punctuation">:</span> fast<span class="token punctuation">-</span>ssd</span>
<span class="line">  <span class="token key atrule">resources</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">requests</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token key atrule">storage</span><span class="token punctuation">:</span> 50Gi</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>이 PVC가 만들어진 뒤 실제로 무슨 일이 일어나는지를 단계별로 보면 다음과 같다.</p><pre class="mermaid">sequenceDiagram
    participant U as 사용자
    participant API as kube-apiserver
    participant P as external-provisioner
    participant D as CSI Controller
    participant Cloud as 클라우드 스토리지 API
    participant Sched as 스케줄러
    participant K as kubelet (Node)

    U-&gt;&gt;API: PVC 생성 (storageClassName=fast-ssd)
    Note over API: WaitForFirstConsumer면&lt;br&gt;Pod 스케줄까지 대기
    Sched-&gt;&gt;API: Pod를 노드에 배정
    P-&gt;&gt;API: PVC watch → 프로비저닝 필요 감지
    P-&gt;&gt;D: CreateVolume(50Gi, topology)
    D-&gt;&gt;Cloud: 디스크 생성 요청
    Cloud--&gt;&gt;D: volumeID 반환
    D--&gt;&gt;P: 볼륨 정보
    P-&gt;&gt;API: PV 생성 후 PVC와 Bound
    K-&gt;&gt;D: NodeStageVolume / NodePublishVolume
    D-&gt;&gt;Cloud: 노드에 attach + mount
    K--&gt;&gt;API: Pod 안의 컨테이너에 볼륨 마운트
</pre><p>핵심은 두 단계로 나뉜다는 점이다. <strong>provision(생성·바인딩)</strong>은 클러스터 수준에서 디스크를 만들고 PV를 묶는 일이고, <strong>attach/mount</strong>는 그 디스크를 Pod가 배정된 노드에 실제로 붙이고 마운트하는 일이다. <code>volumeBindingMode: WaitForFirstConsumer</code>를 쓰면 provision이 Pod 스케줄 이후로 미뤄져, 디스크가 Pod와 같은 zone에 생성되도록 보장한다. 동적 프로비저닝 상세는 <a href="https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/" target="_blank" rel="noopener noreferrer">Dynamic Provisioning 문서</a>를 참고한다.</p><h2 id="_3-volumesnapshot-—-스냅샷-뜨기" tabindex="-1"><a class="header-anchor" href="#_3-volumesnapshot-—-스냅샷-뜨기"><span>3. VolumeSnapshot — 스냅샷 뜨기</span></a></h2><p>운영 중인 볼륨의 특정 시점 상태를 보존하고 싶을 때 <strong>VolumeSnapshot</strong>을 쓴다. 백업, 배포 전 안전점 확보, 데이터 복제(예: 운영 DB를 떠서 스테이징에 붙이기) 같은 데 활용한다. 스냅샷도 CSI 드라이버가 그 기능을 지원해야 동작하며, 클러스터에 external-snapshotter 사이드카와 관련 CRD가 설치돼 있어야 한다.</p><p>스냅샷에는 세 오브젝트가 관여한다. PVC/PV 구조와 닮은꼴이다.</p><ul><li><strong>VolumeSnapshotClass</strong>: 스냅샷을 어떤 드라이버로 어떻게 만들지 (StorageClass에 대응)</li><li><strong>VolumeSnapshot</strong>: 사용자가 내는 스냅샷 요청 (PVC에 대응, 네임스페이스 리소스)</li><li><strong>VolumeSnapshotContent</strong>: 실제로 저장된 스냅샷 (PV에 대응, 클러스터 리소스)</li></ul><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token key atrule">apiVersion</span><span class="token punctuation">:</span> snapshot.storage.k8s.io/v1</span>
<span class="line"><span class="token key atrule">kind</span><span class="token punctuation">:</span> VolumeSnapshotClass</span>
<span class="line"><span class="token key atrule">metadata</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">name</span><span class="token punctuation">:</span> csi<span class="token punctuation">-</span>snapclass</span>
<span class="line"><span class="token key atrule">driver</span><span class="token punctuation">:</span> ebs.csi.aws.com</span>
<span class="line"><span class="token key atrule">deletionPolicy</span><span class="token punctuation">:</span> Retain</span>
<span class="line"><span class="token punctuation">---</span></span>
<span class="line"><span class="token key atrule">apiVersion</span><span class="token punctuation">:</span> snapshot.storage.k8s.io/v1</span>
<span class="line"><span class="token key atrule">kind</span><span class="token punctuation">:</span> VolumeSnapshot</span>
<span class="line"><span class="token key atrule">metadata</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">name</span><span class="token punctuation">:</span> db<span class="token punctuation">-</span>snap<span class="token punctuation">-</span><span class="token datetime number">2026-06-15</span></span>
<span class="line"><span class="token key atrule">spec</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">volumeSnapshotClassName</span><span class="token punctuation">:</span> csi<span class="token punctuation">-</span>snapclass</span>
<span class="line">  <span class="token key atrule">source</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">persistentVolumeClaimName</span><span class="token punctuation">:</span> db<span class="token punctuation">-</span>data</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>status.readyToUse: true</code>가 되면 스냅샷이 완성된 것이다. <code>deletionPolicy</code>는 reclaimPolicy처럼 VolumeSnapshot이 삭제될 때 실제 스냅샷 데이터를 지울지(Delete) 남길지(Retain) 결정한다. 자세한 내용은 <a href="https://kubernetes.io/docs/concepts/storage/volume-snapshots/" target="_blank" rel="noopener noreferrer">Volume Snapshots 문서</a>에 정리돼 있다.</p><h2 id="_4-스냅샷으로부터-복원하기" tabindex="-1"><a class="header-anchor" href="#_4-스냅샷으로부터-복원하기"><span>4. 스냅샷으로부터 복원하기</span></a></h2><p>스냅샷의 진짜 가치는 복원이다. 새 PVC를 만들 때 <code>dataSource</code>로 스냅샷을 가리키면, 그 스냅샷 내용으로 채워진 새 볼륨이 프로비저닝된다.</p><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token key atrule">apiVersion</span><span class="token punctuation">:</span> v1</span>
<span class="line"><span class="token key atrule">kind</span><span class="token punctuation">:</span> PersistentVolumeClaim</span>
<span class="line"><span class="token key atrule">metadata</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">name</span><span class="token punctuation">:</span> db<span class="token punctuation">-</span>data<span class="token punctuation">-</span>restored</span>
<span class="line"><span class="token key atrule">spec</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">storageClassName</span><span class="token punctuation">:</span> fast<span class="token punctuation">-</span>ssd</span>
<span class="line">  <span class="token key atrule">dataSource</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">name</span><span class="token punctuation">:</span> db<span class="token punctuation">-</span>snap<span class="token punctuation">-</span><span class="token datetime number">2026-06-15</span></span>
<span class="line">    <span class="token key atrule">kind</span><span class="token punctuation">:</span> VolumeSnapshot</span>
<span class="line">    <span class="token key atrule">apiGroup</span><span class="token punctuation">:</span> snapshot.storage.k8s.io</span>
<span class="line">  <span class="token key atrule">accessModes</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token punctuation">-</span> ReadWriteOnce</span>
<span class="line">  <span class="token key atrule">resources</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">requests</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token key atrule">storage</span><span class="token punctuation">:</span> 50Gi</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><pre class="mermaid">flowchart LR
    pvc1[&quot;PVC db-data&quot;] -- &quot;source&quot; --&gt; snap[&quot;VolumeSnapshot&quot;]
    snap -- &quot;저장&quot; --&gt; content[&quot;VolumeSnapshotContent&quot;]
    snap -- &quot;dataSource&quot; --&gt; pvc2[&quot;PVC db-data-restored&lt;br&gt;(복원된 새 볼륨)&quot;]
</pre><p>복원 시 주의점이 있다. 복원 PVC의 요청 용량은 원본 스냅샷의 크기 이상이어야 하며, 같은 CSI 드라이버·호환되는 StorageClass라야 한다. 또 스냅샷은 특정 시점의 사본이므로, 데이터베이스라면 스냅샷을 뜨기 전에 정합성(애플리케이션 레벨 quiesce/flush)을 확보해야 복원본이 깨지지 않는다. CSI 스냅샷 자체는 블록 수준 사본일 뿐 애플리케이션 일관성을 보장하지는 않는다.</p><p>비슷한 메커니즘으로 기존 PVC를 직접 <code>dataSource</code>로 지정해 볼륨을 통째 복제(clone)하는 것도 가능하다.</p><h2 id="_5-볼륨-확장-expansion" tabindex="-1"><a class="header-anchor" href="#_5-볼륨-확장-expansion"><span>5. 볼륨 확장(expansion)</span></a></h2><p>운영하다 보면 디스크가 가득 차서 더 큰 용량이 필요해진다. CSI는 무중단에 가까운 <strong>볼륨 확장</strong>을 지원한다(축소는 불가능하다 — 늘리기만 된다).</p><p>전제 조건은 두 가지다. StorageClass에 <code>allowVolumeExpansion: true</code>가 있어야 하고, CSI 드라이버가 확장을 지원해야 한다.</p><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token key atrule">apiVersion</span><span class="token punctuation">:</span> storage.k8s.io/v1</span>
<span class="line"><span class="token key atrule">kind</span><span class="token punctuation">:</span> StorageClass</span>
<span class="line"><span class="token key atrule">metadata</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">name</span><span class="token punctuation">:</span> fast<span class="token punctuation">-</span>ssd</span>
<span class="line"><span class="token key atrule">provisioner</span><span class="token punctuation">:</span> ebs.csi.aws.com</span>
<span class="line"><span class="token key atrule">allowVolumeExpansion</span><span class="token punctuation">:</span> <span class="token boolean important">true</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>확장은 PVC의 요청 용량을 키우는 것으로 트리거한다.</p><div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre><code><span class="line">kubectl patch pvc db-data <span class="token punctuation">\\</span></span>
<span class="line">  <span class="token parameter variable">-p</span> <span class="token string">&#39;{&quot;spec&quot;:{&quot;resources&quot;:{&quot;requests&quot;:{&quot;storage&quot;:&quot;100Gi&quot;}}}}&#39;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><p>이후 일어나는 일은 두 단계다.</p><pre class="mermaid">sequenceDiagram
    participant U as 사용자
    participant API as kube-apiserver
    participant R as external-resizer
    participant D as CSI Controller
    participant K as kubelet
    U-&gt;&gt;API: PVC requests.storage 50Gi → 100Gi
    R-&gt;&gt;API: PVC watch → 확장 필요 감지
    R-&gt;&gt;D: ControllerExpandVolume (블록 디바이스 확장)
    D--&gt;&gt;R: 디바이스는 커짐
    Note over API: 파일시스템은 아직 50Gi
    K-&gt;&gt;K: NodeExpandVolume (파일시스템 resize)
    K--&gt;&gt;API: PVC status.capacity = 100Gi
</pre><p>블록 디바이스를 키운 뒤, 파일시스템까지 늘려야 실제로 공간이 보인다. 대부분의 CSI 드라이버는 파일시스템 확장을 위해 Pod 재시작 없이 노드에서 온라인으로 처리하지만, 일부 환경에서는 Pod 재시작이 필요할 수 있다. PVC의 <code>status.capacity</code>가 새 값으로 바뀌면 확장이 끝난 것이다. 상세 조건은 <a href="https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims" target="_blank" rel="noopener noreferrer">Expanding Persistent Volumes Claims 문서</a>를 참고한다.</p><div class="hint-container warning"><p class="hint-container-title">확장은 비가역</p><p>볼륨은 늘릴 수만 있고 줄일 수 없다. 너무 크게 잡으면 클라우드 비용이 그대로 누적되므로, 필요한 만큼 단계적으로 키우는 편이 안전하다.</p></div><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CSI는 스토리지 벤더 코드를 쿠버네티스 본체 밖으로 분리한 표준 gRPC 인터페이스로, Identity·Controller·Node 서비스로 구성된다.</li><li>external-provisioner 등 사이드카가 쿠버네티스 오브젝트를 감시하다 적절한 시점에 벤더 드라이버를 호출한다.</li><li>동적 프로비저닝은 provision(디스크 생성·PV 바인딩)과 attach/mount(노드에 마운트) 두 단계로 나뉜다.</li><li>VolumeSnapshot은 VolumeSnapshotClass·VolumeSnapshot·VolumeSnapshotContent로 구성되며, dataSource로 복원·복제할 수 있다.</li><li>볼륨 확장은 allowVolumeExpansion과 드라이버 지원이 전제이고, 블록 디바이스→파일시스템 두 단계로 진행되며 축소는 불가능하다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p>지금까지 스토리지를 동적으로 만들고 스냅샷·확장하는 메커니즘을 봤다. 이제 이 영속 스토리지를 데이터베이스 같은 스테이트풀 애플리케이션에 어떻게 결합하는지가 남았다. 다음 챕터 <a href="/study/kubernetes/32-statefulset-storage">StatefulSet 스토리지 패턴</a>에서는 volumeClaimTemplates로 Pod마다 안정적인 스토리지를 주는 방법과 스테이트풀 앱 배포·스케일·백업 패턴을 다룬다.</p>`,40)]))}const c=n(l,[["render",p],["__file","31-csi-snapshot.html.vue"]]),r=JSON.parse('{"path":"/study/kubernetes/31-csi-snapshot.html","title":"CSI와 동적 프로비저닝","lang":"en-US","frontmatter":{"title":"CSI와 동적 프로비저닝","description":"스토리지 벤더를 쿠버네티스 코드 밖으로 분리한 CSI(Container Storage Interface) 아키텍처, PVC 한 장으로 디스크가 자동 생성되는 동적 프로비저닝의 내부 흐름, VolumeSnapshot으로 스냅샷을 뜨고 복원하는 방법, 그리고 운영 중 볼륨을 무중단 확장하는 방법까지 깊게 다룬다.","date":"2026-06-15T00:00:00.000Z","tags":["Kubernetes","CSI","Dynamic Provisioning","VolumeSnapshot","Volume Expansion","Storage"],"prev":"/study/kubernetes/30-volume-pv-pvc","next":"/study/kubernetes/32-statefulset-storage"},"headers":[{"level":1,"title":"CSI와 동적 프로비저닝","slug":"csi와-동적-프로비저닝","link":"#csi와-동적-프로비저닝","children":[{"level":2,"title":"1. CSI는 왜 등장했나","slug":"_1-csi는-왜-등장했나","link":"#_1-csi는-왜-등장했나","children":[]},{"level":2,"title":"2. 동적 프로비저닝의 흐름","slug":"_2-동적-프로비저닝의-흐름","link":"#_2-동적-프로비저닝의-흐름","children":[]},{"level":2,"title":"3. VolumeSnapshot — 스냅샷 뜨기","slug":"_3-volumesnapshot-—-스냅샷-뜨기","link":"#_3-volumesnapshot-—-스냅샷-뜨기","children":[]},{"level":2,"title":"4. 스냅샷으로부터 복원하기","slug":"_4-스냅샷으로부터-복원하기","link":"#_4-스냅샷으로부터-복원하기","children":[]},{"level":2,"title":"5. 볼륨 확장(expansion)","slug":"_5-볼륨-확장-expansion","link":"#_5-볼륨-확장-expansion","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/kubernetes/31-csi-snapshot.md"}');export{c as comp,r as data};
