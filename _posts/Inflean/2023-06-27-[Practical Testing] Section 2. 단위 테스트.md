---
categories: "inflearn"
tag: [""]
series: "Practical Testing: 실용적인 테스트 가이드"
series-description: "인프런 우빈님의 'Practical Tesing: 실용적인 테스트 가이드' 강의 내용입니다. 설명이 깔끔하고 목소리가 좋으십니다"
series-link: "https://www.inflearn.com/course/practical-testing-%EC%8B%A4%EC%9A%A9%EC%A0%81%EC%9D%B8-%ED%85%8C%EC%8A%A4%ED%8A%B8-%EA%B0%80%EC%9D%B4%EB%93%9C/dashboard"
teaser: "Practical Testing"
title: "[Practical Testing] Section 2. 단위 테스트"
description: "Practical Testing: 실용적인 테스트 가이드 Section 2 내용입니다."
---

*Section 2 이전은 소개 강의이기 때문에 넣지 않았습니다.*

# 수동 테스트 VS. 자동화된 테스트

코드 : https://github.com/wbluke/practical-testing/tree/lesson2-3

```java
@Test
void add() {
    CafeKiosk cafeKiosk = new CafeKiosk();
    cafeKiosk.add(new Americano());

    System.out.println(">>> 담긴 음료 수 : " + cafeKiosk.getBeverages().size());
    System.out.println(">>> 담긴 음료 : " + cafeKiosk.getBeverages().get(0).getName());
}

/*
>>> 담긴 음료 수 : 1
>>> 담긴 음료 : 아메리카노
*/
```

위 코드를 실행한 결과는 의도대로 잘 나왔습니다. 하지만 해당 테스트는 **수동 테스트**라고 할 수 있습니다.

- 먼저 콘솔에 결과값을 찍어서 사람이 확인합니다. 결국 최종단계에서 사람이 확인해야 해서 휴먼 에러가 발생할 수 있습니다.
- 또한 다른 사람이 이 테스트코드를 봤을 때 뭘 검증하고, 어떤 게 맞는 케이스고 실패하는 케이스인지 알 수 없습니다.

# JUnit5 로 테스트하기

`spring-boot-starter-test` dependency 에 `JUnit5`, `AssertJ` 가 포함되어 있습니다.

​	**단위 테스트란 작은 코드 단위(클래스나 메서드) 를 독립적으로 검증하는 테스트**입니다. 검증 속도가 빠르고 안정적입니다.

> AssertJ
>
> :heavy_check_mark: 테스트 코드 작성을 원활하게 돕는 테스트 라이브러리
> :heavy_check_mark: 풍부한 API, 메서드 체이닝 지원

`CafeKiosk` 에 있는 `add()`, `remove()`, `clear()` 메서드를 `JUnit5` 와 `AssertJ` 를 이용해서 테스트해보겠습니다.

```java
package sample.cafekiosk.unit;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import sample.cafekiosk.unit.beverage.Americano;
import sample.cafekiosk.unit.beverage.Latte;

import static org.assertj.core.api.Assertions.*;
import static org.junit.jupiter.api.Assertions.*;

class CafeKioskTest {

    @Test
    void add_auto_test() {
        CafeKiosk cafeKiosk = new CafeKiosk();
        cafeKiosk.add(new Americano());

        assertThat(cafeKiosk.getBeverages()).hasSize(1);
        assertThat(cafeKiosk.getBeverages().get(0).getName()).isEqualTo("아메리카노");
        
    }
    
    @Test
    void remove() {
        CafeKiosk cafeKiosk = new CafeKiosk();
        Americano americano = new Americano();
        cafeKiosk.add(americano);
        assertThat(cafeKiosk.getBeverages()).hasSize(1);

        cafeKiosk.remove(americano);
        assertThat(cafeKiosk.getBeverages()).isEmpty();
    }

    @Test
    void clear() {
        CafeKiosk cafeKiosk = new CafeKiosk();
        Americano americano = new Americano();
        Latte latte = new Latte();
        cafeKiosk.add(americano);
        cafeKiosk.add(latte);
        assertThat(cafeKiosk.getBeverages()).hasSize(2);

        cafeKiosk.clear();
        assertThat(cafeKiosk.getBeverages()).isEmpty();
    }
}
```

- `.hasSize(1)` : 리스트가 해당 사이즈를 가지고 있는지 검증합니다.
- `.isEmpty()` : 리스트가 비어있는지 검증합니다.

# 테스트 케이스 세분화하기

요구사항 추가

*:heavy_check_mark: 한 종류의 음료 여러 잔을 한번에 담는 기능

:arrow_right: 









