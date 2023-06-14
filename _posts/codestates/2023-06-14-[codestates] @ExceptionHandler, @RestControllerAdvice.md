---
categories: "codestates"
tag: ["ExceptionHandler", "RestControllerAdvice"]
---

# @ExceptionHandler를 이용한 예외 처리

​	ExceptionHandler 를 통해서 Controller 레벨에서의 예외 처리를 해보겠습니다.

```java
@RestController
@RequestMapping("/v6/members")
@Validated
@Slf4j
public class MemberControllerV6 {

    @PostMapping
    public ResponseEntity postMember(@Valid @RequestBody MemberPostDto memberDto) {
        Member member = mapper.memberPostDtoToMember(memberDto);

        Member response = memberService.createMember(member);

        return new ResponseEntity<>(mapper.memberToMemberResponseDto(response),
                HttpStatus.CREATED);
    }

    @ExceptionHandler
    public ResponseEntity handleException(MethodArgumentNotValidException e) {
        // (1)
        final List<FieldError> fieldErrors = e.getBindingResult().getFieldErrors();

        // (2)
        return new ResponseEntity<>(fieldErrors, HttpStatus.BAD_REQUEST);
    }
```

​	 `MethodArgumentNotValidException` 예외가 발생하면 `ResponseEntity<>(fieldErrors, HttpStatus.BAD_REQUEST);` 를 리턴하게 됩니다. 이 때 메세지는 아래와 같습니다.

```json
[
    {
        "codes": [
            "Email.memberPostDto.email",
            "Email.email",
            "Email.java.lang.String",
            "Email"
        ],
        "arguments": [
            {
                "codes": [
                    "memberPostDto.email",
                    "email"
                ],
                "arguments": null,
                "defaultMessage": "email",
                "code": "email"
            },
            [],
            {
                "arguments": null,
                "defaultMessage": ".*",
                "codes": [
                    ".*"
                ]
            }
        ],
        "defaultMessage": "올바른 형식의 이메일 주소여야 합니다",
        "objectName": "memberPostDto",
        "field": "email",
        "rejectedValue": "hgd@",
        "bindingFailure": false,
        "code": "Email"
    }
]
```

​	이 코드는 너무 길고 불필요한 정보가 많기 때문에 응답값으로 적절하지 않습니다. 따라서 아래와 같이 **ErrorResponse** 를 만들어줄 수 있습니다.

```java
@Getter
@AllArgsConstructor
public class ErrorResponse {

    private List<FieldError> fieldErrors;

    @Getter
    @AllArgsConstructor
    public static class FieldError {
        private String field;
        private Object rejectedValue;
        private String reason;
    }
}
```

ErrorResponse 는 내부 클래스인 FieldError 를 리스트형태로 갖는 필드값 fieldErrors 가 있습니다.

이제 ErrorResponse 이용하여 ExceptionHandler 를 수정해보겠습니다.

```java
@ExceptionHandler
    public ResponseEntity handleException(MethodArgumentNotValidException e) {
        // (1)
        final List<FieldError> fieldErrors = e.getBindingResult().getFieldErrors();

        // (2)
        List<ErrorResponse.FieldError> errors =
                fieldErrors.stream()
                            .map(error -> new ErrorResponse.FieldError(
                                error.getField(),
                                error.getRejectedValue(),
                                error.getDefaultMessage()))
                            .collect(Collectors.toList());

        return new ResponseEntity<>(new ErrorResponse(errors), HttpStatus.BAD_REQUEST);
    }
```

이번엔 응답값이 아래와 같이 ErrorResponse 에 설정된 필요한 정보만 나가는 걸 볼 수 있습니다.

```json
[
    "fieldErrors": {
            {
                "field": "email",
                "rejectedValue": "hgd@",
                "reason": "올바른 형식의 이메일 주소여야 합니다."
            },
            {
                "field": "name",
                "rejectedValue": "",
                "reason": "이름은 공백이 아니어야 합니다."
            }    
]
```

# @RestControllerAdvice를 이용한 예외처리

​	**@RestControllerAdvice 를 통해서 예외처리를 전역적으로 할 수 있습니다.**

```java
@RestControllerAdvice
public class GlobalExceptionAdvice {
    @ExceptionHandler
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleMethodArgumentNotValidException(
            MethodArgumentNotValidException e) {
        final ErrorResponse response = ErrorResponse.of(e.getBindingResult());

        return response;
    }

    @ExceptionHandler
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleConstraintViolationException(
            ConstraintViolationException e) {
        final ErrorResponse response = ErrorResponse.of(e.getConstraintViolations());

        return response;
    }
}
```

코드가 굉장히 깔끔해졌습니다. 하나하나 보겠습니다.

- @RestControllerAdvice : ControllerAdvice 에 @ResponseBody 기능을 포함하기 때문에 ResponseEntity 로 데이터를 래핑할 필요가 없습니다.
- @ExceptionHandler : ExceptionHandler 입니다. 전역적으로 처리됩니다.
- ` @ResponseStatus(HttpStatus.BAD_REQUEST)` 해당 응답값에 HTTP Status 를 포함해줍니다.

이제 **ErrorResponse** 를 보겠습니다.

```java
@Getter
public class ErrorResponse {
    private List<FieldError> fieldErrors; // (1)
    private List<ConstraintViolationError> violationErrors;  // (2)

		// (3)
    private ErrorResponse(List<FieldError> fieldErrors, List<ConstraintViolationError> violationErrors) {
        this.fieldErrors = fieldErrors;
        this.violationErrors = violationErrors;
    }

		// (4) BindingResult에 대한 ErrorResponse 객체 생성
    public static ErrorResponse of(BindingResult bindingResult) {
        return new ErrorResponse(FieldError.of(bindingResult), null);
    }

		// (5) Set<ConstraintViolation<?>> 객체에 대한 ErrorResponse 객체 생성
    public static ErrorResponse of(Set<ConstraintViolation<?>> violations) {
        return new ErrorResponse(null, ConstraintViolationError.of(violations));
    }

		// (6) Field Error 가공
    @Getter
    public static class FieldError {
        private String field;
        private Object rejectedValue;
        private String reason;

        private FieldError(String field, Object rejectedValue, String reason) {
            this.field = field;
            this.rejectedValue = rejectedValue;
            this.reason = reason;
        }

        public static List<FieldError> of(BindingResult bindingResult) {
            final List<org.springframework.validation.FieldError> fieldErrors =
                                                        bindingResult.getFieldErrors();
            return fieldErrors.stream()
                    .map(error -> new FieldError(
                            error.getField(),
                            error.getRejectedValue() == null ?
                                            "" : error.getRejectedValue().toString(),
                            error.getDefaultMessage()))
                    .collect(Collectors.toList());
        }
    }

		// (7) ConstraintViolation Error 가공
    @Getter
    public static class ConstraintViolationError {
        private String propertyPath;
        private Object rejectedValue;
        private String reason;

				private ConstraintViolationError(String propertyPath, Object rejectedValue,
                                   String reason) {
            this.propertyPath = propertyPath;
            this.rejectedValue = rejectedValue;
            this.reason = reason;
        }

        public static List<ConstraintViolationError> of(
                Set<ConstraintViolation<?>> constraintViolations) {
            return constraintViolations.stream()
                    .map(constraintViolation -> new ConstraintViolationError(
                            constraintViolation.getPropertyPath().toString(),
                            constraintViolation.getInvalidValue().toString(),
                            constraintViolation.getMessage()
                    )).collect(Collectors.toList());
        }
    }
}
```

MethodArgumentNotValidException 과 ConstraintViolationException 에 따라서 값을 다르게 적용시켜 보내야하기 때문에 각각 만들어줬습니다.
