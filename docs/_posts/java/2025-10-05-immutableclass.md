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

## 1. 불변 클래스란?

**불변(Immutable) 클래스는 한 번 생성되면 객체 내부의 상태(값)를 변경할 수 없는 클래스**를 말한다. 인스턴스는 생성 시점에 모든 상태가 결정되고, 그 이후에는 값이 절대 바뀌지 않는다. 상태 변경이 필요하다면 기존 인스턴스를 수정하는 대신 새 인스턴스를 새로 만들어 반환하는 방식으로 처리한다.

자바에서 가장 대표적인 불변 클래스는 String 이다. String 은 문자열을 바꾼다는 개념이라고 느껴지는 여러 연산이 실제로는 새 문자열 객체를 만들어 반환한다.

불변 객체는 다음과 같은 장점이 있다.

- **Thread-safe** : 상태가 변하지 않으니 동기화(synchronized) 없이도 공유하기가 쉽다. 
- **예측 가능성** : 객체가 어디서 어떻게 변했는지 추적할 필요가 없어서 디버깅이 편하다. 
- **캐싱/공유에 유리** : 같은 값이면 재사용하기 쉽고, 해시 기반 컬렉션(HashMap, HashSet)에서도 안전하게 쓸 수 있다. 
- **방어적 프로그래밍에 도움**: 외부에서 몰래 값을 바꾸는 부작용(side effect)을 차단한다.

반대로 단점도 있다.

- 상태 변경이 잦은 경우 객체 생성 비용과 GC 부담이 증가할 수 있다.
- 설계가 조금 더 번거롭고(방어적 복사 등), 컬렉션을 다룰 때 신경 쓸 포인트가 늘어난다.

# 2. 불변 클래스 구현

불변 클래스를 구현하는 기본 규칙은 다음과 같다.

- 클래스를 final로 선언해 상속을 막는다. 
  - 상속이 가능하면 하위 클래스가 내부 상태를 변경 가능한 형태로 확장해버릴 수 있다. 
- 모든 필드를 private final로 선언한다. 
- setter를 제공하지 않는다. 
- 필드가 List, Map, 배열처럼 가변(mutable) 객체라면, 
  - 생성자에서 defensive copy(방어적 복사)
  - getter에서도 defensive copy 를 적용해 외부에서 내부 상태를 바꾸지 못하게 한다.
- 내부에서 사용하는 가변 필드는 가능하면 불변 컬렉션으로 감싸서 보관한다.
- equals/hashCode/toString 을 구현해 값 객체로의 사용성을 높인다.


```java
public final class Item {
private final String name;
private final List<String> categories;

    public Item(String name, List<String> categories) {
        this.name = Objects.requireNonNull(name, "name must not be null");
        Objects.requireNonNull(categories, "categories must not be null");

        // defensive copy + (선택) unmodifiable로 감싸 내부 보관
        this.categories = Collections.unmodifiableList(new ArrayList<>(categories));
    }

    public String getName() {
        return name;
    }

    public List<String> getCategories() {
        // 내부에서 unmodifiable로 보관하고 있다면 그대로 반환해도 안전
        return categories;
    }

    // "변경"이 필요하면 새 객체를 만들어 반환
    public Item withName(String newName) {
        return new Item(newName, this.categories);
    }

    public Item withAddedCategory(String category) {
        List<String> next = new ArrayList<>(this.categories);
        next.add(category);
        return new Item(this.name, next);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Item)) return false;
        Item item = (Item) o;
        return name.equals(item.name) && categories.equals(item.categories);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, categories);
    }

    @Override
    public String toString() {
        return "Item{name='" + name + "', categories=" + categories + '}';
    }
}
```

## 2.1 getter 에서도 방어적 복사가 필요한 이유

불변 객체에서 getter 를 방어적 복사하지 않으면 필드의 객체 내부가 변경될 수도 있다. 예를 들어 내부 필드를 아래처럼 그냥 반환하면,

```java
public List<String> getCategories() {
return categories; // 위험!
}
```


외부에서 이렇게 바꿀 수 있다.

```java
Item item = new Item("keyboard", List.of("input", "pc"));
item.getCategories().add("hacked"); // 내부 리스트가 mutable이면 상태가 깨짐
```


그래서 두 가지 전략 중 하나를 선택한다.

**전략 A - getter에서 매번 복사해서 반환**

`return new ArrayList<>(categories);`

단, 호출이 잦으면 복사 비용이 생긴다.

**전략 B - 생성자에서 불변 컬렉션으로 만들어 보관하고 그대로 반환**

`Collections.unmodifiableList(new ArrayList<>(categories))`

훨씬 흔하게 쓰는 방식이다. (반환 비용이 거의 없음). 위 예시는 B 를 적용했다.

> **주의**
>
>  Collections.unmodifiableList(...)는 진짜 불변 리스트를 만드는 게 아니라 수정 메서드 호출을 막는 뷰(view)다. 그래서 원본 리스트를 그대로 감싸면 안 되고, 반드시 new ArrayList<>(...) 같은 복사본을 감싼 뒤 보관해야 한다.

# 3. 불변 클래스 구현 시 자주 놓치는 부분

불변 클래스 구현 시 자주 놓치는 패턴들이다.

## 3.1 배열 필드 (byte[], int[])는 특히 위험

배열은 대표적인 가변 객체라서 방어적 복사가 필수다.

```java

public final class Token {
private final byte[] value;

    public Token(byte[] value) {
        this.value = value.clone(); // defensive copy
    }
    
    public byte[] getValue() {
        return value.clone(); // defensive copy
    }
}
```

## 3.2 가변 객체를 필드로 들고 있으면 깊은 불변이 아니다

  예를 들어 LocalDateTime 같은 건 불변이라 괜찮지만, Date(java.util.Date)처럼 가변인 객체는 그대로 들고 있으면 위험하다. 이런 경우도 방어적 복사가 필요하다.

```java
public final class Event {
private final java.util.Date when;

    public Event(Date when) {
        this.when = new java.util.Date(when.getTime());
    }
    
    public Date getWhen() {
        return new java.util.Date(when.getTime());
    }
}
```

## 3.3. 컬렉션 안의 요소가 가변일 때

List<Person>에서 Person이 mutable이면, 리스트 자체는 못 바꿔도 요소는 바뀔 수 있다.

- 얕은 불변(shallow immutability): 컬렉션 구조만 안 바뀜 (추가/삭제 불가)
- 깊은 불변(deep immutability): 요소 객체까지 불변

깊은 불변이 필요하다면, 요소 타입도 불변으로 설계하거나, 요소를 복사해서 들고 있어야 한다.

# 4. 마무리

불변 클래스는 단순히 final을 붙이는 수준이 아니라, 외부에서 내부 상태에 접근해 바꿀 수 있는 모든 경로를 차단하는 것이 핵심이다.
특히 컬렉션/배열/가변 타입 필드에서는 방어적 복사를 습관처럼 적용해야 한다.

정리하면,

- final class
- private final 필드
- setter 없음
- 가변 필드면 복사해서 보관 + 불변 형태로 노출
- 변경이 필요하면 withXxx()처럼 새 객체 반환

<Footer/>