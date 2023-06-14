---
categories: "codestates"
tag: ["DTO", "Validator"]
---

# DTO

​	DTO 란 Data Transfer Object의 약자로 데이터를 전송하기 위한 용도의 객체입니다. DTO 는 **코드의 간결성, 유효성 검증의 단순화**를 위해서 사용합니다.

​	보통 DTO 는 @RequestBody 어노테이션과 사용하는데요. @RequestBody 는 HTTP 메서드의 Body 값의 JSON 을 사용한다는 뜻입니다. JSON 형식의 Request Body를 MemberPostDto 클래스의 객체로 변환을 시켜주는 역할을 합니다. **이를 JSON 역직렬화(JSON -> java 객체) 라고 합니다.**

```java
@PatchMapping("/{member-id}")
public ResponseEntity patchMember(@PathVariable("member-id") long memberId,
                                  @RequestParam String phone) {
    Map<String, Object> body = new HashMap<>();
    body.put("memberId", memberId);
    body.put("email", "hgd@gmail.com");
    body.put("name", "홍길동");
    body.put("phone", phone);

    // No need Business logic

    return new ResponseEntity<Map>(body, HttpStatus.OK);
}
```

반대로 @ResponseBody 는 JSON 형식의 Response Body를 클라이언트에게 전달하기 위해 DTO 클래스의 객체를 Response Body로 변환하는 역할을 합니다. Spring MVC에서는 핸들러 메서드에 @ResponseBody 애너테이션이 붙거나 **핸들러 메서드의 리턴 값이 ResponseEntity**일 경우, 내부적으로 **HttpMessageConverter가 동작하게 되어 응답 객체(여기서는 DTO 클래스의 객체)를 JSON 형식으로 바꿔줍니다.** **이를 JSON 직렬화(객체 -> JSON) 라고 합니다.**



## DTO 클래스와 엔티티 클래스의 역할 분리가 필요한 이유

**계층별 관심사의 분리**

​	DTO 클래스는 API 계층에서 요청 데이터를 전달받고, 응답 데이터를 전송하는 것이 주 목적인 반면에 Entity 클래스는 서비스 계층에서 데이터 액세스 계층과 연동하여 비즈니스 로직의 결과로 생성된 데이터를 다루는 것이 주목적입니다.

**코드 구성의 단순화**

​	DTO 클래스에서 사용하는 유효성 검사 애너테이션이 Entity 클래스에서 사용이 된다면 JPA에서 사용하는 애너테이션과 뒤섞인 상태가 되어 유지보수하기 상당히 어려운 코드가 됩니다.

**REST API 스펙의 독립성 확보**

​	데이터 액세스 계층에서 전달받은 데이터로 채워진 Entity 클래스를 클라이언트의 응답으로 그대로 전달하게 되면 원치 않는 데이터까지 클라이언트에게 전송될 수 있습니다. DTO 클래스를 사용하면 회원의 로그인 패스워드 같은 정보를 클라이언트에게 노출하지 않고, 원하는 정보만 제공할 수 있습니다.

# Custom Validator

​	정규  표현식은 성능면에서 때로 비싼 비용을 치러야 할 가능성이 있습니다. 대신 Custom Validator를 구현하여 직접 애너테이션을 만들어서 유효성 검증을 적용할 수 있습니다.

**Custom Annotation**

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = {NotSpaceValidator.class})
public @interface NotSpace {
    String message() default "공백이 아니어야 합니다";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

**Custom Validator**

```java
public class NotSpaceValidator implements ConstraintValidator<NotSpace, String> {

    @Override
    public void initialize(NotSpace constraintAnnotation) {
        ConstraintValidator.super.initialize(constraintAnnotation);
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        return value == null || StringUtils.hasText(value);
    }
}
```

기본적으로 CustomValidator를 구현하기 위해서는 `ConstraintValidator` 인터페이스를 구현해야 합니다. isValid 의 리턴값이 유효성 검증 결과입니다.
