import{_ as t,c as r,a as n,b as d,d as c,r as e,o as p}from"./app-GZaBdJFr.js";const u="/images/2025-03-08-terraform/image-20250309222039484.png",o="/images/2025-03-08-terraform/image-20250310233826614.png",v={};function m(b,s){const a=e("Header"),l=e("description"),i=e("Footer");return p(),r("div",null,[n(a),s[0]||(s[0]=d("p",null,"처음 AWS 를 배울 때 클라우드는 나에게 미지의 영역이었고 깊은 안개 속에 있었다. 그런 점에서 테라폼을 처음 접했을 때는 놀라웠다. 잘 작성된 tf 파일 하나면 aws 콘솔에 접근할 필요없이 몇 분이면 서버와 애플리케이션을 배포할 수 있다. 테라폼을 깊게 배워서 업무에 적용하고 싶다는 생각이 강하게 들었고 지금도 조금씩 배우며 적용하고 있다.",-1)),n(l),s[1]||(s[1]=c(`<blockquote><p>[!NOTE]<br> 책 전체가 아닌 필요한(모르는) 부분만 정리함</p></blockquote><h1 id="iac-와-테라폼" tabindex="-1"><a class="header-anchor" href="#iac-와-테라폼"><span>IaC 와 테라폼</span></a></h1><p>IaC 도입의 긍정적인 측면은 다음과 같다.</p><ul><li>속도와 효율성</li><li>버전 관리</li><li>협업</li><li>재사용성</li><li>기술의 자산화</li></ul><h1 id="기본-사용법" tabindex="-1"><a class="header-anchor" href="#기본-사용법"><span>기본 사용법</span></a></h1><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">resource &quot;local_file&quot; &quot;abc&quot; {</span>
<span class="line">    content = &quot;Hello, World!&quot;</span>
<span class="line">    filename = &quot;\${path.module}/hello.txt&quot;</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><ul><li>리소스 삭제 후 생성 (대체) <ul><li><code>terraform apply -replace=local_file.abc</code></li></ul></li><li>승인 절차 없는 apply <ul><li><code>terraform apply --auto-approve</code></li></ul></li><li>lifecycle 종류 <ul><li>create_before_destory (bool) : 리소스 수정 시 신규 리소스를 우선 생성하고 기존 리소스 삭제</li><li>prevent_destroy (bool) : 해당 리소스를 삭제하려 할 때 명시적으로 거부(오류)</li><li>ignore_changes (list) : 리소스 요소에 선언된 인수의 변경사항을 테라폼 실행 시 무시</li><li>precondition : 리소스 요소에 선언된 인수의 조건을 검증</li><li>postcondition : Plan 과 Apply 이후의 결과를 속성 값으로 검증</li></ul></li></ul><h2 id="variable" tabindex="-1"><a class="header-anchor" href="#variable"><span>Variable</span></a></h2><h3 id="validation" tabindex="-1"><a class="header-anchor" href="#validation"><span>validation</span></a></h3><p>변수는 validation 으로 유효성을 검사할 수 있다. 중복으로 선언 가능하다.</p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">variable &quot;image_id&quot; {</span>
<span class="line">  type        = string</span>
<span class="line">  description = &quot;The ID of the AMI to use for the instance&quot;</span>
<span class="line">  default     = &quot;ami-0c55b159cbfafe1f0&quot;</span>
<span class="line"></span>
<span class="line">  validation {</span>
<span class="line">    condition     = length(var.image_id) &gt; 4</span>
<span class="line">    error_message = &quot;The image ID must be at least 4 characters long.&quot;</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  validation {</span>
<span class="line">    condition     = can(regex(&quot;^ami-&quot;, var.image_id))</span>
<span class="line">    error_message = &quot;The image ID must start with &#39;ami-&#39;.&quot;</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="변수-우선-순위" tabindex="-1"><a class="header-anchor" href="#변수-우선-순위"><span>변수 우선 순위</span></a></h3><p>숫자가 클수록 우선순위가 높음</p><ol><li><p>실행 후 입력 (변수에 값이 선언되지 않ㅇ나 cli 에서 입력)</p></li><li><p>variable 블록의 default 값</p></li><li><p>환경변수 (TF_VAR_변수명)</p></li><li><p>terraform.tfvars 에 정의된 변수</p></li><li><p>*.auto.tfvars 에 정의된 변수</p></li><li><p>*.auto.tfvars.json 에 정의된 변수</p></li><li><p>CLI 실행 시 -var 인수 지정 또는 -var-file 지정</p><ul><li><p>terraform plan -var=&quot;my_var=var&quot; -var-file=&quot;var9.txt&quot;</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">//var9.txt</span>
<span class="line">my_var = &quot;var9&quot;  </span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div></li></ul></li></ol><h2 id="local" tabindex="-1"><a class="header-anchor" href="#local"><span>local</span></a></h2><p>local 값은 외부에서 입력되지 않고 코드 내에서만 가공되고 동작한다. 선언된 모듈 내에서만 접근 가능하다.</p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">variable &quot;prefix&quot; {</span>
<span class="line">    default = &quot;hello&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">locals {</span>
<span class="line">    name = &quot;terraform&quot;</span>
<span class="line">    content = &quot;\${var.prefix}-\${local.name}&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">resource &quot;local_file&quot; &quot;local_file&quot; {</span>
<span class="line">    content = local.content</span>
<span class="line">    filename = &quot;\${path.module}/hellolocal.txt&quot;</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="output" tabindex="-1"><a class="header-anchor" href="#output"><span>output</span></a></h2><p>자바의 getter 와 비슷한 역할로 모듈의 인터페이스다. 출력 값의 용도는 다음과 같다.</p><ul><li>루트 모듈에서 사용자가 확인하고 하는 특정 속성 출력</li><li>잣기 모듈의 특정 값을 정의하고 루트 모듈에서 결과를 참조</li><li>서로 다른 루트 모듈의 결과를 원격으로 읽기 위한 접근 요소</li></ul><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">resource &quot;local_file&quot; &quot;abcd&quot; {</span>
<span class="line">    content = &quot;hello&quot;</span>
<span class="line">    filename = &quot;\${path.module}/abcd.txt&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;abcd_content&quot; {</span>
<span class="line">    value = local_file.abcd.content</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;abcd_abspath&quot; {</span>
<span class="line">    value = abspath(local_file.abcd.filename)</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;abcd_id&quot; {</span>
<span class="line">    value = local_file.abcd.id</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="for" tabindex="-1"><a class="header-anchor" href="#for"><span>for</span></a></h2><p>for 구문의 규칙</p><ul><li>list 는 반환 받는 값이 하나로 되어있으면 값을, 두 개인 경우 앞의 인수가 인덱스를 반환하고 뒤의 인수가 값을 반환 (관용적으로 i, v)</li><li>map 유형은 반환받는 값이 하나로 되어있으면 키를, 두 개인 경우 앞의 인수가 키, 뒤의 인수가 값을 반환 (관용적으로 k, v)</li><li>결과 값은 for 문을 묶는 기회가 [ ] 인 경우 tuple 로 반환되고 { } 인 경우 object 형태로 반환</li><li>object 형태의 경우 키 값에 대한 쌍은 =&gt; 기호로 구분</li><li>{ } 형식을 사용해 object 형태로 결과를 반환하는 경우 키 값은 고유해야 하므로 값 뒤에 그룹화 모드 심볼 (...)을 붙여서 키의 중복을 방지</li><li>if 구문을 추가해 조건 부여 가능</li></ul><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">variable &quot;names&quot; {</span>
<span class="line">    type = list(string)</span>
<span class="line">    default = [&quot;alice&quot;, &quot;bob&quot;, &quot;charlie&quot;]</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;A_uuper_values&quot; {</span>
<span class="line">    value = [for v in var.names : upper(v)]</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;B_index_and_value&quot; {</span>
<span class="line">    value = [for i, v in var.names : &quot;\${i} : \${v}&quot;]</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;C_make_object&quot; {</span>
<span class="line">    value = {for v in var.names : v =&gt; upper(v)}</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;D_with_filter&quot; {</span>
<span class="line">    value = {for v in var.names : v =&gt; upper(v) if v != &quot;bob&quot;}</span>
<span class="line">}</span>
<span class="line">  </span>
<span class="line">variable &quot;members&quot; {</span>
<span class="line">  type = map(object({</span>
<span class="line">      role = string</span>
<span class="line">      age = number</span>
<span class="line">  }))</span>
<span class="line">  default = {</span>
<span class="line">      alice = {role = &quot;admin&quot;, age = 20}</span>
<span class="line">      bob = {role = &quot;user&quot;, age = 25}</span>
<span class="line">      charlie = {role = &quot;user&quot;, age = 30}</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;E_to_tuple&quot; {</span>
<span class="line">    value = [for k, v in var.members : &quot;\${k} : \${v.role}&quot;]</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;F_get_only_role&quot; {</span>
<span class="line">    value = {</span>
<span class="line">        for name, user in var.members : name =&gt; user.role</span>
<span class="line">        if user.role == &quot;admin&quot;</span>
<span class="line">    }</span>
<span class="line">}</span>
<span class="line">  </span>
<span class="line"># output</span>
<span class="line">A_uuper_values = [</span>
<span class="line">  &quot;ALICE&quot;,</span>
<span class="line">  &quot;BOB&quot;,</span>
<span class="line">  &quot;CHARLIE&quot;,</span>
<span class="line">]</span>
<span class="line">B_index_and_value = [</span>
<span class="line">  &quot;0 : alice&quot;,</span>
<span class="line">  &quot;1 : bob&quot;,</span>
<span class="line">  &quot;2 : charlie&quot;,</span>
<span class="line">]</span>
<span class="line">C_make_object = {</span>
<span class="line">  &quot;alice&quot; = &quot;ALICE&quot;</span>
<span class="line">  &quot;bob&quot; = &quot;BOB&quot;</span>
<span class="line">  &quot;charlie&quot; = &quot;CHARLIE&quot;</span>
<span class="line">}</span>
<span class="line">D_with_filter = {</span>
<span class="line">  &quot;alice&quot; = &quot;ALICE&quot;</span>
<span class="line">  &quot;charlie&quot; = &quot;CHARLIE&quot;</span>
<span class="line">}</span>
<span class="line">E_to_tuple = [</span>
<span class="line">&quot;alice : admin&quot;,</span>
<span class="line">&quot;bob : user&quot;,</span>
<span class="line">&quot;charlie : user&quot;,</span>
<span class="line">]</span>
<span class="line">F_get_only_role = {</span>
<span class="line">&quot;alice&quot; = &quot;admin&quot;</span>
<span class="line">}</span>
<span class="line">G_age = {</span>
<span class="line">&quot;admin&quot; = [</span>
<span class="line">  &quot;alice&quot;,</span>
<span class="line">]</span>
<span class="line">&quot;user&quot; = [</span>
<span class="line">    &quot;bob&quot;,</span>
<span class="line">    &quot;charlie&quot;,</span>
<span class="line">  ]</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="함수" tabindex="-1"><a class="header-anchor" href="#함수"><span>함수</span></a></h2><p><code>terraform console</code> 명령어로 함수의 동작을 콘솔로 테스트할 수 있다.</p><h2 id="프로비저너" tabindex="-1"><a class="header-anchor" href="#프로비저너"><span>프로비저너</span></a></h2><p>프로바이더로 실행되지 않는 커맨드와 파일 복사같은 역할을 수행한다. 종류로는 file, local-exec, remote-exec 가 있다.</p><h2 id="moved" tabindex="-1"><a class="header-anchor" href="#moved"><span>Moved</span></a></h2><p>테라폼의 state 에서 리소스 주소의 이름이 변경되면 기존 리소스는 삭제되고 새로운 리소스가 생성된다. 하지만 리소스 이름을 변경하면서 프로비저닝된 환경을 그대로 유지하고자 하면 moved 블록을 사용하면 된다.</p><p><strong>기존 코드</strong></p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">resource &quot;local_file&quot; &quot;moved_file&quot; {</span>
<span class="line">    content = &quot;moved&quot;</span>
<span class="line">    filename = &quot;\${path.module}/moved.txt&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;moved_file_content&quot; {</span>
<span class="line">    value = local_file.moved_file.content</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>변경 코드</strong></p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">resource &quot;local_file&quot; &quot;moved_file_b&quot; {</span>
<span class="line">    content = &quot;moved&quot;</span>
<span class="line">    filename = &quot;\${path.module}/moved.txt&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">moved {</span>
<span class="line">    from = local_file.moved_file</span>
<span class="line">    to = local_file.moved_file_b</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;moved_file_content&quot; {</span>
<span class="line">    value = local_file.moved_file_b.content</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h1 id="프로바이더" tabindex="-1"><a class="header-anchor" href="#프로바이더"><span>프로바이더</span></a></h1><h2 id="프로바이더의-다중-정의" tabindex="-1"><a class="header-anchor" href="#프로바이더의-다중-정의"><span>프로바이더의 다중 정의</span></a></h2><p>동일한 프로바이더를 사용하지만 다른 조건을 갖는 경우 아래와 같이 alias 를 사용할 수 있다.</p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">provider &quot;aws&quot; {</span>
<span class="line">    region = &quot;us-east-1&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">provider &quot;aws&quot; {</span>
<span class="line">    alias = &quot;seoul&quot;</span>
<span class="line">    region = &quot;ap-northeast-2&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">resource &quot;aws_instance&quot; &quot;example&quot; {</span>
<span class="line">    provider = aws.seoul</span>
<span class="line">    ami = &quot;ami-0c55b159cbfafe1f0&quot;</span>
<span class="line">    instance_type = &quot;t2.micro&quot;</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h1 id="state" tabindex="-1"><a class="header-anchor" href="#state"><span>State</span></a></h1><h2 id="워크스페이스" tabindex="-1"><a class="header-anchor" href="#워크스페이스"><span>워크스페이스</span></a></h2><p>state 를 관리하는 논리적인 가상 공간이다. 테라폼 구성 파일은 동일하지만 작업자는 서로 다른 state 를 갖는 실제 대상을 프로비저닝할 수 있다.</p><p><img src="`+u+`" alt="image-20250309222039484"></p><p>terraform workspace list 로 워크스페이스의 목록을 볼 수 있다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">$ terraform workspace list</span>
<span class="line">* default</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><p>아래 리소스를 배포하면 default 워크스페이스에 배포된다.</p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">resource &quot;aws_instance&quot; &quot;example&quot; {</span>
<span class="line">    provider = aws.seoul</span>
<span class="line">    ami = &quot;ami-08d0e13d30abef253&quot;</span>
<span class="line">    instance_type = &quot;t2.micro&quot;</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>그리고 terraform workspace new &lt;워크스페이스이름&gt; 명령으로 새로운 워크스페이스를 생성한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">$ terraform workspace new myworkspace1</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div><p>새로운 워크스페이스가 생성되면 루트 모듈 디렉토리에 terraform.tfstate.d 디렉토리가 생성되고 하위에 myworkspace1 이 생긴다. 현재 사용 중인 워크스페이스는 show 로 확인할 수 있다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">$ terraform workspace show</span>
<span class="line">myworkspace1</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><p>이 상태에서 plan, apply 는 새로운 리소스를 생성한다. 그리고 워크스페이스를 리소스 블록 내에서 읽을 수 있다. 아래는 workspace 가 default 일 때 5개, 아닐 때 1개만 배포하는 구성이다.</p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">resource &quot;aws_instance&quot; &quot;example&quot; {</span>
<span class="line">    count = &quot;\${terraform.workspace == &quot;default&quot; ? 5: 1}&quot;</span>
<span class="line">    provider = aws.seoul</span>
<span class="line">    ami = &quot;ami-08d0e13d30abef253&quot;</span>
<span class="line">    instance_type = &quot;t2.micro&quot;</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>다시 워크스페이스를 변경하려면 아래와 같이 바꾼다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">$ terraform workspace select default</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div><p>apply, plan 시점에서 state 를 지정하려면 아래와 같이 state 파일을 지정한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">terraform destroy -state=terraform.tfstate.d/myworkspace1/terraform.tfstate</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div><p>워크스페이스를 사용하는 장단점은 다음과 같다.</p><p><strong>장점</strong></p><ul><li>하나의 루트 모듈에서 다른 환경을 위한 리소스를 동일한 테라폼 구성으로 프로비저닝하고 관리</li><li>기존 프로비저닝된 환경에 영향을 주지 않고 변경 사항 실험 가능</li><li>깃으 브랜치 전략처럼 동일한 구성에서 서로 다른 리소스 결과 관리</li></ul><p><strong>단점</strong></p><ul><li>satte 가 동일한 저장소(로컬 또는 백엔드)에 저장되어 state 접근 권한 관리가 불가능</li><li>모든 환경이 동일한 리소스를 요구하지 않을 수 있으므로 테라폼 구성에 분기 처리가 다수 발생 가능</li><li>프로비저닝 대상에 대한 인증 요소를 완벽히 분리하기 어려움</li></ul><h1 id="모듈" tabindex="-1"><a class="header-anchor" href="#모듈"><span>모듈</span></a></h1><p><strong>모듈 구조 (예시)</strong></p><p><img src="`+o+`" alt="image-20250310233826614"></p><p><strong>06-01-basic/main.tf</strong></p><div class="language-terraform line-numbers-mode" data-highlighter="prismjs" data-ext="terraform" data-title="terraform"><pre><code><span class="line">module &quot;mypw1&quot; {</span>
<span class="line">    source = &quot;../modules/terraform-random-pwgen&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">module &quot;mypw2&quot; {</span>
<span class="line">    source = &quot;../modules/terraform-random-pwgen&quot;</span>
<span class="line">    isDB = true</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;pw1&quot; {</span>
<span class="line">    value = module.mypw1</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">output &quot;pw2&quot; {</span>
<span class="line">    value = module.mypw2</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="모듈-사용-방식" tabindex="-1"><a class="header-anchor" href="#모듈-사용-방식"><span>모듈 사용 방식</span></a></h2><h3 id="모듈과-프로바이더" tabindex="-1"><a class="header-anchor" href="#모듈과-프로바이더"><span>모듈과 프로바이더</span></a></h3><ol><li>자식 모듈에서 프로바이더 정의 <ol><li><strong>모듈에서 사용하는 프로바이더 버전과 구성 상세를 자식 모듈에 고정하는 방법.</strong> 동일한 프로바이더가 루트와 자식 양쪽에 또는 서로 다른 자식 모듈에 버전 조건 합의가 안되면 오류가 발생하고 모듈에 반복문을 사용할 수 없는 단점</li><li><strong>루트 모듈에서 프로바이더 정의</strong>. (권장)</li></ol></li></ol>`,70)),n(i)])}const h=t(v,[["render",m],["__file","2025-03-08-terraform.html.vue"]]),f=JSON.parse('{"path":"/books/all/2025-03-08-terraform.html","title":"테라폼 배우기","lang":"en-US","frontmatter":{"title":"테라폼 배우기","bookName":"테라폼으로 시작하는 IaC","author":"김민수 등","date":"2025-03-08T00:00:00.000Z","tags":["테라폼"]},"headers":[{"level":1,"title":"IaC 와 테라폼","slug":"iac-와-테라폼","link":"#iac-와-테라폼","children":[]},{"level":1,"title":"기본 사용법","slug":"기본-사용법","link":"#기본-사용법","children":[{"level":2,"title":"Variable","slug":"variable","link":"#variable","children":[{"level":3,"title":"validation","slug":"validation","link":"#validation","children":[]},{"level":3,"title":"변수 우선 순위","slug":"변수-우선-순위","link":"#변수-우선-순위","children":[]}]},{"level":2,"title":"local","slug":"local","link":"#local","children":[]},{"level":2,"title":"output","slug":"output","link":"#output","children":[]},{"level":2,"title":"for","slug":"for","link":"#for","children":[]},{"level":2,"title":"함수","slug":"함수","link":"#함수","children":[]},{"level":2,"title":"프로비저너","slug":"프로비저너","link":"#프로비저너","children":[]},{"level":2,"title":"Moved","slug":"moved","link":"#moved","children":[]}]},{"level":1,"title":"프로바이더","slug":"프로바이더","link":"#프로바이더","children":[{"level":2,"title":"프로바이더의 다중 정의","slug":"프로바이더의-다중-정의","link":"#프로바이더의-다중-정의","children":[]}]},{"level":1,"title":"State","slug":"state","link":"#state","children":[{"level":2,"title":"워크스페이스","slug":"워크스페이스","link":"#워크스페이스","children":[]}]},{"level":1,"title":"모듈","slug":"모듈","link":"#모듈","children":[{"level":2,"title":"모듈 사용 방식","slug":"모듈-사용-방식","link":"#모듈-사용-방식","children":[{"level":3,"title":"모듈과 프로바이더","slug":"모듈과-프로바이더","link":"#모듈과-프로바이더","children":[]}]}]}],"git":{},"filePathRelative":"_books/all/2025-03-08-terraform.md"}');export{h as comp,f as data};
