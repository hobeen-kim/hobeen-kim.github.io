---
categories: "spring"
tag: ["coroutine", "spring"]
series: "SpringCamp2024"
title: "[Spring Camp] Spring Coroutine in action"
description: "스프링 캠프 - 코루틴 내용입니다."
---

# 1. Coroutine

- CoroutineScope? 
  - 코루틴을 시작하려면 CoroutineScope 으로 감싸야 합니다. 새로운 코루틴을 실행할 수 있는 범위를 말합니다.
  - 비동기 스레드 실행은 structured progamming 을 망칩니다. 하지만 비동기가 필요한 경우가 있습니다.
  - Structured Concrrency 는 각 스레드의 실행 후 부모 스레드로 돌아오는 것입니다.
  - 발생되는 오류도 손실되지 않고 부모 스레드로 전파 됩니다.
- Builder
  - launch : 현재 스레드를 차단하지 않고 새 코루틴을 비동기로 실행
  - async : 반환되는 타입이 Deferred 로, 실행된 결과를 전달받음.await 로 받음
  - runBlocking : 새 코루틴을 실행하고 완료될 때까지 현재 스레드를 차단하는 Scope
- Suspend
  - delay : 일시 정지 후 필요한 지점에서 스레들르 할당하여 재실행
  - Suspension Point 를 통해 일시 중단 시점이 컴파일 시점에 표시됨.
