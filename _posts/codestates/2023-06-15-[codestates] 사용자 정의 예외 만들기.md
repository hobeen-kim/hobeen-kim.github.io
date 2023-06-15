---
categories: "codestates"
tag: ["custom Exception"]
---

# 비즈니스 예외 만들기

​	비즈니스 예외를 공통 로직으로 처리하기 위해서 enum 타입의 ExceptionCode 를 정의합니다.

**ExceptionCode** 

```java
public enum ExceptionCode {
    MEMBER_NOT_FOUND(404, "Member Not Found");

    @Getter
    private int status;

    @Getter
    private String message;

    ExceptionCode(int status, String message) {
        this.status = status;
        this.message = message;
    }
}
```

​	이제 비즈니스 예외를 만들고, ExceptionCode 를 필드값으로 가지도록 하면 됩니다.

**BusinessLogicException** 

```java
public class BusinessLogicException extends RuntimeException {
    @Getter
    private ExceptionCode exceptionCode;

    public BusinessLogicException(ExceptionCode exceptionCode) {
        super(exceptionCode.getMessage());
        this.exceptionCode = exceptionCode;
    }
}
```

​	BusinessLogicException 은 ExceptionCode 를 필드값으로 가지고 있습니다. 해당 예외를 처리할 때 필드값을 이용하여 메세지를 다르게 보낼 수 있습니다.

**GlobalExceptionAdvice** 

```java
@RestControllerAdvice
public class GlobalExceptionAdvice {
    ...
		...

    @ExceptionHandler
    public ResponseEntity handleBusinessLogicException(BusinessLogicException e) {
        System.out.println(e.getExceptionCode().getStatus());
        System.out.println(e.getMessage());

        return new ResponseEntity<>(HttpStatus.valueOf(e.getExceptionCode().getStatus()));
    }
}
```

​	해당 메서드는 status 만 보내고 있습니다. 기타 메세지나 정보를 보내려면 추가하면 되겠죠.