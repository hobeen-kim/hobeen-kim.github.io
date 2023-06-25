---
categories: "springJPA"
tag: ["Querydsl", "QType", "검색조건", "sort", "paging", "집합", "join", "fetch", "subQuery", "case", "constant", "concat"]
description: "실전! Querydsl 강의 Section 3 내용입니다."
series: "실전! Querydsl"
---

# JPQL vs Querydsl

​	먼저 테스트 예제 코드입니다.

```java
@SpringBootTest
@Transactional
public class QuerydslBasicTest {

    @Autowired
    EntityManager em;

    @BeforeEach
    public void before(){

        queryFactory = new JPAQueryFactory(em);

        Team teamA = new Team("teamA");
        Team teamB = new Team("teamB");

        em.persist(teamA);
        em.persist(teamB);

        Member member1 = new Member("member1", 10, teamA);
        Member member2 = new Member("member2", 20, teamA);
        Member member3 = new Member("member3", 30, teamB);
        Member member4 = new Member("member4", 40, teamB);

        em.persist(member1);
        em.persist(member2);
        em.persist(member3);
        em.persist(member4);
    }
}
```

먼저 JPQL 로 `username = member1` 을 조회하는 로직입니다.

```JAVA
@Test
public void startJPQL(){
    //find member1
    Member findMember = em.createQuery("select m from Member m where m.username = : username", Member.class)
            .setParameter("username", "member1")
            .getSingleResult();

    assertThat(findMember.getUsername()).isEqualTo("member1");
}
```

JPQL 에서 문법 오류가 있다고 해도 런타임 시점에 해당 쿼리문이 실행될 때 오류가 나기 때문에 버그가 나기 쉽습니다.

다음은 Querydsl 로 같은 쿼리문을 짠 코드입니다.

```java
@Test
public void startQuerydsl(){
    JPAQueryFactory queryFactory = new JPAQueryFactory(em);

    QMember m = new QMember("m");

    Member findMember = queryFactory
            .select(m)
            .from(m)
            .where(m.username.eq("member1"))
            .fetchOne();

    assertThat(findMember.getUsername()).isEqualTo("member1");
}
```

`JPAQueryFactory` 클래스를 선언하고 `em` 을 파라미터로 넘겨줍니다. Querydsl 에서는 파라미터 바인딩을 모두 메서드로 하기 때문에 컴파일 시점에 오류를 확인할 수 있습니다.

`JPAQueryFactory` 은 필드 레벨로 선언해도 동시성 문제가 발생하지 않습니다.

```java
@SpringBootTest
@Transactional
public class QuerydslBasicTest {
    @Autowired
    EntityManager em;

    JPAQueryFactory queryFactory; //필드레벨로 들고가도 괜찮음

    @BeforeEach
    public void before(){

        queryFactory = new JPAQueryFactory(em); //queryFactory 할당

        ...
    }

    @Test
    public void startQuerydsl(){ //필드레벨의 queryFactory 사용

        QMember m = new QMember("m");

        Member findMember = queryFactory
                .select(m)
                .from(m)
                .where(m.username.eq("member1"))
                .fetchOne();

        assertThat(findMember.getUsername()).isEqualTo("member1");
    }
}
```

​	**동시성 문제는 `JPAQueryFactory` 를 생성할 때 제공하는 `EntityManager(em)` 에 달려있습니다.** 스프링 프레임워크는 여러 쓰레드에서 동시에 같은 `EntityManager` 에 접근해도, **트랜잭션마다 별도의 영속성 컨텍스트를 제공**하기 때문에, 동시성 문제는 걱정하지 않아도 됩니다.

# 기본 Q-Type 활용

​	Q클래스 인스턴스를 사용하는 방법은 아래와 같이 2가지입니다.

```java
QMember qMember = new QMember("m"); //별칭 직접 지정
QMember qMember = QMember.member; //기본 인스턴스 사용
```

`QMember` 클래스에서 `static QMember` 를 제공해주기 때문에 그대로 사용하면 됩니다.

```java
@Test
public void startQuerydsl(){

	QMember m = QMember.member;

    Member findMember = queryFactory
            .select(m)
            .from(m)
            .where(m.username.eq("member1"))
            .fetchOne();

    assertThat(findMember.getUsername()).isEqualTo("member1");
}
```

또한 `QMember.member` 가 `static` 이기 때문에 `static import` 로 깔끔하게 사용할 수 있습니다.

```java
import static querydsl.entity.QMember.*;

...
public class QuerydslBasicTest {

    ...

    @Test
    public void startQuerydsl(){

        Member findMember = queryFactory
                .select(member)
                .from(member)
                .where(member.username.eq("member1"))
                .fetchOne();

        assertThat(findMember.getUsername()).isEqualTo("member1");
    }
}
```

Querydsl 로 만든 JPQL 문이 어떤 형식인지 보고 싶다면 `yml` 파일에 다음과 같은 속성을 추가하면 됩니다.

```java
spring:
  datasource:
    url: jdbc:h2:tcp://localhost/~/querydsl
    username: sa
    password:
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true # 추가
```

그러면 아래와 같은 JPQL 을 볼 수 있는데요. JPQL 을 보면 alias 가 `member1` 인걸 알 수 있습니다. 해당 alias 는 `QMember` 클래스에서 자동으로 지정한건데 직접 `QMember` 클래스를 선언하면서 새로 만들 수 있습니다. 새로운 alias 를 만드는 경우는 같은 테이블을 조회할 때가 있겠습니다.

```mysql
#Querydsl 로 만든 JPQL
select
    member1 
from
    Member member1 
where
    member1.username = ?1
```

# 검색 조건 쿼리

아래는 JPQL이 제공하는 모든 검색 중 일부입니다. JPQL 은 SQL 문에 있는 거의 모든 검색조건을 지원합니다.

```java
member.username.eq("member1") // username = 'member1'
member.username.ne("member1") //username != 'member1'
member.username.eq("member1").not() // username != 'member1'
member.username.isNotNull() //이름이 is not null
member.age.in(10, 20) // age in (10,20)
member.age.notIn(10, 20) // age not in (10, 20)
member.age.between(10,30) //between 10, 30
member.age.goe(30) // age >= 30
member.age.gt(30) // age > 30
member.age.loe(30) // age <= 30
member.age.lt(30) // age < 30
member.username.like("member%") //like 검색
member.username.contains("member") // like ‘%member%’ 검색
member.username.startsWith("member") //like ‘member%’ 검색
```

아래는 `and` 조건을 이용한 2가지 방법입니다.

```java
@Test
public void search(){
    Member findMember = queryFactory
            .selectFrom(member)
            .where(member.username
                    .eq("member1")
                    .and(member.age.between(10, 20))
            )
            .fetchOne();

    assertThat(findMember.getUsername()).isEqualTo("member1");
}

@Test
public void searchAndParam(){
    Member findMember = queryFactory
            .selectFrom(member)
            .where( //and를 쓰지 않아도 알아서 and로 처리해줍니다. 
                    member.username.eq("member1"),
                    member.age.between(10, 20)
            )
            .fetchOne();

    assertThat(findMember.getUsername()).isEqualTo("member1");
}
```

`searchAndParam` 에서는 `and` 를 사용하지 않고 `.where` 안에서 콤마(`,`) 를 통해 구분해줍니다. 그렇게 하면 나중에 null 은 무시해주기 때문에 동적 쿼리를 만들기 좋습니다.

# 결과 조회

- `fetch()` : 리스트 조회, 데이터 없으면 빈 리스트 반환
- `fetchOne()` : 단 건 조회 결과가 없으면 `null` 결과가 둘 이상이면`NonUniqueResultException`
- `fetchFirst()` : `limit(1).fetchOne()` 
- `fetchResults()` : 페이징 정보 포함, total count 쿼리 추가 실행 (복잡한 쿼리에서 count 쿼리 오류로 deprecated)
- `fetchCount()` : count 쿼리로 변경해서 count 수 조회 (복잡한 쿼리에서 count 쿼리 오류로 deprecated)

```java
@Test
    public void resultFetch(){
        List<Member> fetch = queryFactory
                .selectFrom(member)
                .fetch();

        Member fetchOne = queryFactory
                .selectFrom(member)
                .fetchOne();

        Member fetchFirst = queryFactory
                .selectFrom(member)
                .fetchFirst();//.limit(1).fetchOne()과 같음

        QueryResults<Member> results = queryFactory 
                .selectFrom(member)
                .fetchResults();

        results.getTotal();
        List<Member> content = results.getResults();

        long total = queryFactory 
                .selectFrom(member)
                .fetchCount();

    }
```

# 정렬

`orderBy` 메서드를 통해 정렬이 가능합니다.

```java
/**
 * 회원 정렬 순서
 * 1. 회원 나이 내림차순(desc)
 * 2. 회원 이름 올림차순(asc)
 * 단, 2에서 회원이름이 없으면 마지막에 출력(nulls last)
 */
@Test
public void sort(){
    em.persist(new Member(null, 100));
    em.persist(new Member("member5", 100));
    em.persist(new Member("member6", 100));

    List<Member> result = queryFactory
            .selectFrom(member)
            .where(member.age.eq(100))
            .orderBy(member.age.desc(), member.username.asc().nullsLast())
            .fetch();

    Member member5 = result.get(0);
    Member member6 = result.get(1);
    Member memberNull = result.get(2);

    assertThat(member5.getUsername()).isEqualTo("member5");
    assertThat(member6.getUsername()).isEqualTo("member6");
    assertThat(memberNull.getUsername()).isNull();
}
```

`.orderBy(member.age.desc(), member.username.asc().nullsLast())` 처럼, 정렬조건을 여러 개 줄 수 있습니다. `.nullsLast()` 를 통해 `null` 값은 마지막으로 정렬합니다. `.nullsFirst()` 는 `null` 값을 처음으로 정렬합니다.

# 페이징

페이징 처리는 `orderBy` 를 해줘야 합니다. `offset`, `limit` 메서드로 페이징 처리를 합니다.

```java
@Test
public void paging1(){

    List<Member> result = queryFactory
            .selectFrom(member)
            .orderBy(member.username.desc())
            .offset(1) //0부터 시작(zero index)
            .limit(2) //최대 2건 조회
            .fetch();

    assertThat(result.size()).isEqualTo(2);
}
```

전체 조회 수가 필요하면 아래와 같이 `.fetchResults()` 를 사용합니다.

```java
@Test
public void paging2(){

    QueryResults<Member> queryResults = queryFactory
            .selectFrom(member)
            .orderBy(member.username.desc())
            .offset(1) //0부터 시작(zero index)
            .limit(2) //최대 2건 조회
            .fetchResults();


    assertThat(queryResults.getTotal()).isEqualTo(4);
    assertThat(queryResults.getLimit()).isEqualTo(2);
    assertThat(queryResults.getOffset()).isEqualTo(1);
    assertThat(queryResults.getResults().size()).isEqualTo(2);
}
```

복잡한 쿼리는 count 쿼리문을 직접 작성해야 합니다.

# 집합

집합은 다음과 같이 사용할 수 있습니다. 결과값은 `com.querydsl.core.Tuple` 로 나옵니다. JPQL이 제공하는 모든 집합 함수를 제공합니다.

```java
@Test
public void aggregation(){

    List<Tuple> result = queryFactory
            .select(
                    member.count(),
                    member.age.sum(),
                    member.age.avg(),
                    member.age.max(),
                    member.age.min()
            )
            .from(member)
            .fetch();

    Tuple tuple = result.get(0);

    assertThat(tuple.get(member.count())).isEqualTo(4);
    assertThat(tuple.get(member.age.sum())).isEqualTo(100);
    assertThat(tuple.get(member.age.avg())).isEqualTo(25);
    assertThat(tuple.get(member.age.max())).isEqualTo(40);
    assertThat(tuple.get(member.age.min())).isEqualTo(10);
}
```

예를 들어서 팀의 이름과 각 팀의 평균 연령을 구하는 Querydsl 은 아래와 같이 작성할 수 있습니다.

```java
@Test
void group() throws Exception {
    List<Tuple> result = queryFactory
            .select(team.name, member.age.avg())
            .from(member)
            .join(member.team, team)
            .groupBy(team.name)
            .fetch();

    Tuple teamA = result.get(0);
    Tuple teamB = result.get(1);

    assertThat(teamA.get(team.name)).isEqualTo("teamA");
    assertThat(teamA.get(member.age.avg())).isEqualTo(15);

    assertThat(teamB.get(team.name)).isEqualTo("teamB");
    assertThat(teamB.get(member.age.avg())).isEqualTo(35);
}
```

# 조인

## 기본조인

​	조인의 기본 문법은 첫 번째 파라미터에 조인 대상을 지정하고, 두 번째 파라미터에 별칭(alias)으로 사용할 Q 타입을 지정하면 됩니다. `join(조인 대상, 별칭으로 사용할 Q타입)`

```java
/**
 * 팀 A에 소속된 모든 회원
 */
@Test
void join() throws Exception {
    List<Member> result = queryFactory
            .selectFrom(member)
            .join(member.team, team)
            .where(team.name.eq("teamA"))
            .fetch();

    assertThat(result)
            .extracting("username")
            .containsExactly("member1", "member2");
}
```

연관관계가 없는 필드를 조인하는 **세타 조인** 또한 사용할 수 있습니다. 

```java
/**
 * 세타 조인, 회원의 이름이 팀 이름과 같은 회원 조히 (연관관계가 없는 필드로 조인)
 * @throws Exception
 */
@Test
void theta_join() throws Exception {
    em.persist(new Member("teamA"));
    em.persist(new Member("teamB"));
    em.persist(new Member("teamC"));

    List<Member> result = queryFactory
            .select(member)
            .from(member, team)
            .where(member.username.eq(team.name))
            .fetch();

    assertThat(result)
            .extracting("username")
            .containsExactly("teamA", "teamB");
}
```

## 조인 - on 절

**조인 대상 필터링**

`left join` 에서 `on` 을 통해 조인 대상을 필터링할 수 있습니다. 아래 예시는  회원과 팀을 조인하면서, 팀 이름이 teamA인 팀만 조인하고 회원은 모두 조회하는 Querydsl 입니다.

```java
/**
 * 회원과 팀을 조인하면서, 팀 이름이 teamA 인 팀만 조회, 회원은 모두 조회
 * JPQL : select m, t from Member m left join m.team t on t.name = 'teamA'
 */
@Test
void join_on_filtering() {

    List<Tuple> result = queryFactory
            .select(member, team)
            .from(member)
            .leftJoin(member.team, team).on(team.name.eq("teamA"))
            .fetch();

    for (Tuple tuple : result) {
        System.out.println("tuple = " + tuple);
    }
}
```

출력 결과는 아래와 같습니다.

```
tuple = [Member(id=3, username=member1, age=10), Team(id=1, name=teamA)]
tuple = [Member(id=4, username=member2, age=20), Team(id=1, name=teamA)]
tuple = [Member(id=5, username=member3, age=30), null]
tuple = [Member(id=6, username=member4, age=40), null]
```

`team.name.eq("teamA")` 조건에 해당되는 `Team` 만 출력이 되었습니다. 만약 `left join` 이 아닌 `inner join` 을 사용한다면 당연히 `Team` 이 `null` 이면 출력되지 않습니다.

```java
@Test
void join_on_filtering() {

    List<Tuple> result = queryFactory
            .select(member, team)
            .from(member)
            .join(member.team, team).on(team.name.eq("teamA"))
            .fetch();

    for (Tuple tuple : result) {
        System.out.println("tuple = " + tuple);
    }
}

/*
tuple = [Member(id=3, username=member1, age=10), Team(id=1, name=teamA)]
tuple = [Member(id=4, username=member2, age=20), Team(id=1, name=teamA)]
*/
```

하지만 그러면 `.on(team.name.eq("teamA")` 대신 `.where(team.name.eq("teamA")` 를 사용해도 같은 결과입니다. 더 보기 쉬운 `Where` 를 사용하는 게 좋습니다.

**연관관계 없는 엔티티 외부 조인**

회원의 이름과 팀의 이름이 같은 대상을 외부 조인해보겠습니다.

```java
/**
 * 연관관계가 없는 엔티티 외부 조인
 * 회원의 이름이 팀 이름과 같은 대상 외부 조인
 */
@Test
void join_on_no_relation() throws Exception {
    em.persist(new Member("teamA"));
    em.persist(new Member("teamB"));
    em.persist(new Member("teamC"));

    List<Tuple> result = queryFactory
            .select(member, team)
            .from(member)
            .leftJoin(team).on(member.username.eq(team.name))
            .fetch();

    for (Tuple tuple : result) {
        System.out.println("tuple = " + tuple);
    }
}
```

일반조인이 `leftJoin(member.team, team)` 와 같은 형식이라면, 연관관계 없는 엔티티 외부 조인은 ` from(member).leftJoin(team).on(xxx)` 과 같은 형식입니다. 결과값은 아래와 같습니다.

```
t=[Member(id=3, username=member1, age=10), null]
t=[Member(id=4, username=member2, age=20), null]
t=[Member(id=5, username=member3, age=30), null]
t=[Member(id=6, username=member4, age=40), null]
t=[Member(id=7, username=teamA, age=0), Team(id=1, name=teamA)]
t=[Member(id=8, username=teamB, age=0), Team(id=2, name=teamB)]
```

## 페치 조인

Querydsl 로 페치조인을 하는 방법입니다. `emf.getPersistenceUnitUtil().isLoaded(findMember.getTeam());` 으로 해당 값이 로딩이 영속성 컨텍스트로 로딩되었는지 확인할 수 있습니다.

```java
@PersistenceUnit
EntityManagerFactory emf;

@Test
void fetchJoinUse() {
    em.flush();
    em.clear();

    Member findMember = queryFactory
            .selectFrom(member)
            .join(member.team, team).fetchJoin()
            .where(member.username.eq("member1"))
            .fetchOne();

    boolean loaded = emf.getPersistenceUnitUtil().isLoaded(findMember.getTeam());
    assertThat(loaded).as("페치조인 적용").isTrue();
}
```

`.join(member.team, team).fetchJoin()` 처럼 조인문 뒤에 **`fetchJoin()`** 을 붙여줘야 합니다. 그렇지 않으면 지연로딩 전략이 적용됩니다. `loaded` 값은 `true` 가 나옵니다.

# 서브쿼리

아래는 서브쿼리의 예시입니다. 일부러 서브쿼리를 사용하기 위한 비효율적인 코드도 포함되어 있습니다.

```java
/**
 * 나이가 가장 많은 회원 조회
 */
@Test
public void subQuery() {

    QMember memberSub = new QMember("memberSub");

    List<Member> result = queryFactory
            .selectFrom(member)
            .where(member.age.eq(
                    JPAExpressions
                            .select(memberSub.age.max())
                            .from(memberSub)
            ))
            .fetch();

    assertThat(result).extracting("age")
            .containsExactly(40);
}

/**
 * 나이가 평균 이상인 회원
 */
@Test
public void subQueryGoe() {

    QMember memberSub = new QMember("memberSub");

    List<Member> result = queryFactory
            .selectFrom(member)
            .where(member.age.goe(
                    JPAExpressions
                            .select(memberSub.age.avg())
                            .from(memberSub)
            ))
            .fetch();

    assertThat(result).extracting("age")
            .containsExactly(30, 40);
}

/**
 * 나이가 10살보다 큰 회원 (예제용이며 효율적이지 않음)
 */
@Test
public void subQueryIn() {

    QMember memberSub = new QMember("memberSub");

    List<Member> result = queryFactory
            .selectFrom(member)
            .where(member.age.in(
                    JPAExpressions
                            .select(memberSub.age)
                            .from(memberSub)
                            .where(memberSub.age.gt(10))
            ))
            .fetch();

    assertThat(result).extracting("age")
            .containsExactly(20, 30, 40);
}

/**
 * select 절에 subQuery, 비효율적인 코드
 */
@Test
public void selectSubQuery() {

    QMember memberSub = new QMember("memberSub");

    List<Tuple> result = queryFactory
            .select(member.username,
                    JPAExpressions
                            .select(memberSub.age.avg())
                            .from(memberSub))
            .from(member)
            .fetch();

    for (Tuple tuple : result) {
        System.out.println("tuple = " + tuple);
    }
}
```

서브쿼리는 `JPAExpressions` 클래스를 통해 생성합니다.(`static import` 가능) 또한 alias 가 달라야 하므로 `new QMember("memberSub")` 를 선언해줘야 합니다.

JPQL 이 `from` 의 서브쿼리(인라인 뷰) 는 지원하지 않습니다. 따라서 Querydsl 에서도 사용할 수 없습니다. 해당 문제는 **서브쿼리를 `JOIN` 으로 변경**하거나, **쿼리를 2번 분리**해서 실행해서 해결할 수 있습니다. **nativeSQL 을 사용**해서도 해결할 수 있습니다. 

# Case 문

SELECT, 조건절(WHERE), ORDERBY 에서 사용 가능합니다. 하지만 DB 쿼리문은 적절한 Raw Data 를 가져오는 역할로 써야 하고 Data 의 변경은 어플리케이션에서 하는 게 좋습니다.

아래는 다양한 Case 문 예시입니다. 복잡한 Case 문은 `new CaseBuilder()` 를 사용해야 합니다.

```java
@Test
public void basicCase() {
    List<String> result = queryFactory
            .select(member.age
                    .when(10).then("열살")
                    .when(20).then("스무살")
                    .otherwise("기타"))
            .from(member)
            .fetch();

    for (String s : result) {
        System.out.println("s = " + s);
    }
}

@Test
public void complexCase() {
    List<String> result = queryFactory
            .select(new CaseBuilder()
                    .when(member.age.between(0, 20)).then("0~20살")
                    .when(member.age.between(21, 30)).then("21~30살")
                    .otherwise("기타"))
            .from(member)
            .fetch();

    for (String s : result) {
        System.out.println("s = " + s);
    }
}
```

아래는 OrderBy 예시입니다.

```java
@Test
public void caseOrderBy() {
    NumberExpression<Integer> rankPath = new CaseBuilder()
            .when(member.age.between(0, 20)).then(2)
            .when(member.age.between(21, 30)).then(1)
            .otherwise(3);

    List<Tuple> result = queryFactory
            .select(member.username, member.age, rankPath)
            .from(member)
            .orderBy(rankPath.desc())
            .fetch();

    for (Tuple tuple : result) {
        String username = tuple.get(member.username);
        Integer age = tuple.get(member.age);
        Integer rank = tuple.get(rankPath);
        System.out.println("username = " + username + " age = " + age + " rank = " + rank);
    }
}

/*
username = member4 age = 40 rank = 3
username = member1 age = 10 rank = 2
username = member2 age = 20 rank = 2
username = member3 age = 30 rank = 1
*/
```

# 상수, 문자 더하기

## 상수 출력

상수가 필요하면 `Expressions.constant(xxx)` 을 사용해야 합니다. JPQL 쿼리문이 나가는 걸 보면 상수가 없는데, Querydsl 에서 자체적으로 상수를 넣습니다.

```java
@Test
public void constant() {
    List<Tuple> result = queryFactory
            .select(member.username, Expressions.constant("A"))
            .from(member)
            .fetch();

    for (Tuple tuple : result) {
        System.out.println("tuple = " + tuple);
    }
}
/*
tuple = [member1, A]
tuple = [member2, A]
tuple = [member3, A]
tuple = [member4, A]
*/
```

JPQL 쿼리문 : `select member1.username from Member member1`(`A` 없음)

## 문자 더하기

테이블로 문자를 더하고 싶을 때 사용합니다. 아래는 `username` 과 `age` 를 더해서 `{username}_{age}` 을 필드값으로 출력합니다.

```java
@Test
public void concat() {

    //{username}_{age}
    List<String> result = queryFactory
            .select(member.username.concat("_").concat(member.age.stringValue()))
            .from(member)
            .where(member.username.eq("member1"))
            .fetch();

    for (String s : result) {
        System.out.println("s = " + s);
    }
}

/*
s = member1_10
*/
```

이 때 `username` 과 `age` 의 타입이 다르므로 `member.age.stringValue()` 로 타입을 `string` 으로 변경해줘야 합니다.