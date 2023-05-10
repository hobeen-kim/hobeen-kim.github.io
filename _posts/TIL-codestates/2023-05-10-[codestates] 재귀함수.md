---
categories: "TIL-codestates"
tag: [ "recursion"]
---



# 재귀 (recursion) 함수

재귀함수는 문제를 동일한 구조의 더 작은 반복적인 문제로 나누어서 해결하는 방법입니다. 다음과 같은 모양입니다.

```java
public void recursion() {
  System.out.println("This is");
  System.out.println("recursion!");
  recursion();
}
```

recursion() 안에서 출력문 출력 이후 recursion() 이 실행되고, 그 안에서 출력문 출력 이후 recurstion() 이 실행되고... 를 반복합니다. 출력문이 무한 출력되겠죠.

## 특징

**장점**

- 불필요한 반복문을 사용하지 않아 코드가 간결해지고 수정이 용이합니다.
- 변수를 여러 개 사용할 필요가 없습니다.

**단점**

- 코드의 흐름을 직관적으로 파악하기 어렵습니다.

- 반복해서 호출되는 메서드의 지역변수, 매개변수, 반환값을 모두 stack 영역에 저장하게 됩니다. 이러한 과정은 반복문에 비해 더 많은 메모리를 사용하게 됩니다.

- 메서드 호출과 복귀를 위한 context-switching 비용이 발생합니다.

  - context-switching 은 cpu 가 프로세스 간 스위칭을 할 때 발생합니다. 프로세스에 직전까지 실행한 내용을 PCB 에 저장하고, 다음 프로세스의 PCB 를 읽고 작업을 실행하는 겁니다.
  - 하지만 여기서 context-switching 은 프로세스와 CPU 영역에서 일어나는 context-switching 이라기보다는, 일반적인 표현이라고 생각하면 됩니다. 스택 영역에 메서드가 계속 저장되고 복귀하면서 다시 호출되는 과정이죠.

  

## 예제  구구단, 팩토리얼

재귀 함수는 예제로 보는 게 제일 편합니다.

**구구단**

```java
public void Gugudan(int level, int count) {
  if(count > 9) {
    return;
  }
  System.out.printf("%d x %d = %d\n", level, count, level*count);
  Gugudan(level, ++count);
}
```

- count 가 9 가 되면 종료됩니다.

**팩토리얼**

```java
public int Factorial(int number) {
  if(number <= 1) {
    return 1;
  }
  return number * Factorial(number - 1);
}
```

- number 가 1 이 되면 1을 리턴하면서 종료합니다.