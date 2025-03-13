import{_ as p,c as d,b as l,d as o,a,f as t,r as i,o as u,e as n}from"./app-Tj2laqPB.js";const m={},c={class:"table-of-contents"};function v(h,e){const s=i("router-link"),r=i("Footer");return u(),d("div",null,[l("nav",c,[l("ul",null,[l("li",null,[a(s,{to:"#_1-sam"},{default:t(()=>e[0]||(e[0]=[n("1. SAM")])),_:1}),l("ul",null,[l("li",null,[a(s,{to:"#문제점-1-여러-환경을-관리해야-함"},{default:t(()=>e[1]||(e[1]=[n("문제점 1 : 여러 환경을 관리해야 함")])),_:1})]),l("li",null,[a(s,{to:"#문제점-2-공통-코드와-변수의-일관성-유지-및-관리의-어려움"},{default:t(()=>e[2]||(e[2]=[n("문제점 2 : 공통 코드와 변수의 일관성 유지 및 관리의 어려움")])),_:1})]),l("li",null,[a(s,{to:"#문제점-3-코드버전-관리-배포-어려움"},{default:t(()=>e[3]||(e[3]=[n("문제점 3 : 코드버전 관리 & 배포 어려움")])),_:1})])])]),l("li",null,[a(s,{to:"#_2-서버리스를-활용해-서버-개발자-1명으로-mau-10만-서비스-운영하기"},{default:t(()=>e[4]||(e[4]=[n("2. 서버리스를 활용해 서버 개발자 1명으로 MAU 10만 서비스 운영하기")])),_:1})])])]),e[5]||(e[5]=o(`<p>이번 세션에서는 2가지에 대해 말했는데, 두번째 세션은 다른 회사의 발전기를 듣는 정도였다. 첫번째 AWS SAM 은 나도 주로 사용하는거라 재밌게 들었다. 크게 특별한 점은 없었지만 lambda layer 를 통해서 ssm parameter store 를 읽어온다는 건 흥미로웠다. 어쨌든 다른 사람의 의견을 들을 수 있는 좋은 자리였다.</p><h1 id="_1-sam" tabindex="-1"><a class="header-anchor" href="#_1-sam"><span>1. SAM</span></a></h1><p>AWS 의 serverless 서비스를 단순히 콘솔을 통해 사용한다면 운영/배포, 인프라 관리가 어려울 수밖에 없다. 이런 문제를 해결하기 위해 IaC 중 하나인 AWS SAM 을 사용할 수 있다.</p><p>AWS SAM(Serverless Application Model)은 코드를 사용해 서버리스 애플리케이션을 빌드하기 위한 오픈 소스 프레임워크다. 나도 Lambda, API Gateway, SQS, SNS 등을 통합하여 사용하면서 많이 이용했다. 특히 각 서비스 간에 권한을 통한 의존 관계를 명확히 하는 데 유용했다.</p><p>이번 세션에서는 아래와 같은 서버리스의 3가지 문제에 대해 SAM 에 해답이 있다고 했다.</p><h2 id="문제점-1-여러-환경을-관리해야-함" tabindex="-1"><a class="header-anchor" href="#문제점-1-여러-환경을-관리해야-함"><span>문제점 1 : 여러 환경을 관리해야 함</span></a></h2><p>lambda 가 일정 개수 이상이 배포되면 dev, prod 환경을 관리하기가 어려워진다. 하지만 SAM 은 code 로 배포하는 것이니만큼 변수 설정으로 관리할 수 있다.</p><ul><li><p>template.yaml</p><ul><li>CloudFormation 템플릿의 일종으로, 서버리스 애플리케이션 리소스를 정의할 수 있다. <ul><li>AWS::Serverless::Function 등등 ...</li></ul></li></ul></li><li><p>samconfig.toml</p><ul><li><p>SAM CLI 명령어의 기본 구성을 저장</p></li><li><p>Sam build, deploy 에 필요한 설정을 넣어둘 수 있다.</p></li><li><p>template.yaml 에 있는 파라미터를 오버라이딩할 수 있다.</p><ul><li><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">parameter_overrides = [&quot;Environment dev&quot;]</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div></li></ul></li><li><p>template.yaml 에서는 이렇게 사용</p><ul><li><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">FunctionName: !Sub &quot;\${Environment}-test&quot;</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div></li></ul></li></ul></li></ul><h2 id="문제점-2-공통-코드와-변수의-일관성-유지-및-관리의-어려움" tabindex="-1"><a class="header-anchor" href="#문제점-2-공통-코드와-변수의-일관성-유지-및-관리의-어려움"><span>문제점 2 : 공통 코드와 변수의 일관성 유지 및 관리의 어려움</span></a></h2><ul><li>여러 개의 람다가 사용하는 환경변수 관리 어려움</li><li>도메인 모델, 툴과 같은 코드 중복으로 인한 재사용성 저하</li></ul><p>이를 중앙에서 관리하고자 SSM Parameter Store 사용한다. SSM Parameter Store 는 CloudFormation, Lambda, EC2 등 다른 AWS 서비스와 쉽게 통합가능하다.</p><p><strong>사용방법</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Environment:</span>
<span class="line">  Variables:</span>
<span class="line">   ENV: !Ref Environment</span>
<span class="line">   DB_URL: !Sub {{resolve:ssm:경로}}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>단점</strong></p><ul><li>환경변수 변경 후 해당하는 모든 람다를 재배포해야하는 단점</li><li>람다 layer 를 사용하면 좋지 않을까?</li></ul><p><strong>Lambda layer</strong></p><p>람다 레이어 내의 공유 라이브러리에 get_ssm_parameter() 메서드만 넣으면 됨. 람다가 호출될 때 get_ssm_parameter() 를 호출하면서 parameter 를 ssm 에서 가져오게 됨</p><blockquote><p>나의 생각</p><p>ssm parameter 를 사용할 때 다음과 같은 고민을 해야할 것 같다.</p><ul><li>최초 get_ssm_parameter 호출 시 지연이 발생한다면?</li><li>(그럴 일은 없곘지만) parameter store 가 정상적으로 작동하지 않을 땐?</li><li>parameter store 에 없는 값을 가져올 땐?</li></ul></blockquote><h2 id="문제점-3-코드버전-관리-배포-어려움" tabindex="-1"><a class="header-anchor" href="#문제점-3-코드버전-관리-배포-어려움"><span>문제점 3 : 코드버전 관리 &amp; 배포 어려움</span></a></h2><ul><li><p>github action 과 통합해서 CI/CD 를 구성함</p></li><li><p>카나리아/리니어 배포를 IsProd 일때만 적용함</p><ul><li><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">DeploymentPreference:</span>
<span class="line"> - Type:</span>
<span class="line">   - !If [IsProd, (prod 일 때), (아닐 때)]</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></li></ul></li></ul><h1 id="_2-서버리스를-활용해-서버-개발자-1명으로-mau-10만-서비스-운영하기" tabindex="-1"><a class="header-anchor" href="#_2-서버리스를-활용해-서버-개발자-1명으로-mau-10만-서비스-운영하기"><span>2. 서버리스를 활용해 서버 개발자 1명으로 MAU 10만 서비스 운영하기</span></a></h1><p><em><strong>썰 중심이다.</strong></em></p><p>발표자는 &#39;맞춤분양&#39;이라는 서비스를 하면서 혼자서 2년 동안 MAU 10만 명 서비스를 만들어온 개발자라고 한다. &#39;맞춤분양&#39;은 분양을 세부적으로 필터링할 수 있는 서비스다. 처음 배포는 aws Lambda 에 직접 zip 파일을 올리는 식으로 했다고 한다... 이후에는 servless framework 로 로컬에서 deploy 를 진행했다.</p><p>이후에 시드 투자를 받을 떄는 AWS Fargate 를 사용했다. Github action 으로 배포하려면 무료 배포시간이 부족해서 dockerize 로 우선 ECR 로 보낸다. 그리고 Fargate 에서 최종적인 배포를 했다. 15만원 정도 월비용이 나왔는데 cloudwatch 비용이 가장 많았다고 한다.</p><p>최종적으로는 지금 AWS App Runner 를 사용한다. Aurora 도 Cluster 로 대응할 정도의 트래픽이 아니라서 Serverless 를 사용한다. Serverless 를 사용할 때는 비용을 가장 많이 고려했다고 한다.</p>`,25)),a(r)])}const b=p(m,[["render",v],["__file","2025-02-25-aws.html.vue"]]),g=JSON.parse('{"path":"/posts/cloud/2025-02-25-aws.html","title":"[AWSKRUG] AWS Serverless Meetup (센터필드)","lang":"en-US","frontmatter":{"title":"[AWSKRUG] AWS Serverless Meetup (센터필드)","date":"2025-02-25T00:00:00.000Z","tags":["sam","aws"],"description":"AWSKRUG 서버리스 모임에 다녀온 후기와 요약"},"headers":[{"level":1,"title":"1. SAM","slug":"_1-sam","link":"#_1-sam","children":[{"level":2,"title":"문제점 1 : 여러 환경을 관리해야 함","slug":"문제점-1-여러-환경을-관리해야-함","link":"#문제점-1-여러-환경을-관리해야-함","children":[]},{"level":2,"title":"문제점 2 : 공통 코드와 변수의 일관성 유지 및 관리의 어려움","slug":"문제점-2-공통-코드와-변수의-일관성-유지-및-관리의-어려움","link":"#문제점-2-공통-코드와-변수의-일관성-유지-및-관리의-어려움","children":[]},{"level":2,"title":"문제점 3 : 코드버전 관리 & 배포 어려움","slug":"문제점-3-코드버전-관리-배포-어려움","link":"#문제점-3-코드버전-관리-배포-어려움","children":[]}]},{"level":1,"title":"2. 서버리스를 활용해 서버 개발자 1명으로 MAU 10만 서비스 운영하기","slug":"_2-서버리스를-활용해-서버-개발자-1명으로-mau-10만-서비스-운영하기","link":"#_2-서버리스를-활용해-서버-개발자-1명으로-mau-10만-서비스-운영하기","children":[]}],"git":{},"filePathRelative":"_posts/cloud/2025-02-25-aws.md"}');export{b as comp,g as data};
