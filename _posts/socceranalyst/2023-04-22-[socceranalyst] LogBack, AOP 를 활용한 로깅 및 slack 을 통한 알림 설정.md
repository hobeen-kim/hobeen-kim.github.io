---
categories: "socceranalyst"
tag: ["aop", "logging", "toyproject", "logback", "spring"]
---

오늘은 LogBack 을 이용해서 로그를 남기고 slack 으로 알림을 보내는 것까지 해보겠습니다. 

하면서 xml 파일 설정이 굉장히 어려웠고, 키메라 마냥 짜집기 + gpt 도움을 많이 받았습니다. 공부를 하면 할수록 드는 생각인데, 제 지식수준이 사상누각이라는 생각이 많이 들었습니다. 원래 이번 포스팅을 한 후에 프로메테우스, 그라파나 적용을 해보려고 했는데, 그전에 기본적인 WEB 지식, 알고리즘 및 자료구조 등을 배우는 게 우선되어야 할 것 같다는 생각이 많이 듭니다... (현타는 xml 에서 받았지만 xml 공부는 할 생각이 안드네요 ㅋㅋ)

일단 현재 배포하고 있는 서비스에서는 RefreshToken 구현까지 되어있어서, RTR 및 오늘 하는 Logging 까지 업데이트하고 정상 작동하는지 확인해야 합니다. 이후 Refactoring 진행하면서 기본적인 개념을 정리해야 겠습니다.

일단 Log 공부를 하면서, log 도 그냥 찍히는 게 아니라 spring 에서 일정한 format 을 가지고 출력한다는 걸 깨달았습니다. 김영한님이 말씀하시는 것처럼 자바는 마법을 부리지 않죠... 그 기능을 정의해놓았기 때문이 실행되는 겁니다. 당연한 걸 저는 이제야 깨달았구요 ㅎㅎ

# 무엇을 위해 Log 를 남기나?

[[spring\] 시스템 관리를 위한 로그 작성](https://hobeen-kim.github.io/til-spring/Spring-%EC%8B%9C%EC%8A%A4%ED%85%9C-%EA%B4%80%EB%A6%AC%EB%A5%BC-%EC%9C%84%ED%95%9C-%EB%A1%9C%EA%B7%B8-%EC%9E%91%EC%84%B1/) 로그 작성에 관한 제 포스팅입니다.

사실 제 프로젝트에 log 요구사항까지 생각하진 않아서요. 어느정도 깊이로 할까 고민을 많이 했었는데, 기본적인 부분만 하려고 합니다. 

1. 기본적인 서비스 호출, 동작 상태 확인
2. Error 발생 시 따로 LogFile 에 저장 및 알림
3. 기타 DEBUG 설정 (hibernate, springsecurity, root)

그 이유는, 요구사항이 명확하지 않은 것도 있고, 서비스 호출, 에러 출력 외에 필요성을 못느끼는 부분도 있습니다. 그리고 일단 만들어놓으면 나중에 추가하기는 쉬우니까요.

## 로그 레벨 설정

다음과 같이 로그 레벨을 설정했습니다

1. 기본적인 서비스 호출, 동작 상태 : INFO
2. 의도된 Exception : INFO
3. 의도되지 않은 모든 Exception : ERROR
4. hibernate sql log, springsecurity 접근, root : DEBUG

이외의 Performance 추적은 다음에 프로메테우스 및 그라파나로 해보겠습니다.



# Spring 적용

**build.gradle**

다음과 같이 라이브러리를 추가합니다.

```java
//logback 추가
implementation 'org.slf4j:slf4j-api'
implementation 'ch.qos.logback:logback-classic'
//logback slack appender
implementation 'com.github.maricn:logback-slack-appender:1.4.0'
```

- `logback-slack-appender` 는 알림 설정을 위해 넣었습니다.

## AOP 적용

AOP 입니다. AOP 를 통해서 메서드가 실행되기 전, 후로 메서드 누가 어떤 메서드를 실행하는지 확인하겠습니다.

### LogAspect 클래스

```java
package soccer.backend.aop;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

@Aspect
@Slf4j
@Component
public class LogAspect {

    private static final Logger errorFileLogger = LoggerFactory.getLogger("ERROR_FILE_LOGGER");

    @Around("execution(* soccer.backend..*Controller.*(..))")
    public Object Controllerlog(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().getName();
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String name = authentication != null ? authentication.getName() : "Unknown";

        log.info("{} called the method: {}", name, methodName);
        Object result = joinPoint.proceed();
        log.info("{} method has finished: {}", name, methodName);
        return result;
    }

    @Around("execution(* soccer.backend..*ExceptionHandler.*(..)) && !execution(* soccer.backend..*ExceptionHandler.handleException(..))")
    public Object IntendedExceptionHandlerLog(ProceedingJoinPoint joinPoint) throws Throwable {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String name = authentication != null ? authentication.getName() : "Unknown";
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        Exception e = null;

        for (Object arg : args) {
            if(arg instanceof Exception) {
                e = (Exception) arg;
                break;
            }
        }

        if (e != null) {
            log.info("{} 실행", methodName);
            log.info("{} Error detail: ", name, e);
        } else {
            log.warn("No exception found in the method arguments for {}", methodName);
        }

        log.info("{} called the method: {}", name, methodName);
        Object result = joinPoint.proceed();
        log.info("{} method has finished: {}", name, methodName);
        return result;
    }

    @Around("execution(* soccer.backend..*ExceptionHandler.handleException(..))")
    public Object ExceptionHandlerLog(ProceedingJoinPoint joinPoint) throws Throwable {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String name = authentication != null ? authentication.getName() : "Unknown";
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        Exception e = null;

        for (Object arg : args) {
            if(arg instanceof Exception) {
                e = (Exception) arg;
                break;
            }
        }

        if (e != null) {
            errorFileLogger.error("{} 실행", methodName);
            errorFileLogger.error("{} Error detail: ", name, e);
        } else {
            log.error("No exception found in the method arguments for {}", methodName);
        }

        log.info("{} called the method: {}", name, methodName);
        Object result = joinPoint.proceed();
        log.info("{} method has finished: {}", name, methodName);
        return result;
    }
}
```

세부적으로 확인해보겠습니다.

**Controllerlog**

```java
@Around("execution(* soccer.backend..*Controller.*(..))")
public Object Controllerlog(ProceedingJoinPoint joinPoint) throws Throwable {
    
    String methodName = joinPoint.getSignature().getName();
    Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
    String name = authentication != null ? authentication.getName() : "Unknown";

    log.info("{} called the method: {}", name, methodName);
    Object result = joinPoint.proceed();
    log.info("{} method has finished: {}", name, methodName);
    return result;
}
```

- methodName, name(유저 아이디) 를 받아서 INFO 로 로깅합니다.



**IntendedExceptionHandlerLog**

```java
@Around("execution(* soccer.backend..*ExceptionHandler.*(..)) && !execution(* soccer.backend..*ExceptionHandler.handleException(..))")
    public Object IntendedExceptionHandlerLog(ProceedingJoinPoint joinPoint) throws Throwable {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String name = authentication != null ? authentication.getName() : "Unknown";
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        Exception e = null;

        for (Object arg : args) {
            if(arg instanceof Exception) {
                e = (Exception) arg;
                break;
            }
        }

        if (e != null) {
            log.info("{} 실행", methodName);
            log.info("{} Error detail: ", name, e);
        } else {
            log.warn("No exception found in the method arguments for {}", methodName);
        }

        log.info("{} called the method: {}", name, methodName);
        Object result = joinPoint.proceed();
        log.info("{} method has finished: {}", name, methodName);
        return result;
    }
```

- 의도된 Exception 은 해당 메서드로 처리합니다.
- @Around 를 보면, ExceptionHandler 클래스는 모두 처리하지만, ExceptionHandler.handleException() 는 제외한다고 했습니다.
- error 를 args[] 로 받아서 INFO level 로 출력합니다.



**ExceptionHandlerLog**

```java
private static final Logger errorFileLogger = LoggerFactory.getLogger("ERROR_FILE_LOGGER");

@Around("execution(* soccer.backend..*ExceptionHandler.handleException(..))")
public Object ExceptionHandlerLog(ProceedingJoinPoint joinPoint) throws Throwable {
    Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
    String name = authentication != null ? authentication.getName() : "Unknown";
    String methodName = joinPoint.getSignature().getName();
    Object[] args = joinPoint.getArgs();
    Exception e = null;

    for (Object arg : args) {
        if(arg instanceof Exception) {
            e = (Exception) arg;
            break;
        }
    }

    if (e != null) {
        errorFileLogger.error("{} 실행", methodName);
        errorFileLogger.error("{} Error detail: ", name, e);
    } else {
        log.error("No exception found in the method arguments for {}", methodName);
    }

    log.info("{} called the method: {}", name, methodName);
    Object result = joinPoint.proceed();
    log.info("{} method has finished: {}", name, methodName);
    return result;
}
```

- `ExceptionHandlerLog` 메서드는 의도되지 않은 모든 Exception 을 로깅합니다. 따라서 logLevel 은 ERROR 입니다.
- `@Around("execution(* soccer.backend..*ExceptionHandler.handleException(..))")` 를 통해 단일 메서드만 별도로 처리합니다. 사실 단일 메서드만 AOP 를 적용할 거면 필요는 없지만 통일성(+학습 목적)을 위해 넣었습니다.
- 해당 ERROR logging 은 별도의 파일로 저장해야 하기 때문에 LoggerName 지정이 필요합니다. 원래 `@Slf4j(topic="ERROR_FILE_LOGGER")` 로 하려고 했으나, @Slf4j 는 메서드 레벨에서 지정할 수 없기 때문에 새로운 Logger 를 선언해주고 사용했습니다.

### GlobalExceptionHandler

- ExceptionHandler 입니다. 기존 ExceptionHandler 에다가 handleException 메서드를 추가했습니다. 해당 Exception 은 의도되지 않은 Exception 을 모두 처리합니다.

```java
package soccer.backend.aop;

import io.jsonwebtoken.ExpiredJwtException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.validation.BindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.ErrorResponse;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

import java.util.List;
import java.util.stream.Collectors;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ExpiredJwtException.class)
    public ResponseEntity<?> handleExpiredJwtException(ExpiredJwtException e) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("토근 유효시간이 지났습니다. 다시 로그인해주세요.");
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<?> handleRuntimeException(RuntimeException e) {
        String errorMessage =  e.getMessage();
        return ResponseEntity.badRequest().body(errorMessage);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<?> handleMethodArgumentNotValidException(MethodArgumentNotValidException e) {
        BindingResult bindingResult = e.getBindingResult();
        List<FieldError> errors = bindingResult.getFieldErrors();
        List<String> errorMessages = errors.stream()
                .map(error -> error.getField() + " : " + error.getDefaultMessage())
                .collect(Collectors.toList());
        String errorMessage = errorMessages.stream().collect(Collectors.joining(", "));

        return ResponseEntity.badRequest().body(errorMessage);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<?> handleException(Exception e) {
        final ErrorResponse response = ErrorResponse.create(e, HttpStatus.INTERNAL_SERVER_ERROR, e.getMessage());
        return new ResponseEntity<>(response, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```



### application.yml

```yaml
logging:
  level:
    root: INFO
    soccer.backend: INFO
    org:
      springframework:
        security: INFO
      hibernate:
        SQL: DEBUG
        type:
          descriptor:
            sql:
              BasicBinder: TRACE
```

- loglevel 기본 값입니다. 변경해야 할 일이 있으면 actuator 로 변경해보도록 하겠습니다. 해당 내용은 추후 프로메테우스, 그라파나를 적용하면서 함께 만들도록 하겠습니다.
- 일단 현재는 hibernate 를 제외하고 INFO 로 출력하겠습니다. DEBUG 를 활용할 일이 현재로썬 거의 없을 듯 합니다.



### slack-logback.yml

슬랙에 logfile 을 보내기 위한 설정입니다. 뒤에 다시 설명해보겠습니다.

```java
webhook-uri: https://hooks.slack.com/services/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
channel: error_log
username: socceranalyst_error_log
emoji: eyes
```

- webhook-uri : 슬랙에서 `Incoming Webhooks` 앱의 주소입니다. 해당 uri 로 값을 보내면 슬랙에서 출력됩니다.
- channel : 슬랙에서 채널입니다.
- username, emoji : 슬랙에서 보여지는 이름과 이모지입니다.

### logback-spring.xml

logback 설정파일입니다. 원래 spring 에는 default 설정파일이 있지만, 이렇게 직접 설정하면 해당 파일을 사용하게 됩니다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <include resource="org/springframework/boot/logging/logback/base.xml"/>

    <property name="home" value="logs"/>

    <appender name="DEFAULT_FILE_APPENDER" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${home}/access-%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <maxFileSize>15mb</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <charset>utf8</charset>
            <pattern>${FILE_LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <appender name="ERROR_FILE_APPENDER" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${home}/error-%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <maxFileSize>15mb</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <charset>utf8</charset>
            <pattern>${FILE_LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <!-- profile 에 따라 slack 에 전송 -->
    <springProfile name="local, production">
        <property resource="slack-logback.yml" />
        <appender name="SLACK_ERROR" class="com.github.maricn.logback.SlackAppender">
            <webhookUri>${webhook-uri}</webhookUri>
            <channel>#${channel}</channel>
            <layout class="ch.qos.logback.classic.PatternLayout">
                <pattern>${FILE_LOG_PATTERN}</pattern>
            </layout>
            <username>${username}</username>
            <iconEmoji>:${emoji}:</iconEmoji>
            <colorCoding>true</colorCoding>
        </appender>
        <appender name="ASYNC_ERROR_APPENDER" class="ch.qos.logback.classic.AsyncAppender">
            <appender-ref ref="SLACK_ERROR"/>
            <appender-ref ref="ERROR_FILE_APPENDER"/>
            <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
                <level>ERROR</level>
            </filter>
        </appender>
    </springProfile>

    <root level="DEBUG">
        <appender-ref ref="DEFAULT_FILE_APPENDER"/>
    </root>

    <logger name="ERROR_FILE_LOGGER" level="ERROR" additivity="true">
        <appender-ref ref="ERROR_FILE_APPENDER"/>
        <appender-ref ref="SLACK_ERROR"/>
    </logger>
</configuration>
```

[[spring\] 시스템 관리를 위한 로그 작성](https://hobeen-kim.github.io/til-spring/Spring-%EC%8B%9C%EC%8A%A4%ED%85%9C-%EA%B4%80%EB%A6%AC%EB%A5%BC-%EC%9C%84%ED%95%9C-%EB%A1%9C%EA%B7%B8-%EC%9E%91%EC%84%B1/) 에서 설명한 내용을 제외하고 리뷰하겠습니다.

```xml
<!-- profile 에 따라 slack 에 전송 -->
    <springProfile name="local, production">
        <property resource="slack-logback.yml" />
        <appender name="SLACK_ERROR" class="com.github.maricn.logback.SlackAppender">
            <webhookUri>${webhook-uri}</webhookUri>
            <channel>#${channel}</channel>
            <layout class="ch.qos.logback.classic.PatternLayout">
                <pattern>${FILE_LOG_PATTERN}</pattern>
            </layout>
            <username>${username}</username>
            <iconEmoji>:${emoji}:</iconEmoji>
            <colorCoding>true</colorCoding>
        </appender>
        <appender name="ASYNC_ERROR_APPENDER" class="ch.qos.logback.classic.AsyncAppender">
            <appender-ref ref="SLACK_ERROR"/>
            <appender-ref ref="ERROR_FILE_APPENDER"/>
            <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
                <level>ERROR</level>
            </filter>
        </appender>
    </springProfile>
     <root level="DEBUG">
        <appender-ref ref="DEFAULT_FILE_APPENDER"/>
    </root>

    <logger name="ERROR_FILE_LOGGER" level="ERROR" additivity="true">
        <appender-ref ref="ERROR_FILE_APPENDER"/>
        <appender-ref ref="SLACK_ERROR"/>
    </logger>
```

- `webhook-uri, channerl, username, emoji` 는 slack-logback.yml 에서 설정한 변수입니다.
- `profile` 이 local, production 일 때 실행합니다. 해당 내용은 모두 같은 채널로 보내는 걸로 되어있지만, local, production 에 따라 `${channel}` 값을 다르게 준다면 다른 채널로 보내집니다.
- `ERROR_FILE_LOGGER` 로거는 `SLACK_ERROR` appender 와 연결되어 보내집니다.

즉 전체적으로 보면, 

1. 기본적으로 DEBUG level (DEBUG, INFO, WARN, ERROR) 까지의 log 는 DEFAULT_FILE_APPENDER 로 출력해라
2. ERROR level 의 log 는 따로 ERROR_FILE_APPENDER 로 출력해라. 그리고 ERROR 발생 시 SLACK_ERROR appender 로 보내서 출력해라

로 확인할 수 있습니다.

## 적용 확인

확인을 위해서 `/player/list` 호출 시 SQLException 이 터지게 했습니다. RuntimeException 은 RuntimeExceptionHandler 로 처리되어 ERROR 를 출력하지 않으므로 checked Exception 인  SQLException 을 throw 합니다. (지금 생각해보니까 그냥 Exception 으로 하면 될텐데요... ㅎㅎ)

```java
@RequestMapping("/player")
public class PlayerController {

    private final PlayerService playerService;

    @GetMapping("/list")
    public ResponseEntity<List<PlayerResponseDto>> playerList() throws SQLException {

        throw new SQLException("SQL Exception");


//        return ResponseEntity.ok(playerService.playerList());
    }
```

- `/player/list` 호출 시 SQLException 이 터집니다.
- 정상적으로 동작한다면 해당 url 호출 시 `LogAspect.Controllerlog()` 호출 -> `PlayerController.playerList()` 호출 -> 예외 발생(SQLException) -> `LogAspect.ExceptionHandlerLog()` 호출 -> Error level 로깅 -> `GlobalExceptionHandler.handleException()` 호출 순으로 진행되겠습니다.

**실행 결과**

```
soccer.backend.aop.LogAspect             : test called the method: playerList
ERROR_FILE_LOGGER                        : handleException 실행
ERROR_FILE_LOGGER                        : test Error detail: 

java.sql.SQLException: SQL Exception
    at soccer.backend.controller.PlayerController.playerList(PlayerController.java:28)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
    ...
```

- 필요없는 Log 는 지웠습니다.
- 먼저 `LogAspect` 에서 `playerList` 메서드를 실행한다는 걸 찍어줬습니다. 
- 그리고 `playerList` 에서 Exception 이 터져서 또 다시 `LogAspect` 에서 `ERROR_FILE_LOGGER` 이라는 logger 가 `handleException 실행`, `test Error detail` 을 남겨줬습니다.

error-2023-04-24.0.log 파일은 다음과 같습니다.

![image-20230425000528028](../../images/2023-04-22-[socceranalyst] LogBack, AOP 를 활용한 로깅 및 slack 을 통한 알림 설정/image-20230425000528028.png)

# Slack 사용

슬랙을 사용하기 위해선 먼저 가입을 하고 채널을 생성해야 합니다. 저는 error_log 라는 채널을 생성해주었습니다. 

과정 자체는 쉬우니 https://slack.com/intl/ko-kr/ 에 접속해서 해보는 걸 추천합니다.

error_log 채널 생성 시 다음과 같이 보입니다.

![image-20230425000713874](../../images/2023-04-22-[socceranalyst] LogBack, AOP 를 활용한 로깅 및 slack 을 통한 알림 설정/image-20230425000713874.png)

- 테스트 하면서 남긴 로그가 있네요. 일단 좌측 배너를 보면 # error_log 가 있습니다. 해당 부분을 error_log 채널이라고 합니다.
- 만약 `local, dev, prod` 환경을 구분하고 싶다면 채널을 추가하고 slack-logback.yml 에서 `channel` 을 `profile` 에 맞게 변경해주면 되겠습니다. 저는 그냥 하나의 채널로 사용했습니다.
- 저기서 제일 상단의 #error_log 를 누르면 다음과 같이 나옵니다.

![image-20230425000836308](../../images/2023-04-22-[socceranalyst] LogBack, AOP 를 활용한 로깅 및 slack 을 통한 알림 설정/image-20230425000836308.png)

- 여기서 통합 > 앱 추가 를 눌러서 `incoming-webhook` 앱을 추가해줘야 합니다. 해당 앱으로 정보를 보내서 알림을 받게 됩니다.
- 추가하면 다음과 같이 됩니다.

![image-20230425000947678](../../images/2023-04-22-[socceranalyst] LogBack, AOP 를 활용한 로깅 및 slack 을 통한 알림 설정/image-20230425000947678.png)

- 해당 앱을 추가하면 url 이 나오는데, 그 값을 `slack-logback.yml` 에 넣어주면 됩니다.
- 이제 ERROR level logging 시 해당 화면과 같이 Error 가 잡힙니다.

![image-20230425000713874](../../images/2023-04-22-[socceranalyst] LogBack, AOP 를 활용한 로깅 및 slack 을 통한 알림 설정/image-20230425000713874.png)



# 마치며

다 구현하고 리뷰하면서 옮겨적은거라서 중간중간에 설정 빠졌을 수도 있습니다. 로깅 자체는 쉽다고 생각했는데 설정할 게 참 많네요. 

일단 로컬 환경에서는 잘 작동하는데요. ec2 로 옮겨주면 아무래도 아웃바운딩 설정을 추가해줘야 할 것 같습니다. 만약 에러가 나면 에러 해결에 관한 포스팅을 쓸 거같네요... 만약 그 포스팅이 없다면 "한번에 생각대로 잘 됐구나" 라고 생각해주시면 될 듯합니다.

하지만 아직 Redis 도 ec2 에 깔아만 놓고 RTR 적용을 안했는데요. 무조건 에러는 날 거 같습니다.

나중에 CI/CD 를 배워서 서버가 다운되는 일이 없도록 해야 하는데 아직까지는 실사용자 1명이라서 사용하는지 물어보고 서버내리면 돼서 편하긴 합니다.