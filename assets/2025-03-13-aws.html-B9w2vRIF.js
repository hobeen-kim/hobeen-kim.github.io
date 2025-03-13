import{_ as o,c as d,a as n,b as l,d as p,f as a,r as i,o as c,e as t}from"./app-Tj2laqPB.js";const u="/images/2025-03-13-aws/image-20250313192725190.png",g="/images/2025-03-13-aws/image-20250313192954390.png",h="/images/2025-03-13-aws/image-20250313201237416.png",m={},k={class:"table-of-contents"};function b(f,e){const r=i("Header"),s=i("router-link");return c(),d("div",null,[n(r),l("nav",k,[l("ul",null,[l("li",null,[n(s,{to:"#bedrock"},{default:a(()=>e[0]||(e[0]=[t("Bedrock?")])),_:1}),l("ul",null,[l("li",null,[n(s,{to:"#bedrock-사용"},{default:a(()=>e[1]||(e[1]=[t("Bedrock 사용")])),_:1})])])]),l("li",null,[n(s,{to:"#hands-on"},{default:a(()=>e[2]||(e[2]=[t("Hands-On")])),_:1})]),l("li",null,[n(s,{to:"#느낌"},{default:a(()=>e[3]||(e[3]=[t("느낌")])),_:1}),l("ul",null,[l("li",null,[n(s,{to:"#프롬프트가-엔지니어링일까"},{default:a(()=>e[4]||(e[4]=[t("프롬프트가 엔지니어링일까")])),_:1})]),l("li",null,[n(s,{to:"#핸즈온-세션"},{default:a(()=>e[5]||(e[5]=[t("핸즈온 세션")])),_:1})])])]),l("li",null,[n(s,{to:"#prefill"},{default:a(()=>e[6]||(e[6]=[t("prefill")])),_:1})]),l("li",null,[n(s,{to:"#기타"},{default:a(()=>e[7]||(e[7]=[t("기타")])),_:1})])])]),e[8]||(e[8]=p('<p>anthropic claude 3 고급 프롬프트엔지니어링(https://catalog.workshops.aws/prompt-eng-claude3/ko-KR)에 대한 핸즈온 섹션이다. aws 에서 제공하는 임시 아이디로 진행되었다.(https://bit.ly/awskrug-250313)</p><blockquote><p>핸즈온 밋업 때는 일찍 가는게 좋을 것 같다. 미리 설정해야 할 게 있기 때문이다.</p></blockquote><h1 id="bedrock" tabindex="-1"><a class="header-anchor" href="#bedrock"><span>Bedrock?</span></a></h1><p>AWS Bedrock은 다양한 생성형 AI 모델을 손쉽게 활용할 수 있도록 지원하는 관리형 서비스다. 사용자는 API를 통해 여러 AI 모델을 선택하고 맞춤형 애플리케이션을 구축할 수 있으며, 인프라 관리 없이 AI 기능을 통합할 수 있다. 이를 통해 기업은 AI 기반 애플리케이션을 빠르게 개발하고 확장할 수 있다.</p><h2 id="bedrock-사용" tabindex="-1"><a class="header-anchor" href="#bedrock-사용"><span>Bedrock 사용</span></a></h2><p><em>(핸즈온에서)</em></p><ol><li><p>bedrock configuration 에서 model acess 선택 (여기서는 claude 3 sonnet, haiku) 선택</p></li><li><p>sagemaker AI 로 이동해서 notebooks instance, 그리고 Open JupyterLabs</p><p><img src="'+u+'" alt="image-20250313192725190"></p></li><li><p>그러면 주피터 화면이 나온다.</p><p><img src="'+g+`" alt="image-20250313192954390"></p></li></ol><h1 id="hands-on" tabindex="-1"><a class="header-anchor" href="#hands-on"><span>Hands-On</span></a></h1><p><a href="https://catalog.workshops.aws/prompt-eng-claude3/ko-KR" target="_blank" rel="noopener noreferrer">핸즈온 세션</a>에 있는 항목에 대해 주피터에서 예시와 함께 진행했다.</p><p><strong>Claude 성능을 향상시키기 위해 배우게 될 프롬프트 엔지니어링 기법</strong></p><ul><li><strong>명확하고 직접적인 지시:</strong> Claude의 응답을 안내하기 위해 명확한 지침과 맥락을 제공합니다.</li><li><strong>응답 예시 활용:</strong> 원하는 출력 형식이나 스타일을 보여주기 위해 프롬프트에 예시를 포함시킵니다.</li><li><strong>Claude에게 역할 부여:</strong> 사용 사례에 따라 성능을 높이기 위해 Claude에게 특정 역할(전문가 역할 등)을 부여합니다.</li><li><strong>XML 태그 사용:</strong> 프롬프트와 응답의 구조를 명확히 하기 위해 XML 태그를 활용합니다.</li><li><strong>프롬프트 체이닝:</strong> 복잡한 작업을 더 나은 결과를 위해 작은 단계로 나눕니다.</li><li><strong>Claude의 사고 유도:</strong> 출력 품질 향상을 위해 단계별 사고를 장려합니다.</li><li><strong>Claude의 응답 미리 채우기:</strong> 원하는 방향으로 출력을 안내하기 위해 Claude의 응답을 몇 단어로 시작합니다.</li><li><strong>출력 형식 제어:</strong> 일관성과 가독성을 위해 원하는 출력 형식을 지정합니다.</li><li><strong>Claude에게 개작 요청:</strong> 루브릭에 따라 개작을 요청하여 Claude가 출력을 반복하고 개선하도록 합니다.</li><li><strong>긴 컨텍스트 활용 팁:</strong> Claude의 긴 컨텍스트를 활용하기 위한 프롬프트 최적화 방법을 배웁니다.</li></ul><h1 id="느낌" tabindex="-1"><a class="header-anchor" href="#느낌"><span>느낌</span></a></h1><h2 id="프롬프트가-엔지니어링일까" tabindex="-1"><a class="header-anchor" href="#프롬프트가-엔지니어링일까"><span>프롬프트가 엔지니어링일까</span></a></h2><p>이전 회사에서 키워드 조합으로 추천문구를 생성하기 위해 <strong>프롬프트 엔지니어링을 신물나게 했다</strong>. 그 때 동료들과 한 말,</p><blockquote><p>처음 &quot;프롬프트 엔지니어링&quot;이라는 말을 만든 사람은 언어적 천재다. 엔지니어링이 아닌 것 같은데 잘 포장했다.</p></blockquote><p>사실, 까고 보면 프롬프트 엔지니어링이란 시키고 싶은 걸 일목요연하게 나열하는 것뿐이다. 순서를 알려준다든가 예시를 준다든가, 역할놀이를 한다든가 하는 것뿐이지 개발적인 엔지니어링은 아닌 것 같다...</p><blockquote><p>그거 그냥 gpt 가스라이팅하는거잖아?</p></blockquote><p>내가 프롬프트 엔지니어링하고 있다고 했을 때 보안쪽 친구한테 들었던 말이다. 반박할 수 없었다. 이번 세션은 <strong>프롬프트 엔지니어링 (무려) 고급 기법</strong>이라고 해서 기대했고 내가 모르는 무언가가 있을까 했는데 기대한만큼은 아니었다.</p><h2 id="핸즈온-세션" tabindex="-1"><a class="header-anchor" href="#핸즈온-세션"><span>핸즈온 세션</span></a></h2><p>핸즈온에서 프롬프트를 작성하고 답변이 제대로 나오는지 true, false 로 검증하는데, 아래와 같이 예상되는 특정 단어가 있는지 검증한다. 그래서 claude3 을 써서 핸즈온을 했나? 3.5 의 대답은 더 다채로울테니까</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line"># Prompt - this is the only field you should change</span>
<span class="line">PROMPT = &quot;please pick any basketball player. simply answer with name except for any words&quot;</span>
<span class="line"></span>
<span class="line"># Get Claude&#39;s response</span>
<span class="line">response = get_completion(PROMPT)</span>
<span class="line"></span>
<span class="line"># Function to grade exercise correctness</span>
<span class="line">def grade_exercise(text):</span>
<span class="line">    return text == &quot;Michael Jordan&quot;</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h1 id="prefill" tabindex="-1"><a class="header-anchor" href="#prefill"><span>prefill</span></a></h1><p>prefill 은 좀 신기했다. 아래 기법이다.</p><blockquote><p><strong>Claude의 응답 미리 채우기:</strong> 원하는 방향으로 출력을 안내하기 위해 Claude의 응답을 몇 단어로 시작합니다.</p></blockquote><p>먼저 첫 몇 단어를 응답으로 강제하고 시작하는 것이다. 최고의 농구선수가 누구냐고 물어보고 첫 단어로 스테픈 커리로 하니까 당연히 스테픈 커리라고 이어서 대답한다.</p><p>주로 사용하는 것은 xml 태그나 json 으로 응답을 받기 위해 <code>&lt;answer&gt;</code>, <code>{</code> 등으로 시작할 수 있다.</p><p><img src="`+h+'" alt="image-20250313201237416"></p><h1 id="기타" tabindex="-1"><a class="header-anchor" href="#기타"><span>기타</span></a></h1><p>소고기 김밥을 줬는데 좀 쉰 것 같다.</p>',29))])}const x=o(m,[["render",b],["__file","2025-03-13-aws.html.vue"]]),_=JSON.parse('{"path":"/posts/cloud/2025-03-13-aws.html","title":"[AWSKRUG] AWS AIEngineering Meetup (센터필드)","lang":"en-US","frontmatter":{"title":"[AWSKRUG] AWS AIEngineering Meetup (센터필드)","date":"2025-03-13T00:00:00.000Z","tags":["ai","prompt_egineering","aws"],"description":"AWSKRUG AIEngineering 모임에 다녀온 후기와 요약"},"headers":[{"level":1,"title":"Bedrock?","slug":"bedrock","link":"#bedrock","children":[{"level":2,"title":"Bedrock 사용","slug":"bedrock-사용","link":"#bedrock-사용","children":[]}]},{"level":1,"title":"Hands-On","slug":"hands-on","link":"#hands-on","children":[]},{"level":1,"title":"느낌","slug":"느낌","link":"#느낌","children":[{"level":2,"title":"프롬프트가 엔지니어링일까","slug":"프롬프트가-엔지니어링일까","link":"#프롬프트가-엔지니어링일까","children":[]},{"level":2,"title":"핸즈온 세션","slug":"핸즈온-세션","link":"#핸즈온-세션","children":[]}]},{"level":1,"title":"prefill","slug":"prefill","link":"#prefill","children":[]},{"level":1,"title":"기타","slug":"기타","link":"#기타","children":[]}],"git":{},"filePathRelative":"_posts/cloud/2025-03-13-aws.md"}');export{x as comp,_ as data};
