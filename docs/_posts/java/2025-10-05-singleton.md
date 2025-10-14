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

싱글톤 패턴은 다음 7가지로 구현할 수 있는데 이중 Bill Pugh Solution 으로 구현해본다.

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
```

# 3. static class 로딩과 초기화

> “클래스가 메모리에 로드되지 않고, getInstance() 메서드가 호출되어야 로드됨”

이 말은 곧 **`SingleInstanceHolder`라는 내부 static 클래스는, 외부 클래스(Singleton)가 로드될 때 즉시 메모리에 올라가지 않는다**는 뜻이다. 즉, `Singleton` 클래스 자체는 프로그램이 실행되면서 로드되지만,  그 안의 내부 클래스 `SingleInstanceHolder`는 `getInstance()` 메서드가 처음 호출되는 순간에야 JVM이 로드하고 초기화한다.

## 3.1 자바의 클래스 로딩 과정

JVM에서 클래스가 메모리에 올라가는 과정은 보통 이렇게 이루어진다.

1. **Loading** : .class 파일을 읽어 메타데이터를 메모리에 올림
2. **Linking** : 상수 풀, static 필드, 메서드 시그니처 등을 확인 및 준비
3. **Initialization** : static 필드 초기화 및 static 블록 실행

즉, 클래스가 **"로딩되고 초기화된다"**는 건 그 클래스의 static 필드나 static 블록이 실행될 준비가 되었다는 뜻이다.

## 3.2 Singleton 클래스 초기화 과정

```java
class Singleton {
    private Singleton() {}

    private static class SingleInstanceHolder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return SingleInstanceHolder.INSTANCE;
    }
}
```

1. 프로그램이 시작해서 `Singleton` 클래스를 처음 참조할 때, JVM은 `Singleton` 클래스를 **로드 및 초기화**함. 하지만 이 시점에는 **`SingleInstanceHolder` 클래스는 로드되지 않음**
2. 누군가 `Singleton.getInstance()`를 호출하는 순간, JVM은 내부 static 클래스인 `SingleInstanceHolder`를 **처음으로 참조**하게 됨.
3. 그때 **`SingleInstanceHolder` 클래스가 로드 및 초기화되고** 그 안의 static 필드 `INSTANCE = new Singleton()`이 실행됨

즉, `INSTANCE` 객체는 **getInstance()가 처음 호출될 때 단 한 번 생성**된다.

## ## 3.3 이 패턴의 장점

- **Lazy Initialization** : `Singleton` 인스턴스는 필요할 때까지 생성되지 않음 (처음부터 메모리를 차지하지 않음)
- **Thread Safe** : JVM의 클래스 로더 초기화 과정은 thread-safe하므로 별도의 synchronized 처리가 필요 없음
- **성능 우수** : 불필요한 동기화 비용 없이 지연 초기화를 구현 가능

# Ref.

- [싱글톤(Singleton) 패턴 - 꼼꼼하게 알아보자](https://inpa.tistory.com/entry/GOF-%F0%9F%92%A0-%EC%8B%B1%EA%B8%80%ED%86%A4Singleton-%ED%8C%A8%ED%84%B4-%EA%BC%BC%EA%BC%BC%ED%95%98%EA%B2%8C-%EC%95%8C%EC%95%84%EB%B3%B4%EC%9E%90)

<Footer/>
