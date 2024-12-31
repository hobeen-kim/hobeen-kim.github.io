---
categories: "WEB"
tag: ["rest", "url", "uri"]
title: "[WEB] url 과 uri 차이"
description: "url 과 uri 차이입니다."
series: "(책) 모던 API 개발"
series-link: "https://product.kyobobook.co.kr/detail/S000214875784"
teaser: "modernapidev"
---

# 0. REST

REST 에 대한 설명은 제 블로그에 있습니다. https://hobeen-kim.github.io/web/WEB-RESTAPI/

## 0.1 REST 의 3개의 주요 컴포넌트

REST 는 3개의 주요 컴포넌트를 사용해서 동작합니다.

- 리소스와 URI
- HTTP 메서드
- HATEOAS

이중 URI 만 보겠습니다.

# 2. URI

  World Wide Web(WWW) 상의 모든 문서는 HTTP 관점에서 리소스로 여겨집니다. 리소스는 URI 로 표시되며 서버 상의 고유 리소스를 나타내는 엔드포인트입니다. URI 는 웹에서 리소스의 위치, 이름, 또는 이 둘을 모두 사용해 리소스를 식별하는 문자열을 의미합니다. URI 에는 URL 과 URN 두 가지 타입이 있습니다.

  URI 구문은 다음과 같습니다.

`scheme:[//authority]path[?query][#fragment]` 

- scheme : HTTP, HTTPS, FILE, FTP ...
- authority : 사용자 정보, 호스트, 포트
- path : 경로
- query : 쿼리 문자열, 비계층적 데이터
- 프래그먼트 : 해시(#)가 앞에 오는 필드. 부속 리소스를 가리키는 프래그먼트 식별자

URI 의 예시

- www.packt.com
- index.html
- https://www.packt.com/index.html

스킴 URI

- mailto:support@packt.com
- telnet://192.168.0.1:23/
- ldap://[2020:ab9::9]/c=AB?objectClass?obj

# 3. URL

  위에 언급된 대부분의 URI 예시들은 사실 URL 이라고도 할 수 있습니다. URI 는 식별자인 반면 URL 은 식별자일 뿐만 아니라 **리소스에 도달하는 방법도 알려줍니다.**

  URL 은 리소스의 전체 웹 주소를 나타내며, 프로토콜 이름(scheme), 호스트 이름과 포트, 경로, 선택 사항은 쿼리 및 프래그먼트 컴포넌트를 포함합니다.

> RFC 3986 (https://datatracker.ietf.org/doc/html/rfc3986#section-1.1.3)
>
> URI는 위치(Locator), 이름(Name), 또는 둘 다로 더 분류될 수 있다. "Uniform Resource Locator"(URL)라는 용어는 리소스를 식별하는 것 외에, 리소스의 주요 접근 메커니즘(예: 네트워크 "위치")을 설명함으로써 리소스를 찾는 수단을 제공하는 URI의 하위 집합을 지칭한다. "Uniform Resource Name"(URN)이라는 용어는 역사적으로 "urn" 스키마 아래의 URI를 지칭하는 데 사용되었으며, 이는 리소스가 존재하지 않거나 접근할 수 없게 되더라도 전 세계적으로 고유하고 지속 가능해야 한다. 또한 이름의 속성을 가진 다른 URI를 가리키는 데에도 사용되었다.
>
> 개별 스키마는 단순히 "이름"이나 "위치" 중 하나로만 분류될 필요는 없다. 특정 스키마에서 생성된 URI는 이름의 속성이나 위치의 속성, 또는 둘 다를 가질 수 있으며, 이는 종종 스키마의 특성보다는 이름을 할당하는 기관의 지속성과 관리 방식에 더 의존한다. 향후 명세와 관련 문서에서는 "URL"과 "URN"이라는 더 제한적인 용어보다는 일반적인 용어인 "URI"를 사용하는 것이 바람직하다.



