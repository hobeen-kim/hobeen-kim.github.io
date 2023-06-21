---
categories: "codestates"
tag: ["JDBC", "Pagination", "paging"]
---

# 요구사항

​	요구사항은 아래와 같습니다.

- `member` 의 memberId, email, name, phone 을 페이징해서 반환합니다.
- 이 때 파라미터는 `page` (페이지 번호), `size` (페이지 사이즈) 입니다.

```json
{
    "data": [
        {
            "memberId": 20,
						"email": "hgd20@gmail.com",
            "name": "홍길동20",
            "phone": "010-2020-2020"
        },
        {
            "memberId": 19,
            "email": "hgd19@gmail.com",
            "name": "홍길동19",
            "phone": "010-1919-1919"
        },
        {
            "memberId": 18,
            "email": "hgd18@gmail.com",
            "name": "홍길동18",
            "phone": "010-1818-1818"
        },
        {
            "memberId": 17,
            "email": "hgd17@gmail.com",
            "name": "홍길동17",
            "phone": "010-1717-1717"
        },
        {
            "memberId": 16,
            "email": "hgd16@gmail.com",
            "name": "홍길동16",
            "phone": "010-1616-1616"
        },
    ],
    "pageInfo": {
        "page": 1,
        "size": 5,
        "totalElements": 20,
        "totalPages": 4
    }
}
```

# Pagination

## Repository

`CrudRepository` 를 상속하는 스프링 `Repository` 인터페이스는 다음과 같은 메서드 서치를 할 수 있습니다.

```java
Page<Member> findAllByOrderByMemberIdDesc(Pageable pageable);
```

- `findAll` : 모두 찾는다.
- `ByOrderByMemberId` : `memberId` 를 기준으로 정렬합니다.
- `Desc` 내림차순 (최신순) 으로 정렬합니다.
- `Pageable` : `Pageable` 타입을 반드시 파라미터로 넘겨야 합니다. 해당 `Pageable` 을 기준으로 페이징합니다.
- 이 때 반환타입은 `Page<Member>` 입니다.

## Service

```java
public Page<Member> findMembers(int page, int size) {
    PageRequest pageRequest = PageRequest.of(page, size);
    return memberRepository.findAllByOrderByMemberIdDesc(pageRequest);
}
```

**`PageRequest` 은 `Pageable` 의 구현체입니다.** `PageRequest.of(page, size)` 를 통해 성성하며, 세번째 인자로 `Sort` 객체를 넘겨서 정렬조건을 설정할 수도 있습니다. `page` 는 페이지 번호로, 0 부터 시작합니다. `size` 는 페이지 당 데이터 개수입니다.

이때 반환타입은 `Page<Member>` 입니다.

## Controller

```java
@GetMapping
public ResponseEntity getMembers(@RequestParam(value = "page", defaultValue = "1") int page,
                                 @RequestParam(value = "size", defaultValue = "10") int size) {

    Page<Member> members = memberService.findMembers(page - 1, size);
    List<MemberResponseDto> response = mapper.membersToMemberResponseDtos(members.getContent());

    MemberResponsePageDto responsePage = new MemberResponsePageDto<>(response, page, size, members);

    return new ResponseEntity<>(responsePage, HttpStatus.OK);
}
```

- 파라미터로 page, size 를 받습니다.
- `memberService.findMembers(page - 1, size);` 를 통해서 `Page<Member>` 를 반환받습니다. 
- `members.getContent()` 를 하면 리스트 형태의 `List<Member>` 가 반환됩니다.
- 해당 `List<Member>` 를 `MemberResponsePageDto` 에 넣어서 반환합니다.

## MemberResponsePageDto

```java
package com.codestates.member.dto;

import lombok.Getter;
import org.springframework.data.domain.Page;

@Getter
public class MemberResponsePageDto<T> {

    T data;
    PageInfo pageInfo;

    public MemberResponsePageDto(T data, int curPage, int size, Page page) {
        this.data = data;
        this.pageInfo = PageInfo.of(curPage, size, page);
    }

    @Getter
    static class PageInfo{
        int page;
        int size;
        long totalElements;
        int totalPages;

        private PageInfo(int page, int size, long totalElements, int totalPages) {
            this.page = page;
            this.size = size;
            this.totalElements = totalElements;
            this.totalPages = totalPages;
        }

        static PageInfo of(int curPage, int size, Page page){
            return new PageInfo(curPage, size, page.getTotalElements(), page.getTotalPages());
        }
    }
}
```

**이거 작성하다가 실수한 부분이 있는데, HTTP 로 반환하기 위해서는 `@Getter` 가 필수입니다.**

`Page` 클래스는 `page.getTotalElements()`, `page.getTotalPages()`로 리스트 내 데이터의 개수(`member` 의 개수), 총 페이지 수를 얻을 수 있습니다.