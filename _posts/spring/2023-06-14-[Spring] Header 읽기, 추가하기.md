---
categories: "spring"
tag: ["httpHeader"]
title: "[Spring] Header 읽기, 추가하기"
---

# HTTP Request 헤더(Header) 정보 얻기

​	SpringMVC 에서 HTTP 헤더 정보를 읽는 방법입니다.

## @RequestHeader

```java
@RestController
@RequestMapping(path = "/test")
public class CoffeeController {
    @PostMapping
    public ResponseEntity postCoffee(@RequestHeader("user-agent") String userAgent) { //user-agent 헤더 읽기
        System.out.println("user-agent: " + userAgent);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

전체 헤더 정보를 받을 수도 있습니다.

```java
@RestController
@RequestMapping(path = "/v1/coffees")
public class CoffeeController {
    @PostMapping
    public ResponseEntity postCoffee(@RequestHeader Map<String, String> headers) { //전체 헤더 읽기
        //헤더 출력
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            System.out.println("key: " + entry.getKey() +
                    ", value: " + entry.getValue());
        }
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

## HttpServletRequest

```java
@RestController
@RequestMapping(path = "/test")
public class CoffeeController {
    @PostMapping
    public ResponseEntity postCoffee(HttpServletRequest httpServletRequest) { //HttpServletRequest 사용
        System.out.println("user-agent: " + httpServletRequest.getHeader("user-agent"));
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

> HttpServletRequest와 HttpServletResponse는 저수준(Low Level)의 서블릿 API를 사용할 수 있기 때문에 복잡한 HTTP Request/Response를 처리하는 데 사용할 수 있습니다.
>
> 반면에 ResponseEntity나 HttpHeaders는 Spring에서 지원하는 고수준(High Level) API로써 간단한 HTTP Request/Response 처리를 빠르게 진행할 수 있습니다.
>
> **복잡한 처리가 아니라면 코드의 간결성이나 생산성 면에서 가급적 Spring에서 지원하는 고수준 API를 사용하길 권장합니다.**

## HttpEntity

```java
@RestController
@RequestMapping(path = "/test")
public class CoffeeController {
    
    @PostMapping
    public ResponseEntity postCoffee(HttpEntity httpEntity) { //HttpEntity 사용
        for(Map.Entry<String, List<String>> entry : httpEntity.getHeaders().entrySet()){
            System.out.println("key: " + entry.getKey()
                    + ", " + "value: " + entry.getValue());
        }
        
        System.out.println("host: " + httpEntity.getHeaders().getHost());
        
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

​	HttpServletRequest 객체를 사용할 때와 마찬가지로 Entry 를 통해서 각각의 헤더 정보에 접근할 수 있는데, 특이한 것은 자주 사용될 만한 헤더 정보들을 getXXXX()로 얻을 수 있습니다. 위 코드에서는 getHost() 메서드를 통해서 host 정보를 확인하고 있습니다.

​	getXXXX() 메서드는 자주 사용되는 헤더 정보만 얻어올 수 있으므로 getXXXX() 메서드로 원하는 헤더 정보를 읽어올 수 없다면 get() 메서드를 사용해서 `get(”host”)`와 같이 해당 헤더 정보를 얻을 수 있습니다.

# HTTP Response 헤더(Header) 정보 추가

​	SpringMVC 에서 클라이언트에게 전달하는 Response에 헤더 정보를 추가하는 방법을 알아보도록 하겠습니다.

## ResponseEntity와 HttpHeaders

```java
@RestController
@RequestMapping(path = "/v1/members")
public class MemberController{
    @PostMapping
    public ResponseEntity postMember(@ResponseBody TestDto testDto) {
        //위치 정보를 헤더에 추가
        HttpHeaders headers = new HttpHeaders();
        headers.set("Client-Geo-Location", "Korea,Seoul");

        return new ResponseEntity<>(testDto, headers, HttpStatus.CREATED); //ResponseEntity 에 header 추가
    }
}
```

## HttpServletResposne

```java
@RestController
@RequestMapping(path = "/v1/members")
public class MemberController{
    @PostMapping
    public ResponseEntity postMember(HttpServletResponse response) {
        response.addHeader("Client-Geo-Location", "Korea,Seoul"); //HttpServletResponse 에 header 추가

        return new ResponseEntity<>(testDto, HttpStatus.CREATED); 
    }
}
```

​	마찬가지로 복잡한 처리가 아니라면 코드의 간결성이나 생산성 면에서 가급적 고수준 API 를 사용해야 합니다.