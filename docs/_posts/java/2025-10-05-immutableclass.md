---
title: "[구현] 불변 클래스 구현"
date: 2025-10-05
tags:
  - java
  - immutable
description: "불변 클래스를 구현해보자"
---

<Header/>

[[toc]]

# 1. 불변 클래스란?

불변 클래스는 한 번 생성되면 객체 내부의 상태(값)를 변경할 수 없는 클래스를 말한다. 불변 클래스의 인스턴스는 생성 시점에 상태가 결정된 후 객체가 메모리에서 사라질 때까지 절대 변하지 않으며, 상태 변경이 필요할 때는 완전히 새로운 객체를 생성해야 한다. 

자바의 String 클래스가 대표적인 불변 클래스이며, 이러한 특성은 코드의 안정성과 신뢰성을 높여 다중 스레드 환경에서 동기화 문제를 예방하는 데 도움이 된다.

# 2. 불변 클래스 구현

1. final 클래스로 만들어서 상속되지 않게 한다.
2. 모든 필드를 private 과 final 로 만든다.
3. setter 를 만들지 않는다.
4. 만약 필드가 List 와 같이 가변 객체이면 생성자와 getter 에서 defensive copy (방어적 복사)를 사용한다.

```java
final class Item {
  private final String name;
  private final List<String> categories;
  
  public Person(String name, List<String> categories) {
    this.name = name;
    this.categories = new ArrayList<>(categories); //defensive copy
  }
  
  public String getName() {
    return name;
  }
  
  public List<String> getCategories() {
    return new ArrayList<>(categories); //defensive copy
  }
}
```

<Footer/>
