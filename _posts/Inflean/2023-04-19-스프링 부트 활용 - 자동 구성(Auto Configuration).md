---
categories: "inflearn"
tag: ["springboot", "spring", "autoconfiguration"]
---

<div class="notice--danger">
    <b>해당 내용 중 일부 실사용 목적의 학습이 아닌, 스프링 부트 이해를 위한 학습입니다.</b>
</div>
# 0. 예제만들기

JdbcTemplate 을 사용해서 회원 데이터를 DB에 저장하고 조회하는 간단한 기능이다.

**Member**

```java
package hello.member;

import lombok.Data;

@Data
public class Member {

    private String memberId;
    private String name;

    public Member(String memberId, String name) {
        this.memberId = memberId;
        this.name = name;
    }

    public Member() {}
}
```

**DbConfig**

```java
package hello.config;

import com.zaxxer.hikari.HikariDataSource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.JdbcTransactionManager;
import org.springframework.transaction.TransactionManager;

import javax.sql.DataSource;

@Slf4j
@Configuration
public class DbConfig {

    @Bean
    public DataSource dataSource() {
        log.info("DataSource 빈 등록");
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setDriverClassName("org.h2.Driver");
        dataSource.setJdbcUrl("jdbc:h2:mem:test");
        dataSource.setUsername("sa");
        dataSource.setPassword("");
        return dataSource;
    }

    @Bean
    public TransactionManager transactionManager() {
        log.info("TransactionManager 빈 등록");
        return new JdbcTransactionManager(dataSource());
    }

    @Bean
    public JdbcTemplate jdbcTemplate() {
        log.info("JdbcTemplate 빈 등록");
        return new JdbcTemplate(dataSource());
    }
}
```

- JdbcTemplate 을 사용해서 회원 데이터를 DB에 보관하고 관리하는 기능이다.
- DataSource , TransactionManager , JdbcTemplate 을 스프링 빈으로 직접 등록한다.
- DB는 별도의 외부 DB가 아니라 JVM 내부에서 동작하는 메모리 DB를 사용한다. 
  - 메모리 모드로 동작 옵선: jdbc:h2:mem:test

**MemberRepository**

```java
package hello.member;

import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class MemberRepository {

    public final JdbcTemplate template;

    public MemberRepository(JdbcTemplate template) {
        this.template = template;
    }

    public void initTable(){
        template.execute("create table member (member_id varchar primary key, name varchar)");
    }

    public void save(Member member){
        template.update("insert into member (member_id, name) values (?, ?)",
                member.getMemberId(),
                member.getName());
    }

    public Member findById(String memberId){
        return template.queryForObject("select member_id, name from member where member_id = ?",
               BeanPropertyRowMapper.newInstance(Member.class), memberId);
    }

    public List<Member> findAll(){
        return template.query("select member_id, name from member",
                BeanPropertyRowMapper.newInstance(Member.class));
    }
}

```

- JdbcTemplate 을 사용해서 회원을 관리하는 리포지토리이다.
- initTable : 보통 리포지토리에 테이블을 생성하는 스크립트를 두지는 않는다. 여기서는 예제를 단순화 하기 위해 이곳에 사용했다.

**MemberRepositoryTest**

```java
package hello.member;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class MemberRepositoryTest {

    @Autowired MemberRepository memberRepository;

    @Transactional
    @Test
    void memberTest(){
        Member member = new Member("IdA", "memberA");
        memberRepository.initTable();
        memberRepository.save(member);
        Member findMember = memberRepository.findById(member.getMemberId());

        assertThat(findMember.getMemberId()).isEqualTo(member.getMemberId());
        assertThat(findMember.getName()).isEqualTo(member.getName());
    }
}
```

- 테이블을 생성하고, 회원 데이터를 저장한 다음 다시 조회해서, 기존 데이터와 같은지 간단히 검증한다.

# 1. 자동 구성 확인

JdbcTemplate , DataSource , TransactionManager 가 스프링 컨테이너에 잘 등록되었는지 간단히 확인해본다.

```java
package hello.config;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.TransactionManager;

import javax.sql.DataSource;

import static org.junit.jupiter.api.Assertions.*;
import static org.assertj.core.api.Assertions.assertThat;

@Slf4j
@SpringBootTest
class DbConfigTest {

    @Autowired
    DataSource dataSource;

    @Autowired
    TransactionManager transactionManager;

    @Autowired
    JdbcTemplate jdbcTemplate;

    @Test
    void checkBean(){

        log.info("DataSource: {}", dataSource);
        log.info("TransactionManager: {}", transactionManager);
        log.info("JdbcTemplate: {}", jdbcTemplate);

        assertThat(dataSource).isNotNull();
        assertThat(transactionManager).isNotNull();
        assertThat(jdbcTemplate).isNotNull();

    }


```

- 해당 빈들을 DbConfig 설정을 통해 스프링 컨테이너에 등록했기 때문에, null 이면 안된다.

- 테스트는 정상이고 모두 의존관계 주입이 정상 처리된 것을 확인할 수 있다.

  - ```
    hello.config.DbConfig : dataSource 빈 등록
    hello.config.DbConfig : jdbcTemplate 빈 등록
    hello.config.DbConfig : transactionManager 빈 등록
    ...
    ..DbConfigTest: dataSource = HikariDataSource (null)
    ..DbConfigTest: transactionManager =
    org.springframework.jdbc.support.JdbcTransactionManager@5e99e2cb
    ..DbConfigTest: jdbcTemplate =
    org.springframework.jdbc.core.JdbcTemplate@76ac68b0
    ```



**빈 등록 제거**

이번에는 DbConfig 에서 해당 빈들을 등록하지 않고 제거해보자. (@Configuration 주석 처리)

```java

@Slf4j
//@Configuration
public class DbConfig {

    @Bean
    public DataSource dataSource() {
        log.info("DataSource 빈 등록");
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setDriverClassName("org.h2.Driver");
        dataSource.setJdbcUrl("jdbc:h2:mem:test");
        dataSource.setUsername("sa");
        dataSource.setPassword("");
        return dataSource;
    }

    @Bean
    public TransactionManager transactionManager() {
        log.info("TransactionManager 빈 등록");
        return new JdbcTransactionManager(dataSource());
    }

    @Bean
    public JdbcTemplate jdbcTemplate() {
        log.info("JdbcTemplate 빈 등록");
        return new JdbcTemplate(dataSource());
    }
}
```

DbConfigTest.checkBean() 테스트를 다시 실행해보자.

```
...
..DbConfigTest: dataSource = HikariDataSource (null)
..DbConfigTest: transactionManager =
org.springframework.jdbc.support.JdbcTransactionManager@5e99e2cb
..DbConfigTest: jdbcTemplate =
org.springframework.jdbc.core.JdbcTemplate@76ac68b0
```

- 등록했던 `log.info("000 빈 등록")` 은 출력되지 않는다.
- 그런데 테스트는 정상 통과하고 심지어 출력결과에 JdbcTemplate , DataSource , TransactionManager 빈들이 존재하는 것을 확인할 수 있다. **이 빈들은 모두 스프링 부트가 자동으로 등록해 준 것이다.**

# 2. 스프링 부트의 자동 구성

스프링 부트는 자동 구성(Auto Configuration)이라는 기능을 제공하는데, 일반적으로 자주 사용하는 수 많은 빈들을 자동으로 등록해주는 기능이다.

스프링 부트는 spring-boot-autoconfigure 라는 프로젝트 안에서 수 많은 자동 구성을 제공한다. JdbcTemplate 을 설정하고 빈으로 등록해주는 자동 구성을 확인해보자.

## JdbcTemplate 자동 구성

**JdbcTemplateAutoConfiguration**

```java
package org.springframework.boot.autoconfigure.jdbc;
import javax.sql.DataSource;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import
org.springframework.boot.autoconfigure.condition.ConditionalOnSingleCandidate;
import
org.springframework.boot.context.properties.EnableConfigurationProperties;
import
org.springframework.boot.sql.init.dependency.DatabaseInitializationDependencyCo
nfigurer;
import org.springframework.context.annotation.Import;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;

@AutoConfiguration(after = DataSourceAutoConfiguration.class)
@ConditionalOnClass({ DataSource.class, JdbcTemplate.class })
@ConditionalOnSingleCandidate(DataSource.class)
@EnableConfigurationProperties(JdbcProperties.class)
@Import({ DatabaseInitializationDependencyConfigurer.class, JdbcTemplateConfiguration.class, NamedParameterJdbcTemplateConfiguration.class })
public class JdbcTemplateAutoConfiguration {
}
```

- `@AutoConfiguration` : 자동 구성을 사용하려면 이 애노테이션을 등록해야 한다.
  - `after = DataSourceAutoConfiguration.class` :  자동 구성이 실행되는 순서를 지정할 수 있다. JdbcTemplate 은 DataSource 가 필요하기 때문에 DataSource 를 자동으로 등록해주는 DataSourceAutoConfiguration 다음에 실행하도록 설정되어 있다.
- `@ConditionalOnClass({ DataSource.class, JdbcTemplate.class })` :이런 클래스가 있는 경우에만 설정이 동작한다. 만약 없으면 여기 있는 설정들이 모두 무효화 되고, 빈도 등록되지 않는다.
- `@Import` : 스프링에서 자바 설정을 추가할 때 사용한다.

@Import 의 대상이 되는 JdbcTemplateConfiguration 를 추가로 확인해보자.

**JdbcTemplateConfiguration** 

```java
/*
 * Copyright 2012-2019 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.springframework.boot.autoconfigure.jdbc;

import javax.sql.DataSource;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.jdbc.core.JdbcOperations;
import org.springframework.jdbc.core.JdbcTemplate;

/**
 * Configuration for {@link JdbcTemplateConfiguration}.
 *
 * @author Stephane Nicoll
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnMissingBean(JdbcOperations.class)
class JdbcTemplateConfiguration {

	@Bean
	@Primary
	JdbcTemplate jdbcTemplate(DataSource dataSource, JdbcProperties properties) {
		JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
		JdbcProperties.Template template = properties.getTemplate();
		jdbcTemplate.setFetchSize(template.getFetchSize());
		jdbcTemplate.setMaxRows(template.getMaxRows());
		if (template.getQueryTimeout() != null) {
			jdbcTemplate.setQueryTimeout((int) template.getQueryTimeout().getSeconds());
		}
		return jdbcTemplate;
	}

}
```

- `@Configuration` : 자바 설정 파일로 사용된다.
- `@ConditionalOnMissingBean(JdbcOperations.class)`
  - JdbcOperations 빈이 없을 때 동작한다. JdbcTemplate 의 부모 인터페이스가 바로 JdbcOperations 이다.
  - 쉽게 이야기해서 개발자가 직접 등록한 JdbcTemplate 이 빈으로 등록되어 있지 않은 경우에만 동작한다.

## 자동 등록 설정

다음과 같은 자동 구성 기능들이 다음 빈들을 등록해준다.

- JdbcTemplateAutoConfiguration : JdbcTemplate 
- DataSourceAutoConfiguration : DataSource 
- DataSourceTransactionManagerAutoConfiguration : TransactionManager

**스프링 부트가 제공하는 자동 구성(AutoConfiguration)**

- https://docs.spring.io/spring-boot/docs/current/reference/html/auto-configurationclasses.html



# 3. 자동 구성 직접 만들기 - 기반 예제

실시간으로 자바 메모리 사용량을 웹으로 확인하는 예제이다. (바로 autoConfiguration 을 적용하는 건 아니다.)

main.java 에 바로 memory 패키지를 만들어서 그 안에 예제를 넣는다. 

즉, 외부에서 라이브러리를 configuration 하는 것처럼 만들 것이다.

**Memory**

```java
package hello.member;

import lombok.Data;

@Data
public class Member {

    private String memberId;
    private String name;

    public Member(String memberId, String name) {
        this.memberId = memberId;
        this.name = name;
    }

    public Member() {}
}

```

- used : 사용중인 메모리, max : 최대 메모리 -> used 가 max 를 넘게 되면 메모리 부족 오류가 발생하도록 할 것이다.

**MemoryFinder**

```java
package memory;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MemoryFinder {

    public Memory get(){
        long max = Runtime.getRuntime().maxMemory();
        long total = Runtime.getRuntime().totalMemory();
        long free = Runtime.getRuntime().freeMemory();
        long used = total - free;

        return new Memory(used, max);
    }

    @PostConstruct
    public void init(){
        log.info("init MemoryFinder");
    }
}
```

JVM에서 메모리 정보를 실시간으로 조회하는 기능이다.

- max 는 JVM이 사용할 수 있는 최대 메모리, 이 수치를 넘어가면 OOM이 발생한다.
- total 은 JVM이 확보한 전체 메모리(JVM은 처음부터 max 까지 다 확보하지 않고 필요할 때 마다 조금씩 확보한다.) 
- free 는 total 중에 사용하지 않은 메모리(JVM이 확보한 전체 메모리 중에 사용하지 않은 것) 
- used 는 JVM이 사용중인 메모리이다. ( used = total - free )

**MemoryController**

```java
package memory;


import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequiredArgsConstructor
public class MemoryController {

    private final MemoryFinder memoryFinder;

    @GetMapping("/memory")
    public Memory system(){
        Memory memory = memoryFinder.get();
        log.info("memory: {}", memory);
        return memory;
    }
}
```

**MemoryConfig**

main.java.hello 패지키 내의 config 폴더이다.

```java
package hello.config;

import memory.MemoryController;
import memory.MemoryFinder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MemoryConfig {

    @Bean
    public MemoryController memoryController(){
        return new MemoryController(memoryFinder());
    }

    @Bean
    public MemoryFinder memoryFinder(){
        return new MemoryFinder();
    }
}
```

memoryController , memoryFinder 를 빈으로 등록한다.

## 실행

- 실행: `http://localhost:8080/memory` 
- 결과 {"used":24385432,"max":8589934592}



# 4. @Conditional

앞서 만든 메모리 조회 기능을 항상 사용하는 것이 아니라 특정 조건일 때만 해당 기능이 활성화 되도록 해보자. 예를 들어서 개발 서버에서 확인 용도로만 해당 기능을 사용하고, 운영 서버에서는 해당 기능을 사용하지 않는 것이다.

같은 소스 코드인데 특정 상황일 때만 특정 빈들을 등록해서 사용하도록 도와주는 기능이 바로 `@Conditional` 이다. 이 기능을 사용하려면 먼저 Condition 인터페이스를 구현해야 한다. 

**MemoryCondition**

```java
package memory;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.type.AnnotatedTypeMetadata;

@Slf4j
public class MemoryCondition implements Condition {
    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {

        //-Dmemory=on
        String memory = context.getEnvironment().getProperty("memory");
        log.info("memory: {}", memory);
        return "on".equals(memory);
    }
}

```

- 환경 정보에 memory=on 이라고 되어 있는 경우에만 true 를 반환한다.

**MemoryConfig - 수정**

```java
package hello.config;

import memory.MemoryCondition;
import memory.MemoryController;
import memory.MemoryFinder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;

@Configuration
@Conditional(MemoryCondition.class) //추가된 로직
public class MemoryConfig {

    @Bean
    public MemoryController memoryController(){
        return new MemoryController(memoryFinder());
    }

    @Bean
    public MemoryFinder memoryFinder(){
        return new MemoryFinder();
    }
}
```

@Conditional(MemoryCondition.class)

- 이제 MemoryConfig 의 적용 여부는 @Conditional 에 지정한 MemoryCondition 의 조건에 따라 달라진다. (true 면 빈등록, false 면 빈 등록이 안됨)

momory=on 조건은 VM 옵션을 추가해서 줄 수 있다.

![image-20230421145216086](../../images/2023-04-19-스프링 부트 활용 - 자동 구성(Auto Configuration)/image-20230421145216086.png)



# 5. @Conditional - 다양한 기능

지금까지 Condition 인터페이스를 직접 구현해서 MemoryCondition 이라는 구현체를 만들었다. 스프링은 이미 필요한 대부분의 구현체를 만들어두었다. 

**MemoryConfig - 수정**

```java
package hello.config;

import memory.MemoryCondition;
import memory.MemoryController;
import memory.MemoryFinder;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConditionalOnProperty(name = "memory", havingValue = "on")
public class MemoryConfig {

    @Bean
    public MemoryController memoryController(){
        return new MemoryController(memoryFinder());
    }

    @Bean
    public MemoryFinder memoryFinder(){
        return new MemoryFinder();
    }
}
```

@ConditionalOnProperty(name = "memory", havingValue = "on") 를 추가한다.

- 환경 정보가 memory=on 이라는 조건에 맞으면 동작하고, 그렇지 않으면 동작하지 않는다. 우리가 앞서 만든 기능과 동일하다.

**@ConditionalOnProperty**

```java
package org.springframework.boot.autoconfigure.condition;
@Conditional(OnPropertyCondition.class)
public @interface ConditionalOnProperty {...}
```

@ConditionalOnProperty 도 우리가 만든 것과 동일하게 내부에는 @Conditional 을 사용한다. 그리고 그 안에 Condition 인터페이스를 구현한 OnPropertyCondition 를 가지고 있다.


**@ConditionalOnXxx**

스프링은 @Conditional 과 관련해서 개발자가 편리하게 사용할 수 있도록 수 많은 @ConditionalOnXxx 를 제공한다.

- @ConditionalOnClass , @ConditionalOnMissingClass 
  - 클래스가 있는 경우 동작한다. 나머지는 그 반대 
- @ConditionalOnBean , @ConditionalOnMissingBean 
  - 빈이 등록되어 있는 경우 동작한다. 나머지는 그 반대 
- @ConditionalOnProperty 
  - 환경 정보가 있는 경우 동작한다. 
- @ConditionalOnResource 
  - 리소스가 있는 경우 동작한다. 
- @ConditionalOnWebApplication , @ConditionalOnNotWebApplication 
  - 웹 애플리케이션인 경우 동작한다. 
- @ConditionalOnExpression 
  - SpEL 표현식에 만족하는 경우 동작한다.

# 6. 순수 라이브러리 만들기

@AutoConfiguration 을 이해하기 위해서는 그 전에 먼저 라이브러리가 어떻게 사용되는지 이해하는 것이 필요하다. 실시간 자바 Memory 조회 기능을 여러곳에서 사용할 수 있도록 라이브러리로 만들어보자.

**빌드하기**

`./gradlew clean build`

빌드 결과 : `build/libs/memory-v1.jar`

# 7. 순수 라이브러리 사용하기

- project-v1 폴더 사용

**HelloController**

프로젝트가 동작하는지 확인하기 위해 간단한 컨트롤러를 추가

```java
package hello.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello(){
        return "hello";
    }
}
```



## 라이브러리 등록

앞서 만든 memory-v1.jar 라이브러리를 project-v1 에 적용해보자.

**라이브러리 추가**

1. project-v1/libs 폴더를 생성
2. memory-v1 프로젝트에서 빌드한 memory-v1.jar 를 이곳에 복사
3. project-v1/build.gradle 에 memory-v1.jar 를 추가

```java
dependencies {
    implementation files('libs/memory-v1.jar') //추가
    implementation 'org.springframework.boot:spring-boot-starter-web'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

- 라이브러리를 jar 파일로 직접 가지고 있으면 files 로 지정하면 된다.

### 라이브러리 설정

라이브러리를 스프링 빈으로 등록해서 동작하도록 만든다.

**MemoryConfig**

```java
package hello.config;

import memory.MemoryController;
import memory.MemoryFinder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MemoryConfig {

    @Bean
    public MemoryFinder memoryFinder(){
        return new MemoryFinder();
    }

    @Bean
    public MemoryController memoryController(){
        return new MemoryController(memoryFinder());
    }
}
```

- 스프링 부트 자동 구성을 사용하는 것이 아니기 때문에 빈을 직접 하나하나 등록해주어야 한다.

실행결과 : 실행 - `http://localhost:8080/memory` 결과 - `{"used": 38174528, "max": 8589934592}`
메모리 조회 라이브러리가 잘 동작하는 것을 확인할 수 있다.

*그런데 라이브러리를 사용하는 클라이언트 개발자 입장을 생각해보면, 라이브러리 내부에 있는 어떤 빈을 등록해야하는지 알아야 하고, 그것을 또 하나하나 빈으로 등록해야 한다. 지금처럼 간단한 라이브러리가 아니라 초기 설정이 복잡하다면 사용자 입장에서는 상당히 귀찮은 작업이 될 수 있다. 이런 부분을 자동으로 처리해주는 것이 바로 **스프링 부트 자동 구성(Auto Configuration)**이다.*



# 8. 자동 구성 라이브러리 만들기

프로젝트에 라이브러리를 추가만 하면 모든 구성이 자동으로 처리되도록 해보자. 쉽게 이야기해서 스프링 빈들이 자동으로 등록되는 것이다. 

## 자동 구성 라이브러리 만들기

memory-v1 프로젝트를 복사해서 memory-v2 를 만든다.

**settings.gradle - 수정**

`rootProject.name = 'memory-v2'` //v1 -> v2로 수정

**MemoryAutoConfig**

```java
package memory;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;

@AutoConfiguration
@ConditionalOnProperty(name = "memory", havingValue = "on")
public class MemoryAutoConfig {

    @Bean
    public MemoryFinder memoryFinder(){
        return new MemoryFinder();
    }

    @Bean
    public MemoryController memoryController(){
        return new MemoryController(memoryFinder());
    }
}
```

`@AutoConfiguration` : 스프링 부트가 제공하는 자동 구성 기능을 적용할 때 사용하는 애노테이션이다.
`@ConditionalOnProperty` : memory=on 이라는 환경 정보가 있을 때 라이브러리를 적용한다. (스프링 빈을 등록한다.)

**자동 구성 대상 지정**

이 부분이 중요하다. 스프링 부트 자동 구성을 적용하려면, 다음과 같은 파일을 생성해서 자동 구성 대상을 꼭 지정해주어야 한다.

파일 생성 : `src/main/resources/META-INF/spring/ org.springframework.boot.autoconfigure.AutoConfiguration.imports`
무조건 해당 디렉토리 구조여야하며, 파일명도 해당 파일명이어야 한다.

org.springframework.boot.autoconfigure.AutoConfiguration.imports

```
memory.MemoryAutoConfig //해당 내용을 넣어야 한다.
```

앞서 만든 자동 구성인 memory.MemoryAutoConfig 를 패키지를 포함해서 지정해준다.

*스프링 부트는 시작 시점에 org.springframework.boot.autoconfigure.AutoConfiguration.imports 의 정보를 읽어서 자동 구성으로 사용한다. 따라서 내부에 있는 MemoryAutoConfig 가 자동으로 실행된다.*

`./gradlew clean build` 로 빌드하여 jar 파일을 만든다.

## 자동 구성 라이브러리 사용하기

`project-v2` 사용

**memory-v2.jar 복사**

memory-v2 에서 만든 jar 파일을 project-v2/libs 폴더에 넣는다.

**build.gradle 수정**

```java
dependencies {
    implementation files('libs/memory-v2.jar') //추가
    implementation 'org.springframework.boot:spring-boot-starter-web'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

**실행**

memory-v2 의 autoConfiguration 에서 memory=on 조건을 할 때만 동작하도록 했기 때문에 VM 옵션을 추가하고 실행한다.

![image-20230421183657718](../../images/2023-04-19-스프링 부트 활용 - 자동 구성(Auto Configuration)/image-20230421183657718.png)

실행 : `http://localhost:8080/memory` 결과 : `{"used": 38174528, "max": 8589934592}`



# 9. 자동 구성 이해1 - 스프링 부트의 동작

스프링 부트는 다음 경로에 있는 파일을 읽어서 스프링 부트 자동 구성으로 사용한다.

```
resources/META-INF/spring/
org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

스프링 부트 자동 구성이 동작하는 원리는 다음 순서로 확인할 수 있다. 

@SpringBootApplication -> @EnableAutoConfiguration -> @Import(AutoConfigurationImportSelector.class)

**AutoConfigApplication**

```java
@SpringBootApplication
public class AutoConfigApplication {
    public static void main(String[] args) {
        SpringApplication.run(AutoConfigApplication.class, args);
}
}
```

- run() 에 보면 AutoConfigApplication.class 를 넘겨주는데, 이 클래스를 설정 정보로 사용한다는 뜻이다.
- AutoConfigApplication 에는 @SpringBootApplication 애노테이션이 있는데, 여기에 중요한 설정 정보들이 들어있다.

**@SpringBootApplication**

```java
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = { @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
	@Filter(type = FilterType.CUSTOM, classes =AutoConfigurationExcludeFilter.class) })
public @interface SpringBootApplication {...}
```

- 여기서 우리가 주목할 애노테이션은 @EnableAutoConfiguration 이다. 이름 그대로 자동 구성을 활성화 하는 기능을 제공한다.

**@EnableAutoConfiguration**

```java
@AutoConfigurationPackage
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {…}
```

- @Import 는 주로 스프링 설정 정보( @Configuration )를 포함할 때 사용한다.
- 그런데 AutoConfigurationImportSelector 를 열어보면 @Configuration 이 아니다.
- **이 기능을 이해하려면 ImportSelector 에 대해 알아야 한다.**



# 10. 자동 구성 이해2 - ImportSelector

@Import 에 설정 정보를 추가하는 방법은 2가지가 있다.

- 정적인 방법: @Import (클래스) 이것은 정적이다. 코드에 대상이 딱 박혀 있다. 설정으로 사용할 대상을 동적으로 변경할 수 없다. 
- 동적인 방법: @Import ( ImportSelector ) 코드로 프로그래밍해서 설정으로 사용할 대상을 동적으로 선택할 수 있다.

## ImportSelector 예제 (src/test)

**HelloBean**

```java
package hello.selector;
public class HelloBean {
}
```

빈으로 등록할 대상이다.

**HelloConfig**

```java
package hello.selector;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class HelloConfig {

    @Bean
    public HelloBean helloBean(){
        return new HelloBean();
    }
}
```

설정 정보이다. HelloBean 을 스프링 빈으로 등록한다.

**HelloImportSelector**

```java
package hello.selector;

import org.springframework.context.annotation.ImportSelector;
import org.springframework.core.type.AnnotationMetadata;

public class HelloImportSelector implements ImportSelector {
    @Override
    public String[] selectImports(AnnotationMetadata importingClassMetadata) {
        return new String[]{"hello.selector.HelloConfig"};
    }
}

```

- 설정 정보를 동적으로 선택할 수 있게 해주는 ImportSelector 인터페이스를 구현했다. 여기서는 단순히 hello.selector.HelloConfig 설정 정보를 반환한다.
- 이렇게 반환된 설정 정보는 선택되어서 사용된다. 여기에 설정 정보로 사용할 클래스를 동적으로 프로그래밍 하면 된다.

**ImportSelectorTest**

```java
package hello.selector;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import static org.assertj.core.api.Assertions.*;

public class ImportSelectorTest {

    @Test
    void selectorConfig(){
        AnnotationConfigApplicationContext appContext =
                new AnnotationConfigApplicationContext(SelectorConfig.class);
        HelloBean bean = appContext.getBean(HelloBean.class);
        assertThat(bean).isNotNull();
    }

    @Configuration
    @Import(HelloImportSelector.class)
    public static class SelectorConfig{
    }
}
```

`selectorConfig()` 

- selectorConfig() 는 SelectorConfig 를 초기 설정 정보로 사용한다.

- SelectorConfig 는 @Import(HelloImportSelector.class) 에서 ImportSelector 의 구현체인 HelloImportSelector 를 사용했다.

- 스프링은 HelloImportSelector 를 실행하고, "hello.selector.HelloConfig" 라는 문자를 반환 받는다.

- 스프링은 이 문자에 맞는 대상을 설정 정보로 사용한다. 따라서 hello.selector.HelloConfig 이 설정 정보로 사용된다. 

- 그 결과 HelloBean 이 스프링 컨테이너에 잘 등록된 것을 확인할 수 있다.

  

## @EnableAutoConfiguration 동작 방식

```java
@AutoConfigurationPackage
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {…}
```

- AutoConfigurationImportSelector 는 ImportSelector 의 구현체이다. 따라서 설정 정보를 동적으로 선택할 수 있다.

- AutoConfigurationImportSelector 는 `selectImports()` 메서드에서 `getAutoConfigurationEntry()` 메서드를 실행하고 해당 메서드는 다음과 같이 Configuration 목록을 받는다.

- ![image-20230421203119212](../../images/2023-04-19-스프링 부트 활용 - 자동 구성(Auto Configuration)/image-20230421203119212.png)

- `getCandidateConfigurations()` 메서드에 들어가보면 다음과 같이 `ImportCandidates.load()` 메서드가 `AutoConfiguration.class` 를 받아서 configurations 를 반환하게 된다.

- ![image-20230421203344642](../../images/2023-04-19-스프링 부트 활용 - 자동 구성(Auto Configuration)/image-20230421203344642.png)

- `ImportCandidates.load(AutoConfiguration.class, getBeanClassLoader())` 에 들어가보면 LOCATION 값으로 AutoConfiguration 의 위치정보를 찾는데, 해당 값은 다음과 같다.

  - LOCATION : `"META-INF/spring/%s.imports"`
  - ![image-20230421203702548](../../images/2023-04-19-스프링 부트 활용 - 자동 구성(Auto Configuration)/image-20230421203702548.png)

  - 따라서 String location = META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 가 되며, 해당 파일에서 값을 읽어서 AutoConfiguration 이 진행된다.



# 정리 (추가 내용)

- @AutoConfiguration 에 자동 구성의 순서를 지정할 수 있다. 
- @AutoConfiguration 도 설정 파일이다. 내부에 @Configuration 이 있는 것을 확인할 수 있다. 
  - 하지만 일반 스프링 설정과 라이프사이클이 다르기 때문에 컴포넌트 스캔의 대상이 되면 안된다. 
  - 파일에 지정해서 사용해야 한다.
  - 그래서 스프링 부트가 제공하는 컴포넌트 스캔에서는 @AutoConfiguration 을 제외하는 AutoConfigurationExcludeFilter 필터가 포함되어 있다.
- 자동 구성이 내부에서 컴포넌트 스캔을 사용하면 안된다. 대신에 자동 구성 내부에서 @Import 는 사용할 수 있다.

## 자동 구성을 언제 사용하는가?

AutoConfiguration 은 라이브러리를 만들어서 제공할 때 사용하고, 그 외에는 사용하는 일이 거의 없다. 

**자동 구성을 알아야 하는 진짜 이유는** 개발을 진행 하다보면 사용하는 특정 빈들이 어떻게 등록된 것인지 확인이 필요할 때가 있다. 이럴 때 스프링 부트의 자동 구성 코드를 읽을 수 있어야 한다. 그래야 문제가 발생했을 때 대처가 가능하다. 자동화는 매우 편리한 기능이지만 자동화만 믿고 있다가 실무에서 문제가 발생했을 때는 파고 들어가서 문제를 확인하는 정도는 이해해야 한다. 이번에 학습한 정도면 자동 구성 코드를 읽는데 큰 어려움은 없을 것이다.