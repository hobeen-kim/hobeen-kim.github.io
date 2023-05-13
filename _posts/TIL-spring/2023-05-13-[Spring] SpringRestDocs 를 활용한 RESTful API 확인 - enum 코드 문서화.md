---
categories: "TIL-spring"
tag: ["spring", "restDocs", "restapi"]
---

[[spring\] springrestdocs 를 활용한 restful api 확인](https://hobeen-kim.github.io/til-spring/Spring-SpringRestDocs-를-활용한-RESTful-API-확인/)

내용이 길어져서 포스팅을 나눴습니다.

# Enum 코드 문서화

지금까지 사용한 필드 중에 Enum 타입이 없었는데요. Member 에 Authority enum 타입을 만들어서 사용해보고, 문서화도 해보겠습니다.

그리고 문서에서 Enum 타입을 확인할 수 있도록 PopUp 창을 띄우는 것까지 만들겠습니다.

아래 이미지는 최종적인 모습입니다. Description 에 링크를 걸어 Enum 에 대한 설명을 볼 수 있습니다.

![image-20230513170330210](../../images/2023-05-13-[Spring] SpringRestDocs 를 활용한 RESTful API 확인(2)/image-20230513170330210.png)

**Gradle**

코드 작성 전에 gradle 에 test 용 lombok 을 추가해줍니다.

```
testCompileOnly 'org.projectlombok:lombok' // 테스트 의존성 추가
testAnnotationProcessor 'org.projectlombok:lombok' // 테스트 의존성 추가
```

그리고 settings 의 Annotation Processors 에서 Enable annotation processing 을 체크해줍니다.

## main.java 

모든 Enum 타입에서 공통적으로 사용할 메서드를 먼저 선언해줍니다. EnumType 의 메서드는 문서화 작업시 사용됩니다. EnumType, Authority 는 main.java 에서 entity 디렉토리에 만들었습니다.

```java
package restapi.restdocs.entity;

public interface EnumType {
    String getName();
    String getDescription();
}

```

Authority 도 만들어 줍니다.

```java
package restapi.restdocs.entity;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public enum Authority implements EnumType{

    USER("일반 사용자"),
    ADMIN("관리자");

    private final String description;

    @Override
    public String getName() {
        return this.description;
    }

    @Override
    public String getDescription() {
        return this.name();
    }
}
```



## Test.java

### custom-response-fields.snippet

enum 타입을 만들 때 사용할 템플릿입니다. test.resources.org.springframework.restdocs.templates 에 만들어줍니다.

```
{{#title}}{{.}}{{/title}}
|===
|code|Description

{{#fields}}
|{{#tableCellContent}}`+{{path}}+`{{/tableCellContent}}
|{{#tableCellContent}}{{description}}{{/tableCellContent}}
{{/fields}}
|===
```

빨간색으로 오류가 떠도 괜찮습니다.


### CustomResponseFieldsSnippet

```java
package restapi.restdocs.restdocsTest.utils;

import org.springframework.http.MediaType;
import org.springframework.restdocs.operation.Operation;
import org.springframework.restdocs.payload.AbstractFieldsSnippet;
import org.springframework.restdocs.payload.FieldDescriptor;
import org.springframework.restdocs.payload.PayloadSubsectionExtractor;

import java.io.IOException;
import java.util.List;
import java.util.Map;

public class CustomResponseFieldsSnippet extends AbstractFieldsSnippet {

    public CustomResponseFieldsSnippet(
        String type, PayloadSubsectionExtractor<?> subsectionExtractor, List<FieldDescriptor> descriptors, Map<String, Object> attributes, boolean ignoreUndocumentedFields) {
        super(type, descriptors, attributes, ignoreUndocumentedFields, subsectionExtractor);
    }
    @Override
    protected MediaType getContentType(Operation operation) {
        return operation.getResponse().getHeaders().getContentType();
    }

    @Override
    protected byte[] getContent(Operation operation) throws IOException {
        return operation.getResponse().getContent();
    }
}
```

​	이 클래스는 default 템플릿이 아닌 custom 템플릿을 사용하기 위한 클래스입니다. 생성자의 parameter 중 type 을 보고 template 을 결정합니다. `custom-response-fields.snippet` 을 사용하기 위해서는 type 값으로 "custom-response" 를 넘겨줘야 합니다.

### ApiResponseDto.java

```java
package restapi.restdocs.restdocsTest.utils;

@ToString
@Getter
@NoArgsConstructor
@Builder
public class ApiResponseDto<T> {

    private T data;

    private ApiResponseDto(T data){
        this.data = data;
    }

    public static <T> ApiResponseDto<T> of(T data) {
        return new ApiResponseDto<>(data);
    }
}
```

​	Test 패키지에서 만들 컨트롤러에서 반환값으로 사용하는 클래스입니다.

### EnumDocs

```java
package restapi.restdocs.restdocsTest.utils;

import lombok.*;

import java.util.Map;

@NoArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class EnumDocs {
    Map<String,String> authority;
}

```

​	마찬가지로 Test 패키지에서 만들 컨트롤러에서 사용할 클래스입니다. 문서화하고자 하는 모든 Enum 값을 명시해줍니다.

### CommonDocController

```java
package restapi.restdocs.restdocsTest.utils;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import restapi.restdocs.entity.Authority;
import restapi.restdocs.entity.EnumType;

import java.util.Arrays;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/test")
public class CommonDocController {

    @GetMapping("/enums")
    public ApiResponseDto<EnumDocs> findEnums() {

        // 문서화할 값들을 다 지정해줍니다.
        Map<String, String> authority = getDocs(Authority.values());

        // ApiResponseDto 에 모두 담아서 return 합니다. 나중에 파싱할 겁니다.
        return ApiResponseDto.of(EnumDocs.builder()
                .authority(authority)
                .build()
        );
    }

    private Map<String, String> getDocs(EnumType[] enumTypes) {
        return Arrays.stream(enumTypes)
                .collect(Collectors.toMap(EnumType::getName, EnumType::getDescription));
    }
}
```

​	EnumDocs 클래스에 문서화하고자 하는 모든 값들을 생성하고 builder 로 담아줍니다. 그리고 그 EnumDocs 를 ApiResponseDto 에 담아서 반환해줍니다. 이를 바탕으로 만들어진 조각으로 문서화를 진행할 예정입니다.

### CommonDocControllerTest

```java
package restapi.restdocs.restdocsTest.controller;

@ExtendWith({RestDocumentationExtension.class, SpringExtension.class})
@SpringBootTest
class CommonDocControllerTest {

    @Autowired
    protected ObjectMapper objectMapper;

    private MockMvc mockMvc;
    @BeforeEach
    public void setUp(WebApplicationContext webApplicationContext,
                      RestDocumentationContextProvider restDocumentation) {
        this.mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext)
                .apply(documentationConfiguration(restDocumentation)
                        .operationPreprocessors()
                        .withResponseDefaults(prettyPrint())
                        .withRequestDefaults(prettyPrint()))
                .build();
    }

    @Test
    public void enums() throws Exception {
        // 요청한 return 값을 받습니다.
        ResultActions result = this.mockMvc.perform(
                get("/test/enums")
                        .contentType(MediaType.APPLICATION_JSON)
        );

        // 결과값을 저장합니다.
        MvcResult mvcResult = result.andReturn();

        // 결과값을 EnumDocs 로 parsing 합니다.
        EnumDocs enumDocs = getData(mvcResult);

        // 문서화를 진행합니다.
        result.andExpect(status().isOk())
                .andDo(document("authority",
                        customResponseFields("custom-response", beneathPath("data.authority").withSubsectionId("authority"),
                                attributes(field("title", "authority")),
                                enumConvertFieldDescriptor(enumDocs.getAuthority())
                        )
                ));
    }

    // 커스텀 템플릿 사용을 위한 함수입니다. 
    public static CustomResponseFieldsSnippet customResponseFields
        (
            String type,
            PayloadSubsectionExtractor<?> subsectionExtractor,
            Map<String, Object> attributes, FieldDescriptor... descriptors
    	) {
        return new CustomResponseFieldsSnippet(type, subsectionExtractor, Arrays.asList(descriptors), attributes, true);
    }

    // Map으로 넘어온 enumValue를 fieldWithPath 로 전부 바꿔서 배열로 넘깁니다.
    private static FieldDescriptor[] enumConvertFieldDescriptor(Map<String, String> enumValues) {
        return enumValues.entrySet().stream()
                .map(x -> fieldWithPath(x.getKey()).description(x.getValue()))
                .toArray(FieldDescriptor[]::new);
    }

    // mvc result 데이터를 parsing 합니다.
    private EnumDocs getData(MvcResult result) throws IOException {
        ApiResponseDto<EnumDocs> apiResponseDto = objectMapper.readValue(result.getResponse().getContentAsByteArray(), new TypeReference<>(){});
        return apiResponseDto.getData();
    }
}
```

`customResponseFields("custom-response", beneathPath("data.authority").withSubsectionId("authority"), attributes(field("title", "authority")), enumConvertFieldDescriptor(enumDocs.getAuthority()))` custom 템플릿을 만들기 위해서 보내는 인자값들입니다. 이 부분을 자세히 보도록 하겠습니다.

- type : custom-response-fields.snippet 템플릿 사용을 위한 인자입니다. "custom-response" 를 넘깁니다.
- subsectionExtractor : 어떤 값에서 데이터를 추출할지 정해줍니다. `beneathPath("data.authority")` 는 result(=ApiResponseDto) 의 data 필드에서 authority 를 뽑아내는 것입니다. 즉, ApiResponseDto.data.authority 라고 볼 수 있습니다. 이 때 data 는 enumDocs 를 넣어주었습니다. 그리고 `.withSubsectionId("authority")` 는 adoc 문서의 이름입니다. `custom-response-fields-[문서이름]` 으로 설정됩니다. 여기서는 `custom-response-fields-authority` 가 되겠습니다.
- attributes : key, value 값으로 보냅니다. title 을 설정하기 위해 authority 를 보냈습니다.
- descriptors : `enumDocs.getAuthority()` 안에는 Enum 값들이 들어있습니다. (USER, ADMIN) 이 값들을 문서화 하기 위해 Descriptor 배열로 변경하여 인자로 넣어줍니다.



## 팝업창 만들기

​	asciidoc 자체에서 팝업 기능을 제공하지는 않습니다. 대신 docinfo.html 을 이용해서 구현합니다. asccidoctor의 docinfo 라는 속성이 있는데 adoc 파일에 html 파일을 주입 할 수 있게 해주는 속성입니다.

전체적인 directory 구조는 아래와 같습니다.
![image-20230513200534716](../../images/2023-05-13-[Spring] SpringRestDocs 를 활용한 RESTful API 확인(2)/image-20230513200534716.png)

**docinfo.html**

```html
<script>
    function ready(callbackFunc) {
        if (document.readyState !== 'loading') {
            // Document is already ready, call the callback directly
            callbackFunc();
        } else if (document.addEventListener) {
            // All modern browsers to register DOMContentLoaded
            document.addEventListener('DOMContentLoaded', callbackFunc);
        } else {
            // Old IE browsers
            document.attachEvent('onreadystatechange', function () {
                if (document.readyState === 'complete') {
                    callbackFunc();
                }
            });
        }
    }

    function openPopup(event) {

        const target = event.target;
        if (target.className !== "popup") {
            return;
        }

        event.preventDefault();
        const screenX = event.screenX;
        const screenY = event.screenY;
        window.open(target.href, target.text, `left=${screenX}, top=${screenY}, width=500, height=600, status=no, menubar=no, toolbar=no, resizable=no`);
    }

    ready(function () {
        const el = document.getElementById("content");
        el.addEventListener("click", event => openPopup(event), false);
    });
</script>
```

클릭 시 팝업으로 띄울 수 있도록 js 문법을 적용했습니다.

**index.adoc**

```
= Rest Docs Practice Application API Document
:doctype: book
:source-highlighter: highlightjs
:toc: left
:toclevels: 2
:sectlinks:
:docinfo: shared-head

include::member.adoc[]
include::post.adoc[]
```

기존 옵션에 `:docinfo: shared-head` 만 추가합니다.

**authority.adoc**

```
:doctype: book
:icons: font

[[authority]]
include::{snippets}/authority/custom-response-fields-authority.adoc[]
```

띄울 팝업 창입니다. `[[authority]]` 는 HTML 로 변환 시 `div id='authority'` 를 붙게 합니다.

## MemberControllerTest.login() 

```java
@Test
    void login() throws Exception {
        final MemberResponse memberResponse = new MemberResponse("memberName", "title", "content", Authority.USER);
        when(memberService.login(any())).thenReturn(memberResponse);

        this.mockMvc.perform(post("/members/login")
                        .content("{\"memberName\": \"memberName\", \"password\": \"password\"}") // Updated JSON payload
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andDo(document("member-login",
                        requestFields(
                                fieldWithPath("memberName").description("Member memberName"),
                                fieldWithPath("password").description("Member password")
                        ),
                        responseFields(
                                fieldWithPath("memberName").description("Member memberName"),
                                fieldWithPath("password").description("Member password"),
                                fieldWithPath("email").description("Member email"),
                                fieldWithPath("authority").description("link:common/authority.html[Enum,role=\"popup\"]")
                        )
                ));
    }
```

​	Enum 이 있는 login() 메서드를 수정합니다. description 값으로 `"link:common/authority.html[Enum,role=\"popup\"]")`  를 줍니다. html 로 변환 시 `<td class="tableblock halign-left valign-top"><p class="tableblock"><a href="common/authority.html" class="popup">Enum</a></p></td>` 으로 됩니다.

이제 build 를 하면 main 의 resources 에 다음과 같이 생깁니다.
![image-20230513201233004](../../images/2023-05-13-[Spring] SpringRestDocs 를 활용한 RESTful API 확인(2)/image-20230513201233004.png)



# 마치며

​	이제 제가 원하는 수준까지는 모두 완성되었습니다. 다음 포스팅은 중복 코드를 제거하기 위한 refactoring 을 하겠습니다.

# Ref.

[[10분 테코톡] 승팡, 케이의 REST Docs](https://youtu.be/BoVpTSsTuVQ)

[SpringRestDocs를 SpringBoot에 적용하기](https://taetaetae.github.io/2020/03/08/spring-rest-docs-in-spring-boot/)

[Spring Rest Docs 적용](https://techblog.woowahan.com/2597/)

[API 문서 자동화 - Spring REST Docs 팔아보겠습니다](https://tecoble.techcourse.co.kr/post/2020-08-18-spring-rest-docs/)

[공식 문서](https://docs.spring.io/spring-restdocs/docs/2.0.4.RELEASE/reference/html5/#getting-started-documentation-snippets-invoking-the-service)

\+ 추가 : [Spring REST Docs 적용 및 최적화 하기](https://backtony.github.io/spring/2021-10-15-spring-test-3/) <- 포스팅 시에는 참고하지 않았지만 이후에도 계속 rest docs 를 공부하면서 찾다보니 제일 도움되는 포스팅입니다.