---
categories: "monthler"
tag: ["querydsl", "query", "native"]
title: "[monthler] querydsl vs native query 속도 간단 비교"
description: "프로젝트 간 발생한 db 조회 속도저하 관련 확인입니다."
---

# 문제 상황

  admin 페이지에서 프로그램 목록을 불러오는데 <u>속도 저하가 발생. 이전에는 300ms 이하였다면 변경 후 800ms 이상이 되었습니다.</u>

**Repo 에 정의된 이전 쿼리메서드 (native)**

```java
@Query(
            "SELECT distinct p.* FROM program p " +
                    "LEFT JOIN program_hashtag h on p.program_id = h.program_id " +
                    "WHERE p.deleted_at IS NULL AND (:title IS NULL OR p.title LIKE %:title%) "+
                    "AND p.published_at IS NULL ",

            nativeQuery = true,
            countQuery = "SELECT count(distinct p.program_id) FROM program p " +
                    "LEFT join program_hashtag h on p.program_id = h.program_id " +
                    "WHERE p.deleted_at IS NULL AND (:title IS NULL OR p.title LIKE %:title%) " +
                    "AND p.published_at IS NULL "
    )

    fun findAllByTitleContainsAndNotPublishedForAdmin(title: String?, pageable: Pageable): Page<Program>
```

**변경된 쿼리메서드 (queryDsl)**

```java
var result = queryFactory
            .selectDistinct(program)
            .from(program)
            .leftJoin(program.adminAuthorities, adminAuthority)
            .where(
                adminIsPublishedAt(filter),
                partnerFilter(userId),
                keywordFilter(keyword),
            )
            .orderBy(*adminSortProgramRefined(order, by).toTypedArray())
            .offset(pageable.offset)
            .limit(pageable.pageSize.toLong())
            .fetch()
```

# 해결

## 추론 1 : 쿼리문 변경

  주요한 변경사항은 `LEFT JOIN program_hashtag h on p.program_id = h.program_id` 이 없어지고 `LEFT JOIN admin_authority aa on p.program_id = aa.program_id` 이 새로 생겼습니다.

  하지만 이전 쿼리에 있던 program_hashtag 을 넣어도 쿼리문 속도는 변경되지 않았습니다.

## 추론 2 : querydsl 이 만드는 쿼리문이 다름

**navtive query**

```
SELECT
        distinct p.* 
    FROM
        program p 
    LEFT JOIN
        program_hashtag h 
            on p.program_id = h.program_id 
    WHERE
        p.deleted_at IS NULL 
        AND (
            NULL IS NULL 
            OR p.title LIKE NULL
        )  
    order by
        p.program_id desc limit 20

```

**querydsl**

```
select
        distinct program0_.program_id as program_1_27_,
        program0_.created_at as created_2_27_,
        program0_.updated_at as updated_3_27_,
        program0_.activity_end_date as activity4_27_,
        program0_.activity_start_date as activity5_27_,
        program0_.announcement_at as announce6_27_,
        program0_.announcement_text as announce7_27_,
        program0_.apply_url as apply_ur8_27_,
        program0_.created_user_id as created37_27_,
        program0_.deleted_at as deleted_9_27_,
        program0_.detail_text as detail_10_27_,
        program0_.first_published_at as first_p11_27_,
        program0_.is_full_subsidy as is_full12_27_,
        program0_.is_global as is_glob13_27_,
        program0_.is_notification as is_noti14_27_,
        program0_.is_published as is_publ15_27_,
        program0_.main_text as main_te16_27_,
        program0_.manager_email as manager17_27_,
        program0_.manager_phone as manager18_27_,
        program0_.max_activity_day as max_act19_27_,
        program0_.max_per_team as max_per20_27_,
        program0_.meta_data_keywords as meta_da21_27_,
        program0_.min_activity_day as min_act22_27_,
        program0_.min_per_team as min_per23_27_,
        program0_.notice_end_at as notice_24_27_,
        program0_.notice_start_at as notice_25_27_,
        program0_.notice_url as notice_26_27_,
        program0_.person_number as person_27_27_,
        program0_.possible_child as possibl28_27_,
        program0_.published_at as publish29_27_,
        program0_.published_reserve_at as publish30_27_,
        program0_.sigg_adm_code as sigg_ad31_27_,
        program0_.team_number as team_nu32_27_,
        program0_.thumbnail as thumbna33_27_,
        program0_.title as title34_27_,
        program0_.total_subsidy as total_s35_27_,
        program0_.view_cnt as view_cn36_27_ 
    from
        program program0_ 
    left outer join
        admin_authority adminautho1_ 
            on program0_.program_id=adminautho1_.program_id 
            and (
                adminautho1_.deleted_at is null
            ) 
    where
        (
            program0_.deleted_at is null
        ) 
    order by
        program0_.program_id desc limit 20
```

querydsl 이 컬럼명을 명시적으로 했다는 것 외에는 차이점이 없습니다. left outer join 이 조금 다르지만 같게 맞춰도 속도 차이는 여전했습니다. 실행계획 상으로도 둘다 type = ref, index 로 같았고 나머지 컬럼도 같았습니다. (아직 인덱싱 전이라 type = ALL 인듯)

## 추론 3 : queryDSL 이 느림

native query 를 사용하는 이유 중 하나가 속도때문이라고 들어서, queryDSL 을 native 로 변경해봤습니다.

```java
@Query(
        "SELECT distinct p.* FROM program p " +
                "LEFT JOIN admin_authority aa on p.program_id = aa.program_id " +
                "WHERE p.deleted_at IS NULL " +
                "AND (:title IS NULL OR p.title LIKE %:title%) " +
                "AND (:userId IS NULL OR aa.user_id = :userId) " +
                "AND (:isPublished IS NULL OR p.is_published = :isPublished) ",
        nativeQuery = true,
        countQuery = "SELECT count(distinct p.program_id) FROM program p " +
                "LEFT JOIN admin_authority aa on p.program_id = aa.program_id " +
                "WHERE p.deleted_at IS NULL " +
                "AND (:title IS NULL OR p.title LIKE %:title%) " +
                "AND (:userId IS NULL OR aa.user_id = :userId) " +
                "AND (:isPublished IS NULL OR p.is_published = :isPublished) ",
    )
    fun findProgramsForAdminPage2(userId: Long?, title: String?, isPublished: Int?, pageable: Pageable): Page<Program>
```

그랬더니 바로 응답속도가 개선되었습니다. 

그래서 querydsl 이 2배정도 느린가... 하고 찾아봤는데 이런 글을 봤습니다.

https://www.inflearn.com/questions/154102/querydsl%EC%99%80-jdbctemplate-%EC%9D%98-%EC%84%B1%EB%8A%A5-%EB%B9%84%EA%B5%90-%EC%A7%88%EB%AC%B8%EC%9E%85%EB%8B%88%EB%8B%A4

영한님이 올려주신 글인데 대부분의 경우 성능 차이는 DB 의 문제라고 합니다. 제 케이스가 예외라고 생각은 안하기 때문에 다시 비교해보기로 했습니다.

# 추론 4 및 결론

전체적인 querydsl 입니다.

```java
//sort 에서 order by 와 desc, asc 를 가져오기
        var result = queryFactory
            .selectDistinct(program)
            .from(program)
            .leftJoin(program.adminAuthorities, adminAuthority)
            .where(
                adminIsPublishedAt(filter),
                partnerFilter(userId),
                keywordFilter(keyword),
            )
            .orderBy(*adminSortProgramRefined(order, by).toTypedArray())
            .offset(pageable.offset)
            .limit(pageable.pageSize.toLong())
            .fetch()

        val count = queryFactory.selectDistinct(program)
            .from(program)
            .leftJoin(program.adminAuthorities, adminAuthority)
            .where(
                adminIsPublishedAt(filter),
                partnerFilter(userId),
                keywordFilter(keyword),
            )
            .fetch()


        return PageImpl(result, pageable, count.size.toLong())
```

result 를 만드는 쿼리는 문제없었는데, 문제는 count 쿼리였습니다. 비슷한 쿼리를 복붙하느라 못봤는데 전체 programs 를 들고 온 후 개수를 세는 로직이었습니다. 당연히 program 을 한번 더 들고 오니까 전체적인 쿼리문이 느릴 수밖에 없었습니다. 1번만 get 하면 될걸 2번 get 하니까요.

```java
val count = queryFactory
            .select(program.countDistinct())
            .from(program)
            .leftJoin(program.adminAuthorities, adminAuthority)
            .where(
                adminIsPublishedAt(filter),
                partnerFilter(userId),
                keywordFilter(keyword),
            )
            .fetchOne()
```

count 쿼리문은 위와 같이 고쳤습니다. 그랬더니 속도가 native query 랑 같게 나왔습니다.

