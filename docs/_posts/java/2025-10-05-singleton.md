---
title: "[구현] 싱글톤 객체 구현"
date: 2025-10-05
tags:
  - java
  - singleton
description: "싱글톤 패턴을 적용한 싱글톤 객체"
---

<Header/>

[[toc]]

# 1. 싱글톤 패턴이란?

싱글톤 패턴이란 단 하나의 유일한 객체를 만들기 위한 패턴이다.

객체가 리소스를 많이 차지할 때 (DB연결, 네트워크 통신 등) 굳이 <u>새로 만들지 않고 기존의 인스턴스를 가져와 활용하는 패턴</u>이다.

# 2. 싱글톤 패턴 구현

싱글톤 패턴은 다음 7가지로 구현할 수 있는데 이중 Bill Pugh Solution 으로 구현한다.

> 1. Eager Initialization
> 2. Static block initialization
> 3. Lazy initialization
> 4. Thread safe initialization
> 5. Double-Checked Locking
> 6. Bill Pugh Solution
> 7. Enum 이용

```java
class Singleton {

    private Singleton() {}

    // static 내부 클래스를 이용
    // Holder로 만들어, 클래스가 메모리에 로드되지 않고 getInstance 메서드가 호출되어야 로드됨
    private static class SingleInstanceHolder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return SingleInstanceHolder.INSTANCE;
    }
}
출처: https://inpa.tistory.com/entry/GOF-💠-싱글톤Singleton-패턴-꼼꼼하게-알아보자 [Inpa Dev 👨‍💻:티스토리]
```




# 3. 싱글톤 패턴의 단점

# Ref.

- [싱글톤(Singleton) 패턴 - 꼼꼼하게 알아보자](https://inpa.tistory.com/entry/GOF-%F0%9F%92%A0-%EC%8B%B1%EA%B8%80%ED%86%A4Singleton-%ED%8C%A8%ED%84%B4-%EA%BC%BC%EA%BC%BC%ED%95%98%EA%B2%8C-%EC%95%8C%EC%95%84%EB%B3%B4%EC%9E%90)

<Footer/>
