---
categories: "springJPA"
tag: ["queryMethod"]
---

# 메소드 이름으로 쿼리 생성

[Spring Data JPA Docs](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#jpa.query-methods) 를 참고하면 쿼리 생성 메소드 규칙을 확인할 수 있습니다.

대표적으로 아래와 같이 사용할 수 있습니다.

- 조회: `find…By` , `read…By` ,`query…By`, `get…By`
  - https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#repositories.query-methods.query-creation 
- COUNT: `count…By` 반환타입 `long` 
- EXISTS: `exists…By` 반환타입 `boolean` 
- 삭제: `delete…By`, `remove…By` 반환타입 `long` 
- DISTINCT: `findDistinct`, `findMemberDistinctBy` 
- LIMIT: `findFirst3`, `findFirst`, `findTop`, `findTop3`
  - https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#repositories.limit-query-result

**username 과 age 로 조회**

```java
@Repository
@RequiredArgsConstructor
public class MemberJpaRepository {

    public List<Member> findByUsernameAndAgeGreaterThan(String username, int age){
        return em.createQuery("select m from Member m where m.username = :username and m.age > :age", Member.class)
                .setParameter("username", username)
                .setParameter("age", age)
                .getResultList();
    }
}

public interface MemberRepository extends JpaRepository<Member, Long> {

    List<Member> findByUsernameAndAgeGreaterThan(String username, int age);
}

```

위 `MemberJpaRepository` 의 `findByUsernameAndAgeGreaterThan` 과 `MemberRepository` 의 `findByUsernameAndAgeGreaterThan` 은 같은 쿼리를 보냅니다. 

# JPA NamedQuery

***\* 실무에서 거의 사용하지 않습니다.***

Entity 에서 @NamedQuery 어노테이션으로 Named 쿼리를 정의합니다.

**Member**

```java
@Entity
@Getter @Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@NamedQuery(
        name = "Member.findByUsername", //임의로 지으면 되지만 관례상 클래스명.메서드명으로 짓습니다.
        query = "select m from Member m where m.username = :username"
)
@ToString(of = {"id", "username", "age"})
public class Member {
...
}
```

**Repository**

```java
@Repository
@RequiredArgsConstructor
public class MemberJpaRepository {

    private final EntityManager em;

	...

    public List<Member> findByUsername(String username){
        return em.createNamedQuery("Member.findByUsername", Member.class)
                .setParameter("username", username)
                .getResultList();
    }
}

```

`createNamedQuery` 메소드를 통해서 `Member.findByUsername` 를 사용합니다. 

**JpaRepository**

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

    ...

	@Query(name = "Member.findByUsername")
    List<Member> findByUsername(@Param("username") String username);
}
```

​	JpaRepository 를 사용한다면 `@Query(name = "Member.findByUsername")` 어노테이션을 통해 NamedQuery 를 실행할 수 있습니다. 이때 `@Param("username")` 을 통해 파라미터값을 줘야합니다.

​	또한 `@Query(name = "Member.findByUsername")` 를 생략할 수 있습니다. 그러면 관례 상 `Repository 의 클래스명.메소드명` 으로 NamedQuery 를 먼저 찾고, 없으면 메소드생성규칙으로 쿼리문이 생성됩니다.

**NamedQuery 는 정적 쿼리이기 때문에 오타가 나면 애플리케이션 로딩 시점에 파싱을 해서 오류를 내줍니다.**

# Query (Repository 에 직접 쿼리 정의)

​	메서드에 직접 JPQL 쿼리를 작성하는 방식입니다.

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

    ...

    @Query("select m from Member m where m.username = :username and m.age = :age") //로딩 시점에 오류를 잡을 수 있습니다. (이름 없는 NamedQuery)
    List<Member> findUser(@Param("username") String username, @Param("age") int age);
}

```

NamedQuery 와 마찬가지로 애플리케이션 로딩 시점이 오류를 잡을 수 있습니다.

## DTO 로 조회하기

​	이번에는 @Query 어노테이션으로 DTO 를 조회하는 방법입니다. DTO 는 아래와 같습니다.

```java
package datajpa.dto;

import lombok.Data;

@Data
public class MemberDto {

    private Long id;
    private String username;
    private String teamName;

    public MemberDto(Long id, String username, String teamName){
        this.id = id;
        this.username = username;
        this.teamName = teamName;
    }
}
```

DTO 로 값을 넘겨받기 위해서는 모든 필드에 대한 생성자가 있어야 합니다.

이제 Repository 를 보겠습니다.

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

   ...

    @Query("select new datajpa.dto.MemberDto(m.id, m.username, t.name) from Member m join m.team t")
    List<MemberDto> findMemberDto();
}

```

`@Query` 에서 `new datajpa.dto.MemberDto(m.id, m.username, t.name)` 와 같이 새로운 클래스를 만드는 것처럼 select 쿼리문을 작성하면 됩니다.

## 파라미터 바인딩

​	파라미터 바인딩에는 위치 기반과 이름 기반이 있습니다.

```mysql
select m from Member m where m.username = ?0 //위치 기반
select m from Member m where m.username = :name //이름 기반
```

**하지만  코드 가독성과 유지보수를 위해 이름 기반 파라미터 바인딩을 사용하는 게 좋습니다.**

컬렉션 파라미터 바인딩 예시는 아래와 같습니다.

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

    ...

    @Query("select m from Member m where m.username in :names")
    List<Member> findByNames(@Param("names") Collection<String> names);
}

```

**`in 절`을 사용할 때는 컬렉션(Collection)을 파라미터로 바로 전달할 수 있습니다.**

아래는 테스트 코드입니다.

```java
@Test
void finByNames(){
    Member member1 = new Member("AAA", 10);
    Member member2 = new Member("BBB", 20);
    memberRepository.save(member1);
    memberRepository.save(member2);

    List<Member> result = memberRepository.findByNames(List.of("AAA", "BBB"));

    for (Member member : result) {
        System.out.println("member = " + member);
    }
}

/* result
member = Member(id=1, username=AAA, age=10)
member = Member(id=2, username=BBB, age=20)
*/
```

# 반환 타입

​	스프링 데이터 JPA는 유연한 반환 타입을 지원합니다. [Spring Docs 확인](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#repository-query-return-types)

아래 예시는 `Username` 으로 `member` 를 찾는 메서드의 다양한 반환타입입니다.(`Collection`, `T`, `Optional<T>`)

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

    List<Member> findListByUsername(String username);

    Member findMemberByUsername(String username); 

    Optional<Member> findOptionalByUsername(String username);
}
```

**컬렉션 반환 타입은 결과가 없으면 빈 컬렉션을 반환합니다.**

단건조회(`T`, `Optional<T>`) 는 결과가 없으면 `null` 을 반환합니다. **결과가 2건 이상이면 `NonUniqueResultException` 예외가 발생하고, `IncorrectResultSizeDataAccessException` 로 변환되어 최종적으로 반환**됩니다.

# 순수 JPA 페이징과 정렬

​	아래는 순수 JPA 를 통한 페이징입니다.

```java
@Repository
@RequiredArgsConstructor
public class MemberJpaRepository {

    ...

    public List<Member> findByPage(int age, int offset, int limit){
        return em.createQuery("select m from Member m where m.age = :age order by m.username desc", Member.class)
                .setParameter("age", age)
                .setFirstResult(offset)
                .setMaxResults(limit)
                .getResultList();
    }

    public long totalCount(int age){
        return em.createQuery("select count(m) from Member m where m.age = :age", Long.class)
                .setParameter("age", age)
                .getSingleResult();
    }
}
```

`findByPage` 메서드는 검색조건(`age`), 시작 위치(`offset`), 페이지 당 보여줄 데이터(`limit`) 를 파라미터로 받아서 결과를 출력합니다. `totalCount` 메서드는 총 레코드 수를 보여줍니다. (저는 offset 이 시작 페이지인줄 알았는데 아니더군요.)

아래는 테스트 코드입니다.

```java
@Test
public void paging(){
    memberJpaRepository.save(new Member("member1", 10));
    memberJpaRepository.save(new Member("member2", 10));
    memberJpaRepository.save(new Member("member3", 10));
    memberJpaRepository.save(new Member("member4", 10));
    memberJpaRepository.save(new Member("member5", 10));

    int age = 10;
    int offset = 0;
    int limit = 3;

    List<Member> members = memberJpaRepository.findByPage(age, offset, limit);
    long totalCount = memberJpaRepository.totalCount(age);

    assertThat(members.size()).isEqualTo(3);
    assertThat(totalCount).isEqualTo(5);
}
```

`username` 이 `"member5"`, `"member4"`, `"member3"` 인 `member` 가 출력됩니다.

# 스프링 데이터 JPA 페이징과 정렬

​	같은 조건으로 스프링 데이터 JPA 로 페이징과 정렬을 해보겠습니다.

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

    ...
    Page<Member> findByAge(int age, Pageable pageable);

    Slice<Member> findSliceByAge(int age, Pageable pageable);

    List<Member> findListByAge(int age, Pageable pageable);

    @Query(value = "select m from Member m left join m.team t",
            countQuery = "select count(m) from Member m")
    Page<Member> findCountByAge(int age, Pageable pageable);
}

```

총 4개의 메서드를 볼 수 있습니다.

## Page 반환타입

**`Page<Member> findByAge(int age, Pageable pageable);`** 테스트 코드

```java
@Test
public void pagingPage(){
    memberRepository.save(new Member("member1", 10));
    memberRepository.save(new Member("member2", 10));
    memberRepository.save(new Member("member3", 10));
    memberRepository.save(new Member("member4", 10));
    memberRepository.save(new Member("member5", 10));

    int age = 10;
    PageRequest pageRequest = PageRequest.of(0, 3, Sort.by(Sort.Direction.DESC, "username"));

    Page<Member> page = memberRepository.findByAge(age, pageRequest);

    Page<MemberDto> toMap = page.map(m -> new MemberDto(m.getId(), m.getUsername(), null));

    List<Member> content = page.getContent();
    long totalElements = page.getTotalElements();

    for (Member member : content) {
        System.out.println("member = " + member);
    }
    System.out.println("totalElements = " + totalElements);

    assertThat(content.size()).isEqualTo(3); //조회된 데이터 수
    assertThat(page.getTotalElements()).isEqualTo(5); //전체 데이터 개수
    assertThat(page.getNumber()).isEqualTo(0); //현재 페이지 번호
    assertThat(page.getTotalPages()).isEqualTo(2); //전체 페이지 개수
    assertThat(page.isFirst()).isTrue(); //첫 페이지인지 여부
    assertThat(page.hasNext()).isTrue(); //다음 페이지 여부
}
```

`Page<T>` 클래스는 paging 을 위한 다양한 메서드를 가지고 있습니다. (주석 참고) `Slice<T>` 와 차이는, `Page<T>` 는 전체 개수를 가지고 있다는 것입니다. (`getTotalElements()`, `getTotalPages()`)

문제점은 항상 count 쿼리문을 날린다는 건데, `left join` 시에서 `left join` 을 한 상태로 count 쿼리문을 날립니다. 따라서 나중에 아래에서 count 쿼리문만 따로 정의해서 날리는 걸 보겠습니다.

## Slice 반환타입

**` Slice<Member> findSliceByAge(int age, Pageable pageable);`** 테스트 코드

```java
@Test
    public void pagingSlice(){
        memberRepository.save(new Member("member1", 10));
        memberRepository.save(new Member("member2", 10));
        memberRepository.save(new Member("member3", 10));
        memberRepository.save(new Member("member4", 10));
        memberRepository.save(new Member("member5", 10));

        int age = 10;
        PageRequest pageRequest = PageRequest.of(0, 3, Sort.by(Sort.Direction.DESC, "username"));

        Slice<Member> page = memberRepository.findSliceByAge(age, pageRequest);

        List<Member> content = page.getContent();

        for (Member member : content) {
            System.out.println("member = " + member);
        }

        assertThat(content.size()).isEqualTo(3); //조회된 데이터 수
        assertThat(page.getNumber()).isEqualTo(0); //현재 페이지 번호
        assertThat(page.isFirst()).isTrue(); //첫 페이지인지 여부
        assertThat(page.hasNext()).isTrue(); //다음 페이지 여부
    }
```

`Slice<T>` 는 `Page<T>` 와 다르게 count 쿼리문을 날리지 않습니다. 대신 `getContent()` 를 하면 원래 `PageRequest` 로 보낸 `size` 값인 3 만큼 반환하지만, 실제 쿼리문은 아래와 같이 4개를 조회합니다. **(limit + 1 개수만큼 조회)**

```mysql
member0_.username as username3_0_ from member member0_ where member0_.age=10 order by member0_.username desc limit 4;
```

**따라서 다음 페이지가 있는지 없는지 확인할 수 있고, 주로 모바일에서 아래로 스크롤 할 때 "더보기" 버튼을 활성화하는 데 사용됩니다.**

## List 반환타입

**`List<Member> findListByAge(int age, Pageable pageable);` 테스트 코드**

```java
@Test
public void pagingList(){
    memberRepository.save(new Member("member1", 10));
    memberRepository.save(new Member("member2", 10));
    memberRepository.save(new Member("member3", 10));
    memberRepository.save(new Member("member4", 10));
    memberRepository.save(new Member("member5", 10));

    int age = 10;
    PageRequest pageRequest = PageRequest.of(0, 3, Sort.by(Sort.Direction.DESC, "username"));

    List<Member> page = memberRepository.findListByAge(age, pageRequest);

    assertThat(page.size()).isEqualTo(3); //조회된 데이터 수
}
```

​	정말 단순히 다른 메타정보는 필요없고 페이징 이후 값만 원할 때 사용할 수 있습니다.

## Page 반환타입 (count 쿼리문 작성)

outer join 으로 페이징 쿼리를 보내려면 `@Query` 로 보낼 수 있습니다. 이 때 `countQuery` 속성을 이용해서 count 쿼리는 따로 작성할 수 있습니다. **개수를 셀 때는 한쪽 테이블의 개수만 세면 되므로 join 이 필요없지만 불필요하게 join 문이 나가게 됩니다. 따라서 따로 count 쿼리를 작성하면 불필요한 자원 낭비를 피할 수 있습니다.**

**`Page<Member> findCountByAge(int age, Pageable pageable);` **

```java
public interface MemberRepository extends JpaRepository<Member, Long> {

    ...
        
    @Query(value = "select m from Member m left join m.team t",
            countQuery = "select count(m) from Member m") 
    Page<Member> findCountByAge(int age, Pageable pageable);
}
```

위 코드처럼 `countQuery` 를 분리해서 최적화할 수 있습니다.

# 벌크성 수정 쿼리

벌크성 수정 쿼리는 모든 튜플 값을 한번에 바꾸는 쿼리입니다. 예를 들어 모든 `Member.age` 를  `+1` 만큼 업데이트 할 때 사용할 수 있습니다.

## JPA 사용

```java
public int bulkAgePlus(int age){
    return em.createQuery("update Member m set m.age = m.age + 1 where m.age >= :age")
            .setParameter("age", age)
            .executeUpdate();
}
```

`executeUpdate()` 를 사용해야 수정 혹은 삭제가 가능합니다. 반환값은 변경된 레코드의 개수입니다.

```java
@Test
public void bulkUpdate(){
    memberJpaRepository.save(new Member("member1", 10));
    memberJpaRepository.save(new Member("member2", 19));
    memberJpaRepository.save(new Member("member3", 20));
    memberJpaRepository.save(new Member("member4", 21));
    memberJpaRepository.save(new Member("member5", 40));

    //when
    int resultCount = memberJpaRepository.bulkAgePlus(20);

    assertThat(resultCount).isEqualTo(3);
}
```

## Spring Data JPA 사용

```java
@Modifying(clearAutomatically = true)
@Query("update Member m set m.age = m.age + 1 where m.age >= :age")
int bulkAgePlus(@Param("age") int age);
```

`@Modifying(clearAutomatically = true)` : `executeUpdate()` 를 실행합니다. 빼면 다른 쿼리가 실행되면서 예외가 발생합니다. `clearAutomatically` 속성은 `em.clear()` 입니다. 벌크 연산은 DB 에 직접 sql 문을 보내기 때문에 영속성 컨텍스트와 값이 달라집니다. **따라서 `em.flush()` 와 `em.clear()` 가 필요한데, `em.flush()` 는 JPQL 문 실행 전에 항상 실행되고, `em.clear()` 를 따로 실행시켜줘야 합니다. **

```java
  @Test
    public void bulkUpdate(){
        memberRepository.save(new Member("member1", 10));
        memberRepository.save(new Member("member2", 19));
        memberRepository.save(new Member("member3", 20));
        memberRepository.save(new Member("member4", 21));
        memberRepository.save(new Member("member5", 40));

        //when
        int resultCount = memberRepository.bulkAgePlus(20);

        Member member = memberRepository.findByUsername("member5").get(0);
        System.out.println("member.age = " + member.getAge()); //41 이 나옵니다. 

        assertThat(resultCount).isEqualTo(3);
    }
```

만약 `@Modifying(clearAutomatically = true)` 에서 속성값을 `false(default)` 로 준다면  위 코드에서 `member.getAge()` 는 40 이 나오게 됩니다.

# @EntityGraph

​	`@EntityGraph` 는 `fetch join` 을 간편하게 사용하는 방법입니다.

```java
@Override
@EntityGraph(attributePaths = {"team"}) //fetch join 을 사용할 수 있습니다.
List<Member> findAll();

@EntityGraph(attributePaths = {"team"})
@Query("select m from Member m")
List<Member> findMemberEntityGraph();

@EntityGraph(attributePaths = {"team"})
List<Member> findEntityGraphByUsername(String username);

@EntityGraph("Member.all")
List<Member> findNamedEntityGraphByUsername(String username);
```

위 예시와 같이 `@EntityGraph` 의 속성값으로 `attributePaths` 를 통해 어떤 테이블을 `fetch join` 할지 명시합니다.

- `findAll()` : 오버라이딩을 통해 메서드를 재정의했습니다.

- `findMemberEntityGraph()` : `@Query` 와 함께 `@EntityGraph` 를 사용했습니다.

- `findEntityGraphByUsername(String username)` : 쿼리 메서드 기능과 함께 `@EntityGraph` 를 사용했습니다.

- `findNamedEntityGraphByUsername(String username)` : `@NamedEntityGraph` 로 미리 정의된 `@EntityGraph` 를 사용했습니다.

  - ```java
    @Entity
    @Getter @Setter
    @NoArgsConstructor(access = AccessLevel.PROTECTED)
    @NamedEntityGraph(name = "Member.all", attributeNodes = @NamedAttributeNode("team"))
    public class Member {
    ```

  - `Member` 엔티티에서 `@NamedEntityGraph` 를 정의해줍니다.

**테스트**

```java
@Test
public void findMemberLazy(){
    Team teamA = new Team("teamA");
    Team teamB = new Team("teamB");

    teamRepository.save(teamA);
    teamRepository.save(teamB);

    memberRepository.save(new Member("member1", 10, teamA));
    memberRepository.save(new Member("member2", 10, teamB));

    em.flush();
    em.clear();

    //when
    List<Member> members = memberRepository.findNamedEntityGraphByUsername("member1");

    //then
    for (Member member : members) {
        System.out.println("member = " + member.getUsername());
        System.out.println("member.teamClass = " + member.getTeam().getClass());
        System.out.println("member.team = " + member.getTeam().getName());
    }
}
```

**테스트에서 쿼리가 한번만 나가는 걸 볼 수 있습니다. (N + 1 문제 해결)**

# JPA Hint (ReadOnly)

조회용 쿼리문을 작성하는 Hint 입니다. 조회용은 변경하지 않기 때문에 1차 캐시에서 스냅샷을 찍을 필요가 없습니다. 따라서 메모리 최적화가 됩니다. **하지만 효과가 크지는 않으며, 해당 Hint 를 사용할 정도라면 쿼리 자체가 잘못되었거나 Redis 등 캐시 메모리를 따로 사용해야 합니다.**

```java
@QueryHints(value = @QueryHint(name = "org.hibernate.readOnly", value = "true"))
Member findReadOnlyByUsername(String username);
```

아래는 테스트 코드입니다.

```java
@Test
void queryHint(){
    Member member = memberRepository.save(new Member("member1", 10));
    em.flush();
    em.clear();

    Member findMember = memberRepository.findReadOnlyByUsername("member1");
    findMember.setUsername("member2");

    em.flush();

}
```

`em.clear();` 이후 `findMember.setUsername("member2");` 를 했지만 DB 에는 변경사항이 반영되지 않습니다. (UPDATE 쿼리문도 나가지 않게 됩니다.)

```java
@QueryHints(value = { @QueryHint(name = "org.hibernate.readOnly",value = "true")},
	forCounting = true)
Page<Member> findByUsername(String name, Pageable pageable);
```

`forCounting` : 반환 타입으로 Page 인터페이스를 적용하면 추가로 호출하는 페이징을 위한 count 쿼리도 쿼리 힌트를 적용합니다. (기본값 true )

