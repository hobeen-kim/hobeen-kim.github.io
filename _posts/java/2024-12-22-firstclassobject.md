---
categories: "java"
tag: ["일급객체", "일급함수", "일급 컬렉션"]
title: "[JAVA] 일급객체, 일급함수, 일급 컬렉션 정리 (With Java)"
description: "자바에서 살펴보는 일급객체, 일급함수, 일급 컬렉션에 대한 정리입니다."
---

# 0. 일급객체란

**일급 객체**는 일급객체(First-class Object)란 다른 객체들에 일반적으로 적용 가능한 연산을 모두 지원하는 객체입니다. 프로그래밍에서 특정 객체가 다음 조건을 만족하는 경우를 말합니다

1. 변수에 할당할 수 있다.
2. 함수의 인자로 전달할 수 있다.
3. 함수의 반환 값으로 사용할 수 있다.

Java의 **모든 객체**는 이 조건을 만족하기 때문에 "일급 객체"로 간주될 수 있습니다. 

# 1. 일급 함수

**일급 함수**는 위의 일급 객체의 조건을 모두 만족하는 **함수**를 의미합니다. 하지만 <u>Java에서 함수는 일급 객체로 간주되지 않습니다.</u> Java의 함수는 메서드로 정의되며, 메서드 자체는 독립적으로 변수에 할당하거나 전달할 수 없기 때문입니다.

즉, 함수가 변수처럼 다뤄질 수 있는 경우를 말하며, 이는 함수형 프로그래밍 언어에서 중요한 특징입니다.

## 1.1 일급 함수 (일급객체) 를 구분하는 이유

일급 함수를 구분하는 이유는 일급함수를 사용해서 얻는 여러 가지 특성과 이점이 있기 떄문입니다.

### 1.1.1 일급 함수의 특성

1. 고차 함수(Higher-Order Function) 생성

   **고차 함수** 란, 다른 함수를 인자로 받거나, 함수를 반환하는 함수를 의미합니다. 모든 고차 함수는 일급 함수이지만, 모든 일급 함수가 고차 함수는 아닙니다. 대표적으로 파이썬에서는 map() 함수가 있습니다.

   ```
   def apply_operation(func, x, y):
       return func(x, y)
   
   def add(x, y):
       return x + y
   
   def subtract(x, y):
       return x - y
   
   result_add = apply_operation(add, 5, 3)
   result_subtract = apply_operation(subtract, 5, 3)
   
   print(result_add)       # 출력: 8
   print(result_subtract)  # 출력: 2
   ```

2. 콜백 함수 사용

   **콜백 함수**란, 다른 함수에 인자로 전달되어 나중에 호출되는 함수를 의미합니다. 주로 이벤트 처리나 비동기 작업에서 사용됩니다.

   ```
   def perform_operation(x, y, callback):
       result = callback(x, y)
       print(f"The result is: {result}")
   
   def multiply(x, y):
       return x * y
   
   def power(x, y):
       return x ** y
   
   perform_operation(2, 3, multiply)  # 출력: The result is: 6
   perform_operation(2, 3, power)     # 출력: The result is: 8
   ```

일급 객체와 일급 함수의 개념은 주로 함수형 프로그래밍에서 강조되며, 이를 통해 코드의 모듈성과 유연성을 증가시킬 수 있습니다. 여기에 더하여, 이러한 개념들이 코드를 간결하게 작성하고 높은 추상화 수준에서 문제를 해결하는 데 도움을 줍니다.

### 1.1.2 일급객체의 이점

1. 가독성 및 모듈성 향상

     함수형 프로그래밍에서는 작은 함수들을 조합하여 복잡한 동작을 수행하는데, 이는 코드의 가독성을 향상하게 시키는 주된 원인 중 하나입니다. 작은 함수는 특정 기능을 수행하며, 각 함수는 자체적으로 명확하고 이해하기 쉬운 역할을 담당합니다. 이를 통해 코드를 읽거나 유지보수하는 데 더 적은 노력이 들며, 개발자는 코드의 각 부분을 독립적으로 이해할 수 있습니다. 

     또한, 작은 함수들을 조합하여 큰 함수나 기능을 만들 수 있어 모듈성이 향상됩니다. 각 함수가 잘 정의되어 있고 독립적으로 동작하기 때문에 코드의 재사용성도 증가하며, 새로운 기능을 추가하거나 수정할 때 기존 코드에 영향을 덜 미칩니다.

2. 테스트 용이성

     작은 함수들은 독립적으로 테스트하기가 쉽습니다. 각 함수는 특정 기능을 수행하고, 함수의 입력과 출력이 명확하게 정의되어 있으므로 단위 테스트를 통해 각 함수의 동작을 쉽게 확인할 수 있습니다. 이는 코드의 안정성과 신뢰성을 높이는 데 기여합니다.

     단위 테스트를 통해 각 함수를 검증하면, 전체 시스템의 동작을 이해하고 예측하는 데 도움이 됩니다. 또한, 함수형 프로그래밍에서는 순수 함수를 중심으로 작성되기 때문에 같은 입력에 대해서는 항상 같은 결과를 반환하므로 테스트의 일관성이 확보됩니다.

3. 병렬 및 분산 프로그래밍

     함수형 프로그래밍은 상태 변경이 없고 부작용이 적은 순수 함수를 강조합니다. 이 특성은 병렬 및 분산 환경에서 더 효과적으로 코드를 작성할 수 있게 만듭니다. 왜냐하면 부작용이 없는 함수들은 여러 스레드나 프로세스에서 병렬로 실행되어도 안전하기 때문입니다.

     또한, 함수형 프로그래밍은 불변성(immutability)을 강조하므로 여러 스레드나 프로세스 간의 데이터 공유가 더 쉬워집니다. 상태가 변경되지 않으면서 데이터를 공유할 수 있으므로 병렬성을 향상하고 데드락(deadlock)이나 경합 조건(race condition)과 같은 문제를 방지할 수 있습니다.

4. 디버깅 용이성

     함수형 프로그래밍에서는 상태 변화가 제한되어 있습니다. 함수가 순수하면서 부작용이 없다면, 특정 입력에 대한 출력이 항상 같이 유지됩니다. 이는 디버깅을 더 쉽게 만듭니다. 같은 입력에 대해서 항상 같은 결과가 나오기 때문에 디버깅 시점에서 예측할 수 있는 동작을 보장할 수 있습니다.

     또한, 함수형 프로그래밍에서는 각 함수가 독립적으로 동작하므로 오류가 발생했을 때 해당 함수로 디버깅하거나 수정하기가 쉽습니다. 모듈성이 높고 부작용이 적은 코드는 오류를 추적하고 해결하는 데 도움이 됩니다.

이러한 이점들은 함수형 프로그래밍이 복잡한 시스템을 다루고 유지보수하는 데 특히 유용하게 만듭니다.



## 1.2 자바에서 일급함수 사용하기

자바는 함수형 프로그래밍 패러다임을 완벽히 지원하지는 않지만, **Java 8**부터 람다 표현식과 함수형 인터페이스의 도입으로 함수형 프로그래밍 스타일을 사용할 수 있게 되었습니다. 이를 활용해 함수나 객체를 일급 객체처럼 다루는 방식이 가능합니다.

### 1.2.1 람다 함수

람다 표현식은 익명 함수를 정의하는 방식으로, 이를 변수에 할당하거나 다른 함수의 인자로 전달할 수 있습니다.

```java
import java.util.function.Consumer;

public class LambdaExample {
    public static void main(String[] args) {
        // 1. 람다식을 변수에 할당
        Consumer<String> greet = (name) -> System.out.println("Hello, " + name);
        greet.accept("Alice"); // Hello, Alice

        // 2. 람다식을 함수의 인자로 전달
        execute(greet, "Bob"); // Hello, Bob

        // 3. 람다식을 반환값으로 사용
        Consumer<String> farewell = createFarewell();
        farewell.accept("Charlie"); // Goodbye, Charlie
    }

    public static void execute(Consumer<String> action, String name) {
        action.accept(name); // 전달받은 함수를 실행
    }

    public static Consumer<String> createFarewell() {
        return (name) -> System.out.println("Goodbye, " + name);
    }
}
```

### 1.2.2 Function

`java.util.function.Function`은 입력값을 받아서 변환하여 출력값을 반환하는 함수형 인터페이스입니다.

```java
import java.util.function.Function;

public class FunctionExample {
    public static void main(String[] args) {
        // 1. Function 인터페이스를 사용해 람다식 정의
        Function<Integer, Integer> square = (x) -> x * x;

        // 2. 함수 실행
        System.out.println(square.apply(5)); // 25

        // 3. Function을 함수의 인자로 전달
        executeFunction(square, 10); // Result: 100

        // 4. Function을 반환하는 고차 함수
        Function<Integer, Integer> doubler = createMultiplier(2);
        System.out.println(doubler.apply(3)); // 6
    }

    public static void executeFunction(Function<Integer, Integer> func, Integer value) {
        Integer result = func.apply(value);
        System.out.println("Result: " + result);
    }

    public static Function<Integer, Integer> createMultiplier(int factor) {
        return (x) -> x * factor;
    }
}

```

### 1.2.3 비동기 콜백

Java에서 비동기 처리는 일반적으로 `CompletableFuture`를 사용하거나 `Runnable` 인터페이스를 활용합니다. 콜백 함수도 람다식으로 전달하여 일급 함수처럼 사용할 수 있습니다.

```java
import java.util.concurrent.CompletableFuture;

public class AsyncCallbackExample {
    public static void main(String[] args) {
        // 1. 비동기 작업 정의
        performAsyncTask(result -> {
            // 콜백 함수 실행
            System.out.println("Callback received: " + result);
        });

        // 메인 스레드 계속 실행
        System.out.println("Main thread is not blocked.");
    }

    public static void performAsyncTask(Callback callback) {
        // 비동기 작업 실행
        CompletableFuture.runAsync(() -> {
            try {
                Thread.sleep(1000); // 작업 시뮬레이션
                callback.onComplete("Task completed!");
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
    }

    // 콜백 함수용 인터페이스 정의
    @FunctionalInterface
    interface Callback {
        void onComplete(String result);
    }
}
```

# 2. 일급 컬렉션

**일급 컬렉션**은 프로그래밍에서 컬렉션(List, Set, Map 등)을 객체로 추상화하여 다루는 설계 패턴입니다. 이는 컬렉션을 객체로 래핑(wrapping)하여 컬렉션과 관련된 로직을 한 곳에 캡슐화함으로써 코드의 **가독성, 유지보수성, 확장성**을 높이기 위한 방법입니다.

일급 컬렉션은 다음과 같은 특징을 가지고 있습니다:

1. 컬렉션을 감싸는 클래스
   - 컬렉션(List, Set, Map 등) 자체를 하나의 객체로 간주하여 별도의 클래스로 정의합니다.
   - 컬렉션 외에 추가적인 멤버 변수는 존재하지 않아야 합니다.
2. 컬렉션과 관련된 모든 로직을 캡슐화
   - 컬렉션과 관련된 검증, 계산, 정렬, 필터링 등의 로직은 컬렉션을 감싸는 클래스 내부에서 처리합니다.
   - 외부에서는 컬렉션을 직접 다루지 않으며, 캡슐화된 메서드를 통해서만 조작합니다.
3. 불변성(Immutability) 유지
   - 컬렉션을 수정하지 않고, 수정된 컬렉션을 새롭게 반환하는 방식으로 처리합니다.
   - 이를 통해 상태를 안전하게 유지합니다.

## 2.1 일급 컬렉션의 이점

1. 캡슐화
   - 컬렉션의 내부 구조를 외부에서 알 필요가 없으며, 관련 로직을 컬렉션 클래스 내부로 한정시킬 수 있습니다.
2. 비즈니스 로직의 응집도 향상
   - 컬렉션 관련 로직이 한 곳에 집중되어, 코드 가독성과 유지보수성이 높아집니다.
3. 데이터 무결성 보장
   - 불변성을 유지하거나 유효성 검사를 통해 컬렉션의 상태를 보호할 수 있습니다.
4. 디버깅 및 테스트 용이성
   - 컬렉션을 감싸는 객체 단위로 테스트를 작성할 수 있어 디버깅과 테스트가 더 쉬워집니다.

## 2.2 예시

### 2.2.1 일반적인 List

```java
import java.util.ArrayList;
import java.util.List;

public class SimpleListExample {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>();
        names.add("Alice");
        names.add("Bob");
        names.add("Charlie");

        // 비즈니스 로직이 여기저기 분산됨
        if (names.contains("Alice")) {
            System.out.println("Alice is in the list.");
        }
    }
}
```

### 2.2.2 일급 컬렉션으로 리팩토링

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Names {
    private final List<String> names;

    // 생성자에서 초기화 및 불변성 유지
    public Names(List<String> names) {
        this.names = new ArrayList<>(names);
    }

    // 컬렉션 반환 시에도 불변성 유지
    public List<String> getNames() {
        return Collections.unmodifiableList(names);
    }

    // 컬렉션 관련 로직 캡슐화
    public boolean contains(String name) {
        return names.contains(name);
    }

    public Names add(String name) {
        List<String> newNames = new ArrayList<>(names);
        newNames.add(name);
        return new Names(newNames);
    }

    public int size() {
        return names.size();
    }
}
```

아래는 일급컬랙션 사용입니다.

```java
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        Names names = new Names(Arrays.asList("Alice", "Bob"));

        System.out.println("Contains Alice: " + names.contains("Alice")); // true
        System.out.println("Size: " + names.size()); // 2

        // 불변성 유지: 새 객체 반환
        Names updatedNames = names.add("Charlie");

        System.out.println("Updated Names Size: " + updatedNames.size()); // 3
        System.out.println("Original Names Size: " + names.size()); // 2
    }
}
```



# Ref.

1. https://incodom.kr/%EC%9D%BC%EA%B8%89_%ED%95%A8%EC%88%98#h_4ab516cde093ae69d94e576543849d8d






