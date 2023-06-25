---
categories: "inflean"
tag: ["Query By Example", "Projections", "Native Query"]
series: "실전! 스프링 데이터 JPA"
title: "[Spring JPA] Section 7. Query By Example, Projections, 네이티브 쿼리"
description: "Section 7. 'Query By Example, Projections, 네이티브 쿼리' 내용 요약입니다."
---

# Query By Example

​	`Query By Example` 은 객체 자체를 검색조건으로 사용하는 방식입니다. `QueryByExampleExecutor<T>` 인터페이스에서 지원하기 때문에 특별한 메서드 생성없이 바로 사용할 수 있습니다.

```java
<S extends T> Iterable<S> findAll(Example<S> example);
```

해당 인터페이스의 `findAll` 메서드를 사용해보겠습니다. `Example<S>` 를 파라미터로 사용해야 합니다.

```java
@Test
public void queryByExample(){
    Team teamA = new Team("teamA");
    em.persist(teamA);

    Member m1 = new Member("m1", 0, teamA);
    Member m2 = new Member("m2", 0, teamA);
    em.persist(m1);
    em.persist(m2);

    em.flush();
    em.clear();

    //Probe
    Member member = new Member("m1"); //엔티티 자체가 검색 condition 이 됩니다.
    Team team = new Team("teamA");
    member.setTeam(team);

    //ExampleMatcher
    ExampleMatcher matcher = ExampleMatcher.matching().withIgnorePaths("age");

    Example<Member> example = Example.of(member, matcher);

    List<Member> result = memberRepository.findAll(example);

    assertThat(result.get(0).getUsername()).isEqualTo("m1");
}
```

- **`Probe` 는 필드에 데이터가 있는 실제 도메인 객체입니다.** 해당 객체에 필드값이 있으면 검색조건이 되며, `null` 이면 검색조건이 아닙니다. `member` 에 `team` 을 넣어주면 `inner join` 으로 조회를 합니다.
- **`ExampleMatcher` 는 특정 필드를 일치시키는 상세한 정보를 제공합니다.** 여기서 `member` 의 `age` 는 `primitive type` 으로 기본값이 `0` 이기 때문에 `null` 이 아니라서 검색조건이 됩니다. 따라서 `withIgnorePaths("age")` 을 통해 검색조건에서 제외시킵니다.
- `Example.of(member, matcher)` 를 통해 쿼리를 생성하는 `Example<S>` 객체를 생성합니다.

​	`Query By Example` 는 도메인 객체를 그대로 사용해서 동적 쿼리를 편리하게 처리합니다. 또한 데이터 저장소를 RDB에서 NOSQL로 변경해도 코드 변경이 없게 추상화 되어 있습니다.

​	하지만 **조인은 가능하지만 내부 조인(INNER JOIN)만 가능하고 외부 조인(LEFT JOIN) 은 안됩니다.** 또한 중첩 제약조건 (ex. `firstname = ?0 or (firstname = ?1 and lastname = ?2)`) 이 안되고, **문자를 제외하고는 매칭 조건이 `=` 만 지원됩니다.** 문자는 `starts/contains/ends/regex` 등으로 조건을 만들 수 있습니다.

​	따라서 **실무에서는 QueryDSL을 사용하는 편이 좋습니다.**

# Projection

​	DB 연산 중 프로젝션 연산을 위한 방법입니다. 만약 전체 엔티티가 아니라 회원 이름만 조회하고 싶은 상황을 가정하겠습니다. 아래와 같이 인터페이스를 만듭니다.

```java
public interface UsernameOnly {
	String getUsername();
}
```

조회할 엔티티의 필드를 `getter` 형식으로 지정하면 해당 필드만 선택해서 조회(Projection) 합니다.

그리고 `JpaRepository` 에 반환타입을 해당 인터페이스로 해줍니다.

```java
public interface MemberRepository ... {
	List<UsernameOnly> findProjectionsByUsername(String username);
}
```

아래와 같은 테스트 코드를 통해서 확인할 수 있습니다.

```java
@Test
public void projections() throws Exception {
    //given
    Team teamA = new Team("teamA");
    em.persist(teamA);
    Member m1 = new Member("m1", 0, teamA);
    Member m2 = new Member("m2", 0, teamA);
    em.persist(m1);
    em.persist(m2);
    em.flush();
    em.clear();
    
    //when
    List<UsernameOnly> result = memberRepository.findProjectionsByUsername("m1");
    
    //then
    Assertions.assertThat(result.size()).isEqualTo(1);
}
```

다음과 같은 SQL 문이 나갑니다.

```mysql
select m.username from member m where m.username='m1';
```

SQL 문을 보면 `m.username` 만 조회하는 걸 알 수 있습니다.

인터페이스 기반 **Open Proejctions** 을 사용할 수도 있는데요. 다음과 같이 스프링의 SpEL 문법도 지원합니다.

```java
public interface UsernameOnly {

    @Value("#{target.username + ' ' + target.age}")
    String getUsername();
        
}
```

다시 테스트를 실행하면 DB 에서 모든 엔티티 속성을 조회한 이후에 `UsernameOnly` 에 `username`, `age` 만 할당합니다. 따라서 JPQL SELECT 절 최적화가 되지 않습니다.

 **클래스 기반 Projection**

다음과 같이 인터페이스가 아닌 구체적인 DTO 형식도 가능합니다. **생성자의 파라미터 이름으로 매칭합니다.**

```java
public class UsernameOnlyDto {

    private final String username;

    public UsernameOnlyDto(String username) { //생성자의 파라미터 이름으로 매칭합니다.
        this.username = username;
    }

    public String getUsername() {
        return username;
    }
}
```

**동적 Projections**

다음과 같이 Generic type을 주면, 동적으로 프로젝션 데이터를 변경할 수 있습니다.

```java
<T> List<T> findProjectionsByUsername(String username, Class<T> type);
```

**중첩 구조 처리**

```java
public interface NestedClosedProjections {

    String getUsername();
    TeamInfo getTeam();

    interface TeamInfo {
        String getName();
    }
}
```

마찬가지로 `getter` 네이밍을 통해 DB 에 접근합니다. **프로젝션 대상이 root 엔티티면 JPQL SELECT 절이 최적화되지만 프로젝션 대상이 ROOT가 아니면 LEFT OUTER JOIN 으로 모든 필드를 SELECT해서 엔티티로 조회한 다음에 계산합니다.**

# 네이티브 쿼리

​	네이티브 쿼리는 가급적 사용하지 않는 게 좋고 어쩔 수 없을 때 사용해야 합니다. 

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

    @Query(value = "select * from member where username = ?", nativeQuery =true)
    Member findByNativeQuery(String username);
    
}
```

네이티브 쿼리는 반환 타입이 제한되어 있어서 엔티티가 아닌 DTO로 변환은 하려면 JPA TUPLE, MAP 으로 조회해야 하는데, 네이티브 SQL을 DTO로 조회할 때는 JdbcTemplate 이나 myBatis 가 권장됩니다.

**Projections 활용**

스프링 데이터 JPA 네이티브 쿼리와 함꼐 인터페이스 기반 Projections 을 활용할 수 있습니다.

```java
public interface MemberProjection {

    Long getId();
    String getUsername();
    String getTeamName();

}
```

```java
@Query(value = "SELECT m.member_id as id, m.username, t.name as teamName " + 
    "FROM member m left join team t ON m.team_id = t.team_id",
    countQuery = "SELECT count(*) from member",
    nativeQuery = true)
Page<MemberProjection> findByNativeProjection(Pageable pageable);
```

Paging 을 사용할 수도 있습니다. 이때 `countQuery` 는 직접 만들어야 합니다. 아래와 같이 사용할 수 있습니다.

```java
@Test
    public void nativeQuery(){
        Team teamA = new Team("teamA");
        em.persist(teamA);

        Member m1 = new Member("m1", 0, teamA);
        Member m2 = new Member("m2", 0, teamA);
        em.persist(m1);
        em.persist(m2);

        em.flush();
        em.clear();

        Page<MemberProjection> result2 = memberRepository.findByNativeProjection(PageRequest.of(0, 10));
        List<MemberProjection> content = result2.getContent();
        for (MemberProjection memberProjection : content) {
            System.out.println("memberProjection.getUsername() = " + memberProjection.getUsername());
            System.out.println("memberProjection.getTeamName() = " + memberProjection.getTeamName());
        }
    }
```

쿼리문은 아래와 같이 나갑니다.

```mysql
select
    m.member_id as id,
    m.username,
    t.name as teamName 
from
    member m 
left join
    team t limit ?
```

