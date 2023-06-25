---
categories: "inflearn"
tag: ["QuerydslPredicateEexcutor", "Querydsl Web", "QuerydslRepostiroySupport"]
description: "실전! Querydsl 강의 Section 7 내용입니다."
series: "실전! Querydsl"
title: "[Querydsl] 실전! Querydsl Section 7. 스프링 데이터 JPA가 제공하는 Querydsl 기능"
---

***여기서 소개하는 기능은 제약이 커서 복잡한 실무 환경에서 사용하기에는 많이 부족합니다.***

# QuerydslPredicateEexcutor

Spring data Repository 에 `implement` 로 추가할 수 있습니다.

```java
public interface MemberRepository extends JpaRepository<Member, Long>, QuerydslPredicateExecutor<Member> {
...
}
```

**QuerydslPredicateExecutor 인터페이스**

```java
public interface QuerydslPredicateExecutor<T> {
    Optional<T> findById(Predicate predicate);
    Iterable<T> findAll(Predicate predicate);
    long count(Predicate predicate);
    boolean exists(Predicate predicate);
    // … more functionality omitted.
}
```

파라미터로 `Predicate` 를 넘깁니다. 아래와 같이 사용할 수 있습니다.

```java
Iterable<Member> result = memberRepository.findAll(member.age.between(10, 40).and(member.username.eq("member1")));

    for (Member findMember : result) {
        System.out.println("findMember = " + findMember);
    }
```

**한계점**

​	해당 인터페이스는 묵시적 조인은 가능하지만 `left join` 이 불가능합니다. 또한 파라미터로 `Predicate` 를 넘겨야 하기 때문에 서비스, 컨트롤러 등 클라이언트가 `Querydsl` 에 의존해야 합니다. 

# Querydsl Web

예제 없이 docs 만 확인했습니다.

https://docs.spring.io/spring-data/jpa/docs/2.2.3.RELEASE/reference/html/#core.web.type-safe

단순한 조건만 가능히거. 조건을 커스텀하는 기능이 복잡하고 명시적이지 않습니다. 컨트롤러가 Querydsl 에 의존하는 문제점도 있어서 복잡한 실무환경에서 사용하기에는 한계가 명확합니다.

# QuerydslRepositorySupport

구현 클래스에 다음과 같이 `QuerydslRepositorySupport` 를 상속받아서 사용할 수 있습니다.

```java
public class MemberRepositoryImpl extends QuerydslRepositorySupport implements MemberRepositoryCustom {
    
    public MemberRepositoryImpl() {
        super(Member.class);
    }
    
    ...
}
```

`super(Member.class)` 와 같이 엔티티를 파라미터로 생성자를 호출합니다.

`from()` 으로 시작하는 문법입니다. 

```java
@Override
public List<MemberTeamDto> search(MemberSearchCondition condition){

    return from(member)
            .leftJoin(member.team, team)
            .where(
                    usernameEq(condition.getUsername()),
                    teamNameEq(condition.getTeamName()),
                    ageGoe(condition.getAgeGoe()),
                    ageLoe(condition.getAgeLoe()))
            .select(new QMemberTeamDto(
                    member.id,
                    member.username,
                    member.age,
                    team.id,
                    team.name))
            .fetch();
}
```

아래와 같이 `Pagination` 도 구현할 수 있습니다.

```java
@Override
public Page<MemberTeamDto> searchPageSimple2(MemberSearchCondition condition, Pageable pageable) {

    JPQLQuery<MemberTeamDto> jpaQuery = from(member)
            .leftJoin(member.team, team)
            .where(
                    usernameEq(condition.getUsername()),
                    teamNameEq(condition.getTeamName()),
                    ageGoe(condition.getAgeGoe()),
                    ageLoe(condition.getAgeLoe())
            )
            .select(new QMemberTeamDto(
                    member.id,
                    member.username,
                    member.age,
                    team.id,
                    team.name));

    JPQLQuery<MemberTeamDto> query = getQuerydsl().applyPagination(pageable, jpaQuery);

    List<MemberTeamDto> content = query.fetch();
    long total = query.fetchCount();

    return new PageImpl<>(content, pageable, total);
}
```

`getQuerydsl().applyPagination()` 으로 스프링 데이터가 제공하는 페이징을 Querydsl로 편리하게 변환 가능합니다. 하지만 `Sort` 는 오류가 발생합니다.

​	`Querydsl 3.x` 버전을 대상으로 만들었기 때문에 `JPAQueryFactory` 로 시작할 수 없습니다. 따라서 select로 시작할 수 없고 from 으로 시작해야 하기 때문에 가독성이 좋지 않습니다.

물론 아래와 같이 생성자 주입으로 `JPAQueryFactory` 를 선언해서 사용할 수 있습니다.

```java
public class MemberRepositoryImpl extends QuerydslRepositorySupport implements MemberRepositoryCustom {

    private final JPAQueryFactory queryFactory;
    public MemberRepositoryImpl(EntityManager em) {
        super(Member.class);
        this.queryFactory = new JPAQueryFactory(em);
    }
    ...
}
```

