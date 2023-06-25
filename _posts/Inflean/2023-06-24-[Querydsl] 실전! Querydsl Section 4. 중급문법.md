---
categories: "inflearn"
tag: ["Querydsl", "projection", "@QueryProjection", "BooleanBuilder", "동적 쿼리", "bulk", "SQL function"]
description: "실전! Querydsl 강의 Section 4 내용입니다."
series: "실전! Querydsl"
title: "[Querydsl] 실전! Querydsl Section 4. 중급문법"

---

# 프로젝션과 결과 반환 

## Tuple 로 결과 반환 (기본)

프로젝션 대상이 하나일 때는 타입을 명확하게 지정할 수 있습니다. **반환 타입은 단일 타입**으로 반환됩니다. **`entity` 전체를 조회할 때도 반환타입은 `entity` 로 할 수 있으므로 단일 타입**입니다.

```java
@Test
public void simpleProjection() { //프로젝션 대상이 하나일 때 

    List<String> result = queryFactory
            .select(member.username)
            .from(member)
            .fetch();

    for (String s : result) {
        System.out.println("s = " + s);
    }
}
```

프로젝션 대상이 둘 이상일 때는 튜플로 반환됩니다.

```java
@Test
public void tupleProjection() {

    List<Tuple> result = queryFactory.select(member.username, member.age)
            .from(member)
            .fetch();

    for (Tuple tuple : result) {
        String username = tuple.get(member.username);
        Integer age = tuple.get(member.age);
        System.out.println("username = " + username);
        System.out.println("age = " + age);
    }
}
```

`Tuple`은 Querydsl 에서 제공하는 기술입니다. `Tuple` 은 `Repository` 안에서만 사용하고, `Service`, `Controller` 등에서는 `DTO` 로 변환해서 반환하는 것이 좋습니다. **구현 기술을 서로 분리해야 하기 때문입니다.**

## DTO 조회

Querydsl 을 통해 결과를 DTO 로 반환하는 방법은 **프로퍼티 접근, 필드 직접 접근, 생성자 사용**으로 총 3가지 방법이 있습니다.

아래는 반환 받는 MemberDto 입니다. `Projections.bean` 메서드를 사용합니다.

```java
@Data
@NoArgsConstructor
public class MemberDto {

    private String username;
    private int age;

    public MemberDto(String username, int age) {
        this.username = username;
        this.age = age;
    }
}
```

아래는 순서대로 프로퍼티 접근, 필드 직접 접근, 생성자 사용 방법입니다.

```java
@Test
void findDtoBySetter() { //기본생성자가 있어야 합니다.
    List<MemberDto> result = queryFactory
            .select(Projections.bean(MemberDto.class, //setter 가 있어야 합니다.
                    member.username,
                    member.age))
            .from(member)
            .fetch();

    for (MemberDto memberDto : result) {
        System.out.println("memberDto = " + memberDto);
    }
}

@Test
void findDtoByField() {
    List<MemberDto> result = queryFactory
            .select(Projections.fields(MemberDto.class, //getter, setter 가 없어도 됩니다.
                    member.username,
                    member.age))
            .from(member)
            .fetch();

    for (MemberDto memberDto : result) {
        System.out.println("memberDto = " + memberDto);
    }
}

@Test
void findDtoByConstructor() {
    List<MemberDto> result = queryFactory
            .select(Projections.constructor(MemberDto.class, //생성자의 타입과 맞아야 합니다.
                    member.username,
                    member.age))
            .from(member)
            .fetch();

    for (MemberDto memberDto : result) {
        System.out.println("memberDto = " + memberDto);
    }
}
```

- `findDtoBySetter()` : `setter` 로 받으려면 당연히 `setter` 가 있어야 하고 기본 생성자도 필요합니다.
- `findDtoByField()` : `setter` 가 없어도 됩니다. 필드에 직접 주입합니다.
- `findDtoByConstructor()` : 생성자의 파라미터와 순서가 맞아야 합니다.

**별칭이 다른 경우**

아래는 별칭이 다른 UserDto 입니다. 별칭이 다르다면 alias 를 통해 매칭해줘야 합니다.

```java
@Data
public class UserDto {
    private String name;
    private int age;
}
```

아래는 별칭이 다른 Dto 테스트입니다.

```java
@Test
void findUserDtoByField() { //매칭이 안되면 null 로 들어갑니다.

    QMember memberSub = new QMember("memberSub");

    List<UserDto> result = queryFactory
            .select(Projections.fields(UserDto.class,
                    member.username.as("name"),

                    ExpressionUtils.as(JPAExpressions
                            .select(memberSub.age.max())
                            .from(memberSub), "age") //두번째 age 는 서브쿼리를 쓰고 alias 로 매칭
                    ))
            .from(member)
            .fetch();

    for (UserDto userDto : result) {
        System.out.println("memberDto = " + userDto);
    }
    /*
        memberDto = UserDto(name=member1, age=40)
        memberDto = UserDto(name=member2, age=40)
        memberDto = UserDto(name=member3, age=40)
        memberDto = UserDto(name=member4, age=40)
     */

}

@Test
void findUserDtoByConstructor() {
    List<UserDto> result = queryFactory
            .select(Projections.constructor(UserDto.class, //생성자 주입은 이름이 맞지 않아도 됩니다.
                    member.username,
                    member.age))
            .from(member)
            .fetch();

    for (UserDto userDto : result) {
        System.out.println("userDto = " + userDto);
    }

    /*
        userDto = UserDto(name=member1, age=10)
        userDto = UserDto(name=member2, age=20)
        userDto = UserDto(name=member3, age=30)
        userDto = UserDto(name=member4, age=40)
     */
}
```

- `findUserDtoByField()` : 필드 주입입니다. 만약 별칭이 달라 매칭이 안되면 `null` 값이 들어갑니다. `member.username.as("name")` 과 같이 `as(xxx)` 로 `UserDto` 의 필드명과 맞춰줍니다.
- 서브쿼리를 사용하려면 `ExpressionUtils.as` 를 사용합니다. (코드 참고)
- `findUserDtoByConstructor()` : 생성자로 주입할 때는 별칭이 달라도 됩니다. `member` 의 속성명과 상관없이 들어가는 순서대로 생성자 파라미터가 됩니다.

## @QueryProjection 으로 프로젝션 결과 반환

​	MemberDto 의 생성자에 아래와 같이 `@QueryProjection` 어노테이션을 붙여서  사용합니다.

```java
@Data
@NoArgsConstructor
public class MemberDto {

    private String username;
    private int age;

    @QueryProjection //추가
    public MemberDto(String username, int age) {
        this.username = username;
        this.age = age;
    }
}
```

**빌드 이후에 QMemberDto 가 생깁니다.** 아래와 같이 사용할 수 있습니다.

```java
@Test
void findDtoByQueryProjection() {

    List<MemberDto> result = queryFactory
            .select(new QMemberDto(member.username, member.age)) //잘못 작성하면 컴파일 오류가 발생합니다.
            .from(member)
            .fetch();

    for (MemberDto memberDto : result) {
        System.out.println("memberDto = " + memberDto);
    }

    /*
        memberDto = MemberDto(username=member1, age=10)
        memberDto = MemberDto(username=member2, age=20)
        memberDto = MemberDto(username=member3, age=30)
        memberDto = MemberDto(username=member4, age=40)
     */
}
```

위에서 `Projections.constructor` 을 사용할 때는 런타임 에러라서 사용 중에 에러가 나는 문제가 있었습니다. 하지만 `new QMemberDto(member.username, member.age)` 처럼 생성자에 **파라미터값을 넘기면 맞지 않는 파라미터가 들어오면 컴파일 오류가 나서 미리 에러를 알 수 있는 장점**이 있습니다. 그리고 깔끔하게 코드를 작성할 수 있습니다.

**하지만 DTO 가 Querydsl 에 의존한다는 문제점이 있습니다.** DTO 는 DAO 뿐만 아니라 Application, API layer 에서도 사용되는데 DB 기술이 해당 계층까지 영향을 미칩니다. 만약 Querydsl 을 전혀 바꿀 일이 없다면 사용해도 괜찮습니다.

# 동적 쿼리 해결

## BooleanBuilder 사용

```java
Test
void dynamicQuery_BooleanBuilder() {

    String usernameParam = "member1";
    Integer ageParam = 10;

    List<Member> result = searchMember1(usernameParam, ageParam);
    assertThat(result.size()).isEqualTo(1);
}

private List<Member> searchMember1(String usernameCond, Integer ageCond) {

    BooleanBuilder builder = new BooleanBuilder();
    if(usernameCond != null) builder.and(member.username.eq(usernameCond));
    if(ageCond != null) builder.and(member.age.eq(ageCond));

    return queryFactory
            .selectFrom(member)
            .where(builder)
            .fetch();
}
```

`searchMember1()` 에서 파라미터로 넘어온 값이 `Null` 이 아니면 `builder.and` 를 통해 `where` 조건을 추가합니다. 마지막에 `.where(builder)` 으로 최종 조건을 추가해줍니다.

## Where 다중 파라미터 사용

​	Where 다중 파라미터를 사용하면 코드를 깔끔하게 만들 수 있습니다.

```java
@Test
    public void dynamicQuery_WhereParam() {

        em.persist(new Member("member5", 10));

        String usernameParam = "member1";
        Integer ageParam = 10;

        List<Member> result = searchMember2(usernameParam, ageParam);
        assertThat(result.size()).isEqualTo(1);
    }

    private List<Member> searchMember2(String usernameCond, Integer ageCond) {
        return queryFactory
                .selectFrom(member)
                .where(usernameEq(usernameCond), ageEq(ageCond)) 
                .fetch();
    }

    private BooleanExpression usernameEq(String usernameCond) {
        return usernameCond != null ? member.username.eq(usernameCond) : null;

    }

    private BooleanExpression ageEq(Integer ageCond) {
        return ageCond != null ? member.age.eq(ageCond) : null;
    }
```

`searchMember2()` 메서드를 보면 `.where(usernameEq(usernameCond), ageEq(ageCond))` 로 각각의 `BooleanExpression` 을 받습니다. **이때 `null` 값이면 무시하게 됩니다.**

아래와 같이 조합해서 사용할수도 있습니다.

```java
private List<Member> searchMember2(String usernameCond, Integer ageCond) {
    return queryFactory
            .selectFrom(member)
            .where(allEq(usernameCond, ageCond))
            .fetch();
}

private BooleanExpression usernameEq(String usernameCond) {
    return usernameCond != null ? member.username.eq(usernameCond) : null;

}

private BooleanExpression ageEq(Integer ageCond) {
    return ageCond != null ? member.age.eq(ageCond) : null;
}

private BooleanExpression allEq(String usernameCond, Integer ageCond) {
    return usernameEq(usernameCond).and(ageEq(ageCond));
}
```

`allEq()` 메서드에서 `usernameEq(usernameCond).or(ageEq(ageCond))` 처럼 조합해서 사용할 수도 있습니다. 하지만 이때는 `usernameCond` 이 `null` 이라면 NPE 가 발생합니다.

## 모든 조건 null 일 때 처리

그보다는 아래와 같이 `BooleanBuilder` 로 사용할 수 있습니다.

```java
@Test
void dynamicQuery() {

    String usernameParam = null;
    Integer ageParam = null;


    List<Member> result = queryFactory
            .selectFrom(member)
            .where(usernameAndAgeEq(usernameParam, ageParam))
            .fetch();

    for (Member member : result) {
        System.out.println("member1 = " + member);
    }
}

private BooleanBuilder usernameAndAgeEq(String username, Integer age){
    return usernameEqB(username).or(ageEqB(age));
}

private BooleanBuilder usernameEqB(String username){
    return nullSafeBuilder(() -> member.username.eq(username));
}

private BooleanBuilder ageEqB(Integer age) {
    return nullSafeBuilder(() -> member.age.eq(age));
}

public static BooleanBuilder nullSafeBuilder(Supplier<BooleanExpression> f){
    try {
        return new BooleanBuilder(f.get());
    } catch (IllegalArgumentException e){
        return new BooleanBuilder();
    }
}
```

`nullSafeBuilder()` 메서드를 지정하고, `null` 값이면 그냥 `BooleanBuilder()` 처럼 빈 값을 출력하도록 했습니다. 그러면 모든 조건이 되니까 `BooleanBuilder` 를 계속 이어나갈 수 있습니다.

# 수정, 삭제 벌크 연산

​	벌크 연산은 대량의 데이터를 쿼리 한번으로 수정하는 연산입니다.

```java
/**
* 나이가 28 미만인 사람의 이름을 "비회원"으로 변경
*/
@Test
void bulkUpdate() {
    long count = queryFactory
            .update(member)
            .set(member.username, "비회원")
            .where(member.age.lt(28))
            .execute();

    em.flush();
    em.clear();

    List<Member> result = queryFactory
            .selectFrom(member)
            .fetch();

    for (Member member1 : result) {
        System.out.println("member1 = " + member1);
    }
}

/**
* 회원 나이를 + 1
*/
@Test
public void bulkAdd(){
    queryFactory
            .update(member)
            .set(member.age, member.age.add(1)) //.multiply(), .divide()
            .execute();
}

/**
* 18살 초과 회원 삭제
*/
@Test
void bulkDelete() {
    queryFactory
            .delete(member)
            .where(member.age.gt(18))
            .execute();
    }
```

# SQL function 호출

SQL function 은 각 DB dialect 에 내장되어있는 함수를 사용하는 것입니다.

```java
@Test
void sqlFunction() {
    List<String> result = queryFactory
            .select(Expressions.stringTemplate(
                    "function('replace', {0}, {1}, {2})",
                    member.username, "member", "M"))
            .from(member)
            .fetch();

    for (String s : result) {
        System.out.println("s = " + s);
    }
}

@Test
public void sqlFunction2(){
    queryFactory
            .select(member.username)
            .from(member)
            .where(member.username.eq(
                    Expressions.stringTemplate("function('lower', {0})", member.username)))
            .fetch();
}

@Test
public void sqlFunction3(){

    queryFactory //위 아래는 같은 쿼리
            .select(member.username)
            .from(member)
            .where(member.username.eq(
                    member.username.lower()))
            .fetch();
}

```

`Expressions.stringTemplate()` 메서드를 사용해 호출합니다. **ANSI 표준에 있는 함수는 `member.username.eq(
member.username.lower())` 와 같이 Querydsl 에서 직접 호출할 수 있습니다.** 따라서 `sqlFunction2` 과 `sqlFunction3` 은 같은 쿼리문이 나갑니다.