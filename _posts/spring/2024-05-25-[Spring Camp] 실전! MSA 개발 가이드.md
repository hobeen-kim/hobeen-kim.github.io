---
categories: "spring"
tag: ["msa", "spring"]
series: "SpringCamp2024"
title: "[Spring Camp] 실전! MSA 개발 가이드"
description: "스프링 캠프 - MSA 개발 가이드 발표 내용입니다."
---

  서버가 나눠져있더라도 DB 가 연결되어있으면 마이크로 서비스라고 할 수 없습니다. 

  API 로 요청할 때 DB 가 나눠져있으면 DB 콜이 많아집니다. 따라서 참조하는 데이터의 속성을 고민해볼 필요가 있습니다. 자주 참조하면서 잘 변경하지 않는 정보(사용자, 역할, 권한, 메뉴 ...)는 데이터를 복제해서 공통 서비스에서 가지고 있을 수도 있습니다. 이때 사용하기 좋은 형태로 바꿔서 저장해야 합니다. 

  A -> B 서비스를 요청할 때 API 콜이 많으면 REST API 의 N+1 Problem 이 발생합니다. 따라서 모아서 한번에 조회할 수 있도록 해야 합니다. 또한 병렬 조회를 생각할 수도 있지만, 순간적으로 큰 부하가 생길 수 있기 때문에 꼭 필요한 경우에만 일괄 조회를 병렬로 실행해야 합니다. 잘 변하지 않는 데이터라면 **로컬 캐시**(EH 캐시)를 사용할 수 있습니다.

  가장 좋은 방식은 일괄 조회 & cache 방식이며, 일괄 조회만 구현해도 잘 사용할 수 있습니다.

# ACID

- Atomicity(원자성) : DB Rollback 이 안됨

  - A -> B 서비스를 호출할 때, A 서비스에서 쓰기에 실패하면 명시적으로 B 서비스의 생성된 데이터를 삭제하는 API 를 날려야 함.
  - 하지만 API 를 날리는 도중 B 서비스가 죽으면 두 데이터가 안맞게 됨
  - API 가 실패했을 때 자동으로 재시도하는 로직은 안티 패턴임! 대부분의 경우는 상대 서버가 죽었을 경우가 높기 때문에 확실하게 죽이는 재시도가 될 뿐임
  - 이벤트로 재시도를 할 수 있음. 다만 여러 번 전달될 수도 있음. 따라서 action 이 2번 일어나도 동일한 결과가 일어나도록 해야 함
  - 네트워크에서 쓰기작업을 할 때 멱등성이 보장되도록 해야 함
  - 긴 트랙잭션 나누기
    - 실패해도 전체를 취소할 필요가 없다면 이벤트로 분리
    - 취소할 수 없는 쓰기는 이벤트로 분리
  - 서비스 경계 변경
    - 너무 구현하기 힘들면 서비스를 합치거나 경계를 변경해도 괜찮음

- Isolation(독립성) : Read Uncommitted 라서 쓰기 시 제3자가 데이터 조회 시 순간적으로 데이터가 일치하지 않을 수 있음.

  - 보통 문제가 되지는 않지만, 동기화가 필요하면 Application Lock 을 사용할 수 있음

  

