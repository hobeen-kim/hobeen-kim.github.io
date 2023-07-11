---
categories: "spring"
tag: ["UsernamePasswordAuthenticationFilter", "AuthenticationManager", "ProviderManager"]
title: "[Spring Security] AuthenticationFilter 흐름 확인하기"
---

# 인증 흐름

![img](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/s61IipWPdcLaHBfsH6gOW-1663488624716.png)

인증 흐름의 구성은 위와 같습니다. 코드 레벨에서 자세히 보겠습니다.

## UsernamePasswordAuthenticationFilter

현재 스프링 시큐리티의 `FilterChainProxy` 에 등록된 필터는 아래와 같습니다.

![image-20230711133943491](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711133943491.png)

`UsernamePasswordAuthenticationFilter` 는 5번째로 실행되는 필터입니다.

먼저 해당 필터의 `doFilter()` 가 실행됩니다. `UsernamePasswordAuthenticationFilter` 는 직접 `doFilter()` 는 확장하지 않고 부모클래스인 `AbstractAuthenticationProcessingFilter` 의 doFilter() 를 사용합니다.

![image-20230711134607168](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711134607168.png)

1. `requiresAuthentication()` 메서드는 로그인 페이지에서의 요청인지 확인합니다. 해당 요청이 맞으면 필터를 계속 진행합니다. 아니면 다음 필터로넘어갑니다. 해당 값은 `SecurityConfig` 의 `http.loginPage("/loginPage")` 설정에 따라 변경가능합니다.

   ![image-20230711134741304](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711134741304.png)

2. `attemptAuthentication()` 메서드는 로그인 정보는 통해 인증정보인 `Authentication` 을 만듭니다. `UsernamePasswordAuthenticationFilter` 에서는 `UsernamePasswordAuthenticationToken` 으로 만듭니다. 해당 `Authentication` 은 나중에 실제 인증에 사용됩니다. 그리고 `AuthenticationManager` 의 `authenticate()` 를 호출합니다. 해당 메서드는 후술하겠습니다.

   ![image-20230711151155506](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711151155506.png)

   - `UsernamePasswordAuthenticationToken.unauthenticated()` 메서드는 권한 정보가 없는 객체 생성 메서드이고, 반대로 `authenticated()` 는 권한 정보가 있는 객체 생성 메서드입니다.

3. 세션 고정 보호 정책에 따른 세션ID 변경입니다. 매 요청마다 세션 ID 를 변경하여 세션 고정 공격에 대해 보호할 수 있도록 합니다. 기본정책은 `ChangeSessionIdAuthenticationStrategy` 으로, 로그인 시마다 세션ID 를 변경합니다. 아래 로직은 세션 정책을 가진 `CompositeSessionAuthenticationStrategy` 의 `onAUthentication()` 메서드입니다.

   ![image-20230711150545615](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711150545615.png)

   - 위 빨간 박스에서 delegate 가 `ChangeSessionIdAuthenticationStrategy` 입니다.

4. 인증 성공 시 `successfulAuthentication()` 메서드를 호출합니다. 해당 메서드는 `SecurityContext` 안에 인증 결과인 `Authentication` 를 담아서 `SecurityContextHolder` 로 감쌉니다. 이제 해당 `ThreadLocal` 에서 `Authentication` 을 조회할 수 있게 됩니다.

   ![image-20230711154148211](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711154148211.png)

   - 또한 `session` 에서도 접근할 수 있게 저장해둡니다. 
   - 마지막으로 `successHandler` 를 호출합니다. 해당 핸들러는 설정 파일인 `SecurityFilterChain` 에서 `.successHandler()` 로 커스텀할 수 있습니다.

5. Exception 발생 시 호출됩니다. `unsuccessfulAuthentication()` 이 호출됩니다. 해당 핸들러 안에서 `failureHandler` 가 실행됩니다. 해당 핸들러도 마찬가지로 설정 파일인 `SecurityFilterChain` 에서 `.failureHandler()` 로 커스텀할 수 있습니다. 

   ![image-20230711154558645](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711154558645.png)

## ProviderManager

위 2번 과정의 `attemptAuthentication()` 메서드 내부에서 `this.getAuthenticationManager().authenticate(authRequest)` 안으로 들어가보겠습니다. 길어서 필요한 부분만 보겠습니다.

해당 메서드는 `ProviderManager` 에 있는 메서드입니다. `ProviderManager` 는 여러 `AuthenticationProvider` 를 가지면서 해당 `Authentication` 객체를 인증할 수 있는 `Provider` 를 선택해서 인증을 위임합니다.

아래는 `ProviderManager` 의 `authenticate()` 메서드입니다.

![image-20230711155054863](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711155054863.png)

1. 받은 `Authentication` 의 클래스입니다. `Authentication` 은 인터페이스이며 여러 구현체가 있는데, 각 구현체마다 처리할 수 있는 `Provider` 가 있기 때문에 미리 `toTest` 객체를 선언하고 어떤 클래스인지 할당합니다.

2. 실제로 반환할 `Authentication` 객체를 `result` 로 선언합니다.

3. `getProviders()` 는 `ProviderManager` 가 가지고 있는 `Provider` 의 목록입니다. 하나씩 순회하며 전달받은 `Authentication` 에 맞는 `Provider` 를 찾습니다.

4. `provider.supports()` 메서드는 해당 `Provider` 가 전달받은 `Authentication` 를 처리할 수 있는지 확인하는 `boolean` 값입니다.

   ![image-20230711155820564](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711155820564.png)

5. 선택된 `Provider` 가 인증을 수행하는 로직입니다. 아래에서 설명하겠습니다.

## AuthenticationProvider

`AuthenticationProvider` 는 인터페이스이며 해당 인터페이스를 구현한 구현체가 빈으로 등록되면 사용할 수 있습니다. `UsernamePasswordAuthenticationToken` 은 기본적으로 `DaoAuthenticationProvider` 를 사용합니다.

아래는 `DaoAuthenticationProvider` 의 추상 클래스인 `AbstractUserDetailsAuthenticationProvider`  의 `authenticate()` 메서드입니다. 먼저 `UserDetails` 를 얻는 로직입니다. 

### 사용자 아이디 검증

![image-20230711161527984](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711161527984.png)

- `determineUsername()` 으로 `Authentication` 에 있는 `name` 을 얻습니다.

- `retrieveUser()` 메서드는 `username` 을 통해 DB 혹은 인메모리에서 `user` 를 조회하고 `UserDetails` 로 반환합니다.

  ![image-20230711161850960](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711161850960.png)

  - `UserDetails` 는 `UserDetailsService` 에서 `loadUserByUsername()` 메서드로 얻습니다. `UserDetailsService` 는 인터페이스로, 빈으로 등록된 `UserDetailsService` 가 사용되거나 인메모리사용 시 `InMemoryUserDetailsManager` 가 사용됩니다.
  - 만약 `username` 으로 조회되는 데이터가 없다면 `UsernameNotFoundException` 을 발생시킵니다.

**이렇게 얻은 `UserDetails` 에는 기본적으로 `username`, `password`, `authorities` 가 있습니다.**

### 사용자 비밀번호 검증

비밀번호도 `AuthenticationProvider` 의 `authenticate()` 메서드 내에서 이루어집니다. 해당 메서드 내 일부입니다.

![image-20230711162319106](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711162319106.png)

위 코드처럼 `additionalAuthenticationChecks()` 메서드에 `UserDetails user` 와 `authentication` 객체를 넘깁니다.

아래는 `DaoAuthenticationProvider` 의 `additionalAuthenticationChecks()` 메서드입니다.

![image-20230711162615201](../../images/2023-07-11-[Spring Security] 인증 구성요소 및 흐름/image-20230711162615201.png)

1. 먼저 `Authentication` 에서 비밀번호를 추출합니다. 여기서 유의해야 할 건 `Authentication` 은 요청으로부터 얻은 정보로 생성된 객체입니다.
2. 그리고 `userDetails` 에 있는 비밀번호와 비교합니다. `userDetails` 는 DB 에서 얻은 정보입니다. 만약 다르다면 `BadCredentialsException` 이 발생합니다.