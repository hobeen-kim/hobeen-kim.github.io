---
categories: "springJPA"
tag: ["custom repository", "auditing", "domain class converter", "web paging and sorting"]
---

# 스프링 데이터 JPA 분석

​	스프링 데이터 JPA가 제공하는 공통 인터페이스의 구현체는 **`org.springframework.data.jpa.repository.support.SimpleJpaRepository`** 입니다.

```java
@Repository
@Transactional(readOnly = true)
public class SimpleJpaRepository<T, ID> ...{

    @Transactional
    public <S extends T> S save(S entity) {
        if (entityInformation.isNew(entity)) {
            em.persist(entity);
            return entity;
        } else {
        	return em.merge(entity);
        }
    }
...
}
```

- `@Repository` : 컴포넌트 스캔 대상이 됩니다. 또한 JPA, JDBC 등에서 발생되는 예외를 공통된 예외로 변환합니다. 따라서 하부 기술이 변경되어도 스프링을 사용하는 한 예외처리 로직을 변경하지 않아도 됩니다.
- `@Transactional(readOnly = true)` : Service 계층에서 트랜잭션이 있으면 이어받아서 동작합니다. 만약 트랜잭션이 없어도 DAO 계층에서 트랜잭션이 생깁니다. 따라서 스프링 데이터 JPA 를 사용할 때 트랜잭션이 없어도 데이터 등록, 변경이 가능합니다.
  - `readOnly = true` 면 커밋 시 플러시를 생략합니다. 약간의 성능 향상을 얻을 수 있습니다.

## 새로운 엔티티를 구별하는 방법

​	`SimpleJpaRepository` 에서 `public <S extends T> S save(S entity)` 에서는 새로운 엔티티를 `entityInformation.isNew(entity)` 를 통해 구별하고 있습니다. 그리고 새로운 엔티티라면 `persist()` 를, 아니라면 `merge()` 를 호출합니다. `merge()` 는 `where T.id = ?` 로 select 쿼리문을 보낸 다음에 해당 엔티티가 테이블에 있으면 1차 캐시로 가져와서 변경하고, 아니면 그대로 1차 캐시로 저장합니다. **결국은 merge() 는 select 를 1번 호출하게 되는 겁니다.**

​	하지만 아래와 같이 Id 를 직접 넣어주게 되면 문제가 발생합니다.

```java
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Item implements Persistable<String> {

    @Id
    private String id;

    public Item(String id) {
        this.id = id;
    }
}

@SpringBootTest
class ItemRepositoryTest {

    @Autowired ItemRepository itemRepository;

    @Test
    public void save(){
        Item item = new Item("A");
        itemRepository.save(item);
    }
}
```

​	위 코드에서 `itemRepository.save(item);` 는 `merge()` 를 호출하게 됩니다. 따라서 불필요하게 select 쿼리를 보내게 되는거죠. **이를 방지하기 위해 해당 엔티티가 새로운 엔티티인지 아닌지 여부를 알려줘야 합니다. `Persistable` 인터페이스를 구현해서 판단 로직을 변경할 수 있습니다.**

```java
@Entity
@EntityListeners(AuditingEntityListener.class)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Item implements Persistable<String> {

    @Id
    private String id;

    @CreatedDate
    private LocalDateTime createdDate;

    public Item(String id) {
        this.id = id;
    }

    @Override
    public String getId() {
        return id;
    }

    @Override
    public boolean isNew() {
        return createdDate == null;
    }
}
```

`Persistable` 인터페이스는 `getId` 와 `isNew` 메서드를 가지고 있습니다. **보통 `createdDate` 를 만들어서 해당 값이 없으면 새로운 객체가 되도록 판단하게 합니다.** 그러기 위해서는 `@EntityListeners(AuditingEntityListener.class)` 를 사용해야 겠죠.