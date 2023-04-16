---

categories: "socceranalyst"
tag: ["token", "jwt", "toyproject", "httponly", "csrf", "xss"]

---

# HttpOnly 

앞선 포스팅에서 refreshToken 을 구현했고, 이제 프론트엔드를 보겠습니다. 

프론트엔드에는 HttpOnly 로 쿠키로 넣어줬고, 그에 따라 백엔드도 수정이 있었습니다. 코드를 보기 전에 HttpOnly 에 대해 알아봅시다.

**HTTPOnly**

HTTPOnly 옵션은 클라이언트측에서 쿠키를 보호하기 위한 보안 플래그입니다. 자바스크립트에 대한 XSS 공격으로부터 쿠키가 보호받을 수 있습니다. 쿠키에 HTTPOnly 옵션이 있으면 클라이언트측의 자바스크립트로는 해당 쿠키를 읽을 수 없기 때문입니다. 해당 쿠키가 HTTPOnly 옵션으로 다시 서버로 보내지면, 서버에서 처리할 수 있습니다. 

HTTPOnly 옵션 적용을 알아보기 전에 XSS, CRSF 공격에 대해 알아보겠습니다.

**XSS, CRSF**

- **XSS**(Cross-Site Scripting) : 공격자가 악성 스크립트를 웹페이지에 삽입하여 다른 사용자가 이를 실행하도록 하는 공격입니다. 이 악성 스크립트로 민감한 정보를 가진 쿠키, 세션 토큰, 개인정보 등을 탈취합니다. 3가지 유형이 있습니다.

  1. Stored XSS : 악성 스크립트가 타겟 어플리케이션에 저장되어 사용자가 해당 페이지를 실행할 때마다 실행됩니다.
  2. Reflected XSS : 악성 스크립트가 링크나 inputField 에 포함되어서, 사용자가 해당 링크나 입력을 실행시킬 때마다 해당 스크립트가 실행됩니다.
  3. DOM-based XSS : 악성 스크립트가 Document Object Model (DOM) 을 조작해서 어플리케이션 스크립트와 상호작용 없이 브라우저 내에서 실행됩니다.

- **CRSF**(Cross-Site Request Forgery) : CRSF 는 공격자가 인증된 사용자로 하여금 웹페이지에서 의도되지 않은 요청을 하도록 하는 공격입니다. 공격자는 악성 링크 등을 통해 사용자가 웹페이지에서 서버로 특정 request 를 보내도록 합니다. 

  예를 들어, 특정 request 를 보내면 사용자의 계좌에서 다른 사람의 계좌로 돈을 옮기는 과정이 진행된다고 한다면, 공격자는 링크를 클릭할 때 자동으로 인증된 사용자의 계좌에서 공격자의 계좌로 돈을 송금하도록 할 수 있습니다. 서버측은 해당 request 가 사용자로 부터 보내졌으므로 CRSF 공격으로 인지하지 못합니다.

  현재처럼 LocalStorage 와 HTTPOnly 옵션을 사용하면 CSRF 공격으로부터 안전할 수 있습니다. 

  참고글입니다. [CSRF(Cross-Site Request Forgery) 공격과 방어](https://junhyunny.github.io/information/security/spring-boot/spring-security/cross-site-reqeust-forgery/)

**왜 RefreshToken 에 HTTPOnly 를 적용하나?**

1. XXS 공격으로부터 보안

   refreshToken 은 클라이언트의 리소스를 얻을 수 있는 중요한 정보이기 때문에 클라이언트 사이드의 script 로부터 보호받아야 합니다. HTTPOnly 옵션을 사용함으로써, 자바스크립트로부터의 접근을 방지하여 XSS 공격 위험성을 낮춥니다.

2. 관심사의 분리

   accessToken 과 refreshToken 모두 같은 JWT Token 이지만 사용목적이 다릅니다. 따라서 accessToken 은 script 변수, localStorage 에 저장하여 사용하고, RefreshToken 은 HTTPOnly 플래그를 설정함으로써 이러한 구분을 강제하여, 클라이언트 측 스크립트가 RefreshToken 을 잘못 사용하는 것을 어렵게 만듭니다.

   

## 스프링에서 RefreshToken 에 HTTPOnly 옵션 적용

**fetch-action**

axios 에서 REST API 요청과 에러캐치의 구조를 통일하기 위해 추상화하여 작성된 파일입니다. 해당 js 로 모든 요청을 실시합니다.

```react
import axios from 'axios';
import { TestURI } from '../../utility/uri';

const uri = TestURI;

const fetchAuth = async (fetchData) => {
  const method = fetchData.method;
  const url = fetchData.url;
  const data = fetchData.data;
  const header = fetchData.header;

  try {
    const response =
      (method === 'get' && (await axios.get(uri + url, header))) ||
      (method === 'post' && (await axios.post(uri + url, data, header))) ||
      (method === 'put' && (await axios.put(uri + url, data, header))) ||
      (method === 'delete' && (await axios.delete(uri + url, header)));

    if(response.data.message==='만료된 토큰입니다.'){

      const refreshTokenUrl = '/auth/refreshToken';
      const refreshTokenHeader = {
        withCredentials: 'include'
      }
      const refreshResponse = await axios.get(uri + refreshTokenUrl, refreshTokenHeader)
      if(refreshResponse.status===401){
        alert('로그인이 만료되었습니다. 다시 로그인해주세요.');
        return null;
      }else{
        localStorage.setItem('accessToken', refreshResponse.data.accessToken);
        localStorage.setItem('accessTokenExpirationTime', String(refreshResponse.data.accessTokenExpirationTime));
        const accessToken = localStorage.getItem('accessToken');
        const accessTokenHeader = {
          headers: {
            'Authorization': 'Bearer ' + accessToken
          }
        }
        const response =
          (method === 'get' && (await axios.get(uri + url, accessTokenHeader))) ||
          (method === 'post' && (await axios.post(uri + url, data, accessTokenHeader))) ||
          (method === 'put' && (await axios.put(uri + url, data, accessTokenHeader))) ||
          (method === 'delete' && (await axios.delete(uri + url, accessTokenHeader)));
        return response;
      }
    }

    if (!response) {
      alert('false!');
      return null;
    }

    return response;
  } catch (err) {

    window.alert(err.response.data);
    
    if (axios.isAxiosError(err)) {
      const serverError = err;
      if (serverError && serverError.response) {
        return null;
      }
    }
    return null;
  }
};

const GET = (url, header) => {
  const response = fetchAuth({ method: 'get', url, header });
  return response;
};

const POST = (url, data, header) => {
  const response = fetchAuth({ method: 'post', url, data, header });
  return response;
};

const PUT = async (url, data, header) => {
  const response = fetchAuth({ method: 'put', url, data, header });
  return response;
};

const DELETE = async (url, header) => {
  const response = fetchAuth({ method: 'delete', url, header });
  return response;
};

export { GET, POST, PUT, DELETE };

```

**refeshToken 을 요청하는 코드만 다시 보도록 하겠습니다.**

```react
... 
const method = fetchData.method;
const url = fetchData.url;
const data = fetchData.data;
const header = fetchData.header;

try {
    const response =
      (method === 'get' && (await axios.get(uri + url, header))) ||
      (method === 'post' && (await axios.post(uri + url, data, header))) ||
      (method === 'put' && (await axios.put(uri + url, data, header))) ||
      (method === 'delete' && (await axios.delete(uri + url, header)));

    if(response.data.message==='만료된 토큰입니다.'){

      const refreshTokenUrl = '/auth/refreshToken';
      const refreshTokenHeader = {
        withCredentials: 'include'
      }
      const refreshResponse = await axios.get(uri + refreshTokenUrl, refreshTokenHeader)
      if(refreshResponse.status===401){
        alert('로그인이 만료되었습니다. 다시 로그인해주세요.');
        return null;
      }else{
        localStorage.setItem('accessToken', refreshResponse.data.accessToken);
        localStorage.setItem('accessTokenExpirationTime', String(refreshResponse.data.accessTokenExpirationTime));
        const accessToken = localStorage.getItem('accessToken');
        const accessTokenHeader = {
          headers: {
            'Authorization': 'Bearer ' + accessToken
          }
        }
        const response =
          (method === 'get' && (await axios.get(uri + url, accessTokenHeader))) ||
          (method === 'post' && (await axios.post(uri + url, data, accessTokenHeader))) ||
          (method === 'put' && (await axios.put(uri + url, data, accessTokenHeader))) ||
          (method === 'delete' && (await axios.delete(uri + url, accessTokenHeader)));
        return response;
      }
    }
     
     ...
```

1. 먼저 try 문 안에서 REST API 요청이 보내집니다. 이때 accessToken 이 만료되었다면 200 응답 코드로 `만료된 토큰입니다.` 이라는 메세지가 옵니다. 

2. `if(response.data.message==='만료된 토큰입니다.')` 으로 해당 메세지를 잡아서 `/auth/refreshToken` 로 다시 요청을 합니다. 

3. 요청 시 Header 에 `withCredentials: 'include'` 을 포함시켜 로그인 시 받은 HTTPOnly 쿠키도 같이 보냅니다.

4. `const refreshResponse = await axios.get(uri + refreshTokenUrl, refreshTokenHeader)` 을 통해 accessToken 을 발급받습니다.

5. 만약 refreshToken 도 만료되었다면 401 에러를 반환받습니다. 

6. refreshToken 이 만료되지 않았다면 localStorage 에 accessToken  을 저장합니다.

7. 해당 accessToken 으로 다시 원래 요청 url 에 대해 같은 데이터로 요청을 실시합니다.

   - ```react
     const accessToken = localStorage.getItem('accessToken');
         const accessTokenHeader = {
           headers: {
             'Authorization': 'Bearer ' + accessToken
           }
         }
         const response =
           (method === 'get' && (await axios.get(uri + url, accessTokenHeader))) ||
           (method === 'post' && (await axios.post(uri + url, data, accessTokenHeader))) ||
           (method === 'put' && (await axios.put(uri + url, data, accessTokenHeader))) ||
           (method === 'delete' && (await axios.delete(uri + url, accessTokenHeader)));
         return response;
     ```



# Spring 에 HTTPOnly 적용

AuthController 에서 login 시 HTTPOnly 쿠키를 발급하고, refreshToken 으로 accessToken 발급 요청 시 해당 과정을 수행합니다. 먼저 login 입니다.

**login**

```java
@PostMapping("/login")
    public ResponseEntity<TokenDto> login(
            @RequestBody MemberRequestDto requestDto, HttpServletResponse response,
            @Value("${cookie.secure}") boolean secure,
            @Value("${cookie.domain}") String domain
    ) {
        TokenDto token = authService.login(requestDto);

        ResponseCookie cookie = ResponseCookie.from("refreshToken", token.getRefreshToken())
                .domain(domain)
                .path("/")
                .httpOnly(true)
                .secure(secure)
                .sameSite("Strict")
                .maxAge(60 * 60 * 24 * 14)
                .build();

        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());

        token.setRefreshToken(null);

        return ResponseEntity.ok(token);
    }
```

먼저 `@Value` 를 통해 yml 파일의 `cookie.secure` 과 `cookie.domain` 불러왔습니다. local 과 production 값이 다르다보니 구분하였습니다.

```
# 로컬환경
cookie:
  secure: false
  domain: "localhost"
  ---
 # 배포 환경
cookie:
  secure: true
  domain: "socceranalyst.net"
  
```

잘 모르시면 제 포스팅 참고하셔도 될 것 같습니다. [로컬 환경과 배포 환경 분리](https://hobeen-kim.github.io/socceranalyst/socceranalyst-local,-production-%ED%99%98%EA%B2%BD-%EB%B6%84%EB%A6%AC/) 

그리고 `ResponseCookie` 를 통해 값을 세팅해주었습니다. `domain` 은 해당 도메인("socceranalyst.net"), `secure` 은 https 사용 시 사용하시면 됩니다. `sameSite` 는 설정된 쿠키는 크로스 사이트 요청에는 항상 전송되지 않도록 `Strict` 로 설정합니다. 다음 포스팅을 참고하면 이해가 빠릅니다.

[브라우저 쿠키와 SameSite 속성](https://seob.dev/posts/%EB%B8%8C%EB%9D%BC%EC%9A%B0%EC%A0%80-%EC%BF%A0%ED%82%A4%EC%99%80-SameSite-%EC%86%8D%EC%84%B1/)

`response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());` 로 쿠키를 Header 에 포함해줍니다. `token.setRefreshToken(null);` 로 TokenDto 에서 RefreshToken 을 빼줍니다. Refresh 토큰은 Header 로 전송되니 body 에 포함될 필요는 없죠.

**refreshToken**

다음은 refreshToken 메서드 입니다. AuthService 의 메서드는 이전 포스팅을 참고하면 됩니다.

```java
@GetMapping("/refreshToken")
public ResponseEntity<?> refreshToken(HttpServletRequest request) {

    String refreshToken = null;
    if (request.getCookies() != null) {
        for (Cookie cookie : request.getCookies()) {
            if ("refreshToken".equals(cookie.getName())) {
                refreshToken = cookie.getValue();
                break;
            }
        }
    }

    if (refreshToken == null) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("No refresh token found");
    }

    log.info("refreshToken published : {}", refreshToken);

    TokenDto token = authService.refreshToken(refreshToken);
    return ResponseEntity.ok(token);
}
```

먼저 `request.getCookies()` 로 쿠키를 꺼낸 후 `"refreshToken"` 쿠키를 찾아서 꺼냅니다. 해당 토큰을 `authService.refreshToken()` 메서드로 검증하고 accessToken 을 발급받습니다. 

해당 token 을 200ok 응답과 함께 클라이언트측으로 보냅니다.

## corsConfigurationSource 빈 등록

Cookie 를 주고받기 위해서 해야 할 설정이 있습니다.

```java
@Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();

        ...

        config.addAllowedMethod("*"); // 모든 메소드 허용.
        config.addAllowedHeader("*");
        config.setAllowCredentials(true);
        config.addExposedHeader("Set-Cookie");

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
```

`CorsConfiguration config` 에서 모든 메서드 허용, 모든 헤더를 허용해주고(특정 헤더만 허용해줘도 됩니다.) `config.setAllowCredentials(true);`, `config.addExposedHeader("Set-Cookie");` 옵션으로 쿠키를 주고받을 수 있도록 설정합니다.





# 마치며

refreshToken 을 HTTPOnly 옵션으로 쿠키로 저장하고, 서버와 다시 주고받는 걸 확인하기 위해 모든 주말을 다 쏟았습니다... ㅎㅎ

보안적으로 아직 할 일이 많이 남았습니다. 

- AccessToken 의 저장공간 고민 : localStorage 와 js 변수 중 고민인데요. 그냥 localStorage 사용할 듯 합니다.
- RTR(Refresh Token Rotation) 적용 : RTR 은 refreshToken 탈취에 대한 보안조치입니다. accessToken 재발급 시마다 refreshToken 도 재발급하여 refreshToken 이 탈취당하더라도 1번밖에 사용하지 못하도록 합니다. 

다음에는 OAuth2 를 이용해 네이버, 구글, 카카오 로그인을 구현해보겠습니다.
