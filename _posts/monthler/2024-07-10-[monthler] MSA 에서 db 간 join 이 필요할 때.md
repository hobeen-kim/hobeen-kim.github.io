---
categories: "monthler"
tag: ["MSA"]
title: "[monthler] MSA 에서 db 간 join 이 필요할 때"
description: "msa 에서 DB 가 분리됐을 떄 각 db 간 조건식을 처리하는 방법입니다."
---

# 1. 문제 상황

User 테이블과 Accommodation 테이블이 각각 다른 DB 에 있을 때 각 테이블 간 조건식이 필요한 경우입니다. 테이블은 아래와 같습니다.

- User 테이블
  - user_id
  - email
  - role (ADMIN, USER)
  - password
- Accommodation 테이블
  - accommodation_id
  - content (숙소 설명)
  - type (숙소 타입)
  - user_id (숙소 주인, User 테이블의 FK)

이때 숙소 주인의 이메일이 "test@gmail.com" 인 숙소를 검색하려고 합니다. 만약 DB 가 분리되어 있지 않다면 아래와 같이 쿼리문을 작성하면 됩니다.

```sql
select * from accommodation
join user on user.user_id = accommodation.user_id
where user.email = "test@gmail.com"
```

하지만 accommodation 과 user 가 다른 테이블이면 join 문을 사용하지 못합니다.

# 2. 해결 방법

  Accommodation 테이블에 user_id 와 email 을 넣는 방법도 있지만 정규화가 안되고(제3정규형) user 서비스에서 email 업데이트 시 변경사항 전파가 힘듭니다.

Accommodation 에서 아는 건 user_id 뿐입니다. 따라서 accommodation 서비스에서 email 을 통한 질의가 들어오면 user 서비스에게 다시 email 로 user_id 를 받아야 합니다.

1. 클라이언트에서 email = "test@gmail.com" 인 숙소 주인의 숙소를 accomomdation 서비스에 질의

2. accommodation 서비스는 email = "test@gmail.com" 인 user 를 user 서비스에 질의

3. user 서비스는 해당 유저의 user_id 를 반환 (ex. 100)

4. accommodation 서비스는 user_id = 1 로 질의하여 accommodaiton 결과 반환

   - ```mysql
     select * from accommodation
     where user_id = 100
     ```

# 3. 아직 생각 중인 문제

user 에 성별(gender) 가 추가되었다고 가정하겠습니다. 아래와 같은 조건을 질의한다고 하면,

- accommodation 중 주인의 성별이 남자인 숙소

기존 해결방법으로는 먼저 user 서비스에 성별이 남자인 user 의 id 를 모두 받아와야 합니다. user 가 10억명이라고 가정할 때 남자는 5억명이므로 5억명의  user_id 를 모두 받아와야 합니다. 즉 row 수가 많을 때 카디널리티(cadinality) 가 매우 낮은 성별, 나이 등을 조건으로 검색하려면 해결하기 힘들어집니다.

이 문제는 해결할 필요가 있을 때 다시 생각해보겠습니다.

