---
categories: "socceranalyst"
tag: ["token", "jwt", "toyproject", "rtr", "redis"]
---

# RTR 기술 적용 (백엔드)

안녕하세요. 오늘은 RTR 기술을 적용해보겠습니다. 기본적인 내용은 해당 링크를 참고해주세요. [[Spring] refreshToken 과 RTR, Redis 기술](https://hobeen-kim.github.io/til-spring/Spring-refreshToken-%EA%B3%BC-RTR,-Redis-%EA%B8%B0%EC%88%A0/)

현재 상태입니다.

1. Redis 설치 및 테스트 완료
2. accessToken, refreshToken 발급 기능 구현 완료

구현해야 할 기능입니다.

1. Redis & 스프링 연동
2. `/auth/refreshToken` 에서 refreshToken 재발급 기능 구현

## Redis 연동

먼저 Redis 와  스프링을 연결해보겠습니다. 필요한 dependency 를 먼저 추가해줍니다.

**build.gradle** -> dependencies

`implementation 'org.springframework.boot:spring-boot-starter-data-redis-reactive'`

**application.yml**

그 다음 `application.yml` 파일에 다음과 같이 추가합니다.

```java
spring:
  redis:
    lettuce:
      pool:
        max-active: 10
        max-idle: 10
        min-idle: 2
    port: 6379
    host: 127.0.0.1
    password:
```

**RedisConfig**

다음은 redis 설정을 위한 Configuration 파일입니다.

```java
package soccer.backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisConfig {

    @Value("${spring.redis.host}")
    private String redisHost;

    @Value("${spring.redis.port}")
    private String redisPort;

    @Value("${spring.redis.password}")
    private String redisPassword;

    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        RedisStandaloneConfiguration redisStandaloneConfiguration = new RedisStandaloneConfiguration();
        redisStandaloneConfiguration.setHostName(redisHost);
        redisStandaloneConfiguration.setPort(Integer.parseInt(redisPort));
        redisStandaloneConfiguration.setPassword(redisPassword);
        LettuceConnectionFactory lettuceConnectionFactory = new LettuceConnectionFactory(redisStandaloneConfiguration);
        return lettuceConnectionFactory;
    }

    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        RedisTemplate<String, Object> redisTemplate = new RedisTemplate<>();
        redisTemplate.setConnectionFactory(redisConnectionFactory());
        redisTemplate.setKeySerializer(new StringRedisSerializer());
        redisTemplate.setValueSerializer(new StringRedisSerializer());
        return redisTemplate;
    }
}
```

이제 Redis 를 사용할 준비가 다 됐습니다.

## AuthService

```java
...
public TokenDto refreshToken(String refreshToken) {
    if (StringUtils.hasText(refreshToken) && tokenProvider.validateToken(refreshToken)) {
        Authentication authentication = tokenProvider.getAuthenticationFromRefreshToken(refreshToken);
        TokenDto newToken = tokenProvider.generateTokenDto(authentication);
        // Return the new access token in the response
        return newToken;
    } else {
        throw new RuntimeException("로그인 정보를 확인해주세요.");
    }
}

public String getMemberId(String accessToken) {
    return tokenProvider.getMemberIdFromExpiredToken(accessToken);
}
```

- `refreshToken()` : 원래는 `tokenProvider.createAccessToken()` 로 accessToken 만 만들었지만, refreshToken 도 함께 재발급해야 하기 때문에 `tokenProvider.generateTokenDto()` 메서드를 사용합니다. 기존의 `createAccessToken()` 는 더 이상 사용할 일이 없어 삭제했습니다.

- `getMemberId()` : `tokenProvider.getMemberIdFromExpiredToken(accessToken)` 으로 accessToken 의 MemberId 를 반환받습니다. `tokenProvider.getAuthentication()` 도 비슷한 메서드이지만 accessToken 이 만료되어 사용할 수 없습니다. 아래에 설명하겠습니다.

## TokenProvider

```java
...
public Authentication getAuthentication(String accessToken) {
        Claims claims = parseClaims(accessToken);

        if (claims.get(AUTHORITIES_KEY) == null) {
            throw new RuntimeException("권한 정보가 없는 토큰입니다.");
        }

        Collection<? extends GrantedAuthority> authorities =
                Arrays.stream(claims.get(AUTHORITIES_KEY).toString().split(","))
                        .map(SimpleGrantedAuthority::new)
                        .collect(Collectors.toList());

        UserDetails principal = new User(claims.getSubject(), "", authorities);

        return new UsernamePasswordAuthenticationToken(principal, "", authorities);
    }

    public String getMemberIdFromExpiredToken(String expiredToken) {

        Claims claims = null;
        try {
            claims = Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(expiredToken).getBody();
        } catch (ExpiredJwtException e) {
            claims = e.getClaims();
            return claims.getSubject();
        }
        throw new RuntimeException("토큰이 만료되지 않았습니다.");
    }
...
private Claims parseClaims(String token) {
    try {
        return Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token).getBody();
    } catch (ExpiredJwtException e) {
        throw new ExpiredJwtException(e.getHeader(), e.getClaims(), "만료된 토큰입니다.");
    }
}
...
```

토큰을 생성, 인증여부 확인 및 반환 등을 담당하는 TokenProvider 클래스 중 RTR 구현을 위한 `getMemberIdFromExpiredToken()` 메서드와, 비교를 위한 `getAuthentication()`, `parseClaims()`  메서드입니다.

기존의 `getAuthentication()` 메서드는  `Claims claims = parseClaims(accessToken)` 을 통해 만료여부를 판단하고 만료되었다면 `ExpiredJwtException` 을 던졌습니다.

따라서 `parseClaims()` 메서드에 `boolean isExpired` 파라미터를 넣어서 코드를 추가해야 했는데요. 그것보다는 `getMemberIdFromExpiredToken()` 메서드를 새로 만들었습니다.

`getMemberIdFromExpiredToken()` 메서드는 Token 이 만료되었을 때 `claims.getSubject()` 로 MemberId 를 반환하고, 만료되지 않았다면 `RuntimeException("토큰이 만료되지 않았습니다.");` 을 던집니다.

**<u>즉, accessToken 이 만료되지 않았는데도 다시 발급받으려는 Attacker 에 대한 보안조치를 한 것입니다.</u>**

## AuthController

로그인, accessToken 재발급을 위한, AuthController 중 일부입니다.

```java
public class AuthController {

    private final AuthService authService;
    private final RedisTemplate<String, String> redisTemplate;
    ValueOperations<String, String> vop = redisTemplate.opsForValue();
    @Value("${cookie.secure}")
    private boolean secure;
    @Value("${cookie.domain}")
    private String domain;

	...
	
    @PostMapping("/login")
    public ResponseEntity<TokenDto> login(
            @RequestBody MemberRequestDto requestDto, HttpServletResponse response,
            @Value("${cookie.secure}") boolean secure,
            @Value("${cookie.domain}") String domain
    ) {

        TokenDto token = authService.login(requestDto);

        //create Cookie and set it in response
        createCookie(response, token);

        //store refresh token in redis
        vop.set(requestDto.getMemberId(), token.getRefreshToken());

        token.setRefreshToken(null);

        return ResponseEntity.ok(token);
    }

    @GetMapping("/refreshToken")
    public ResponseEntity<?> refreshToken(
            HttpServletRequest request,
            HttpServletResponse response,
            @Value("${cookie.secure}") boolean secure,
             @Value("${cookie.domain}") String domain
    ) {

        String accessToken = request.getHeader("X-Expired-Access-Token").substring(7);
        String memberId = authService.getMemberId(accessToken);
        String refreshToken = null;


        if (request.getCookies() != null) {
            for (Cookie cookie : request.getCookies()) {
                if ("refreshToken".equals(cookie.getName())) {
                    refreshToken = cookie.getValue();
                    break;
                }
            }
        }
        //refreshToken 이 없을 때
        if (refreshToken == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("No refresh token found");
        }
        //accessToken 의 memberId 로 얻은 저장된 refreshToken 값과 받은 refreshToken 값이 다를 때
        if(!refreshToken.equals(vop.get(memberId))){
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("No refresh token found");
        }

        //issue Token (accessToken, refreshToken)
        TokenDto token = authService.refreshToken(refreshToken);

        //store refreshToken in cookie
        createCookie(response, token);

        //store refresh token in redis
        vop.set(memberId, token.getRefreshToken());

        //remove refreshToken from response
        //because it is stored in cookie
        token.setRefreshToken(null);

        return ResponseEntity.ok(token);
    }

    private void createCookie(HttpServletResponse response, TokenDto token) {
        ResponseCookie cookie = ResponseCookie.from("refreshToken", token.getRefreshToken())
                .domain(domain)
                .path("/")
                .httpOnly(true)
                .secure(secure)
                .sameSite("Strict")
                .maxAge(60 * 60 * 24 * 14)
                .build();

        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
    }
}
```

하나하나 살펴보도록 하겠습니다.

**필드()**

```java
private final AuthService authService;
private final RedisTemplate<String, String> redisTemplate;
@Value("${cookie.secure}")
private boolean secure;
@Value("${cookie.domain}")
private String domain;
```

redisTemplate 을 사용하기 위해 `RedisTemplate<String, String>` 을 선언해주었습니다.

yml 파일에서 secure 과 domain 값을 가져오기 위해 `@Value` 어노테이션을 사용하였습니다.

**login()**

```java
@PostMapping("/login")
public ResponseEntity<TokenDto> login(
        @RequestBody MemberRequestDto requestDto, HttpServletResponse response,
        @Value("${cookie.secure}") boolean secure,
        @Value("${cookie.domain}") String domain
) {

    TokenDto token = authService.login(requestDto);

    //create Cookie and set it in response
    createCookie(response, token);

    //store refresh token in redis
    vop.set(requestDto.getMemberId(), token.getRefreshToken());

    token.setRefreshToken(null);

    return ResponseEntity.ok(token);
}
```

login 시 authService 의 login() 으로 Token 을 받아옵니다. 그리고 내부 메서드인 createCookie() 으로 response 와 token 값을 넘겨서 refreshToken 을 response 에 담아줍니다.

생성된 refreshToken 은 Redis 에 넣습니다. 나중에 refreshToken 으로 재발급 요청 시 사용할 예정입니다.

**refreshToken()**

```java
 @GetMapping("/refreshToken")
    public ResponseEntity<?> refreshToken(
            HttpServletRequest request,
            HttpServletResponse response
    ) {

        String accessToken = request.getHeader("X-Expired-Access-Token").substring(7);
        String memberId = authService.getMemberId(accessToken);
        String refreshToken = null;


        if (request.getCookies() != null) {
            for (Cookie cookie : request.getCookies()) {
                if ("refreshToken".equals(cookie.getName())) {
                    refreshToken = cookie.getValue();
                    break;
                }
            }
        }
        //refreshToken 이 없을 때
        if (refreshToken == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("No refresh token found");
        }
        //accessToken 의 memberId 로 얻은 저장된 refreshToken 값과 받은 refreshToken 값이 다를 때
        if(!refreshToken.equals(vop.get(memberId))){
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("No refresh token found");
        }

        //issue Token (accessToken, refreshToken)
        TokenDto token = authService.refreshToken(refreshToken);

        //store refreshToken in cookie
        createCookie(response, token);

        //store refresh token in redis
        vop.set(memberId, token.getRefreshToken());

        //remove refreshToken from response
        //because it is stored in cookie
        token.setRefreshToken(null);

        return ResponseEntity.ok(token);
    }
```

`request.getHeader("X-Expired-Access-Token").substring(7);` 으로 만료된 accessToken 을 받아옵니다. 원래는 `Authentication` 헤더로 받아와야 하지만, 만료되었기 때문에 JwtFilter 에서의 검증 메서드를 통과하지 못합니다. 따라서 헤더 이름을 바꿔서 받아옵니다.

`authService.getMemberId(accessToken);` 메서드로 `MemberId` 를 가져옵니다.

`request` 에 refreshToken 이 있는지 확인 후 있으면 해당 값과 Redis DB 에 저장된 값이 같은지 비교합니다. 이 때 key 값은 accessToken 에서 얻은 `MemberId` 입니다.

같다면 Token 을 재발급 후 반환해줍니다. 재발급된 refreshToken 은 다시 Redis DB 에 저장해줍니다.



# RTR 기술 적용 (프론트 엔드)

프론트 엔드에서는 크게 바뀔 게 없습니다.

다만, accessToken 을 `Authentication` 헤더와 함께 전달하던 것과 달리 `X-Expired-Access-Token` 헤더로 서버로 전달해야 합니다.

```java
const fetchAuth = async (fetchData) => {
  const method = fetchData.method;
  const url = fetchData.url;
  const data = fetchData.data;
  const header = fetchData.header;

  try {
    ...

    if(response.data.message==='만료된 토큰입니다.'){
      const refreshTokenUrl = '/auth/refreshToken';
      const refreshTokenHeader = {
        withCredentials: 'include',
        headers: {
          'X-Expired-Access-Token': header.headers.Authorization
        }
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

중요 변경사항은 다음과 같습니다.

```java
const refreshTokenHeader = {
        withCredentials: 'include',
        headers: {
          'X-Expired-Access-Token': header.headers.Authorization
        }
      }
```

- 원래 `/auth/refreshToken` 으로 보낼 때 `withCredentials: 'include'` 만 있으면 되었지만, accessToken 도 함께 보내기 위해 `X-Expired-Access-Token` 을 추가해줍니다. 해당 accessToken 은 원래 요청헤더에서 가져오도록 합니다.



# 마치며

RTR 기술을 간단하게 구현하는 건 생각보다 쉬웠습니다. 이제 같은 방법으로 Ec2 에 Redis 를 설치하고 사용하면 됩니다.

[[AWS] Amazon Linux2 Redis 설치](https://small-stap.tistory.com/109?category=989595) (이거 하느라 2시간 걸렸습니다...)

배포 및 테스트는 주말에 해보도록 하겠습니다... ㅎㅎ 감사합니다.

