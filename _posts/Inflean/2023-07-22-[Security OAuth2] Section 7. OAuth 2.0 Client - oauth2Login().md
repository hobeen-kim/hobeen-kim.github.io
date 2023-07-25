---
categories: "inflearn"
tag: ["LoginConfigurer", "OAuth2User", "OidcUser", "OAuth2AuthorizationRequestResolver"]
series: "Spring Boot 기반으로 개발하는 Spring Security OAuth2"
teaser: "Spring Security2"
title: "[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()"
description: "Spring Security Section 7. OAuth 2.0 Client - oauth2Login() 내용입니다."
---

# OAuth2LoginConfiguerer 초기화 이해

먼저 `Configurer` 의 `init()` 메서드를 보겠습니다.

![image-20230722115247108](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722115247108.png)

`init()` 메서드에서는 `OAuth2LoginAuthenticationFilter` 를 생성하고 `AuthenticationProvider` 를 2개 생성합니다. 각각 OAuth2Login 과 OIDC provider 입니다. 그리고 로그인페이지를 생성하는 필터도 만듭니다.

![image-20230722115425264](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722115425264.png)

그 다음은 `configure()` 메서등니데요. `OAuth2AuthrizationRequestRedirectFilter` 가 생성됩니다. 생성 순서는  `OAuth2LoginAuthenticationFilter` 이후에 생성되지만 실행순서는 `OAuth2AuthrizationRequestRedirectFilter` 가 먼저입니다. 해당 필터는 임시 코드를발급하는 엔드포인트를 요청합니다.

`OAuth2LoginConfigurer` 가 가지고 있는 설정 파일은 아래와 같이 4개입니다.

![image-20230722115759460](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722115759460.png)

- **AuthorizationEndpointConfig** 는 코드 발급 요청 시 설정들을 관리합니다.
- **RedirectionEndpointConfig** 는 리다이렉트 정보를 관리합니다.
- **TokenEndpointConfig** 는 토큰 요청 시 필요한 정보를 관리합니다.
- **UserInfoEndpointConfig** 는 토큰을 통해 userInfo 를 가지고 오는 정보를 관리합니다.

설정이 완료되면 아래와 같은 필터가 생깁니다.

![image-20230722115759460](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722115842184.png)

## 코드 레벨

먼저 다음과 같이 `OAuth2ClientConfig` 설정 정보를 구성합니다.

```java
@Configuration
public class OAuth2ClientConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeRequests()
                .anyRequest().authenticated()
            .and()
                .oauth2Login()
        ;

        return http.build();
    }
}
```

그러면 `OAuth2LoginConfigurer` 가 구성됩니다.

먼저 `init()` 을 보겠습니다.

![image-20230722121006912](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722121006912.png)

OAuth2LoginAuthenticationFilter 를 만들어서 Configurer 의 AuthenticationFilter 로 등록하고 있습니다. 생성자 파라미터로 보이는 `this.loginProcessingUrl` 은 기본값으로 `/login/oauth2/code/*` 을 가지고 있습니다. <u>즉, 해당 url 로 오는 모든 요청에 대해 필터를 적용한다는 뜻입니다.</u>

![image-20230722121845140](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722121845140.png)

그 외에도 여러 설정 정보를 구성하는데요.

1. 유저 정보를 담는 `OAuth2UserService` 클래스
2. Provider 클래스인 `OAuth2LoginAuthenticationProvider`
3. `oidcAuthenticationProviderEnabled` 가 true 이면 `OidcAuthorizationCodeAuthenticationProvider` 도 provider 로 등록
4. `initDefaultLoginFilter()` 로 기본 로그인필터 등록

다음은 `configure()` 메서드입니다.

![image-20230722122321868](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722122321868.png)

해당 메서드에도 많은 정보가 있지만 `OAuth2AuthorizationRequestRedirectFilter` 클래스 설정만 보겠습니다. 해당 클래스는 임시 코드를 요청하는 Base uri 을 가집니다. uri 는 `/oauth2/authorization` 로, 해당 uri 로 접근하면 임시 코드를 요청하는 로직을 실행하겠다는 뜻입니다.

# OAUth 2.0 Login Page 생성

​	기본적으로 OAuth 2.0 로그인 페이지는 `DefaultLoginPageGeneratingFilter` 가 자동으로 생성해줍니다. 이 디폴트 로그인 페이지는 OAuth 2.0 클라이언트명을 보여주며 링크를 누르면 인가 요청을 (또는 OAuth 2.0 로그인을) 시작할 수 있습니다.

![image-20230722130843687](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722130843687.png)

요청 매핑 Url 은 `/oauth2/authorization/{registrationId}` 입니다. 디폴트 로그인 페이지를 재정의하려면 oauth2Login().loginPage() 를 사용하면 됩니다.

## 실습

loginPage 를 커스텀으로 만들어보겠습니다. 

### LoginController

아래와 같이 컨트롤러를 만듭니다.

```java
@RestController
public class LoginController {

    @GetMapping("/loginPage")
    public String loginPage(){
        return "loginPage";
    }
}
```

### OAuth2ClientConfig

config 파일에서 설정 정보에 로그인 페이지를 설정합니다.

```java
@Configuration
public class OAuth2ClientConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeRequests(authorize ->
                        authorize
                                .antMatchers("/loginPage").permitAll()
                                .anyRequest().authenticated()
                        )
                .oauth2Login(oauth2 -> oauth2.loginPage("/loginPage"))
        ;

        return http.build();
    }
}
```

루트 페이지로 접속하면 자동으로 `loginPage` 로 접속하게 됩니다. 따로 인증 처리 등은 거치지 않았고 단순히 로그인 페이지 설정하는 방법만 확인했습니다.

![image-20230722134506195](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722134506195.png)

아래는 custom 지정을 하지 않은 설정 정보입니다.

```java
@Configuration
public class OAuth2ClientConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeRequests(authorize ->
                        authorize
                                .anyRequest().authenticated()
                        )
                .oauth2Login(Customizer.withDefaults())
        ;

        return http.build();
    }
}
```

루트로 접속하면 인가 서버로 접속하게 됩니다.

![image-20230722134622613](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722134622613.png)

# Authorization Code 요청하기

​	주요 클래스는 **`OAuth2AuthorizationRequestRedirectFilter`** 입니다. 클라이언트는 사용자의 브라우저를 통해 인가 서버의 권한 부여 엔드포인트로 리다이렉션하여 권한 코드 부여 흐름을 시작합니다. 요청 매핑 Url 은 `/oauth2/authorization/{registrationId}` 입니다.

​	**`DefaultOAuth2AuthorizationRequestResolver`** 클래스는 웹 요청에 대하여 `OAuth2AuthorizationRequest` 객체를 최종 완성하는 역할을 합니다. `/oauth2/authorization/{registrationId}` 와 일치하는지 확인해서 일치하면 `registrationId` 를 추출하고 이를 사용해서 `ClientRegistration` 을 가져와 `OAuth2AuthorizationRequest` 를 빌드합니다.

​	**`OAuth2AuthorizationRequest`** 클래스는 토큰 엔드포인트 요청 파라미터를 담은 객체로서 인가 응답을 연계하고 검증할 때 사용합니다.

​	**`OAuth2AuthorizationRequestRepository`** 인가 요청을 시작한 시점부터 인가 요청을 받는 시점까지 (리다이렉트) `OAuth2AuthorizationRequest` 를 유지해줍니다.

아래는 code 를 요청하는 과정입니다.

![image-20230722204951947](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722204951947.png)

만약 코드 요청 uri 일 경우 `DefaultOAuth2AUthorizationRequestResolver` 에서 해당 uri 인지 확인한 후 `OAuth2AuthorizationRequest` 를 만들고 `Repository` 에 저장한 후 redirect uri 로 code 요청을 보냅니다.

만약 인가가 없는데 코드 요청 uri 가 아닐 경우 `ExceptionTranslationFilter` 에 걸려 `EntryPoint` 를 통해 코드 요청 uri 로 이동합니다.

## 코드 레벨

먼저 기본 설정에서 `/login` 으로 이동하면 아래와 같이 로그인 페이지가 뜹니다.

![image-20230722210326674](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722210326674.png)

해당 로그인을 클릭하면 `OAuth2AuthorizationRequestRedirectFilter` 에서 리다이렉트가 시작됩니다.

![image-20230722210505745](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722210505745.png)

`doFilterInternal()` 을 보면 `authorizationRequestResolver` 에서 `resolve()` 메서드를 통해 request 가 code 요청 uri 인지 확인합니다.

![image-20230722210845000](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722210845000.png)

`resolve()` 메서드에서 `RegistrationId` ("keycloak") 를 얻습니다. 그리고 `redirectUriAction` 으로 default 값인 "login" 을 설정합니다. 그리고 `private` 오버로딩 메서드인 `resolve()` 를 내부적으로 호출합니다.

![image-20230722212057916](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722212057916.png)

해당 `resolve()` 를 보면 `clientRegistration` 정보를 이용해서 빌더 클래스를 만들고 redirectUri 를 결정합니다. 여기서 `redirectUri` 는 `http://localhost:8081/login/oauth2/code/keycloak` 입니다. 해당 Uri 는 인가 서버에 등록되어있어야 합니다. 최종적으로 `builder` 를 구성해서 `.build()` 를 하면 인가서버에 전달되는 최종 정보인 `OAuth2AuthorizationRequest` 가 만들어집니다.

![image-20230722212406920](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722212406920.png)

다시 `doFilterInternal()` 메서드로 오면 `OAuth2AuthorizationRequest` 가 있으므로 `sendRedirectForAuthorization()` 이 실행됩니다.

![image-20230722212552860](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722212552860.png)

해당 메서드에서는 `authorizationRequestRepository` 에 해당 `OAuth2AuthorizationRequest` 을 저장한 후 `sendRedirect()` 로 인가 서버로 리다이렉트합니다.

그러면 사용자는 다음과 같은 화면을 받습니다.

![image-20230722212656895](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722212656895.png)

해당 페이지에서 로그인을 하고 성공하면 redirectUri 인 `localhost:8081/login/oauth2/code/keycloack` 로 가게 됩니다. 그러면 `OAuthLoginAUthenticationFilter` 에서 해당 uri 를 필터링하고 있기 때문에 `attemptAuthentication()` 가 실행됩니다.

![image-20230722213259345](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722213259345.png)

보면 `request` 에서 `params` 를 가지고 있는데요. 처음에 보낸 `state` 와 임시 `code` 를 가지고 있습니다.

해당 필터의 동작은 아래에서 확인해보겠습니다.

# Access Token 교환하기

​	주요 클래스는 `OAuth2LoginAuthenticationFilter` 입니다. `"/login/oauth/code/"` 로 오는 요청에 대해 필터링합니다. 인가서버로부터 리다이렉트 되면서 전달된 code 를 인가서버의 Access Token 으로 교환하고 Access Token 이 저장된 `OAuth2LoginAuthenticationToken` 을 `AuthenticationManager` 에 위임하여 `UserInfo` 정보를 요청해서 최종 사용자에 로그인합니다. 그리고 `OAuth2AuthorizedClientRepository` 를 사용하여 `OAuth2AuthorizedClient` 를 저장합니다. 인증에 성공하면 `OAuth2AuthenticationToken` 이 생성되고 `SecurityContext` 에 저장되어 인증 처리를 완료합니다.

## OAuth2LoginAuthenticationProvider

​	인가서버로부터 리다이렉트 된 이후 프로세스를 처리하며 Access Token 으로 교환하고 이 토큰을 사용하여 `UserInfo` 처리를 담당합니다. Scope 에 openid 가 포함되어 있으면 `OidcAuthorizationCodeAuthenticationProvider` 를 호출하고 아니면 `OAuth2AuthorizationCodeAuthenticationProvider` 를 호출하도록 제어합니다.

​	`DefaultAuthorizationCodeTokenResponseClient` 클래스는 인가서버의 token 엔드 포인트로 통신을 담당하며 `AccessToken` 을 받은 후 `OAuth2AccessTokenResponse` 에 저장하고 반환합니다.

![image-20230722232622595](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722232622595.png)

## 요청 흐름

​	흐름이 복잡하기는 하지만 4가지 큰 흐름으로 나눠서 보겠습니다.

![image-20230722233752678](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230722233752678.png)

1. `HttpSessionOAuth2AuthorizationRequestRepository` 에는 1차 code 요청에서의 Request 객체가 있고, 인가서버로부터 코드를 응답 내용으로 Response 객체를 만듭니다. 해당 request, response 로 `OAuth2LoginAuthenticationToken` 을 만듭니다.
2. AuthenticationProvider 로 인증 절차를 시작합니다. 위 흐름은 OIDC 가 아닌 일반적인 OAuth2 인증 절차입니다.
3. `DefaultAuthorizationCodeTokenResponseClient` 에서 `RequestEntity` 를 만들어서 `RestTemplate` 으로 토큰을 요청합니다. 그러면 Token 이 담겨진 `ResponseEntity` 가 만들어집니다.
4. `ResponseEntity` 에 담겨진 토큰을 포함한 정보들로 다시  `OAuth2UserRequest` 를 만들어서 `DefaultOAuth2UserService` 로 전송합니다. 해당 클래스는 `RequestEntity` 를 만들어서 UserInfo 엔드포인트로 요청을 보내고 최종 사용자 속성을 획득하여 `OAuth2User` 타입의 객체를 반환합니다.

# Oauth 2.0 User 모델 소개

​	UserInfo 를 받아오는 흐름은 아래와 같습니다.

![image-20230723114448187](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230723114448187.png)

`OAuth2UserService` 의 구현체로 `DefaultOAuth2UserService` 와 `OidcUserService` 가 제공됩니다. 해당 클래스들은 액세스 토큰을 사용해서 `UserInfo` 엔드포인트 요청으로 최종 사용자의 (리소스 소유자) 속성을 가져오며 `OAuth2User` 타입의 객체를 리턴합니다.

1. 먼저 Cleint 가 `/token` 으로 받은 토큰으로 `userinfo` 엔드포인트로 요청하고 사용자 속성(userAttributes) 를 리턴합니다. 그러면 최종적으로 `OAuth2User` 타입으로 리턴합니다.
2. `/token?scope=openid` 로 accessToken 과 id_token 을 받으면 `OidcUserService` 에서 인가서버와 통신하지 않고 인증처리를 합니다. 그리고 `OidcUser` 를 반환합니다.
3. 필요에 따라서 Scope 조건에 따라 `OidcUserService` 가 `DefaultOAuth2UserService` 로 사용자 정보를 조회할 수도 있습니다. 필수는 아닙니다.

## OAuth2User & OidcUser

​	시큐리티는 UserAttributes 및 ID Token Claims 을 집계 & 구성하여 OAuth2User 와 OidcUser 타입의 클래스를 제공합니다.

**OAuth2User**

- OAuth 2.0 Provider 에 연결된 사용자 주체를 나타냅니다.
- 최종 사용자의 인증에 대한 정보인 `Attributes` 를 포함하고 있으며 first name, middle name, last name, email, phone number, address 등으로 구성됩니다.
- 기본 구현체는 **`DefaultOAuth2User`** 이며 인증 이후 `Authentication` 의 `principal` 속성에 저장됩니다.

**OidcUser**

- <u>OAuth2User 를 상속한 인터페이스</u>이며 OIDC Provider 에 연결된 사용자 주체를 나타냅니다.
- 최종 사용자의 인증에 대한 정보인 `Claims` 를 포함하고 있으며 `OidcIdToken` 및 `OidcUserInfo` 에서 집계 및 구성됩니다.
- •기본 구현체는 **`DefaultOidcUser`** 이며 `DefaultOAuth2User` 를 상속하고 있으며 인증 이후 `Authentication` 의 `principal` 속성에 저장됩니다.

## 구조

![image-20230723120428946](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230723120428946.png)

​	OAuth 2.0 로그인을 통해 인증받은 최종 사용자의 Principal 에는 `OAuth2User` 혹은 `OidcUser` 타입의 객체가 저장됩니다. `OAuth2UserAuthority` 는 인가서버로부터 수신한 scope 정보를 집계해서 권한정보를 구성합니다.

​	`OidcUser` 객체를 생성할 때 ID 토큰이 필요한데 이 때 JSON 웹 토큰 (JWT)으로 된 ID 토큰은 JSON Web Signature (JWS)로 서명이 되어 있기 때문에 반드시 정해진 알고리즘에 의한 검증이 성공하면 `OidcUser` 객체를 생성 해야 합니다.

## 코드 레벨

​	AccessToken, idToken 을 가지고 인가 서버와 통신을 하는 부분을 살펴보겠습니다. <u>아래 코드는 이해를 위한 목적이며 실제로는 모두 구현되어있어서 직접 구현할 필요는 없습니다.</u>

### DefaultOAuth2UserService

```java
@RestController
public class IndexController {

    @Autowired private ClientRegistrationRepository clientRegistrationRepository;

    @GetMapping("/user")
    public OAuth2User user(String accessToken){

        ClientRegistration clientRegistration = clientRegistrationRepository.findByRegistrationId("keycloak"); //1

        OAuth2AccessToken oAuth2AccessToken =
                new OAuth2AccessToken(OAuth2AccessToken.TokenType.BEARER, accessToken, Instant.now(), Instant.MAX); //2

        ` oAuth2UserRequest = new OAuth2UserRequest(clientRegistration, oAuth2AccessToken); //3
        DefaultOAuth2UserService defaultOAuth2UserService = new DefaultOAuth2UserService();
        OAuth2User oAuth2User = defaultOAuth2UserService.loadUser(oAuth2UserRequest); //4

        return oAuth2User;
    }
}
```

`/user` 로 accessToken 을 받아 `OAuth2User` 를 반환하는 엔드포인트입니다. **해당 로직은 먼저 accessToken 을 얻은 후 실행되어야 합니다.** 저는 password Grant Type 으로 accessToken 을 얻은 후 진행했습니다.

1. `clientRegistration` 정보를 `ClientRegistrationRepository` 에서 추출합니다.
2. `oAuth2AccessToken` 을 만듭니다. 발행일 및 만료일은 임의로 지정합니다.
3. `clientRegistration` 와 `oAuth2AccessToken` 을 통해 요청 정보인 `OAuth2UserRequest` 를 만듭니다.
4. `defaultOAuth2UserService.loadUser()` 를 통해 `/token` 엔드포인트에 userInfo 를 요청합니다. `OAuth2User` 가 반환됩니다.

![image-20230723131121688](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230723131121688.png)

이런 식으로 `OAuth2User` 를 반환받습니다.

### OidcUserService

```java
@GetMapping("/oidc")
public OAuth2User oidc(String accessToken, String idToken){

    ClientRegistration clientRegistration = clientRegistrationRepository.findByRegistrationId("keycloak");

    OAuth2AccessToken oAuth2AccessToken =
            new OAuth2AccessToken(OAuth2AccessToken.TokenType.BEARER, accessToken, Instant.now(), Instant.MAX); 

    Map<String, Object> idTokenClaims = new HashMap<>(); //1
    idTokenClaims.put(IdTokenClaimNames.ISS, "http://localhost:8080/realms/oauth2");
    idTokenClaims.put(IdTokenClaimNames.SUB, "5a8b2f03-09f0-427f-a1f1-a3a7e8e53c19");
    idTokenClaims.put("preferred_username", "user");

    OidcIdToken oidcIdToken = new OidcIdToken(idToken, Instant.now(), Instant.MAX, idTokenClaims);

    OidcUserRequest oidcUserRequest = new OidcUserRequest(clientRegistration, oAuth2AccessToken, oidcIdToken); //2
    OidcUserService oidcUserService = new OidcUserService();
    OAuth2User oAuth2User = oidcUserService.loadUser(oidcUserRequest); //3

    return oAuth2User;
}
```

`/oidc` 로 accessToken, idToken 을 받아 `OAuth2User` 를 반환하는 엔드포인트입니다. **해당 로직도 먼저 accessToken 과 idToken 을 얻은 후 실행되어야 합니다.**  password Grant Type 의 scope 에 openid 를 주고 accessToken, idToken 을 얻은 후 진행했습니다.

1. `OidcIdToken` 을 생성하기 위해 Claims 를 만듭니다. `IdTokenClaimNames.SUB` 는 user 의 Subject 입니다. keycloack 에 있습니다.
2. `clientRegistration`, `accessToken`, `idToken` 을 이용해서 `OidcUserRequest` 을 만듭니다. 
3. `oidcUserService.loadUser()` 으로 `OAuth2User` 을 반환받습니다.

![image-20230723131702638](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230723131702638.png)

인증처리까지 한 번에 된 객체를 반환받습니다.

# UserInfo 엔드포인트 요청하기

## accessToken 으로 요청

![image-20230724102745178](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724102745178.png)

openid 가 아닌 일반적인 OAuth 요청을 보겠습니다. **`DefaultOAuth2UserService`** 클래스의 `loadUser()` 메서드를 통해 userinfo 엔드포인트로 요청합니다. 그리고 받은 값을 `DefaultOAuth2User` 로 변경한 뒤 인증 객체로 변환하여 저장합니다.

## OpenId 로 요청

![image-20230724103908499](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724103908499.png)

​	위 흐름에서 `OidcUserService` 위의 과정은 앞에서 살펴본 과정입니다. `OidcUserService` 의 `loadUser()` 메서드로 `OAuth2User` 를 꺼내는데, 이때 Scope 중에 OIDC 사양에 부합하는 Scope 가 있다면 인가서버의 UserInfo 엔드포인트로 요청객체를 다시 보냅니다.

![image-20230724104059043](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724104059043.png)

​	위 흐름은 인가서버의 UserInfo 엔드포인트로 요청객체를 다시 보내고 응답을 받는 과정입니다. 기본 OAuth 의 userinfo 요청/응답과 크게 다르지 않습니다.

# OpenID Connect 로그아웃

​	로그아웃은 `LogoutFilter` 를 사용합니다. 클라이언트는 로그아웃 엔드포인트를 사용하여 웹 브라우저에 대한 세션과 쿠키를 지우고 로그아웃 성공 후 `OidcClientInitiatedLogoutSuccessHandler` 를 호출하여 OpenID Provider 세션 로그아웃 요청합니다.

​	그리고•OpenID Provider 로그아웃이 성공하면 지정된 위치로 리다이렉트 합니다. 인가서버 메타데이터 사양에 있는 로그아웃 엔드 포인트는 `end_session_endpoint` 로 정의되어 있습니다.

## 로그아웃 설정

```java
@Configuration
public class OAuth2ClientConfig {

    private final ClientRegistrationRepository clientRegistrationRepository;

    public OAuth2ClientConfig(ClientRegistrationRepository clientRegistrationRepository) {
        this.clientRegistrationRepository = clientRegistrationRepository;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeRequests(authorize ->
                        authorize
                                .anyRequest().permitAll()
                        )
                .oauth2Login(Customizer.withDefaults())
                .logout(logout ->
                        logout
                                .logoutSuccessHandler(oidcLogoutSuccessHandler())
                                .invalidateHttpSession(true)
                                .clearAuthentication(true)
                                .deleteCookies("JSESSIONID"));
        ;

        return http.build();
    }

    private LogoutSuccessHandler oidcLogoutSuccessHandler() {

        OidcClientInitiatedLogoutSuccessHandler successHandler = new OidcClientInitiatedLogoutSuccessHandler(clientRegistrationRepository);

        successHandler.setPostLogoutRedirectUri("http://localhost:8081/login");

        return successHandler;
    }
}
```

​	`http.logout()` 을 통해 로그아웃을 만듭니다. `successHandler` 를 지정하고 (리다이렉트) 세션과 인증 객체를 지우도록 설정합니다. 그리고 쿠키까지 지웁니다. 로그아웃 성공 후 리다이렉트 uri 는 keycloack 에 저장되어있어야 합니다.

![image-20230724115441619](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724115441619.png)

로그아웃을 시도(POST /logout) 하면 다음과 같이 LogoutFilter 가 시작됩니다.

![image-20230724115623132](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724115623132.png)

이중 this.handler 는 logoutHandlers 로 로그아웃을 시도할 때 해야할 여러가지 일들을 합니다. (쿠키제거, 세션제거, Csrf 제거 등등..)

![image-20230724115808652](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724115808652.png)

그리고 logoutSuccessHandler 중 `AbstractAuthenticationTargetUrlRequestHandler` 의 `handle()` 메서드에서 로그아웃을 하면서 인가 서버의 세션 정보를 삭제하도록 요청합니다. 이때 로그아웃 엔드 포인트인 `end_session_endpoint` 로 호출됩니다.

# Spring MVC 인증 객체 참조하기

​	스프링 API 계층에서 인증 객체가 바인딩되는 방법은 2가지가 있습니다.

1. **Authentication**
   - `public void dashboard(Authentication authentication) {}`
   - `oauth2Login()` 로 인증을 받게 되면 `Authentication` 은 `OAuth2AuthenticationToken` 타입의 객체로 바인딩됩니다.
   - `principal` 에는 `OAuth2User` 타입 혹은 `OidcUser` 타입의 구현체가 저장됩니다.
   - `DefaultOAuth2User` 는 `/userInfo` 엔드포인트 요청으로 받은 User 클레임 정보로 생성된 객체입니다.
   - `DefaultOidcUser` 는 OpenID Connect 인증을 통해 ID Token 및 클레임 정보가 포함된 객체입니다.
2. **@AuthenticationPrincipal**
   - `public void dashboard(@AuthenticationPrincipal OAuth2User principal or OidcUser principal) {}`
   - `AuthenticationPrincipalArgumentResolver` 클래스에서 요청을 가로채어 바인딩 처리를 합니다. 
   - `Authentication` 를 `SecurityContext` 로부터 꺼내어 와서 `Principal` 속성에 `OAuth2User` 혹은 `OidcUser` 타입의 객체를 저장합니다.

## 코드 레벨

​	컨트롤러에서 파라미터로 받습니다.

```java
@RestController
public class IndexController {

    @Autowired private ClientRegistrationRepository clientRegistrationRepository;

    @GetMapping("/")
    public String index(){

        return "index";
    }

    @GetMapping("/user")
    public OAuth2User user(Authentication authentication){
        OAuth2AuthenticationToken authenticationToken = (OAuth2AuthenticationToken) authentication;
        OAuth2User oauth2User = (OAuth2User) authenticationToken.getPrincipal();
        return oauth2User;
    }

    @GetMapping("/oauth2User")
    public OAuth2User oAuth2User(@AuthenticationPrincipal OAuth2User oAuth2User){
        System.out.println("oauth2User = " + oAuth2User);
        return oAuth2User;
    }

    @GetMapping("/oidcUser")
    public OidcUser oidcUser(@AuthenticationPrincipal OidcUser oidcUser){
        System.out.println("oauth2User = " + oidcUser);
        return oidcUser;
    }
}
```

기본 OAtuh 방식으로 받으면 `OAuth2User` 로 받을 수 있고, OIDC 방식으로 받으면 `OidcUser` 으로 받을 수 있습니다. OIDC 방식으로 받은 객체는 `OAuth2User` 로 바인딩할 수 있지만 반대로는 안됩니다.

# Authorization BaseUrl & Redirection BaseUrl

​	인가서버로 로그인을 요청하는 url 과 리다이렉트 url 을 지정하는 방법입니다.

![image-20230724204805291](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724204805291.png)

**Authorization BaseUrl** 은 `.authorizationEndPoint()` 로 지정합니다. 1단계 권한 부여 요청을 처리하는 **`OAuth2AuthorizationRequestRedirectFilter`** 에서 요청에 대한 매칭여부를 판단합니다. 설정에서 변경한 값이 클라이언트의 링크 정보와 일치하도록 맞추어야 합니다.

![image-20230724205042735](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724205042735.png)

인증 페이지로 가는 버튼을 클릭하면 `"oauth2/v1/authorization/keycloak"` 으로 이동합니다.

![image-20230724205146617](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724205146617.png)

**Redirection BaseUrl**

`redirectionEndpoint.**baseUri**("/login/v1/oauth2/code/\*")` 은 인가 응답의 baseUri 를 커스텀합니다. Token 요청을 처리하는 `OAuth2LoginAuthenticationFilter` 에서 요청에 대한 매칭여부를 판단합니다. 

​	SecurityConfig 파일 포함 총 3군데를 변경해야 합니다.

- `application.yml` 설정 파일에서 `registration` 속성의 `redirectUri` 설정에도 변경된 값을 적용해야 합니다.

  ![image-20230724205456507](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724205456507.png)

- 인가서버의 redirectUri 설정에도 변경된 값을 적용해야 합니다.

  ![image-20230724205537271](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724205537271.png)

`loginProcessingUrl("/login/v1/oauth2/code/*")` 를 설정해도 결과는 동일하지만 `redirectionEndpoint.baseUri` 가 더 우선입니다.

![image-20230724205359173](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724205359173.png)

# OAuth2AuthorizationRequestResolver

​	Authorization Code Grant 방식에서 클라이언트가 인가서버로 권한부여 요청할 때 실행되는 클래스로  OAuth 2.0 인가 프레임워크에 정의된 표준 파라미터 외에 다른 파라미터를 추가하는 식으로 인가 요청을 할 때 사용합니다.

![image-20230724210126715](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724210126715.png)

먼저 아래와 같이 3개의 client 로 로그인하는 방식을 살펴보겠습니다.

![image-20230724232440118](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724232440118.png)

기존 oauth2-client-app 에다가 PKCE 방식과 implicit 방식을 추가했습니다.

그리고 로그인 기능을 구현하는 home url 을 지정합니다.

```html
!DOCTYPE html SYSTEM "http://www.thymeleaf.org/dtd/xhtml1-strict-thymeleaf-4.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:th="http://www.thymeleaf.org"
      xmlns:sec="http://www.thymeleaf.org/extras/spring-security">

<head>
  <meta charset="UTF-8">
  <title>Insert title here</title>
  <script>
    function authorizationCode(){
      window.location = new URL('http://localhost:8081/oauth2/authorization/keycloak1');
    }

    function authorizationCodeWithPKCE(){
      window.location = new URL('http://localhost:8081/oauth2/authorization/keycloakWithPKCE');
    }

    function implicit(){
      window.location = new URL('http://localhost:8081/oauth2/authorization/keycloak2');
    }

  </script>
</head>
<body>
<div>Welcome</div>
<div sec:authorize="isAuthenticated()"><a th:href="@{/logout}">Logout</a></div>
<form sec:authorize="isAnonymous()" action="#">
  <p><input type="button" onclick="authorizationCode()" value="AuthorizationCode Grant" />
  <p><input type="button" onclick="authorizationCodeWithPKCE()" value="AuthorizationCode Grant with PKCE" />
  <p><input type="button" onclick="implicit()" value="Implicit Grant" />
</form>
</body>
</html>
```

home 에 접속하면 아래와 같이 나옵니다.

![image-20230724232647560](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724232647560.png)

첫번째 방법은 앞에서 한 방법입니다. 세번째 방법은 Implicit 으로 요청합니다. Url 로 accessToken 이 옵니다.

![image-20230724232736520](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230724232736520.png)

​	Implicit 에서 redirect uri 는 `/home` 으로 지정했습니다. 스프링 시큐리티는 Implicit 을 지원하지 않으므로 커스텀으로 accessToken 을 userInfo 로 보내야 합니다.

​	PKCE  방법은 인가 서버에서 먼저 아래와 같이 설정합니다.

![image-20230725174405471](../../images/2023-07-22-[Security OAuth2] Section 7. OAuth 2.0 Client - oauth2Login()/image-20230725174405471.png)

​	두번째 방법인 PKCE 는 문제가 좀 있는데요. `application.yml` 에서 `clientAuthorizationMethod` 를 `none` 으로 해야만 PKCE 를 사용할 수 있는데, `clientAuthorizationMethod ` 이 `none` 이면 `client`-secret 을 `request` 에 포함하지 않습니다. 따라서 `code` 까지 요청할 수 있지만 accessToken 을 받지 못합니다.

## PKCE 문제 해결

PKCE 방식을 사용하려면 `OAuth2AuthorizationRequestResolver` 클래스를 커스텀으로 만들어야 합니다.

```java
ublic class CustomOAuth2AuthorizationRequestResolver implements OAuth2AuthorizationRequestResolver {

    private static final String REGISTRATION_ID_URI_VARIABLE_NAME = "registrationId";
    private static final Consumer<OAuth2AuthorizationRequest.Builder> DEFAULT_PKCE_APPLIER = OAuth2AuthorizationRequestCustomizers
            .withPkce();
    private ClientRegistrationRepository clientRegistrationRepository;
    DefaultOAuth2AuthorizationRequestResolver defaultResolver;

    private final AntPathRequestMatcher authorizationRequestMatcher;

    public CustomOAuth2AuthorizationRequestResolver(ClientRegistrationRepository clientRegistrationRepository, String authorizationRequestBaseUri) {
        this.clientRegistrationRepository = clientRegistrationRepository;
        this.authorizationRequestMatcher = new AntPathRequestMatcher(
                authorizationRequestBaseUri + "/{" + REGISTRATION_ID_URI_VARIABLE_NAME + "}");

        defaultResolver = new DefaultOAuth2AuthorizationRequestResolver(clientRegistrationRepository, authorizationRequestBaseUri);
    }

    @Override
    public OAuth2AuthorizationRequest resolve(HttpServletRequest request) {
        String registrationId = resolveRegistrationId(request);
        if (registrationId == null) {
            return null;
        }

        ClientRegistration clientRegistration = clientRegistrationRepository.findByRegistrationId(registrationId);
        if(registrationId.equals("keycloakWithPKCE")){
            OAuth2AuthorizationRequest oAuth2AuthorizationRequest = defaultResolver.resolve(request);
            return customResolve(oAuth2AuthorizationRequest, clientRegistration);

        }


        return defaultResolver.resolve(request);
    }

    @Override
    public OAuth2AuthorizationRequest resolve(HttpServletRequest request, String clientRegistrationId) {
        ClientRegistration clientRegistration = clientRegistrationRepository.findByRegistrationId(clientRegistrationId);
        if(clientRegistrationId.equals("keycloakWithPKCE")){
            OAuth2AuthorizationRequest oAuth2AuthorizationRequest = defaultResolver.resolve(request);
            return customResolve(oAuth2AuthorizationRequest, clientRegistration);
        }
        return defaultResolver.resolve(request,clientRegistrationId);
    }

    private OAuth2AuthorizationRequest customResolve(OAuth2AuthorizationRequest authorizationRequest, ClientRegistration clientRegistration) {

        Map<String,Object> extraParam = new HashMap<>();
        extraParam.put("customName1","customValue1");
        extraParam.put("customName2","customValue2");
        extraParam.put("customName3","customValue3");

        OAuth2AuthorizationRequest.Builder builder = OAuth2AuthorizationRequest
                .from(authorizationRequest)
                .additionalParameters(extraParam)
                ;
        DEFAULT_PKCE_APPLIER.accept(builder);

        return builder.build();
    }

    private String resolveRegistrationId(HttpServletRequest request) {
        if (this.authorizationRequestMatcher.matches(request)) {
            return this.authorizationRequestMatcher.matcher(request).getVariables()
                    .get(REGISTRATION_ID_URI_VARIABLE_NAME);
        }
        return null;
    }
}
```

대부분의 메서드나 로직은 `DefaultOAuth2AuthorizationRequestResolver` 와 같습니다. 다만 `if(clientRegistrationId.equals("keycloakWithPKCE"))` 을 체크해서 PKCE 방식이면 `customResolve()` 메서드를 실행시킵니다.

`OAuth2ClientConfig` 의 설정으로 `customOAuth2AuthenticationRequestResolver()` 을 등록하면 됩니다.

```java
@Configuration
public class OAuth2ClientConfig {

    private final ClientRegistrationRepository clientRegistrationRepository;

    public OAuth2ClientConfig(ClientRegistrationRepository clientRegistrationRepository) {
        this.clientRegistrationRepository = clientRegistrationRepository;
    }


    @Bean
    SecurityFilterChain oauth2SecurityFilterChain(HttpSecurity http) throws Exception {
        http.authorizeRequests((requests) -> requests.antMatchers("/home").permitAll()
                .anyRequest().authenticated());
        http.oauth2Login(authLogin ->
                authLogin.authorizationEndpoint(authEndpoint ->
                        authEndpoint.authorizationRequestResolver(customOAuth2AuthenticationRequestResolver())));
        http.logout().logoutSuccessUrl("/home");
        return http.build();
    }

    private OAuth2AuthorizationRequestResolver customOAuth2AuthenticationRequestResolver() {
        return new CustomOAuth2AuthorizationRequestResolver(clientRegistrationRepository, "/oauth2/authorization");
    }
}
```

