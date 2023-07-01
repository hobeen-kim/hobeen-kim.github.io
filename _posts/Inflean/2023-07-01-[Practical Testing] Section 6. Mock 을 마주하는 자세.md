---
categories: "inflearn"
tag: ["test Double", "Stubbing", "@Spy", "@Mock", "@InjectMocks", "@MockBean", "Classicist VS. Mockist"]
series: "Practical Testing: 실용적인 테스트 가이드"
teaser: "Practical Testing"
title: "[Practical Testing] Section 6. Mock 을 마주하는 자세"
description: "Practical Testing: 실용적인 테스트 가이드 Section 6 내용입니다."
---

# Mock 예제 만들기

​	:heavy_check_mark: 요구사항

- 특정 기간 매출에 대한 메일 전송 로직

해당 요구사항을 위한 기능은 매출에 대한 계산뿐만 아니라 메일을 전송하는 로직까지 포함합니다. 하지만 메일을 실제로 전송하는 행위는 그 자체가 외부세계와 연결된 로직으로, 테스트가 힘들 수 있습니다. 

따라서 이를 해결하기 위해 Mock 객체를 사용합니다. Test 에서 `@MockBean` 을 이용합니다.

먼저 아래는 Mail 을 보내는 로직입니다. (실제 구현 x) 

```java
@Component
@Slf4j
public class MailSendClient {

    public boolean sendMail(String fromEmail, String toEmail, String subject, String content) {

        log.info("메일 전송");
        throw new IllegalArgumentException("메일 전송에 실패했습니다.");

    }
}
```

실제 해당 `sendMail()` 메서드를 이용 시 오류가 발생해서 테스트가 되지 않습니다. 따라서 아래와 같이 `MailSendClient` 를 목 객체로 만들어서 주입합니다.

```java
@SpringBootTest
class OrderStatisticsServiceTest {

    @Autowired OrderStatisticsService orderStatisticsService;
    @Autowired OrderRepository orderRepository;
    @Autowired ProductRepository productRepository;
    @Autowired MailSendHistoryRepository mailSendHistoryRepository;
    @Autowired OrderProductRepository orderProductRepository;

    //MailSendClient 주입
    @MockBean MailSendClient mailSendClient;

    @AfterEach
    void tearDown() {
        orderProductRepository.deleteAllInBatch();
        orderRepository.deleteAllInBatch();
        productRepository.deleteAllInBatch();
        mailSendHistoryRepository.deleteAllInBatch();
    }

    @Test
    @DisplayName("결제 완료 주문들을 조회하여 매출 통계 매일을 전송한다.")
    void sendOrderStaticsMail() {
        // given
        LocalDateTime now = LocalDateTime.of(2023, 3, 5, 0, 0);

        Product product1 = createProduct(HANDMADE, "001", 1000);
        Product product2 = createProduct(HANDMADE, "002", 2000);
        Product product3 = createProduct(HANDMADE, "003", 3000);
        List<Product> products = List.of(product1, product2, product3);
        productRepository.saveAll(products);

        Order order1 = createPaymentCompletedOrder(LocalDateTime.of(2023, 3, 4, 23, 59, 59), products);
        Order order2 = createPaymentCompletedOrder(now, products);
        Order order3 = createPaymentCompletedOrder(LocalDateTime.of(2023, 3, 4, 23, 59, 59, 999999999), products);
        Order order4 = createPaymentCompletedOrder(LocalDateTime.of(2023, 3, 6, 0, 0), products);

        given(mailSendClient.sendMail(anyString(), anyString(), anyString(), anyString()))
                .willReturn(true);

        // when
        boolean result = orderStatisticsService.sendOrderStaticsMail(LocalDate.of(2023, 3, 5), "test@test.com");
        List<MailSendHistory> histories = mailSendHistoryRepository.findAll();

        // then
        assertThat(result).isTrue();
        assertThat(histories).hasSize(1)
                .extracting("content")
                .contains("총 매출 합계는 12000원입니다.");

    }
```

가장 중요한 로직은 `given(mailSendClient.sendMail(anyString(), anyString(), anyString(), anyString())).willReturn(true);` 인데요. `mailSendClient.sendMail(...)` 의 파라미터로 어떠한 값이 들어오든지 `true` 를 리턴한다는 뜻입니다. 

​	이 로직을 사용하기 위해선 먼저 `mailSendClient` 가 목 객체여야 합니다. 따라서 `@MockBean MailSendClient mailSendClient;` 로 주입합니다. 나머지는 이전 Business Layer Test 와 비슷합니다.

# Test Double

[Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html#TheDifferenceBetweenMocksAndStubs) << 참고

테스트 더블은 '스턴드 터블'이라는 용어에서 아이디어를 얻어서 만들어졌습니다. 말 그대로 액터가 해야 할 행위를 대신하는 스턴트맨처럼 대체할 **모의 객체**를 생성해서 테스트를 진행하는 기술이라고 보면 됩니다. 

- Dummy : 아무 것도 하지 않는 깡통 객체입니다. 활용할 일은 거의 없습니다.
- Fake : 단순한 형태로 동일한 기능은 수행하나, 프로덕션에서 쓰기에는 부족한 객체입니다.
- Stub : 테스트에서 요청한 것에 대해 미리 준비한 결과를 제공하는 객체입니다. 정의한 것 외에는 응답하지 않습니다.
- Spy : Stub 이면서 호출된 내용을 기록하여 보여줄 수 있는 객체입니다. 일부는 실제 객체와 동일하게 동작시키고 일부만 Stubbing 할 수 있습니다.
- Mock : 행위에 대한 기대를 명세하고, 그에 따라 동작하도록 만들어진 객체입니다.

## Stub vs Mock

​	둘 다 가짜 객체이지만 검증하려는 목적이 다릅니다.

Stub 는 상태를 검증합니다. 기능을 요청했을 때 상태가 어떻게 변경되었는지에 대해 초점이 맞춰져있습니다. 반면 Mock 은 행위를 검증합니다. 어떤 기능을 요청했을 때 어떤 값을 리턴하는지 설정합니다.

**Stub** 

아래는 해당 사이트의 예시입니다.

```java
public interface MailService {
	public void send (Message msg);
}

public class MailServiceStub implements MailService {
    private List<Message> messages = new ArrayList<Message>();
    
    public void send (Message msg) {
    	messages.add(msg);
    }
    public int numberSent() {
    	return messages.size();
    }
}
```

```java
class OrderStateTester...

  public void testOrderSendsMailIfUnfilled() {
    Order order = new Order(TALISKER, 51);
    
    MailServiceStub mailer = new MailServiceStub();
    
    order.setMailer(mailer);
    order.fill(warehouse);
    
    assertEquals(1, mailer.numberSent());
  }
```

메일을 보냈을 때 올바른 상태 값이 나오는지(mail 을 1번 보냈는지) 체크합니다. 위 로직은 테스트를 위해서 MailServiceStub 라는 추가적은 클래스가 생성되었습니다.

**Mock** 

```java
class OrderInteractionTester...

  public void testOrderSendsMailIfUnfilled() {
    Order order = new Order(TALISKER, 51);
    
    Mock warehouse = mock(Warehouse.class);
    Mock mailer = mock(MailService.class);
    
    order.setMailer((MailService) mailer.proxy());

    mailer.expects(once()).method("send");
    warehouse.expects(once()).method("hasInventory")
      .withAnyArguments()
      .will(returnValue(false));

    order.fill((Warehouse) warehouse.proxy());
  }
}
```

`order.setMailer(mock mailer 객체)` 를 했을 때 `"send"` 와 `"hasInventory` 메서드가 1번씩 호출되었는지 봅니다. 즉, 행위에 대한 검증입니다.

# 순수 Mockito 로 검증해보기(@Mock, @Spy, @InjectMocks)

​	스프링을 이용하지 않고 `MailService` 의 단위 테스트를 해보겠습니다. 그러기 위해서는 `MailService` 가 DI 받는 요소를 `Mock` 으로 만들어줘야 합니다.

```java
class MailServiceTest {

    @Test
    @DisplayName("메일 전송 테스트")
    void sendMail() {

        // given
        MailSendClient mailSendClient = Mockito.mock(MailSendClient.class);
        MailSendHistoryRepository mailSendHistoryRepository = Mockito.mock(MailSendHistoryRepository.class);

        MailService mailService = new MailService(mailSendClient, mailSendHistoryRepository);

        ...
    }
}
```

`Mockito.mock(...)` 을 이용해서 `MailSendClient`, `MailSendHistoryRepository` 를 만들어줍니다. 그리고 `MailService` 를 만들면서 직접 주입합니다.

그리고 아래와 같이 테스트를 완성합니다.

```java
class MailServiceTest {

    @Test
    @DisplayName("메일 전송 테스트")
    void sendMail() {

        // given
        MailSendClient mailSendClient = Mockito.mock(MailSendClient.class);
        MailSendHistoryRepository mailSendHistoryRepository = Mockito.mock(MailSendHistoryRepository.class);

        MailService mailService = new MailService(mailSendClient, mailSendHistoryRepository);

        given(mailSendClient.sendMail(anyString(), anyString(), anyString(), anyString())).willReturn(true);

        // when
        boolean result = mailService.sendMail("", "", "", "");

        // then
        verify(mailSendHistoryRepository, times(1)).save(any(MailSendHistory.class)); //save 가 1번 호출되었는지 확인
        assertThat(result).isTrue();
    }
}
```

- `given` : `mailSendClient.sendMail()` 메서드 호출 시 항상 `true` 가 반환되도록 합니다.
- `verify` : `mailSendHistoryRepository.save()` 메서드가 몇번 호출되었는지 확인합니다. 이때 `mailSendHistoryRepository.save()` 의 리턴값은 반환타입의 기본값입니다. (null)

위 테스트를 `@Mock`, `@InjectMocks` 를 이용해서 리팩토링해보겠습니다.

```java
package sample.cafekiosk.spring.api.service.mail;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import sample.cafekiosk.spring.client.mail.MailSendClient;
import sample.cafekiosk.spring.domain.history.MailSendHistory;
import sample.cafekiosk.spring.domain.history.MailSendHistoryRepository;

import static org.assertj.core.api.Assertions.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class MailServiceTest {

    @Mock MailSendClient mailSendClient;
    @Mock MailSendHistoryRepository mailSendHistoryRepository;
    @InjectMocks MailService mailService;
    
    @Test
    @DisplayName("메일 전송 테스트")
    void sendMail() {

        // given
        given(mailSendClient.sendMail(anyString(), anyString(), anyString(), anyString())).willReturn(true);

        // when
        boolean result = mailService.sendMail("", "", "", "");

        // then
        verify(mailSendHistoryRepository, times(1)).save(any(MailSendHistory.class)); /
        assertThat(result).isTrue();
    }
}
```

- `@ExtendWith(MockitoExtension.class)` : `@Mock`, `@InjectMocks` 어노테이션을 인식할 수 있도록 지정합니다.
- `@Mock` : Mock 객체로 만들 클래스를 지정합니다.
- `@InjectMocks` :  Mock 객체를 주입받을 객체를 지정합니다.

## @Spy 사용

​	`@Spy` 는 실제 객체를 사용하되, 지정한 메서드의 반환 값은 특정하는 방법입니다. 예를 들어 `MailSendClient` 클래스에 다음과 같이 `a`, `b`, `c` 메서드를 추가한다고 가정하겠습니다.

```java
@Component
@Slf4j
public class MailSendClient {

    public boolean sendMail(String fromEmail, String toEmail, String subject, String content) {
        log.info("메일 전송");
        throw new IllegalArgumentException("메일 전송에 실패했습니다.");
    }

    public void a(){log.info("a");}

    public void b(){log.info("b");}

    public void c(){log.info("c");}
}
```

이때 테스트에서 원하는 건 `sendMail()` 메서드만 반환값을 `true` 로 지정하고, 나머지는 그대로 사용하는 겁니다. 만약 `@Mock` 어노테이션을 그대로 사용한다면 `a()`, `b()`, `c()` 도 마찬가지로 반환 타입의 기본 값으로 반환됩니다. 지금은 `void` 이니 출력값이 나오지 않습니다. 이를 해결하기 위해 `@Spy` 를 사용합니다.

```java
@ExtendWith(MockitoExtension.class)
class MailServiceTest {

    @Spy //spy 로 변경
    MailSendClient mailSendClient;
    @Mock MailSendHistoryRepository mailSendHistoryRepository;
    @InjectMocks MailService mailService;

    @Test
    @DisplayName("메일 전송 테스트")
    void sendMail() {

        doReturn(true)
                .when(mailSendClient)
                .sendMail(anyString(), anyString(), anyString(), anyString());


        // when
        boolean result = mailService.sendMail("", "", "", "");

        // then
        verify(mailSendHistoryRepository, times(1)).save(any(MailSendHistory.class)); //save 가 1번 호출되었는지 확인
        assertThat(result).isTrue();
    }
```

-  `doReturn(true).when(mailSendClient).sendMail(anyString(), anyString(), anyString(), anyString());` : Spy 는 실제 객체를 대상으로 하기 때문에 Mock 과 동작이 다릅니다. `doXXX.when()` 을 사용합니다.

# Classicist vs. Mockist

​	Mockist 는 모든 걸 Mocking 처리해서 하자는 거고, Classicist 는 반대로 Mocking 은 프로덕션 코드가 동작할 때의 기능을 검증할 수 없다는 입장입니다.

​	물론 Classicist 가 모든 Mocking 을 거부하는 건 아닙니다. 예를 들어 Persistence Layer 를 먼저 검증하고, 이후에 Business Layer 를 검증할 때 Persistence Layer 와 함께 통합 테스트를 구현할 수 있습니다. 하지만 Presentation Layer 는 요청과 응답이 잘 되는지만 확인하기 위해 Mocking 처리를 할 수 있습니다.

​	반대로 Mockist 는 Business Layer 를 테스트할 때도 Persistence Layer 를 Mocking 합니다.

​	하지만 **A, B 모듈이 둘다 단위 테스트를 통과한다고 하더라도, 함께 사용되었을 때 A + B 가 AB 로 동작할지, BA 로 동작할지, 전혀 다른 C 로 동작할지 모르게 됩니다**. (우빈님은 Classicist 에 가깝다고 하십니다. ㅎㅎ) 그래서 모듈 간의 통합적인 동작을 보는 테스트가 중요합니다. **또한, 실제 프로덕션 코드에서 런타임 시점에 일어날 일을 정확하게Stubbing 했다고 단언할 수 없는 점도 문제입니다.**

​	그럼 언제 Mocking 을 사용할까요? **바로 "우리 시스템" 의 "외부 시스템"을 요청할 때입니다.** 외부 시스템이 잘 동작하지 않거나 장애가 났을 때 따로 대응할 방법이 없기떄문에 해당 시스템을 Mocking 처리합니다.

​	