---
categories: "springJPA"
tag: ["transaction aop", "트랜잭션 전파", "트랜잭션 격리레벨"]
title: "[Transaction] AOP 방식 트랜잭션 적용"
description: "AOP 로 트랜잭션을 선언해서 서비스 계층의 @Transactional 을 제거할 수 있습니다."
series: "Transaction"
---

# 트랜잭션

​	트랜잭션은 **여러 개의 작업을 하나의 그룹으로 묶어서 처리하는 처리 단위**입니다. 물리적으로는 여러 개의 작업이지만 논리적으로는 마치 하나의 작업으로 인식해서 **전부 성공하든가 전부 실패하든가(All or Nothing)**의 둘 중 하나로만 처리되어야 트랜잭션의 의미를 가집니다. 이러한 트랜잭션은 아래와 같은 **ACID 원칙**을 가집니다.

- 원자성(Atomicity) : 트랜잭션에서의 원자성이란 작업을 더 이상 쪼갤 수 없음을 의미합니다.
- 일관성(Consistency) : 트랜잭션이 에러 없이 성공적으로 종료될 경우, 비즈니스 로직에서 의도하는 대로 일관성 있게 저장되거나 변경되는 것을 의미합니다.
- 격리성(Isolation) : 여러 개의 트랜잭션이 실행될 경우 각각 독립적으로 실행이 되어야 함을 의미합니다.
- 지속성(Durability) : 트랜잭션이 완료되면 그 결과는 지속되어야 한다는 의미입니다.

# 선언형 방식의 트랜잭션 적용

`@Transactional` 은 클래스와 메서드에 적용할 수 있습니다.

```java
@Transactional
public class MemberService {
    private final MemberRepository memberRepository;
    
    public MemberService(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }

    public Member create(Member member) {
        return memberRepository.save(member);
    }
    
    @Transactional(readOnly=true)
    public Member find(Member member) {
        return memberRepository.findById(member.getId());
    }
    
    ...
        
}
```

`@Transactional` 애너테이션을 클래스 레벨에 추가하면 기본적으로 해당 클래스에서 MemberRepository의 기능을 이용하는 모든 메서드에 트랜잭션이 적용됩니다. **이때 메서드 로직 실행 중 unchecked 예외가 발생하면 롤백이 되고 checked 예외는 커밋이 됩니다.**

`find()` 메서드처럼 메서드레벨에 트랜잭션이 있다면 해당 트랜잭션이 실행됩니다.

## 트랜잭션 전파

​	메서드 내에서 실행되는 모든 작업은 하나의 트랜잭션으로 묶입니다. 트랜잭션 전파란 트랜잭션의 경계에서 진행 중인 트랜잭션이 존재할 때 또는 존재하지 않을 때, 어떻게 동작할 것인지 결정하는 방식을 의미합니다.

```java
@Transactional
@RequiredArgsConstructor
public class OrderService {
    private final MemberService memberService;
    private final OrderRepository orderRepository;
    private final CoffeeService coffeeService;

    public Order createOrder(Order order) {

        Order savedOrder = saveOrder(order); // 1
        updateStamp(savedOrder); // 2

        return savedOrder;
    }

    private void updateStamp(Order order) {
        Member member = memberService.findMember(order.getMember().getMemberId());
        int stampCount = calculateStampCount(order);
        
        Stamp stamp = member.getStamp();
        stamp.setStampCount(stamp.getStampCount() + stampCount);
        member.setStamp(stamp);

        memberService.updateMember(member);
    }

    private int calculateStampCount(Order order) {
        return order.getOrderCoffees().stream()
                .map(orderCoffee -> orderCoffee.getQuantity())
                .mapToInt(quantity -> quantity)
                .sum();
    }

    private Order saveOrder(Order order) {
        return orderRepository.save(order);
    }
		...
		...
        
}
```

`createOrder` 메서드에서 `saveOrder` 메서드가 성공해도 `updateStamp` 메서도가 실패하면 전체가 롤백되게 됩니다. `createOrder` 트랜잭션이 하위 메서드로 전파되기 때문입니다.

트랜잭션 전파는 아래와 같은 종류가 있습니다. default 는 `    @Transactional(propagation = Propagation.REQUIRED)` 입니다.

- `Propagation.REQUIRED` : 진행 중인 트랜잭션이 없으면 새로 시작하고, 진행 중인 트랜잭션이 있으면 해당 트랜잭션에 참여합니다.
- `Propagation.REQUIRES_NEW` : 이미 진행 중인 트랜잭션과 무관하게 새로운 트랜잭션이 시작됩니다. 기존에 진행 중이던 트랜잭션은 새로 시작된 트랜잭션이 종료할 때까지 중지됩니다.
- `Propagation.MANDATORY` : `Propagation.REQUIRED`는 진행 중인 트랜잭션이 없으면 새로운 트랜잭션이 시작되는 반면, `Propagation.MANDATORY`는 진행 중인 트랜잭션이 없으면 예외를 발생시킵니다.
- `Propagation.NOT_SUPPORTED` : 트랜잭션을 필요로 하지 않음을 의미합니다. 진행 중인 트랜잭션이 있으면 메서드 실행이 종료될 때까지 진행 중인 트랜잭션은 중지되며, 메서드 실행이 종료되면 트랜잭션을 계속 진행합니다.
- `Propagation.NEVER` : 트랜잭션을 필요로 하지 않음을 의미하며, 진행 중인 트랜잭션이 존재할 경우에는 예외를 발생시킵니다.

## 트랜잭션 격리 레벨(Isolation Level)

​	트랜잭션은 다른 트랜잭션에 영향을 주지 않고, 독립적으로 실행되어야 하는 격리성이 보장되어야 하는데 Spring 은 이러한 격리성을 조정할 수 있는 옵션을 `@Transactional` 애너테이션의 `isolation` 속성을 통해 제공하고 있습니다.

- `Isolation.DEFAULT` 데이터베이스에서 제공하는 기본 값입니다.
- `Isolation.READ_UNCOMMITTED` 다른 트랜잭션에서 커밋하지 않은 데이터를 읽는 것을 허용합니다.
- `Isolation.READ_COMMITTED` 다른 트랜잭션에 의해 커밋된 데이터를 읽는 것을 허용합니다.
- `Isolation.REPEATABLE_READ` 트랜잭션 내에서 한 번 조회한 데이터를 반복해서 조회해도 같은 데이터가 조회되도록 합니다.
- `Isolation.SERIALIZABLE` 동일한 데이터에 대해서 동시에 두 개 이상의 트랜잭션이 수행되지 못하도록 합니다.

# AOP 방식의 트랜잭션 적용

​	`@Transactional` 어노테이션을 사용하지 않고 AOP 방식으로 적용할 수 있습니다.

```java
@Configuration
public class TxConfig {
    private final TransactionManager transactionManager;

    public TxConfig(TransactionManager transactionManager) { //1
        this.transactionManager = transactionManager;
    }

    @Bean
    public TransactionInterceptor txAdvice() { //2
        NameMatchTransactionAttributeSource txAttributeSource = new NameMatchTransactionAttributeSource(); 

        RuleBasedTransactionAttribute txAttribute = new RuleBasedTransactionAttribute(); //3. 트랜잭션 속성을 정의
        txAttribute.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRED);

        RuleBasedTransactionAttribute txFindAttribute = new RuleBasedTransactionAttribute(); //4
        txFindAttribute.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRED);
        txFindAttribute.setReadOnly(true);

        Map<String, TransactionAttribute> txMethods = new HashMap<>();
        txMethods.put("find*", txFindAttribute); //5
        txMethods.put("*", txAttribute);

        txAttributeSource.setNameMap(txMethods); //6

        return new TransactionInterceptor(transactionManager, txAttributeSource);
    }

    @Bean
    public Advisor txAdvisor() { //7

        AspectJExpressionPointcut pointcut = new AspectJExpressionPointcut();
        pointcut.setExpression("execution(* com.codestates.coffee.service." + "CoffeeService.*(..))");

        return new DefaultPointcutAdvisor(pointcut, txAdvice());
    }
}
```

1. `TransactionManager` 객체를 주입받습니다. `TransactionManager` 는 스프링에서 관리하는 공통 트랜잭션 인터페이스입니다.
2. `TransactionInterceptor` 을 빈으로 등록해서 대상 클래스 또는 인터페이스에 트랜잭션 경계를 설정하고 트랜잭션을 적용할 수 있습니다.
3. `txAttribute` 은 트랜잭션 전파속성이 `PROPAGATION_REQUIRED` 인 트랜잭션입니다.
4. `txFindAttribute` 은 트랜잭션 전파속성이 `PROPAGATION_REQUIRED` 인 `readOnly` 트랜잭션입니다.
5. `txMethods` 으로 각각의 `RuleBasedTransactionAttribute` 가 어느 메서드에 매핑되는지 설정합니다. `txFindAttribute` 는 `find*` 메서드에 매핑되고 나머지는 모두 `txAttribute` 에 매핑됩니다.
6. `NameMatchTransactionAttributeSource` 에 `txMethods` 를 넘겨줍니다.
7. 어드바이저를 만듭니다. 어드바이스는 위에서 만든 `txAdvice()` 이며 `pointcut` 은 직접 지정합니다.