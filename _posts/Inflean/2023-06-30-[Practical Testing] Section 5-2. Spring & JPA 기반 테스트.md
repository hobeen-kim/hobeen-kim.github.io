---
categories: "inflearn"
tag: ["Api Layer", "TDD", "슬라이스 테스트"]
series: "Practical Testing: 실용적인 테스트 가이드"
teaser: "Practical Testing"
title: "[Practical Testing] Section 5-2. Spring & JPA 기반 테스트"
description: "Practical Testing: 실용적인 테스트 가이드 Section 5 내용 중 Presentation Layer 테스트입니다."
---

# Presentation Layer

​	Presentation Layer 는 외부 세계의 요청을 가장 먼저 받는 계층으로, **파라미터에 대한 최소한의 검증**을 수행합니다.

*코드는 생략하고 테스트 로직만 적겠습니다.*

## ProductControllerTest

```java
@WebMvcTest(ProductController.class) //@WebMvcTest 를 사용합니다.
class ProductControllerTest {

    @Autowired MockMvc mockMvc;

    @MockBean ProductService productService; //ProductController 에서 사용하는 productService 는 Mock 으로 주입합니다.

    @Autowired ObjectMapper objectMapper;

    @Test
    @DisplayName("신규 상품을 생성한다.")
    void createProduct() throws Exception {
        //given
        ProductCreateRequest request = ProductCreateRequest.builder()
                .type(HANDMADE)
                .sellingStatus(SELLING)
                .name("아메리카노")
                .price(4000)
                .build();

        //when
        ResultActions actions = mockMvc.perform(post("/api/v1/products/new")
                .content(objectMapper.writeValueAsString(request))
                .contentType(MediaType.APPLICATION_JSON)
        );

        //then
        actions
                .andDo(print())
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("신규 상품을 등록할 때 상품 타입은 필수값이다.")
    void createProductWithoutType() throws Exception {
        //given
        ProductCreateRequest request = ProductCreateRequest.builder()
                .sellingStatus(SELLING)
                .name("아메리카노")
                .price(4000)
                .build();

        //when
        ResultActions actions = mockMvc.perform(post("/api/v1/products/new")
                .content(objectMapper.writeValueAsString(request))
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
        );

        //then
        actions
                .andDo(print())
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(400))
                .andExpect(jsonPath("$.status").value("BAD_REQUEST"))
                .andExpect(jsonPath("$.message").value("상품 타입은 필수입니다."))
                .andExpect(jsonPath("$.data").isEmpty());
    }

    ... //다른 validation 검증 테스트

    @Test
    @DisplayName("판매 상품을 조회한다.")
    void getSellingProducts() throws Exception {
        //given
        List<ProductResponse> result = List.of();

        given(productService.getSellingProducts()).willReturn(result);

        //when
        ResultActions actions = mockMvc.perform(get("/api/v1/products/selling")
        );

        //then
        actions
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.status").value("OK"))
                .andExpect(jsonPath("$.message").value("OK"))
                .andExpect(jsonPath("$.data").isArray());
    }

}
```

Presentation Layer 의 테스트는 크게 두가지입니다.

1. 요청한 `Status` 와 `message` 가 그대로 오는지
2. `Validation` 이 잘 작동하는지

인데요. 그 외에 로직이 잘 수행되는지는 이미 Business Layer 를 검증하면서 확인했기 때문에 `Mock` 객체도 값을 구체적으로 반환할 필요는 없습니다.

몇가지 중요한 점만 짚어보겠습니다.

### validation 의 분리

아래는 API 가 받는 요청메세지인 `ProductCreateRequest` 입니다.

```java
@Getter
@NoArgsConstructor
public class ProductCreateRequest {

    @NotNull(message = "상품 타입은 필수입니다.")
    private ProductType type;
    
    @NotNull(message = "상품 판매상태는 필수입니다.")
    private ProductSellingStatus sellingStatus;
    
    @NotBlank(message = "상품 이름은 필수입니다.")
    @Length(max = 20, message = "상품 이름은 20자 이하여야 합니다.") //20자 -> 도메인에 맞는 특정한 값... String 에 대한 최소한의 조건만 검사
    private String name;

    @Positive(message = "상품 가격은 양수여야 합니다.")
    private int price;
```

`name` 필드를 보면 ` @NotBlank` 와 `@Length` 를 함께 사용하고 있습니다. **하지만 이렇게 설계하는 게 좋을까요?** `@NotBlank` 는 어떻게 보면 String 을 검증하는 데 있어서 당연한 검증입니다. **하지만 `@Length` 는 엄연히 도메인 지식이 필요한 비즈니스 로직입니다.** 이러한 비즈니스 로직은 Business Layer 나 Persistence Layer 가 처리할 문제이지, API 계층이 처리할 문제는 아닙니다. 따라서 모든 `Validation` 을 API 계층이 처리한다고 생각하면 안됩니다. 만약 비즈니스에 따라 검증 결과가 변경되어야 하는 경우에 곤란해지는 상황이 발생하겠죠.

### API 계층과 Business 계층 사이의 DTO 사용

API 계층에서 받는 DTO 를 그대로 Business 계층으로 보내면 어떻게 될까요? 몇 가지 문제점이 있습니다.

1. API 계층이 확장될 때 확장된 컨트롤러가 기존 컨트롤러의 DTO 를 알아야 합니다.
   - 만약 A API 계층이 B Business 계층으로 데이터를 넘길 때 `RequestDto` 를 곧장 넘긴다고 가정해봅시다. 이때 서비스를 확장해서 모바일용 A2 API 계층이 생겼고, 해당 계층 또한 B Business 계층으로 데이터를 넘겨야 합니다. 이때 A2 API 계층은 A API 계층의 `RequestDto` 를 사용할 수밖에 없습니다. 즉 모든 API 계층이 논리적으로 결합이 되는 겁니다.
2. 또한 하위 레이어가 상위 레이어에 따라 변경되는 문제점이 있습니다.
   - 위 예시에서, B Business 계층이 A API 계층의 Dto 를 사용하기 때문에 해당 `Dto` 가 변경된다면 B Business 의 코드도 변경되어야 합니다. 
3. 모듈로 분리할 때 `Validation` 문제가 생깁니다.
   - API `Dto` 는 `validation` 이 있는데, 모듈을 분리할 때 해당 `validation` 도 함께 Business 계층이 있는 곳으로 따라가야하는 문제가 있습니다.

### CQRS

​	**CQRS** 는 Command and Query Responsibility Segregation의 약자로, 이는 커**맨드(명령, 상태를 변경하는 작업)와 쿼리(조회, 상태를 읽는 작업)를 분리하는 패턴**입니다. 이렇게 하면 읽기와 쓰기에 최적화된 모델을 따로 구성할 수 있으며, 시스템의 복잡성을 관리하는 데 도움이 됩니다.

​	CQRS는 단순한 애플리케이션에는 과도한 복잡성을 추가할 수 있지만, 대규모 시스템에서는 성능 최적화, 유연성 향상, 복잡성 분리 등의 이점을 제공합니다. 

CUD 와 R 의 비율은 도메인에 따라 다르지만 2:8 정도이며, CQRS 를 사용하여 DB 에 대한 엔드포인트 구분을 할 수 있습니다. (readOnly DB 와 Write DB 구분)

### @webMvcTest 테스트에서 @EnableJpaAuditing을 스캔하지 못하는 문제

`@SpringBootApplication` 에서 `@EnableJpaAuditing` 붙여놓으면 `@webMvcTest` 테스트에서 스캔하지 못합니다. 따라서 Entity 를 등록할 때 오류가 발생합니다. 

이를 해결하기 위해 아래와 같이 `@Configuration` 파일을 따로 만들고 `@SpringBootApplication` 에서는 삭제합니다.

```java
//webMVC 테스트에서 @EnableJpaAuditing을 스캔하지 못하는 문제를 해결하기 위해 추가
@Configuration 
@EnableJpaAuditing // JPA Auditing 활성화
public class JpaAuditingConfig {
}
```

