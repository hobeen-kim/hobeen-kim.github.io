---
categories: "codestates"
tag: ["service", "Mapper"]
---

# Mapper 클래스

​	Mapper 클래스는 DTO 와 객체를 서로 변환해주는 클래스입니다. 해당 클래스는 컨트롤러와 서비스 레이어의 강한 결합을 분리하고 종속적이지 않게 하지 위해 사용합니다.  예를 들어 아래와 같은 **컨트롤러**가 있다고 보겠습니다.

```java
@PostMapping
public ResponseEntity<Void> createMember(MemberPostDto memberPostDto) {
        MemberResponseDto = memberService.create(memberPostDto);
    	return ResponseEntity.created(URI.create(String.format("/members/%s", responseDto.getId()))).build();
    }
```

memberService 는 memberPostDto 를 그대로 받아서 MemberResponseDto 를 반환하고 있습니다. 위의 경우 문제는 다음과 같습니다.

- Service가 받고 싶은 포맷(Parameter)이 Controller에 종속적이게 됩니다. 즉, Service가 Controller 패키지에 의존하게 됩니다.
- Service 레이어가 모듈로 분리되는 경우 해당 Type을 사용할 수 없게 됩니다.

대신 아래와 같이 변경할 수 있습니다.

```java
@PostMapping
public ResponseEntity<Void> createMember(MemberPostDto memberPostDto) {
        MemberResponseDto = memberService.create(memberPostDto.toServiceDto());
    	return ResponseEntity.created(URI.create(String.format("/members/%s", responseDto.getId()))).build();
    }
```

`memberPostDto.toServiceDto()` 를 통해 service 가 원하는 형태로 변경해서 인자로 넘깁니다. 이 부분을 ServiceDto 로 변경해도 되고, 엔티티로 변경해도 됩니다. 만약 엔티티로 변경하게 되면 불완전한 엔티티를 Service 파라미터로 받게 되고, `Service` 메소드별로 원하는 포맷이 달라지는 경우 결국 DTO로 분리될 것이기 때문에 잘 생각해보는 게 좋을 듯합니다.

## Custom Mapper 클래스 만들기

​	DTO 클래스 안에서가 아닌 Mapper 클래스를 직접만들어서 Dto 를 변환한다면 아래와 같이 만들 수 있습니다.

```java
@Component
public class MemberMapper {
		//MemberPostDto를 Member로 변환
    public Member memberPostDtoToMember(MemberPostDto memberPostDto) {
        return new Member(0L,
                memberPostDto.getEmail(), 
                memberPostDto.getName(), 
                memberPostDto.getPhone());
    }

		//MemberPatchDto를 Member로 변환
    public Member memberPatchDtoToMember(MemberPatchDto memberPatchDto) {
        return new Member(memberPatchDto.getMemberId(),
                null, 
                memberPatchDto.getName(), 
                memberPatchDto.getPhone());
    }

    //Member를 MemberResponseDto로 변환
    public MemberResponseDto memberToMemberResponseDto(Member member) {
        return new MemberResponseDto(member.getMemberId(),
                member.getEmail(), 
                member.getName(), 
                member.getPhone());
    }
}
```

이 때 스프링빈으로 등록해서 객체가 여러 번 생성되는 일을 방지하도록 합니다.

## MapStruct를 이용한 Mapper 자동 생성

​	MapStruct 를 통해서 Mapper 클래스를 깔끔하게 만들 수 있습니다. 먼저 아래와 같이 의존성을 추가해줍니다.

```
dependencies {
	...
	...
	implementation 'org.mapstruct:mapstruct:1.4.2.Final'
	annotationProcessor 'org.mapstruct:mapstruct-processor:1.4.2.Final'
}
```

그리고 MemberController에서 사용하는 DTO 클래스(MemberPostDto, MemberPatchDto, MemberResponseDto)와 Member 클래스 간의 변환 기능을 제공하는 매퍼(Mapper) 인터페이스를 정의해야 합니다.

```java
@Mapper(componentModel = "spring")
public interface MemberMapper {
    Member memberPostDtoToMember(MemberPostDto memberPostDto);
    Member memberPatchDtoToMember(MemberPatchDto memberPatchDto);
    MemberResponseDto memberToMemberResponseDto(Member member);
}
```

이제  MemberMapper 인터페이스의 구현 클래스는 **Gradle의 build task를 실행하면 자동으로 생성**됩니다. 아래와 같이 구현됩니다.

```java
@Component
public class MemberMapperImpl implements MemberMapper {
    public MemberMapperImpl() {
    }

    public Member memberPostDtoToMember(MemberPostDto memberPostDto) {
        if (memberPostDto == null) {
            return null;
        } else {
            Member member = new Member();
            member.setEmail(memberPostDto.getEmail());
            member.setName(memberPostDto.getName());
            member.setPhone(memberPostDto.getPhone());
            return member;
        }
    }

    public Member memberPatchDtoToMember(MemberPatchDto memberPatchDto) {
        if (memberPatchDto == null) {
            return null;
        } else {
            Member member = new Member();
            member.setMemberId(memberPatchDto.getMemberId());
            member.setName(memberPatchDto.getName());
            member.setPhone(memberPatchDto.getPhone());
            return member;
        }
    }

    public MemberResponseDto memberToMemberResponseDto(Member member) {
        if (member == null) {
            return null;
        } else {
            long memberId = 0L;
            String email = null;
            String name = null;
            String phone = null;
            memberId = member.getMemberId();
            email = member.getEmail();
            name = member.getName();
            phone = member.getPhone();
            MemberResponseDto memberResponseDto = new MemberResponseDto(memberId, email, name, phone);
            return memberResponseDto;
        }
    }
}
```

