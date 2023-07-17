---
categories: "inflearn"
tag: ["WebSecurity", "HttpSecurity", "AuthenticationEntryPoint"]
series: "Spring Boot 기반으로 개발하는 Spring Security OAuth2"
series-description: "인프런 정수원님의 'Spring Boot 기반으로 개발하는 Spring Security OAuth2' 강의 내용입니다."
series-link: "https://www.inflearn.com/course/%EC%A0%95%EC%88%98%EC%9B%90-%EC%8A%A4%ED%94%84%EB%A7%81-%EC%8B%9C%ED%81%90%EB%A6%AC%ED%8B%B0/dashboard"
teaser: "Spring Security2"
title: "[Security OAuth2] Section 1. Spring Secuirty Fundamentals"
description: "Spring Security Section 1. Spring Secuirty Fundamentals 내용입니다."
---

# 스프링 시큐리티 초기화 과정

​	`SecurityBuilder` 는 빌더 클래스로서 웹 보안을 구성하는 빈 객체와 설정클래스들을 생성하는 역할을 하며 `WebSecurity`, `HttpSecurity` 가 있습니다.

​	`SecurityConfigurer` 는 Http 요청과 관련된 보안처리를 담당하는 필터들을 생성하고 여러 초기화 설정에 관여합니다. `SecurityBuilder` 는 `SecurityConfigurer` 를 포함하고 있으며 인증 및 인가 초기화 작업은 `SecurityConfigurer` 에 의해 진행됩니다.

![image-20230714202425443](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230714202425443.png)

아래 그림과 같이 `AutoConfiguration` 이 `SecurityBuilder` 의 `build()` 를 호출하는데요. 이 때 `SecurityBuilder` 는 내부적으로 `SecurityConfigurer` 를 가지고 있으면서 `build()` 가 실행되는 동안 초기화작업을 진행합니다.

![image-20230714221740143](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230714221740143.png)

이것을 좀 더 상세히 보겠습니다.

![image-20230716115454854](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230716115454854.png)

`SecurityBuilder` 는 `WebSecurity` 와 `HttpSecurity` 구현체가 있습니다. 먼저 `apply()` 메서드로 초기화 대상을 적용시킵니다. 그래서 어떤 `Cnofigurer` 를 초기화할지 대상을 정하게 됩니다.

이후 `build()` 메서드가 호출되고, 그 안에서 각각의 `Configurere` 들의 `init()`, `configure()` 메서드가 호출되면서 그 안에서 `Filter` 도 만들고 인증과 인가에 필요한 객체를 만듭니다. 

​	`WebSucurity` 의 최종 반환값은 `FilterChainProxy` 입니다. 그리고 `HttpSecurity` 의 최종 반환값은 `SecurityFilterChain` 입니다.

## WebSecurityConfiguration

해당 Config 파일의 `setFilterChainProxySecurityConfigurer()` 메서드에서 `WebSecurity` 클래스를 만듭니다.

![image-20230716131449761](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230716131449761.png)

첫 번째 박스에서 `WebSecurity` 를 만드는 것을 볼 수 있고, 두 번째 박스에서는 `SecurityConfigurer` 를 `apply()` 메서드로 적용시키고 있습니다.

## HttpSecurityConfiguration

![image-20230716131945958](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230716131945958.png)

`HttpSecurity` 는 scope 가 prototype 으로, 여러 개를 생성할 수 있습니다. 세 번째 박스를 보면 Default 구현체를 생성하고 적용시키고 있습니다. 

예를 들어 .`csrf()` 메서드를 보면,

![image-20230717154107100](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717154107100.png)

이렇게 되어있는데, `getOrApply()` 메서드로 들어가서 다시 `apply()` 로 들어가면, `AbstractConfiguredSecurityBuilder` 클래스의 `apply()` 메서드를 적용하고 있습니다. 여기에서 `Configurer` 를 추가해줍니다.

아래와 같이 `HttpSecurityConfiguration` 의 `configurers` 필드에 `CsrfConfigurer` 가 추가된 걸 볼 수 있습니다.

![image-20230717154629185](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717154629185.png)

그렇다면 이렇게 구성된 `http` 는 어디서 빈으로 등록될까요? 바로 `SpringBootWebSecurityConfiguration` 클래스입니다.

![image-20230717155158573](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717155158573.png)

해당 클래스에서 기본적인 `SecurityFilterChain` 을 빈으로 등록합니다.

여기서 `build()` 를 하게 되면 **`AbstractSecurityBuilder`** 의 `build()` 메서드가 사용되는데요. 해당 메서드 내부에서는 `doBuild()` 를 사용합니다.

![image-20230717155400847](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717155400847.png)

`doBuild()` 내부에서는 `configurers` 를 가지고 여러 가지 초기화 과정이 시작됩니다.

![image-20230717155555015](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717155555015.png)

`init()` 메서드에는 각 `configurer` 의 `init()` 메서드를 호출합니다.

![image-20230717162951121](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717162951121.png)

그리고 `configure()` 메서드에서는 각 `configurer` 의 `configure()` 메서드를 호출합니다.

![image-20230717163131459](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717163131459.png)

예를 들어, 아래는 `CsrfConfigurer` 의 `configure()` 메서드입니다.

![image-20230717163255119](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717163255119.png)

메서드 내부에서 필터, 핸들러 등을 만들고 `addFilter` 를 합니다.

마지막으로 `performBuild()` 는 `HttpSecurity` 에 있고 `DefaultSecurityFilterChain` 을 리턴합니다.

![image-20230717163658727](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717163658727.png)

`DefaultSecurityFilterChain` 은 만들어진 필터(`sortedFilters`) 와 `requestMatcher` 를 받고 있습니다. `requestMatcher` 는 `SpringBootWebSecurityConfiguration` 에 있습니다. (`http.authorizeRequests().anyRequest().authenticated();`)

이렇게 만들어진 Filter 들은 `WebSecurity` 로 전달되어 `FilterChainProxy` 를 만드는 데 사용됩니다. `WebSecurity` 에도 `performBuild()` 가 동작하는데, 해당 메서드에서 `FilterChainProxy filterChainProxy = new FilterChainProxy(securityFilterChains);` 형태로 `securityFilterChains` 가 전달됩니다.

## CustomSecurityConfigurer

`CustomSecurityConfigurer` 은 `AbstractHttpConfigurer` 를 상속받아야 합니다. 제네릭 타입은 아래와 같이 만듭니다.

```java
public class CustomSecurityConfigurer extends AbstractHttpConfigurer<CustomSecurityConfigurer, HttpSecurity> {

    private boolean isSecure;

    @Override
    public void init(HttpSecurity builder) throws Exception {
        super.init(builder);
        System.out.println("init method called ... ");
    }

    @Override
    public void configure(HttpSecurity builder) throws Exception {
        super.configure(builder);
        System.out.println("configure method called ... ");
        if(isSecure){
            System.out.println("https is required");
        }else{
            System.out.println("https is optional");
        }
    }

    public CustomSecurityConfigurer setFlag(boolean isSecure){
        this.isSecure = isSecure;
        return this;
    }
}

```

간단하게 `init()` 과 `configure()` 를 구현했습니다. `isSecure` 값은 `Config` 파일에서 줍니다.

### SecurityConfig

```java
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .authorizeRequests()
                .anyRequest().authenticated()
            .and()
                .formLogin()
            .and()
                .apply(new CustomSecurityConfigurer().setFlag(true));

        return http.build();
    }
}
```

`.setFlag(true)` 를 통해 메서드 체이닝 방식으로 `isSecure` 값을 줍니다. 빌드를 하면 다음과 같이 작동합니다.

![image-20230717170752059](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717170752059.png)

# 자동설정에 의한 초기화 과정 

자동설정에 의해 초기화를 진행하면 아래와 같은 과정으로 진행됩니다.

![image-20230717171314930](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717171314930.png)

1. 어떤 조건에 따라 빈을 등록하는 로직을 구현하려면 `SpringWebMvcImportSelector` 을 사용합니다.
2. `SecurityFilterAutoConfiguration` 클래스는 `DelegatingFilterProxyRegistrationBean` 클래스를 만듭니다. 그러면 그 빈 클래스가 `DelegatingFilterProxy` 를 등록합니다.
3. 이후 `WebMvcSecurityConfiguration` 은 여러 `ArgumentResolver` 를 생성하는데 이중 `AuthenticationPrincipalArgumentResolver` 는 `@AuthenticationPrincipal` 에 `Principal` 객체를 바인딩합니다.
4. `HttpSecurityConfiguration` 에서는 프로토타입 빈인 `SecurityFilterChain` 빈을 생성합니다. 아래와 같이 각각의 Configurer 가 등록되고 초기화과정을 통해 각각의 필터가 만들어집니다.

![image-20230717172310604](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717172310604.png)

예를 들어서 `UsernamePasswordAuthenticationFilter` 는 `FormLoginConfigurer` 에서 만듭니다.

## SpringBootWebSecurityConfiguration 에 의한 자동설정

아래는 WebSecurity 가 만들어지는 과정입니다.

![image-20230717172852135](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717172852135.png)

​	`WebSecurity` 에는 `securityFilterChainBuilders` 라는 필드가 있는데, 여러 개의 SecurityBuilder 가 들어갈 수 있습니다. 그리고 `SecurityBuilder` 는 `SecurityFilterChain` 을 가지고 있는데, 그게 바로 빈으로 등록한 `SecurityFilterChain` 입니다.

​	초기화 과정에서 `WebSecurity` 가 `build()` 를 실행하면 `FilterChainProxy` 를 생성합니다. `FilterChainProxy` 는 `SecurityFilterChains` 필드가 있는데, 여러 개의 `SecurityFilterChain` 을 가집니다.

​	최종적으로, `SecurityFilterChain` 빈들은 `FilterchainProxy` 안에 위치하게 됩니다.

## 코드레벨

### SpringWebMvcImportSelector

![image-20230717201907429](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717201907429.png)

먼저 `selectImports()` 메서드를 통해 `DispatcherServlet` 이 있는지 확인하고 있다면 `~WebMvcSecurityConfiguration` 을 반환합니다.

### SecurityFilterAutoConfiguration

그 다음으로 `SecurityFilterAutoConfiguration` 의 `securityFilterChainRegistration()` 메서드를 보면 `DelegatingFilterProxyRegistrationBean` 을 만들고 있습니다.

![image-20230717202419376](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717202419376.png)

이 때 DEFAULT_FILTER_NAME 은 `springSecurityFilterChain` 입니다.

### WebMvcSecurityConfiguration

그리고 resolver 를 등록시키는 `addArgumentResolvers()` 메서드입니다.

![image-20230717202718625](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717202718625.png)

### SpringBootWebSecurityConfiguration

해당 클래스에서 SecurityFilterChain 을 만들고 있습니다.

![image-20230717202948969](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717202948969.png)

여기서 참조하는 `HttpSecurity` 는 `HttpSecurityConfiguration` 에서 프로토 타입 빈으로 생성됩니다.

![image-20230717203055190](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717203055190.png)

`SpringBootWebSecurityConfiguration` 를 다시보면 `@ConditionalOnDefaultWebSecurity` 라는 어노테이션이 있습니다.

![image-20230717203316556](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717203316556.png)

해당 어노테이션은 빈 등록은 어떤 조건일 때 하는지 정해놓는데요.

![image-20230717203354456](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717203354456.png)

`@Conditional`  조건이 있습니다. `DefaultWebSecurityCondition` 클래스로 들어가보겠습니다.

![image-20230717203436477](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717203436477.png)

첫번째 조건은 classpath 에 `SecurityFilterChain`, `HttpSecurity` 가 잡혀져있느냐 이고, 두번째는 `WebSecurityConfigurerAdapter`, `SecurityFilterChain` 이 빈으로 등록된 게 없느냐 입니다.

### WebSecurityConfiguration

해당 클래스의 `setFilterChains()` 메서드를 통해 필드값으로 `securityFilterChains` 를 받습니다.

![image-20230717204358485](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717204358485.png)

그리고 반환 타입이 Filter 인 `springSecurityFilterChain()` 을 실행합니다.

![image-20230717204539850](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717204539850.png)

`webSecurity` 에 `FilterChain` 을 주고 `build()` 를 하면 최종적으로 `FilterChainProxy` 가 반환됩니다.

## custom SecurityFilterChain 등록

아래와 같이 `SecurityFilterChain` 을 2개 만들어보겠습니다.

```java
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain1(HttpSecurity http) throws Exception {
        http
                .authorizeRequests()
                .anyRequest().authenticated()
            .and()
                .formLogin()
		;

        return http.build();
    }

    @Bean
    public SecurityFilterChain securityFilterChain2(HttpSecurity http) throws Exception {
        http
                .authorizeRequests()
                .anyRequest().authenticated()
                .and()
                .httpBasic()
		;

        return http.build();
    }
}

```

이렇게 하면 `@ConditionalOnDefaultWebSecurity` 에 의해 `SpringBootWebSecurityConfiguration` 은 거치지 않게 됩니다.

**`SecurityFilterChain` 을 2번 등록하면 프로토 타입 빈이기 때문에 각각 생성되어야 합니다.** 따라서 `HttpSecurityConfiguration` 클래스의 `httpSecurity()` 메서드가 2번 호출되는 것으로 알 수 있습니다.

그리고 `WebSecurityConfiguration` 클래스의 `setFilterChains` 에도 2개의 `SecurityFilterChain` 이 들어오는 것을 볼 수 있습니다.

![image-20230717205512716](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717205512716.png)

# AuthenticationEntryPoint 이해

`AuthenticationEntryPoint` 는 **인증**실패 시 처리 방법입니다. (인가 x)

![image-20230717210202878](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717210202878.png)

각각의 인증 방법마다 인증 실패 처리 방법이 다를건데요. 그 구성은 각 `Configurer` 가 초기화될 때 생성됩니다. `FormLoginConfigurer` 는 초기화되면서 `ExceptionHandlingConfigurer` 설정 클래스 안에 있는 `DufaultEntryPointMapping` 에 자신의 `EntryPoint` 를 추가합니다. (`LoginUrlAuthenticationEntryPoint`) 그리고 `HttpBasicConfigurer` 도 마찬가지로 자신의 `EntryPoint` 를 추가합니다. (`DelegatingAuthenticationEntryPoint`) 만약 custom EntryPoint 를 만들 게 된다면 default 로 설정된 위 `entryPoint` 는 무시됩니다.

![image-20230717225828029](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717225828029.png)

만약 `FormLogin` 과 `HttpBasic` 도 설정하지 않는다면 표에서 보이듯 Http4`0`3ForbiddenEntryPoint 를 호출합니다. 그리고 만약 `EntryPoint` 가 1개 설정되었다면 그거를 사용하고, 2개 이상이면 어떤 인증방식인지에 따라 내부로직을 통해 결정합니다.

## 코드레벨

예를 들어 아래와 같이 `SecurityFilterChain` 에 `FormLogin`, `httpBasic`, `custom EntryPoint` 3개가 있습니다.

```java
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain1(HttpSecurity http) throws Exception {
        http
                .formLogin()
            .and()
                .httpBasic()
            .and()
                .authorizeRequests()
                .anyRequest().authenticated()
            .and()
                .exceptionHandling()
                .authenticationEntryPoint(((request, response, authException) -> {
                    System.out.println("custom entryPoint");
                }))

            ;

        return http.build();
    }
}
```

이 때 인증받지 않은 사용자가 접근할 때 실행되는 EntryPoint 는 custom 입니다.

## EntryPoint 등록

아래 코드는 `AbstractAuthenticationFilterConfigurer` 입니다. `FormLoginConfigurer` 의 부모 클래스입니다.

![image-20230717232033351](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717232033351.png)

해당 클래스의 init 을 통해 초기화가 진행되는데 이때 `registerDefaultAuthenticationEntryPoint()` 메서드를 통해 `ExceptionHandlingConfigurer` 를 불러와서 자신의 EntryPoint 를 등록시킵니다.

마찬가지로 `HttpBasicConfigurer` 도 `authenticationEntryPoint()` 메서드로 동일한 작업을 거칩니다.

마지막으로 `ExceptionHandlingConfigurer` 는 `configure()` 메서드 실행 시 그렇게 받은 `EntryPoint` 를 `ExceptionTranslationFilter` 로 전달합니다. 해당 필터가 인증 예외 처리를 하기 때문입니다.

![image-20230717233312408](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717233312408.png)

그러면 서비스 중 인증 예외가 발생했을 때 `ExceptionTranslationFilter` 의 `sendStartAuthentication()` 메서드에서 commence 를 통해 예외를 발생시킵니다.

![image-20230717234522373](../../images/2023-07-14-[Security OAuth2] Section 1. Spring Secuirty Fundamentals/image-20230717234522373.png)