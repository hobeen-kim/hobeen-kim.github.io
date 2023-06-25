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

## Querydsl Web