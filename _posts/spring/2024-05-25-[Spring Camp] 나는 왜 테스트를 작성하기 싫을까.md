---
categories: "spring"
tag: ["test", "spring"]
series: "SpringCamp2024"
title: "[Spring Camp] 나는 왜 테스트를 작성하기 싫을까"
description: "스프링 캠프 - 테스트 작성에 대한 내용입니다."
---

# 0. 문제점

  테스트를 위해 Fixture Monkey 를 사용했음(네이버에서 개발한 테스트 모듈). 객체에 대한 생성이 쉬워짐

**문제점**

- 간헐적으로 테스트가 깨짐
- 스펙을 추가할 때마다 DomainFixture 를 작성해줘야 함

**회고**

1. Fixture Monkey 를 사용해 낮아진 테스트 작성 비용과 넓어진 테스트 범위
2. 주문서 특성상 모든 코드를 테스트해야 한다라는 생각
3. DominFixture 유지보수 비용을 생각 못함

-> 테스트 이득과 비용에 대해 진지하게 고민하게 되는 계기

테스트를 작성하기 싫은 이유는 비용(작성비용, 유지보수 비용)이 확장 비용보다 크기 때문입니다. 비용을 결정하는 요소는,

1. 작성하는 로직이 어떤 요청이 필요한지(Given)
2. 작성하는 로직은 어떤 결과가 나와야 하는지 (Then)

제거할 수 있는 테스트 비용

1. (Given) 테스트를 복잡하게 작성하려 한다. -> 작성비용
2. (Then) 하나의 테스트에서 많은 검증을 하려한다. -> 유지보수 비용
   - ex. 기능 테스트에서 리스트 결과값이 2개 이상 나오도록 해야 하나? 작동하는지만 검증하면 되는데?
   - 계좌의 잔액을 비교하려면 assert(accout, mockAccount) 보다는 assert(account.amount, 3000) 과 같이 필요한 것만 비교해야 함. aacount 가 확장되면 결국 깨지 것이기 떄문임.

# 테스트 비용 줄이기

1. 픽스쳐 몽키 사용하기
2. 최대한 간단한 경우의 수 테스트 하기