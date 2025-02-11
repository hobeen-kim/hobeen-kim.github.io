import{_ as i,c as t,a,b as p,d as r,r as n,o as d}from"./app-B-vOc4-r.js";const c="/images/2025-02-11-kafka/image-20250211221713862.png",o="/images/2025-02-11-kafka/image-20250211221921990.png",m={};function v(h,e){const s=n("Header"),l=n("description");return d(),t("div",null,[a(s),e[0]||(e[0]=p("p",null,"카프카는 디커플링, 큐, 로그 시스템, pub/sub, 빅데이터 처리 등등 다재다능하게 사용된다. 특히 카프카를 설명할 수 있는 단어는 '안정적인 운영'과 '빠른 확장성'이다. 이러한 특성때문에 의외로 스타트업에서 많이 사용된다. 빠른 성장 속에서도 데이터 관련 작업을 안정적으로 할 수 있기 때문이다. 스타트업 개발자든, 대기업 개발자든 카프카는 이제 필수이다.",-1)),a(l),e[1]||(e[1]=r(`<blockquote><p>[!NOTE]<br> 책 전체가 아닌 필요한 부분만 정리함</p></blockquote><h1 id="_1-카프카가-데이터를-저장하는-방법" tabindex="-1"><a class="header-anchor" href="#_1-카프카가-데이터를-저장하는-방법"><span>1. 카프카가 데이터를 저장하는 방법</span></a></h1><p>카프카는 프로듀서에게 데이터를 전달받아 파티션에 데이터를 저장한다. 이때 전달받은 데이터는 파일 시스템에 저장된다.</p><p>파일은 config/server.properties 의 log.dir 옵션에 정의한 디렉토리에 저장된다. 그리고 토픽이름과 파티션 번호의 조합으로 하위 디렉토리를 생성하여 데이터를 저장한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">tmp/</span>
<span class="line"> ㄴ kafka-logs/</span>
<span class="line">    ㄴ hello.kafka-1/</span>
<span class="line">       ㄴ 00000000000000000000.index</span>
<span class="line">       ㄴ 00000000000000000000.log</span>
<span class="line">       ㄴ 00000000000000000000.timeindex</span>
<span class="line">       ㄴ partition.metadata</span>
<span class="line">       ㄴ leader-epoch-checkpoint</span>
<span class="line">    ㄴ hello.kafka-2/</span>
<span class="line">       ㄴ ...</span>
<span class="line">       ㄴ ...</span>
<span class="line">    ㄴ hello.kafka-3/</span>
<span class="line">       ㄴ ...</span>
<span class="line">       ㄴ ...</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><ul><li>index : 메시지의 오프셋을 인덱싱한 정보를 담은 파일</li><li>log : 메시지와 메타데이터</li><li>timeindex : 메시지에 포함된 timestamp 값을 기준으로 인덕싱한 정보가 담겨있음</li></ul><h2 id="_1-1-파일에-저장하면-느리지-않을까" tabindex="-1"><a class="header-anchor" href="#_1-1-파일에-저장하면-느리지-않을까"><span>1.1 파일에 저장하면 느리지 않을까?</span></a></h2><p>카프카는 데이터를 메모리나 데이터베이스에 저장하지 않고 파일에 직접 저장한다. 하지만 파일 입출력으로 인한 속도 이슈가 발생하지 않는다.</p><p>그 이유는 <strong>페이지 캐시를 사용하여 디스크 입출력 속도를 높였기 때문</strong>이다. 페이지 캐시란 OS 에서 파일 입출력의 성능 향상을 위해 만들어 놓은 메모리 영역이다. 한번 읽은 파일의 내용은 메모리의 페이지 캐시에 저장되고, 추후 동일한 파일의 접근이 일어나면 디스크에서 읽지 않고 메모리에서 직접 읽는다.</p><h2 id="_1-2-데이터-복제" tabindex="-1"><a class="header-anchor" href="#_1-2-데이터-복제"><span>1.2 데이터 복제</span></a></h2><p>카프카는 데이터를 다른 브로커에도 저장하여 장애에 대응한다. 카프카의 복제는 파티션 단위로 이루어진다. 같은 토픽의 파티션이라도 리 브로커가 다를 수 있다.</p><p><img src="`+c+'" alt="image-20250211221713862"></p><p>복제된 파티션은 리더와 팔로워로 구성된다. 팔로워 파티션은 리더 파티션과 오프셋이 차이날 경우 데이터를 가져온다. (복제, replication)</p><p>만약 리더 파티션을 가진 브로커에서 장애가 발생하면 팔로워 파티션 중 하나가 리더 파티션 지위를 넘겨받는다.</p><p><img src="'+o+'" alt="image-20250211221921990"></p><h2 id="_1-3-데이터-삭제" tabindex="-1"><a class="header-anchor" href="#_1-3-데이터-삭제"><span>1.3 데이터 삭제</span></a></h2><p>카프카는 파일 단위(세그먼트)로 삭제가 이루어진다. 그리고 오직 브로커만 파일을 삭제할 수 있고 컨슈머나 프로듀서에서는 삭제할 수 없다.</p><p>세그먼트는 log.segment.bytes 또는 log.segment.ms 옵션값을 통해 닫힌다. 기본값은 1GB 이다.</p><p>닫힌 세그먼트 파일은 log.retention.bytes 또는 log.retention.ms 옵션의 설정값으로 체크되어 삭제된다.</p>',19))])}const g=i(m,[["render",v],["__file","2025-02-11-kafka.html.vue"]]),_=JSON.parse('{"path":"/books/all/2025-02-11-kafka.html","title":"데브원영님의 카프카 바이블","lang":"en-US","frontmatter":{"title":"데브원영님의 카프카 바이블","bookName":"아파치 카프카 애플리케이션 프로그래밍","author":"최원영","date":"2025-02-11T00:00:00.000Z","tags":["카프카"]},"headers":[{"level":1,"title":"1. 카프카가 데이터를 저장하는 방법","slug":"_1-카프카가-데이터를-저장하는-방법","link":"#_1-카프카가-데이터를-저장하는-방법","children":[{"level":2,"title":"1.1 파일에 저장하면 느리지 않을까?","slug":"_1-1-파일에-저장하면-느리지-않을까","link":"#_1-1-파일에-저장하면-느리지-않을까","children":[]},{"level":2,"title":"1.2 데이터 복제","slug":"_1-2-데이터-복제","link":"#_1-2-데이터-복제","children":[]},{"level":2,"title":"1.3 데이터 삭제","slug":"_1-3-데이터-삭제","link":"#_1-3-데이터-삭제","children":[]}]}],"git":{},"filePathRelative":"_books/all/2025-02-11-kafka.md"}');export{g as comp,_ as data};
