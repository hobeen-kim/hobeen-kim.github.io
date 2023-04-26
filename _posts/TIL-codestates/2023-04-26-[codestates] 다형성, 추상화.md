---
categories: "TIL-codestates"
tag: [ "codestates", "polymorphism", "abstraction"]
---

<div class="notice--danger">
   four fundamental OOP concepts : Inheritance, Encapsulation, Polymorphism, Abstraction
</div>

<div class="notice--primary">
   앞으로 기본적인 개념에서는 예시를 좀 줄이도록 하겠습니다.
</div>

# 다형성(Polymorphism)

자바 프로그래밍에서 다형성은 **한 타입의 참조 변수를 통해 여러 타입의 객체를 참조할 수 있도록 만든 것**을 의미합니다.

예를 들어 다음과 같습니다.

```java
class Friend {
    ...
}

class BoyFriend extends Friend {
   ...
}

class GirlFriend extends Friend {
    ...
}

public class FriendTest {

    public static void main(String[] args) {
        Friend friend = new Friend(); // 객체 타입과 참조 변수 타입의 일치
        BoyFriend boyfriend = new BoyFriend();
        Friend girlfriend = new GirlFriend(); // 객체 타입과 참조 변수 타입의 불일치
    }
}


```

`Friend girlfriend = new GirlFriend();` 처럼 상위 클래스 타입의 참조 변수로 하위 클래스의 객체를 참조할 수 있습니다.



## 참조 변수 타입 변환

다음과 같이 타입 변환이 일어날 수 있습니다.

```java
...

public class FriendTest {

    public static void main(String[] args) {
        BoyFriend boyFriend = new BoyFriend();
        Friend friend = boyFriend; // BoyFriend 타입은 상위 타입은 Friend 로 변환 가능
        BoyFriend boyFriend2 = (BoyFriend) friend // 상위 타입에서 하위 타입으로 변환은 가능하나 타입 생략 불가능
         
    }
}

```



# instanceof 연산자

`참조_변수 instanceof 타입` 와 같이 선언하고, return 값으로 boolean 을 받습니다.

해당 참조변수가 타입으로 변환이 가능하다는 것을 나타냅니다.

예를 들어 `BoyFriend instanceof Friend` 는 true 를 반환합니다.
하지만 `BoyFriend instanceof GirlFriend` 는 false 입니다.



# 추상화

상속이 하위 클래스를 정의하는데 상위 클래스를 사용하는 것이라고 한다면 추상화는 반대로 **기존 클래스들의 공통적인 요소들을 뽑아서 상위 클래스를 만들어 내는 것**이라고 할 수 있습니다.

## 추상 클래스(abstract)

`abstract`는 주로 클래스와 메서드를 형용하는 키워드로 사용되는데, **메서드 앞에 붙은 경우를 ‘추상 메서드(abstract method)’, 클래스 앞에 붙은 경우를 ‘추상 클래스(abstract class)’**라 각각 부릅니다.

**어떤 클래스에 추상 메서드가 포함되어 있는 경우 해당 클래스는 자동으로 추상 클래스가 됩니다.**

```java
abstract class Animal {
	public String kind;
	public abstract void sound();
}
```

추상클래스의 추상 메서드는 subclass 에서 @overriding 으로 무조건 구현해야 합니다.

이를 통해서 각각의 subclass 는 **각각 상황에 맞는 메서드 구현이 가능**하다는 장점이 있습니다.



## final modifier

final 키워드는  필드, 지역 변수, 클래스 앞에 위치할 수 있으며 그 위치에 따라 그 의미가 조금씩 달라지게 됩니다.

| 위치   | 의미                                      |
| ------ | ----------------------------------------- |
| 클래스 | 변경 또는 확장 불가능한 클래스, 상속 불가 |
| 메서드 | 오버라이딩 불가                           |
| 변수   | 값 변경이 불가한 상수                     |

```java
final class FinalEx { // 확장/상속 불가능한 클래스
	final int x = 1; // 변경되지 않는 상수

	final int getNum() { // 오버라이딩 불가한 메서드
		final int localVar = x; // 상수
		return x;
	}
}
```

즉, 클래스에 선언되면 superclass 로 사용될 수 없고, 메서드에 사용되면 overriding 이 불가능 합니다.



## 인터페이스

인터페이스는 모든 메서드가 추상메서드로 되어 있는 클래스입니다. 또한 내부 필드는 모두 `public static final ` 로 상수만 선언할 수 있습니다.

다음과 같은 구조를 가집니다.

```java
public interface InterfaceEx {
    public static final int rock =  1; // 인터페이스 인스턴스 변수 정의
    final int scissors = 2; // public static 생략
    int paper = 3; // public & final & static 생략

    public abstract String getPlayingNum();
    void call() //public abstract 생략 
}
```

- 생략되는 부분은 컴파일러가 자동으로 추가해줍니다.

### 인터페이스를 사용하는 이유

인터페이스의 가장 큰 장점 중에 하나는 앞서 봤었던 일반적인 인터페이스의 기능처럼 **역할과 구현을 분리**시켜 사용자 입장에서는 **복잡한 구현의 내용 또는 변경과 상관없이 해당 기능을 사용할 수 있다는 점**입니다.

**다음은 인터페이스를 구현하지 않았을 때입니다.**

```java
public class InterfaceExample {
    public static void main(String[] args) {
        User user = new User(); // User 클래스 객체 생성
        user.callProvider(new Provider1()); // Provider 객체 생성 후에 매개변수로 전달
    }
}

class User { 
    // Provider 객체를 매개변수로 받는 callProvider 메서드
    public void callProvider(Provider1 provider) { 
        provider.call();
    }
}

class Provider1 { 
    public void call() {
        System.out.println("Provider1");
    }
}

class Provider2 { 
    public void call() {
        System.out.println("Provider2");
    }
}


```

User 클래스가 callProvider() 메서드를 사용하기 위해 Provider1 이 필요합니다. 이 때 변경이 되어서 Provider2 가 필요하다면 이렇게 변경해야 합니다.

```java
ublic class InterfaceExample {
    public static void main(String[] args) {
        User user = new User(); 
        user.callProvider(new Provider2()); // Provider2 객체 생성 후에 매개변수로 전달
    }
}

class User { 
    // Provider2 로 객체 변경
    public void callProvider(Provider2 provider) { 
        provider.call();
    }
}

...
```

- 이처럼 User 클래스 안에서 Provider2 를 모두 변경해주어야 합니다. 코드가 길면 길수록 변경할 소요는 커집니다.

**인터페이스 사용하는 예시입니다.**

위 같은 문제를 인터페이스를 사용하여 해결할 수 있습니다.

```java
public class Main {
    public static void main(String[] args) {
        User user = new User();
        // 주입되는 값만 변경해주면 된다.
		user.callProvider(new Provider1());
        user.callProvider(new Provider2());
    }
}

class User {
    public void callProvider(Cover cover) { // 매개변수의 다형성 활용
        cover.call();
    }
}

interface Cover {
    void call();
}

class Provider1 implements Cover {
    public void call() {
        System.out.println("Provider1");
    }
}

class Provider2 implements Cover {
    public void call() {
        System.out.println("Provider2");
    }
}

/*출력값
Provider1
Provider2
*/
```

위와 같이 main 메서드에서 User 객체의 `user.callProvider()` 메서드의 매개변수만 변경해줌으로써 Provider1, Provider2 를 모두 사용할 수 있습니다.