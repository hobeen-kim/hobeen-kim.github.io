---
categories: "inflearn"
tag: ["OAuth2ClientConfigurer", "DefaultOAuth2AuthroizedClientManager", "인증 흐름"]
series: "Spring Boot 기반으로 개발하는 Spring Security OAuth2"
teaser: "Spring Security2"
title: "[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()"
description: "Spring Security Section 8. OAuth 2.0 Client - oauth2Client() 내용입니다."
---

# OAuth2ClientConfigurer 초기화 이해

`OAuth2ClientConfigurer` 를 초기화하면 다음과 같은 클래스가 만들어집니다.

![image-20230725175910780](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230725175910780.png)

설정은 아래와 같이 합니다.

```java
@Configuration
public class OAuth2ClientConfig {

    @Bean
    SecurityFilterChain oauth2SecurityFilterChain(HttpSecurity http) throws Exception {
        http.authorizeRequests((requests) -> requests.antMatchers("/home").permitAll()
                .anyRequest().authenticated())
                .oauth2Client(Customizer.withDefaults());
        return http.build();
    }
}
```

`.oauth2Client()` 와 `.oauth2Login()` 의 차이점은, Login 은 인증절차까지 함께 있지만 Client 는 인가절차만 있다는 점입니다.

# OAuth2AuthorizedClient

​	**`OAuth2AuthorizedClient`** 는 인가받은 클라이언트를 의미하는 클래스입니다. 최종 사용자(리소스 소유자) 가 클라이언트에게 리소스에 접근할 수 있는 권한을 부여하면, 클라이언트를 인가된 클라이언트로 간주합니다.

​	`OAuth2AuthorizedClient` 는 `AccessToken` 과 `RefreshToken` 을 `ClientRegistration` (클라이언트) 와 권한을 부여한 최종 사용자인 `Principal` 과 함께 묶어줍니다. 그러면 `OAuth2AuthorizedClient` 의 AccessToken 을 사용해서 리소스 서버의 자원에 접근 할 수 있으며 인가서버와의 통신으로 토큰을 검증할 수 있습니다.

`OAuth2AuthorizedClient` 의 `ClientRegistration` 과 `AccessToken` 을 사용해서 UserInfo 엔드 포인트로 요청할 수 있습니다.

아래와 같이 요청합니다.

![image-20230725233317032](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230725233317032.png)

- `OAuth2AuthorizedClientRepository` 는 다른 웹 요청이 와도 동일한 `OAuth2AuthorizedClient` 를 유지하는 역할을 담당합니다. `OAuth2AuthorizedClientService` 에게 `OAuth2AuthorizedClient` 의 저장, 조회, 삭제 처리를 위임합니다.
- `•OAuth2AuthorizedClientService` 는 어플리케이션 레벨에서 OAuth2AuthorizedClient 를 관리(저장, 조회, 삭제 )하는 일을 합니다.

## ClientController

`code` 를 얻어서 자체적으로 인증하는 단계입니다. `/userInfo` 로 요청해서 객체를 얻은 뒤 토큰을 만들고 스레드로컬에 저장합니다.

```java
@Controller
public class ClientController {

    @Autowired private OAuth2AuthorizedClientRepository authorizedClientRepository;
    @Autowired private OAuth2AuthorizedClientService authorizedClientService;

    @GetMapping("/client")
    public String client(HttpServletRequest request, Model model){

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        //1
        String clientRegistrationId = "keycloak"; //2

        OAuth2AuthorizedClient authorizedClient1 = authorizedClientRepository
                .loadAuthorizedClient(clientRegistrationId, authentication, request); //3

        OAuth2AuthorizedClient authorizedClient2 = authorizedClientService
                .loadAuthorizedClient(clientRegistrationId, authentication.getName()); //4

        OAuth2AccessToken accessToken = authorizedClient1.getAccessToken(); //5

        OAuth2UserService oAuth2UserService = new DefaultOAuth2UserService();
        OAuth2User oAuth2User = oAuth2UserService.loadUser(new OAuth2UserRequest(authorizedClient1.getClientRegistration(), accessToken)); //6

        OAuth2AuthenticationToken authenticationToken =
                new OAuth2AuthenticationToken(oAuth2User, List.of(new SimpleGrantedAuthority("ROLE_USER")),
                        authorizedClient1.getClientRegistration().getRegistrationId()); //7

        SecurityContextHolder.getContext().setAuthentication(authenticationToken); //8

        model.addAttribute("accessToken", accessToken.getTokenValue());
        model.addAttribute("refreshToken", authorizedClient1.getRefreshToken().getTokenValue());
        model.addAttribute("principalName", oAuth2User.getName());
        model.addAttribute("clientName", authorizedClient1.getClientRegistration().getClientName());

        return "client"; //9
    }
}
```

1. 저장되어 있는 인증 객체를 꺼냅니다. 현재는 인증이 되지 않았기 때문에 `AnonymousAuthenticationToken` 입니다.
2. `clientRegistrationId` 를 설정합니다. `yml` 에서 정보를 가져오기 위함입니다.
3. `authorizedClientRepository` 에서 `.loadAuthorizedClient()` 로 `"/token"` 으로 요청해 `accessToken`, `refreshToken` 을 받습니다.
4. `authorizedClientService` 도 `authorizedClientRepository` 와 같은 역할입니다.
5. `OAuth2AuthorizedClient` 객체에서 `accessToken` 을 꺼냅니다.
6. `DefaultOAuth2UserService` 으로 `"/userinfo"` 로 user 정보를 받습니다. 이 때 `accessToken` 을 사용합니다.
7. `DefaultOAuth2UserService` 에서 받은 인증 객체인 `OAuth2User` 를 통해 `OAuth2AuthenticationToken` 를 만듭니다.
8. `OAuth2AuthenticationToken` 을 스레드로컬에 저장합니다.
9. 화면에 렌더링할 정보들을 model 에 담고 client 페이지를 리턴합니다. 아래와 같이 표시됩니다.

![image-20230726004737182](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230726004737182.png)

## OAuth2ClientConfig

​	설정정보입니다. 로그인 시도 페이지인 `/home` 과 code 발행 후 리다이렉트 위치인 `/client` 는 permitAll 로 합니다.

```java
@Configuration
public class OAuth2ClientConfig {

    @Bean
    SecurityFilterChain oauth2SecurityFilterChain(HttpSecurity http) throws Exception {
        http.authorizeRequests((requests) -> requests
                        .antMatchers("/home", "/client").permitAll()
                        .anyRequest().authenticated())
                .oauth2Client(Customizer.withDefaults());
        return http.build();
    }
}
```

## application.yml

```yml
server:
  port: 8081

spring:
  security:
    oauth2:
      client:
        registration:
          keycloak:
            client-id: oauth2-client-app
            client-secret: LAk7jhgzab8xJIurXyamYFuLe5vtBEAZ
            client-name: oauth2-client-app
            authorization-grant-type: authorization_code
            scope: profile, openid
            client-authentication-method: client_secret_basic
            redirect-uri: http://localhost:8081/client
            provider: keycloak

        provider:
          keycloak:
            issuer-uri: http://localhost:8080/realms/oauth2
            authorization-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/auth
            token-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/token
            user-info-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/userinfo
            jwk-set-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/certs
            user-name-attribute: preferred_username

```

`redirect-uri` 을 `http://localhost:8081/client` 로 합니다.

# DefaultOAuth2AuthorizedClientManager

`DefaultOAuth2AuthorizedClientManager` 는 `OAuth2AuthorizedClient` 를 전반적으로 관리하는 인터페이스로, `OAuth2AuthorizedClientProvider` 로 OAuth 2.0 클라이언트에 권한을 부여합니다.

![image-20230726095315879](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230726095315879.png)

​	`OAuth2AuthorizedClientService` 나 `OAuth2AuthorizedClientRepository` 에 `OAuth2AuthorizedClient` 저장을 위임한 후 **`OAuth2AuthorizedClient`** 을 최종 반환합니다.

​	사용자 정의 `OAuth2AuthorizationSuccessHandler` 및 `OAuth2AuthorizationFailureHandler` 를 구성하여 성공/실패 처리를 변경할 수 있습니다.

​	invalid_grant 오류로 인해 권한 부여 시도가 실패하면 이전에 저장된 `OAuth2AuthorizedClient` 가 `OAuth2AuthorizedClientRepository` 에서 제거됩니다.

아래는 `DefaultOAuth2AuthorizedClientManager` 가 가진 각각의 클래스 특징입니다.

![image-20230726095354692](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230726095354692.png)

구조는 아래와 같은데, 인증된 사용자일 경우 `OAuth2AuhroizedClientService` 에서 메모리나 DB 에 저장하게 됩니다. 또한 `SuccessHandler` 와 `FailureHandler` 가 있습니다.

![image-20230726095528116](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230726095528116.png)

## DefaultOAuth2AuthorizedClientManager 기본 환경 구성

 스프링 시큐리티의 `OAuth2Login` 필터에 의한 자동 인증처리를 하지 않고 <u>`DefaultOAuth2AuthorizedClientManager` 클래스를 사용하여 Spring MVC 에서 **직접** 인증처리를 하는 로그인 기능을 구현</u>하겠습니다.

### application.yml

```yml
server:
  port: 8081

spring:
  security:
    oauth2:
      client:
        registration:
          keycloak:
            client-id: oauth2-client-app
            client-secret: LAk7jhgzab8xJIurXyamYFuLe5vtBEAZ
            client-name: oauth2-client-app
            authorization-grant-type: authorization_code
            scope: profile, openid
            client-authentication-method: client_secret_basic
            redirect-uri: http://localhost:8081/client
            provider: keycloak

        provider:
          keycloak:
            issuer-uri: http://localhost:8080/realms/oauth2
            authorization-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/auth
            token-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/token
            user-info-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/userinfo
            jwk-set-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/certs
            user-name-attribute: preferred_username
```

`authorization_code` 방식입니다. `redirect-uri` 은`http://localhost:8081/client` 입니다.

### HomeController

```java
@Controller
public class HomeController {

    @GetMapping("/home")
    public String home(){
        return "index";
    }
}
```

### LoginController

```java
@Controller
public class LoginController {

    @GetMapping("/oauth2Login")
    public String oauth2Login(Model model, HttpServletRequest request, HttpServletResponse response){
        return "redirect:/";
    }

    @GetMapping("/logout")
    public String logout(Authentication authentication, HttpServletResponse response, HttpServletRequest request){

        SecurityContextLogoutHandler logoutHandler = new SecurityContextLogoutHandler(); // 로그아웃을 진행하는 핸들러
        logoutHandler.logout(request, response, authentication);

        return "redirect:/";
    }
}
```

로그인 및 로그아웃 핸들러입니다.

### ClientController

 위에서 사용했던 `/client` API 입니다. 인증 후 리다이렉트 위치입니다.

```java
@Controller
public class ClientController {

    @Autowired private OAuth2AuthorizedClientRepository authorizedClientRepository;
    @Autowired private OAuth2AuthorizedClientService authorizedClientService;

    @GetMapping("/client")
    public String client(HttpServletRequest request, Model model){

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String clientRegistrationId = "keycloak";

        OAuth2AuthorizedClient authorizedClient1 = authorizedClientRepository
                .loadAuthorizedClient(clientRegistrationId, authentication, request);

        OAuth2AuthorizedClient authorizedClient2 = authorizedClientService
                .loadAuthorizedClient(clientRegistrationId, authentication.getName());

        OAuth2AccessToken accessToken = authorizedClient1.getAccessToken();

        OAuth2UserService oAuth2UserService = new DefaultOAuth2UserService();
        OAuth2User oAuth2User = oAuth2UserService.loadUser(new OAuth2UserRequest(authorizedClient1.getClientRegistration(), accessToken));

        OAuth2AuthenticationToken authenticationToken =
                new OAuth2AuthenticationToken(oAuth2User, List.of(new SimpleGrantedAuthority("ROLE_USER")),
                        authorizedClient1.getClientRegistration().getRegistrationId());

        SecurityContextHolder.getContext().setAuthentication(authenticationToken);

        model.addAttribute("accessToken", accessToken.getTokenValue());
        model.addAttribute("refreshToken", authorizedClient1.getRefreshToken().getTokenValue());
        model.addAttribute("principalName", oAuth2User.getName());
        model.addAttribute("clientName", authorizedClient1.getClientRegistration().getClientName());

        return "client";
    }
}
```



### OAuth2ClientConfig

```java
@Configuration
public class OAuth2ClientConfig {

    @Bean
    SecurityFilterChain oauth2SecurityFilterChain(HttpSecurity http) throws Exception {
        http.authorizeRequests((requests) -> requests
                        .antMatchers("/", "/oauth2Login", "/client").permitAll()
                        .anyRequest().authenticated())
            .oauth2Client(Customizer.withDefaults())
        ;
        return http.build();
    }
}
```

`.oauth2Client(Customizer.withDefaults())` 로 기본설정을 사용합니다.

### AppConfig

```java
@Configuration
public class AppConfig {

    @Bean
    public OAuth2AuthorizedClientManager auth2AuthorizedClientManager(ClientRegistrationRepository clientRegistrationRepository,
                                                                      OAuth2AuthorizedClientRepository authorizedClientRepository) {

        OAuth2AuthorizedClientProvider auth2AuthorizedClientProvider = OAuth2AuthorizedClientProviderBuilder.builder()
                .authorizationCode()
                .password()
                .clientCredentials()
                .refreshToken()
                .build();

        DefaultOAuth2AuthorizedClientManager oAuth2AuthorizedClientManager = new DefaultOAuth2AuthorizedClientManager(clientRegistrationRepository, authorizedClientRepository);

        oAuth2AuthorizedClientManager.setAuthorizedClientProvider(auth2AuthorizedClientProvider);

        return oAuth2AuthorizedClientManager;
    }
}
```

`DefaultOAuth2AuthorizedClientManager` 를 빈으로 등록합니다. 생성자가 `ClientRegistrationRepository` 와 `OAuth2AuthorizedClientRepository` 를 받기 때문에 넣어줍니다. 그리고 `OAuth2AuthorizedClientProvider` 도 설정해줍니다.

### 로그인 과정

1. `DefaultOAuth2AuthorizedClientManager` 빈 생성 및 파라미터 초기 값들을 정의합니다.
2. 권한 부여 유형에 따라 요청이 이루어도록 `application.yml` 설정을 조정합니다.
3. `/oauth2Login` 주소로 권한 부여 흐름을 요청합니다.
4. `DefaultOAuth2AuthorizedClientManager` 에게 권한 부여를 요청합니다.
5. 권한 부여가 성공하면 `OAuth2AuthorizationSuccessHandler` 를 호출하여 인증 이후 작업을 진행합니다.
6. `DefaultOAuth2AuthorizedClientManager` 의 최종 반환값인 `OAuth2AuthorizedClient` 를 `OAuth2AuthorizedClientRepository` 에 저장합니다.
7. `OAuth2AuthorizedClient` 에서 Access Token 을 참조하여 `/userinfo` 엔드포인트 요청으로 최종 사용자 정보를 가져옵니다.
8. 사용자 정보와 권한을 가지고 인증객체를 만든 후 SecurityContext 에 저장하고 인증을 완료합니다.
9. 인증이 성공하면 1~8 번의 과정을 커스텀 필터를 만들어서 처리하도록 합니다.

## Resource Owner Password Flow

Resource Owner Password 방식의 인증 흐름입니다.

![image-20230726110920063](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230726110920063.png)

`OAuth2AuthorizedClientManager` 가 인가처리를 하는데 `OAuth2AuthorizedClient` 가 있다면 인증할 필요가 없고, 없다면 `PasswordOAuth2AuthorizedClientProvider` 에게 `/token` 엔드포인트로 요청하도록 합니다.

### UserInfo 요청

![image-20230726111240606](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230726111240606.png)

`OAuth2AuthorizedClient` 를 OAuth2UserService 로 넘겨서 `/userinfo` 엔드포인트와 통신하여 인증을 처리하고 결과를 저장합니다.

### application.yml

```yml
server:
  port: 8081

spring:
  security:
    oauth2:
      client:
        registration:

          keycloak:
            client-id: oauth2-client-app
            client-secret: LAk7jhgzab8xJIurXyamYFuLe5vtBEAZ
            client-name: oauth2-client-app
            authorization-grant-type: password
            scope: profile, openid
            client-authentication-method: client_secret_basic
            provider: keycloak

        provider:
          keycloak:
            issuer-uri: http://localhost:8080/realms/oauth2
            authorization-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/auth
            token-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/token
            user-info-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/userinfo
            jwk-set-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/certs
            user-name-attribute: preferred_username

```

이번에는 password 방식입니다.

### AppConfig

```java
@Configuration
public class AppConfig {

    @Bean
    public OAuth2AuthorizedClientManager auth2AuthorizedClientManager(ClientRegistrationRepository clientRegistrationRepository,
                                                                      OAuth2AuthorizedClientRepository authorizedClientRepository) {

        OAuth2AuthorizedClientProvider auth2AuthorizedClientProvider = OAuth2AuthorizedClientProviderBuilder.builder()
                .authorizationCode()
                .password()
                .clientCredentials()
                .refreshToken()
                .build();

        DefaultOAuth2AuthorizedClientManager oAuth2AuthorizedClientManager = new DefaultOAuth2AuthorizedClientManager(clientRegistrationRepository, authorizedClientRepository);

        oAuth2AuthorizedClientManager.setAuthorizedClientProvider(auth2AuthorizedClientProvider);
        oAuth2AuthorizedClientManager.setContextAttributesMapper(contextAttributesMapper());

        return oAuth2AuthorizedClientManager;
    }

    //인가 서버에 통신할 때 request 에 담긴 파라미터를 가지고 인가 요청을 하게 된다.
    private Function<OAuth2AuthorizeRequest, Map<String, Object>> contextAttributesMapper() {
        return oAuth2AuthorizeRequest -> {
            HashMap<String, Object> contextAttributes = new HashMap<>();
            HttpServletRequest request = oAuth2AuthorizeRequest.getAttribute(OAuth2AuthorizeRequest.class.getName());
            String username = request.getParameter(OAuth2ParameterNames.USERNAME);
            String password = request.getParameter(OAuth2ParameterNames.PASSWORD);

            if(StringUtils.hasText(username) && StringUtils.hasText(password)){
                contextAttributes.put(OAuth2AuthorizationContext.USERNAME_ATTRIBUTE_NAME, username);
                contextAttributes.put(OAuth2AuthorizationContext.PASSWORD_ATTRIBUTE_NAME, password);
            }

            return contextAttributes;
        };
    }
}
```

`OAuth2AuthorizedClientManager` 에 `contextAttributesMapper` 를 등록해줍니다. `contextAttributesMapper` 는 인가서버와 통신할 때 username 과 password 를 Map 형태로 담은 파라미터입니다.

### index.html

```html
<!DOCTYPE html SYSTEM "http://www.thymeleaf.org/dtd/xhtml1-strict-thymeleaf-4.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:th="http://www.thymeleaf.org"
      xmlns:sec="http://www.thymeleaf.org/extras/spring-security">

<head>
  <meta charset="UTF-8">
  <title>Insert title here</title>
  <script>
    function authorizationCode() {
      window.location = new URL('http://localhost:8081/oauth2/authorization/keycloak');
    }

  </script>
</head>
<body>
<div>Welcome</div>
<div sec:authorize="isAuthenticated()"><a th:href="@{/logout}">Logout</a></div>
<form sec:authorize="isAnonymous()" action="#">
  <p><input type="button" onclick="authorizationCode()" value="AuthorizationCode Grant" />

<div sec:authorize="isAnonymous()"><a th:href="@{/oauth2Login(username='user', password='1234')}">Password Flow</a></div>
</form>
</body>
</html>
```

`Password Flow` 를 보면 <a> 태그로 username 과 password 를 바로 보냅니다. 지금은 html 이지만 password grant type 방식은 서버와의 통신이기 때문에 미리 username 과 password 를 가지고 있다가 보내는 것을 의미합니다.

### LoginController

​	마지막으로 password 방식의 endPoint API 입니다. index.html 에서 `Password Flow` 를 클릭하면 해당 API 로 username 과 password 를 보냅니다.

```java
@Controller
public class LoginController {

    @Autowired
    private DefaultOAuth2AuthorizedClientManager oAuth2AuthorizedClientManager;

    @Autowired
    private OAuth2AuthorizedClientRepository oAuth2AuthorizedClientRepository;

    @GetMapping("/oauth2Login")
    public String oauth2Login(Model model, HttpServletRequest request, HttpServletResponse response){

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        OAuth2AuthorizeRequest authorizeRequest = OAuth2AuthorizeRequest
                .withClientRegistrationId("keycloak")
                .principal(authentication)
                .attribute(HttpServletRequest.class.getName(), request)
                .attribute(HttpServletResponse.class.getName(), response)
                .build(); //1

        OAuth2AuthorizationSuccessHandler successHandler = (authorizedClient, principal, attributes) -> {
            oAuth2AuthorizedClientRepository
                    .saveAuthorizedClient(authorizedClient, principal,
                            (HttpServletRequest) attributes.get(HttpServletRequest.class.getName()),
                            (HttpServletResponse) attributes.get(HttpServletResponse.class.getName()));
            System.out.println("authorizedClient = " + authorizedClient);
            System.out.println("principal = " + principal);
            System.out.println("attributes = " + attributes);
        };

        oAuth2AuthorizedClientManager.setAuthorizationSuccessHandler(successHandler); //2

        OAuth2AuthorizedClient authorizedClient = oAuth2AuthorizedClientManager.authorize(authorizeRequest); //3

        if(authorizedClient != null){
            OAuth2UserService<OAuth2UserRequest, OAuth2User> oAuth2UserService = new DefaultOAuth2UserService();
            ClientRegistration clientRegistration = authorizedClient.getClientRegistration();
            OAuth2AccessToken accessToken = authorize dClient.getAccessToken();
            OAuth2UserRequest oAuth2UserRequest = new OAuth2UserRequest(clientRegistration, accessToken); //4
            OAuth2User oAuth2User = oAuth2UserService.loadUser(oAuth2UserRequest); //5

            SimpleAuthorityMapper authorityMapper = new SimpleAuthorityMapper();
            authorityMapper.setPrefix("SYSTEM_");
            Set<GrantedAuthority> grantedAuthorities = authorityMapper.mapAuthorities(oAuth2User.getAuthorities());

            OAuth2AuthenticationToken oAuth2AuthenticationToken =
                    new OAuth2AuthenticationToken(oAuth2User, grantedAuthorities, clientRegistration.getRegistrationId()); //6

            SecurityContextHolder.getContext().setAuthentication(oAuth2AuthenticationToken);

            model.addAttribute("oAuth2AuthenticationToken", oAuth2AuthenticationToken);
        }

        return "home";
    }

    @GetMapping("/logout")
    public String logout(Authentication authentication, HttpServletResponse response, HttpServletRequest request){

        SecurityContextLogoutHandler logoutHandler = new SecurityContextLogoutHandler(); // 로그아웃을 진행하는 핸들러
        logoutHandler.logout(request, response, authentication);

        return "redirect:/";
    }
}
```

1. 토큰을 받기 위해 만드는 요청 객체 `OAuth2AuthorizeRequest` 입니다.
2. 토큰 인증에 성공하면 실행하는 `successHandler` 를 지정합니다. `successHandler` 는 위에서 만들었습니다. `DefaultOAuth2AuthorizedClientManager` 클래스에 있는 로직을 그대로 가져온 겁니다.
3. 토큰을 RestTemplate 으로 인증받은 응답 객체인 `OAuth2AuthorizedClient` 입니다.
4. `/userinfo` 로 유저 정보를 요청하기 위해 `OAuth2UserRequest` 를 만듭니다.
5. `oAuth2UserService.loadUser()` 로 유저 정보를 요청하여 `OAuth2User` 를 받습니다.
6. `OAuth2AuthenticationToken` 을 만들고 `SecurityContextHolder` 에 저장합니다.

# Client Credentials Flow

​	흐름 자체는 Password 방식과 거의 동일합니다.

![image-20230726210716661](../../images/2023-07-25-[Security OAuth2] Section 8. OAuth 2.0 Client - oauth2Client()/image-20230726210716661.png)

대신 RefreshToken 이 없습니다. 

## 구현

### application.yml

```yml
server:
  port: 8081

spring:
  security:
    oauth2:
      client:
        registration:
          keycloak:
            client-id: oauth2-client-app
            client-secret: LAk7jhgzab8xJIurXyamYFuLe5vtBEAZ
            client-name: oauth2-client-app
            authorization-grant-type: client_credentials
            client-authentication-method: client_secret_basic
            provider: keycloak

        provider:
          keycloak:
            issuer-uri: http://localhost:8080/realms/oauth2
            authorization-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/auth
            token-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/token
            user-info-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/userinfo
            jwk-set-uri: http://localhost:8080/realms/oauth2/protocol/openid-connect/certs
            user-name-attribute: preferred_username

```

### LoginController

```java
package io.security.springsecurityoauth2.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.mapping.SimpleAuthorityMapper;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.client.OAuth2AuthorizationSuccessHandler;
import org.springframework.security.oauth2.client.OAuth2AuthorizeRequest;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClientManager;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserService;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizedClientManager;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizedClientRepository;
import org.springframework.security.oauth2.core.OAuth2AccessToken;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.logout.SecurityContextLogoutHandler;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.security.oauth2.client.OAuth2AuthorizedClient;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Set;

@Controller
public class LoginController {

    @Autowired
    private DefaultOAuth2AuthorizedClientManager oAuth2AuthorizedClientManager;

    @Autowired
    private OAuth2AuthorizedClientRepository oAuth2AuthorizedClientRepository;

    @GetMapping("/oauth2Login")
    public String oauth2Login(Model model, HttpServletRequest request, HttpServletResponse response) {

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        OAuth2AuthorizeRequest authorizeRequest = OAuth2AuthorizeRequest
                .withClientRegistrationId("keycloak")
                .principal(authentication)
                .attribute(HttpServletRequest.class.getName(), request)
                .attribute(HttpServletResponse.class.getName(), response)
                .build();

        OAuth2AuthorizationSuccessHandler successHandler = (authorizedClient, principal, attributes) -> {
            oAuth2AuthorizedClientRepository
                    .saveAuthorizedClient(authorizedClient, principal,
                            (HttpServletRequest) attributes.get(HttpServletRequest.class.getName()),
                            (HttpServletResponse) attributes.get(HttpServletResponse.class.getName()));
            System.out.println("authorizedClient = " + authorizedClient);
            System.out.println("principal = " + principal);
            System.out.println("attributes = " + attributes);
        };

        oAuth2AuthorizedClientManager.setAuthorizationSuccessHandler(successHandler);

        OAuth2AuthorizedClient authorizedClient = oAuth2AuthorizedClientManager.authorize(authorizeRequest);

        model.addAttribute("authorizedClient", authorizedClient.getAccessToken().getTokenValue());

        return "home";

    }
}
```

`LoginController` 도 password 방식과 완전히 같습니다. 다만 인가까지만 처리되고 인증 처리는 별도로 해줘야 합니다.

