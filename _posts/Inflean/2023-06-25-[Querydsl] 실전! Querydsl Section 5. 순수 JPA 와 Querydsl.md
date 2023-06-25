---
categories: "springJPA"
tag: ["동적쿼리", "BooleanBuilder", "where 파라미터"]
description: "실전! Querydsl 강의 Section 5 내용입니다."
series: "실전! Querydsl"
title: "[Querydsl] 실전! Querydsl Section 5. 순수 JPA 와 Querydsl"
---

# 순수 JPA 리포지토리와 Querydsl

아래 코드는 순수 JPA 로 작성한 코드입니다.

```java
package querydsl.repository;

@Repository
public class MemberJpaRepository {

    private final EntityManager em;

    public MemberJpaRepository(EntityManager em) {
        this.em = em;
        this.queryFactory = new JPAQueryFactory(em);
    }

    public void save(Member member) {
        em.persist(member);
    }

    public Optional<Member> findById(Long id){
        Member findMember = em.find(Member.class, id);
        return Optional.ofNullable(findMember);
    }

    public List<Member> findAll(){
        return em.createQuery("select m from Member m", Member.class)
                .getResultList();
    }

    public List<Member> findByUsername(String username){
        return em.createQuery("select m from Member m where m.username = :username", Member.class)
                .setParameter("username", username)
                .getResultList();
    }
}
```

아래 코드는 `findAll` 메서드와 `findByUsername` 을 Querydsl 로 변경한 코드입니다.

```java
@Repository
public class MemberJpaRepository {

    private final EntityManager em;
    private final JPAQueryFactory queryFactory;

    public MemberJpaRepository(EntityManager em) {
        this.em = em;
        this.queryFactory = new JPAQueryFactory(em);
    }

    public void save(Member member) {
        em.persist(member);
    }

    public Optional<Member> findById(Long id){
        Member findMember = em.find(Member.class, id);
        return Optional.ofNullable(findMember);
    }

    public List<Member> findAll_Querydsl(){
        return queryFactory
                .selectFrom(member)
                .fetch();
    }

    public List<Member> findByUsername_Querydsl(String username){
        return queryFactory
                .selectFrom(member)
                .where(member.username.eq(username))
                .fetch();
    }
}
```

`JPAQueryFactory` 을 새롭게 선언해줍니다. 스프링 빈이 아니기 때문에 `@RequiredArgsConstructor` 는 사용할 수 없습니다. 만약 아래와 같이 빈 등록을 한다면 사용할 수도 있습니다.

```java
@Bean
JPAQueryFactory jpaQueryFactory(EntityManager em) {
    return new JPAQueryFactory(em);
}
```

> 동시성 문제는 걱정하지 않아도 됩니다. 왜냐하면 여기서 스프링이 주입해주는 엔티티 매니저는 실제 동작 시점에 진짜 엔티티 매니저를 찾아주는 프록시용 가짜 엔티티 매니저이기 때문입니다. 이 가짜 엔티티 매니저는 실제 사용 시점에 트랜잭션 단위로 실제 엔티티 매니저(영속성 컨텍스트)를 할당해줍니다.

# 동적 쿼리와 성능 최적화 조회

## Builder 사용

먼저 조회 최적화용 DTO 를 추가하겠습니다. `member` 와 `team` 을 조회하는 DTO 입니다.

```java
package querydsl.dto;

import com.querydsl.core.annotations.QueryProjection;
import lombok.Data;

@Data
public class MemberTeamDto {

    private Long memberId;
    private String username;
    private int age;
    private Long teamId;
    private String teamName;

    @QueryProjection
    public MemberTeamDto(Long memberId, String username, int age, Long teamId, String teamName) {
        this.memberId = memberId;
        this.username = username;
        this.age = age;
        this.teamId = teamId;
        this.teamName = teamName;
    }
}
```

그리고 회원 검색조건도 작성합니다. (`MemberSearchCondition`)

```java
package querydsl.dto;

import lombok.Data;

@Data
public class MemberSearchCondition {

    // 회원명, 팀명, 나이(ageGoe, ageLoe)
    private String username;
    private String teamName;
    private Integer ageGoe;
    private Integer ageLoe;
}
```

검색조건은 회원명, 팀명, 최소나이, 최대나이 입니다.

아래는 `BooleanBuilder` 를 사용한 예제입니다.

```java
@Repository
public class MemberJpaRepository {

   ...

    public List<MemberTeamDto> searchByBuilder(MemberSearchCondition condition){

        BooleanBuilder builder = new BooleanBuilder();
        if (hasText(condition.getUsername())) {
            builder.and(member.username.eq(condition.getUsername()));
        }
        if (hasText(condition.getTeamName())) {
            builder.and(team.name.eq(condition.getTeamName()));
        }
        if(condition.getAgeGoe() != null){
            builder.and(member.age.goe(condition.getAgeGoe()));
        }
        if(condition.getAgeLoe() != null){
            builder.and(member.age.loe(condition.getAgeLoe()));
        }

        return queryFactory
                .select(new QMemberTeamDto(
                        member.id,
                        member.username,
                        member.age,
                        team.id,
                        team.name))
                .from(member)
                .leftJoin(member.team, team)
                .where(builder)
                .fetch();
    }
}
```

모든 조건을 비교하고, `Null` 값이면 조건을 포함시키지 않습니다.

## Where 절 파라미터 사용

간단하게 구현 코드만 보겠습니다.

```java
public List<MemberTeamDto> search(MemberSearchCondition condition){
        return queryFactory
                .select(new QMemberTeamDto(
                        member.id,
                        member.username,
                        member.age,
                        team.id,
                        team.name))
                .from(member)
                .leftJoin(member.team, team)
                .where(
                        usernameEq(condition.getUsername()),
                        teamNameEq(condition.getTeamName()),
                        ageGoe(condition.getAgeGoe()),
                        ageLoe(condition.getAgeLoe()))
                .fetch();
    }

    private BooleanExpression usernameEq(String username) {
        return hasText(username) ? member.username.eq(username) : null;
    }

    private BooleanExpression teamNameEq(String teamName) {
        return hasText(teamName) ? team.name.eq(teamName) : null;
    }

    private BooleanExpression ageGoe(Integer ageGoe) {
        return ageGoe != null ? member.age.goe(ageGoe) : null;
    }

    private BooleanExpression ageLoe(Integer ageLoe) {
        return ageLoe != null ? member.age.loe(ageLoe) : null;
    }
```

Where 절 파라미터를 사용하면 가독성이 높아지고, 재사용 가능하다는 장점이 있습니다. 아래와 같이 `Member` 를 조건으로 조회할 때도 사용할 수 있습니다.

```java
public List<Member> searchMember(MemberSearchCondition condition){
    return queryFactory
            .selectFrom(member)
            .leftJoin(member.team, team)
            .where(
                    usernameEq(condition.getUsername()),
                    teamNameEq(condition.getTeamName()),
                    ageGoe(condition.getAgeGoe()),
                    ageLoe(condition.getAgeLoe()))
            .fetch();
}
```

# 조회 API 컨트롤러 개발 (예제)

편리한 데이터 확인을 위해 샘플 데이터를 추가해보겠습니다. `application.yml` 에서 `test` 와 `local` 프로파일은 분리시켜둡니다.

```java
@Profile("local")
@Component
@RequiredArgsConstructor
public class InitMember {

    private final InitMemberService initMemberService;

    @PostConstruct // @Transactional 과 같이 쓰면 안되기 때문에 분리함
    public void init(){
        initMemberService.init();
    }

    @Component
    static class InitMemberService{
        @PersistenceContext
        private EntityManager em;

        @Transactional
        public void init(){
            Team teamA = new Team("teamA");
            Team teamB = new Team("teamB");
            em.persist(teamA);
            em.persist(teamB);

            for (int i = 0; i < 100; i++) {
                Team selectedTeam = i % 2 == 0 ? teamA : teamB;
                em.persist(new Member("member"+i, i, selectedTeam));
            }
        }
    }
}
```

`@PostConstruct` 를 통해 스프링 실행 시점에 데이터를 추가합니다. `@PostConstruct` 와 `@Transactional` 은 라이프 사이클 상 함꼐 사용할 수가 없어서 분리했습니다.

조회 컨트롤러는 아래와 같이 만듭니다.

```java
@RestController
@RequiredArgsConstructor
public class MemberController {

    private final MemberJpaRepository memberJpaRepository;

    @GetMapping("/v1/members")
    public List<MemberTeamDto> searchMemberV1(MemberSearchCondition condition){
        return memberJpaRepository.search(condition);
    }
}
```

`http://localhost:8080/v1/members?teamName=teamB&ageGoe=31&ageLoe=35` 와 같이 파라미터로 조건을 주어서 검색할 수 있습니다.