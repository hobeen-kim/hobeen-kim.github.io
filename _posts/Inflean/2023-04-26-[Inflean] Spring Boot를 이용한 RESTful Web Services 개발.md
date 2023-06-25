---
categories: "inflearn"
tag: ["springboot", "spring", "restfulapi"]
series: "Spring Boot를 이용한 RESTful Web Services 개발"
series-link: "https://www.inflearn.com/course/spring-boot-restful-web-services/dashboard"
---

이번 강의는 Dowon Lee 님의 "Spring Boot를 이용한 RESTful Web Services 개발" 입니다.

6시간짜리 짧은 강의이고, 그 다음 강의인 MSA 를 듣기 위해 앞 강의를 듣고 있습니다.

내용 자체는 Spring MVC 쪽이라서 듣는 데 큰 어려움은 없었고, 몰랐거나 알았는데 까먹은 부분만 간단하게 정리했습니다.



# 1. ReponseEntity 에 location(URI) 정보 보내기

POST 를 통해서 user 정보를 받아 User 를 만들고 만들어진 user 에 접근하려면 다시 userId 값을 요청해서 받아야 합니다.

이때 POST 의 응답으로 해당 id 값을 보낸다면 두 번 요청할 일이 없습니다.

```java
@PostMapping("/users")
public ResponseEntity<User> createUser(@RequestBody User user){
    User savedUser = service.save(user);

    URI location = ServletUriComponentsBuilder.fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(savedUser.getId())
            .toUri();

    return ResponseEntity.created(location).build();
}
```

- 다음과 같이 URI location 을 만들어준 뒤, ResponseEntity.created() 의 파라미터로 넘겨주어서 201 Created 응답 header 에 넣어줍니다.

  ![image-20230426150020802](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230426150020802.png)

# 2. custom Exceptoin 의 응답코드 설정

Exception 이 던져질 때 응답코드는 기본적으로 500 입니다.

```java
@GetMapping("/users/{id}")
    public User retrieveUser(@PathVariable int id){
        User user = service.findOne(id);

        if(user == null){
            throw new UserNotFoundException(String.format("ID[%s] not found", id));
        }
        return user;
    }
```

- 위와 같이 user 정보를 조회할 때 id 값이 맞지않으면 UserNotFoundException 이 던져지는데, 해당 StatusCode 는 500 입니다. 

```java
package com.example.restfulwebservice.user;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.NOT_FOUND)
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
}
```

- 404 로 반환하기 위해 Exception 클래스에 `@ResponseStatus(HttpStatus.NOT_FOUND)` 를 추가해줍니다.

# 3. Locale 적용

locale 정보에 따라 message 를 변경하는 방법입니다.

1. **`LocaleResolver` 빈 등록**

```java
package com.example.restfulwebservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.servlet.LocaleResolver;
import org.springframework.web.servlet.i18n.SessionLocaleResolver;

import java.util.Locale;

@SpringBootApplication
public class RestfulWebServiceApplication {

public static void main(String[] args) {
		SpringApplication.run(RestfulWebServiceApplication.class, args);
	}

	@Bean
	public LocaleResolver localeResolver(){
		SessionLocaleResolver localeResolver = new SessionLocaleResolver();
		localeResolver.setDefaultLocale(Locale.KOREA);
		return localeResolver;
	}
}
```

- default 는 Locale.KOREA 로 합니다.



2. **언어별 message 등록**

- korean (messages.properties)

```properties
greeting.message=안녕하세요
```

- english (messages_en.properties)e

```properties
greeting.message=Hello
```

- french (messages_fr.properties)

```properties
greeting.message=Bonjour
```



3. Controller 에서 MessageSource 주입 및 사용

```java
...

@RestController
public class HelloWorldController {

    private final MessageSource messageSource;

    public HelloWorldController(MessageSource messageSource) {
        this.messageSource = messageSource;
    }

    ...

    @GetMapping("/hello-world-internationalized")
    public String helloWorldInternationalized(
            @RequestHeader(name="Accept-Language", required=false) Locale locale) {
        return messageSource.getMessage("greeting.message", null, locale);
    }
}

```

- Header 의 locale 정보를 가져옵니다.
- 해당 locale 정보로 `messageSource.getMessage()` 메서드를 통해 값을 return 합니다.

클라이언트측에서 locale 정보를 헤더로 변경했을 때 다음과 같이 반환받습니다.

![image-20230426162604741](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230426162604741.png)



# 4. JSON 에서 특정 필드 제거해서 전송(필터링)

## Response 데이터 제어를 위한 Filtering

jackson-datatype-jdk8 을 사용합니다.

**dependency**

```xml
<!-->jackson-dataformat-xml 추가-->
    <dependency>
        <groupId>com.fasterxml.jackson.datatype</groupId>
        <artifactId>jackson-datatype-jdk8</artifactId>
    </dependency>
```

강의에서는 `com.fasterxml.jackson.dataformat` 의 `jackson-dataformat-xml` 를 추가했지만 해당 라이브러리가 deprecated 됐는지 없어서 비슷한 거 추가했습니다. 필요한 어노테이션 (`@JsonIgnore`) 은 있어서 그대로 사용하면 될 듯합니다.

**User**

```java
package com.example.restfulwebservice.user;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AllArgsConstructor;
import lombok.Data;

import javax.validation.constraints.Past;
import javax.validation.constraints.Size;
import java.util.Date;

@Data
@AllArgsConstructor
@JsonIgnoreProperties(value={"password", "ssn"})
public class User {
    private Integer id;

    @Size(min = 2, message = "Name은 2글자 이상 입력해주세요.")
    private String name;
    @Past
    private Date joinDate;
//    @JsonIgnore
    private String password;
//    @JsonIgnore
    private String ssn;
}
```

- 다음과 같이 배열 형태로 class 에 무시할 properties 를 적용해줍니다. `@JsonIgnoreProperties(value={"password", "ssn"})`
- 주석처리한 것처럼 필드에 직접 선언해도 무방합니다.

**결과**

![image-20230426164432451](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230426164432451.png)

- password, ssn 값이 안넘어오는 것을 볼 수 있습니다.

> 주의 
>
> 1. 클라이언트 측으로 넘어가지는 않지만 해당 도메인(User)이 controller 나 dao 로 넘어갈 때(서버 내에서 사용될 때) 값은 여전히 넘어갑니다.
>
>    ![image-20230426164627910](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230426164627910.png)
>
> 2. 따라서 Dto 를 사용하는 방법이 아직까지는 더 나아보입니다.

## 프로그래밍으로 데이터 제어(@JsonFilter)

**User**

```java
package com.example.restfulwebservice.user;

import com.fasterxml.jackson.annotation.JsonFilter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AllArgsConstructor;
import lombok.Data;

import javax.validation.constraints.Past;
import javax.validation.constraints.Size;
import java.util.Date;

@Data
@AllArgsConstructor
@JsonFilter("UserInfo")
public class User {
    private Integer id;

    @Size(min = 2, message = "Name은 2글자 이상 입력해주세요.")
    private String name;
    @Past
    private Date joinDate;
    private String password;
    private String ssn;
}

```

- 다음과 같이 `@JsonFilter("UserInfo")` 로 Filter 를 설정합니다. 이제 해당 User 를 가져오기 위해선 UserInfo 필터를 사용해야 ㅎ바니다.

**AdminUserController**

관리자 전용 UserController 입니다. (관리자 전용으로 controller 를 만드는 건 좋은 아이디어다. 프로젝트에 적용해봐야겠습니다.)

```java
package com.example.restfulwebservice.user;

import com.fasterxml.jackson.databind.ser.FilterProvider;
import com.fasterxml.jackson.databind.ser.impl.SimpleBeanPropertyFilter;
import com.fasterxml.jackson.databind.ser.impl.SimpleFilterProvider;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.json.MappingJacksonValue;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import javax.validation.Valid;
import java.net.URI;
import java.util.List;

@RestController
@RequestMapping("/admin")
public class AdminUserController {

    private final UserDaoService service;

    public AdminUserController(UserDaoService service) {
        this.service = service;
    }

    @GetMapping("/users")
    public MappingJacksonValue retrieveAllUsers(){
        List<User> users = service.findAll();

        SimpleBeanPropertyFilter filter = SimpleBeanPropertyFilter
                .filterOutAllExcept("id", "name", "joinDate", "ssn");

        FilterProvider filters = new SimpleFilterProvider().addFilter("UserInfo", filter);

        MappingJacksonValue mapping = new MappingJacksonValue(users);
        mapping.setFilters(filters);

        return mapping;
    }

    @GetMapping("/users/{id}")
    public MappingJacksonValue retrieveUser(@PathVariable int id){
        User user = service.findOne(id);

        if(user == null){
            throw new UserNotFoundException(String.format("ID[%s] not found", id));
        }

        SimpleBeanPropertyFilter filter = SimpleBeanPropertyFilter
                .filterOutAllExcept("id", "name", "joinDate", "ssn");

        FilterProvider filters = new SimpleFilterProvider().addFilter("UserInfo", filter);

        MappingJacksonValue mapping = new MappingJacksonValue(user);
        mapping.setFilters(filters);

        return mapping;
    }
}

```

- 사용자 전체 조회(`retrieveAllUsers()`), 특정 사용자 조회(`retrieveUser()`)가 가능하다.
- 필터를 만들고 등록한다.
  1. `SimpleBeanPropertyFilter` 클래스로 어떤 필드를 받을 것인지 설정합니다.
  2. `FilterProvider` 클래스로 만들어진 객체인 `filters` 에 `filter` 를 추가한 뒤,
  3. `new MappingJacksonValue(user)` 으로 `MappingJacksonValue` 객체를 만든 후,
  4. `mapping` 과 `filters` 를 연결해준다.



# 5. REST API 버전 관리

카카오의 버전 관리 예시입니다.

![image-20230426213351783](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230426213351783.png)

- url 을 잘 보면, `v2` 라고 되어있습니다. 이렇게 API 에 직접 버전을 표시해주어 버전관리가 가능합니다.

예제 코드로 살펴보면 다음과 같습니다.

**AdminUserController**

```java
@GetMapping("/v1/users/{id}")
public MappingJacksonValue retrieveUserV1(@PathVariable int id){
    User user = service.findOne(id);

    if(user == null){
        throw new UserNotFoundException(String.format("ID[%s] not found", id));
    }

    SimpleBeanPropertyFilter filter = SimpleBeanPropertyFilter
            .filterOutAllExcept("id", "name", "joinDate", "ssn");

    FilterProvider filters = new SimpleFilterProvider().addFilter("UserInfo", filter);

    MappingJacksonValue mapping = new MappingJacksonValue(user);
    mapping.setFilters(filters);

    return mapping;
}

@GetMapping("/v2/users/{id}")
public MappingJacksonValue retrieveUserV2(@PathVariable int id){
    User user = service.findOne(id);

    if(user == null){
        throw new UserNotFoundException(String.format("ID[%s] not found", id));
    }

    // User -> User2
    UserV2 userV2 = new UserV2("VIP");
    BeanUtils.copyProperties(user, userV2);

    SimpleBeanPropertyFilter filter = SimpleBeanPropertyFilter
            .filterOutAllExcept("id", "name", "joinDate", "grade");

    FilterProvider filters = new SimpleFilterProvider().addFilter("UserInfoV2", filter);

    MappingJacksonValue mapping = new MappingJacksonValue(userV2);
    mapping.setFilters(filters);

    return mapping;
}
```

- v1 은 기존코드, v2 는 새로운 UserV2 도메인을 사용합니다.

**UserV2**

```java
package com.example.restfulwebservice.user;

import com.fasterxml.jackson.annotation.JsonFilter;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.validation.constraints.Past;
import javax.validation.constraints.Size;
import java.util.Date;

@Data
@AllArgsConstructor
@JsonFilter("UserInfoV2")
public class UserV2 extends User{
    private String grade;

}
```

- UserV2 는 User 를 상속받고 grade 필드를 추가합니다.

## 추가적인 버전관리

다음과 같이 `@GetMapping` 어노테이션에 값을 추가하여 버전관리를 할 수 있습니다.

```java
@GetMapping("/v1/users/{id}")
@GetMapping(value = "/users/{id}/", params = "version=1")
@GetMapping(value = "/users/{id}", headers = "X-API-VERSION=1")
@GetMapping(value = "/users/{id}", produces = "application/vnd.company.appv1+json")
```

1. pathVariable 사용
2. params 사용
3. 헤더 사용
4. 헤더 accept 사용



# 6. HATEOAS 

HATEOAS(Hypermedia As the Engine Of Application State) 는 현재 리소스와 연관된(호출 가능한) 자원 상태 정보를 제공하는 것입니다. 쉽게 말해 현재 페이지에서 호출 가능한 URI 입니다.

스프링 부트에서는 `spring-boot-starter-hateoas` dependency 로 hateoas 를 만들 수 있습니다.

**pom.xml**

```xml
<!--hateoas 추가-->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-hateoas</artifactId>
    </dependency>
```

**UserController**

```java
...;

@RestController
public class UserController {

    private final UserDaoService service;

    public UserController(UserDaoService service) {
        this.service = service;
    }

    @GetMapping("/users")
    public List<User> retrieveAllUsers(){
        return service.findAll();
    }

    @GetMapping("/users/{id}")
    public EntityModel<User> retrieveUser(@PathVariable int id){
        User user = service.findOne(id);

        if(user == null){
            throw new UserNotFoundException(String.format("ID[%s] not found", id));
        }

        //HATEOAS
        EntityModel<User> model = EntityModel.of(user);
        WebMvcLinkBuilder linkTo =
                linkTo(methodOn(this.getClass()).retrieveAllUsers());

        model.add(linkTo.withRel("all-users"));

        return model;
    }

    ...
}

```

- 반환타입 : EntityModel<User>
- `EntityModel` :  해당 클래스로 반환할 user 정보를 받습니다.
- `WebMvcLinkBuilder` : linkTo 메서드로 현재 객체의 `retrieveAllUsers()` 메서드의 링크를 받습니다.
- `model.add(linkTo.withRel("all-users"));` user 정보가 담긴 model 에 link 를 추가합니다. 해당 링크의 이름은 `all-users` 입니다.
- 결과는 아래와 같습니다.

![image-20230427114537496](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230427114537496.png)

# 7. Swagger

Swagger 는 애플리케이션의 RESTful API 문서를 자동으로 구성하는 특수 도구입니다.

Swagger 는 애플리케이션의 모든 엔드포인트를 살펴볼 수 있을 뿐만 아니라 요청을 보내고 응답을 수신하여 작동 중인 엔드포인트를 즉시 테스트할 수 있습니다.

**pom.xml**

```xml
<!--swagger 추가-->
    <dependency>
        <groupId>io.springfox</groupId>
        <artifactId>springfox-boot-starter</artifactId>
        <version>3.0.0</version>
    </dependency>
    <!--swagger ui 추가-->
    <dependency>
        <groupId>io.springfox</groupId>
        <artifactId>springfox-swagger-ui</artifactId>
        <version>3.0.0</version>
    </dependency>
```

**application.yml**

```yml
spring:
  mvc:
    pathmatch:
      matching-strategy: ant_path_matcher
```

**SwaggerConfig**

```java
package com.example.restfulwebservice.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

@Configuration
@EnableSwagger2
public class SwaggerConfig {

    @Bean
    public Docket api() {
        return new Docket(DocumentationType.SWAGGER_2);
    }
}
```

- swagger config 를 등록하여 swagger 를 볼 수 있도록 설정합니다.

**결과**

http://localhost:8088/v2/api-docs

![image-20230427125906264](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230427125906264.png)

- swagger 로 나타내지는 정보, tag, 각 api 의 status code 별 응답 등을 볼 수 있습니다.

http://localhost:8088/swagger-ui/index.html#/

![image-20230427125954191](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230427125954191.png)

- swagger-ui 로 API Doucmentation 을 만들어서 보기 쉽도록 나타낼 수 있습니다.

## Swagger Custom

다음과 같이 Config 파일을 수정해서 custom 을 만들 수 있습니다.

**SwaggerConfig**

```java
package com.example.restfulwebservice.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.service.ApiInfo;
import springfox.documentation.service.Contact;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

@Configuration
@EnableSwagger2
public class SwaggerConfig {

    private static final Contact DEFAULT_CONTACT = new Contact(
            "kennth Lee",
            "http://www.joneconsulting.co.kr",
            "edowon@joneconsulting.co.kr"
            );
    private static final ApiInfo DEFAULT_API_INFO = new ApiInfo(
            "Awesome API Title",
            "My User management REST API service",
            "1.0",
            "urn:tos",
            DEFAULT_CONTACT,
            "Apache 2.0",
            "http://www.apache.org/licenses/LICENSE-2.0",
            new ArrayList<>()
    );
    private static final Set<String> DEFAULT_PRODUCES_AND_CONSUMES =
            new HashSet<>(Arrays.asList("application/json", "application/xml"));

    @Bean
    public Docket api() {
        return new Docket(DocumentationType.SWAGGER_2)
                .apiInfo(DEFAULT_API_INFO) // apiInfo() 메소드를 통해 API 문서에 표시될 정보를 설정한다.
                .produces(DEFAULT_PRODUCES_AND_CONSUMES) // produces() 메소드를 통해 API가 생산하는 MIME 타입을 지정한다.
                .consumes(DEFAULT_PRODUCES_AND_CONSUMES); // consumes() 메소드를 통해 API가 소비하는 MIME 타입을 지정한다.
    }
}
```

다음과 같이 info 가 변경된 것을 확인할 수 있습니다.

![image-20230427133246664](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230427133246664.png)

**User**

- user 도메인에 Api 어노테이션을 추가하여 swagger-ui 페이지에 description 을 추가할 수 있습니다.

```java
package com.example.restfulwebservice.user;

import com.fasterxml.jackson.annotation.JsonFilter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.validation.constraints.Past;
import javax.validation.constraints.Size;
import java.util.Date;

@Data
@AllArgsConstructor
@NoArgsConstructor
//@JsonFilter("UserInfo") //HATEOAS 확인을 위해 잠시 주석처리
@ApiModel(description = "사용자 상세 정보를 위한 도메인 객체") //Swagger
public class User {
    private Integer id;

    @Size(min = 2, message = "Name은 2글자 이상 입력해주세요.")
    @ApiModelProperty(notes = "사용자 이름을 입력해주세요.") //Swagger
    private String name;
    @Past
    @ApiModelProperty(notes = "사용자 등록일을 입력해주세요.") //Swagger
    private Date joinDate;
    @ApiModelProperty(notes = "사용자 패스워드를 입력해주세요.") //Swagger
    private String password;
    @ApiModelProperty(notes = "사용자 주민번호를 입력해주세요.") //Swagger
    private String ssn;
}
```

![image-20230427133347588](../../images/2023-04-26-[inflearn] Spring Boot를 이용한 RESTful Web Services 개발/image-20230427133347588.png)