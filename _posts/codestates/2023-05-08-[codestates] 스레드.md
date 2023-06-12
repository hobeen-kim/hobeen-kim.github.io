---
categories: "codestates"
tag: [ "thread"]
---

# Thread

thread 는 하나의 코드 실행 흐름으로, 데이터와 어플리케이션이 확보한 자원으로 소스 코드를 실행합니다.

이러한 thread 가 여러 개 있으면 Multi-thread processing 이라고 합니다. 여러 개의 thread 를 가지면 여러  thread 가 동시에 작업을 수행할 수 있으며, 이를 멀티 스레딩(Multi-Threading) 이라고 합니다. Multi-Threading 은 하나의 어플리케이션 내에서 여러 작업을 동시에 수행하는 멀티 태스킹을 구현하는 데 핵심적인 역할을 합니다.

## Thread 생성

Thread 는 Runnable 인터페이스와 Thread 클래스로 구현할 수 있습니다.

**Runnable**

```java
public class ThreadExample1 {
    public static void main(String[] args) {
        Runnable task1 = new ThreadTask1();
        Thread thread1 = new Thread(task1);

        thread1.start();
    }
}

class ThreadTask1 implements Runnable {
    public void run() {
        for (int i = 0; i < 100; i++) {
            System.out.print("#");
        }
    }
}
```

- Runnable 을 구현하는 ThreadTask1 클래스를 정의한 뒤 인스턴스를 만들어줍니다.
- 해당 인스턴스를 Thread 인스턴스의 생성자의 parameter 로 넣어줍니다.
- `thread1.start()` 로 thread 를 시작해줍니다.

다음과 같이 익명함수인 람다식으로 대체할 수 있습니다.

```java
public class ThreadExample1 {
    public static void main(String[] args) {
        Runnable task1 = () -> {
            for (int i = 0; i < 10; i++) {
                System.out.print("#");
            }
        };
        Thread thread1 = new Thread(task1);
 
        thread1.start();
    }
}
```

**Thread**

runnable 과 비슷합니다.

```java
public class ThreadExample2 {
    public static void main(String[] args) {

        ThreadTask2 thread2 = new ThreadTask2();

        thread2.start();

    }
}

class ThreadTask2 extends Thread {
    public void run() {
        for (int i = 0; i < 100; i++) {
            System.out.print("#");
        }
    }
}
```

- Thread 를 상속받는 ThreadTask2 클래스를 만듭니다.
- 해당 클래스의 인스턴스를 만들어주고 `.start()` 를 사용하여 Thread 를 시작합니다.

다음과 같이 익명함수로 대체할 수 있습니다.

```java
public class ThreadExample2 {
    public static void main(String[] args) {

        Thread thread2 = new Thread(()->{
        	for (int i = 0; i < 100; i++) {
            	System.out.print("#");
        	}
        });

        thread2.start();

    }
}
```

더 축약하면 아래와 같습니다. 생성과 함께 `start()` 로 시작합니다.

```java
public class ThreadExample2 {
    public static void main(String[] args) {

        new Thread(()->{
        	for (int i = 0; i < 100; i++) {
            	System.out.print("#");
        	}
        })
		.start();

    }
}
```



## Thread 이름, 주소값 얻기

Thread 이름은 다음과 같이 설정합니다. (`.setName()` / `.getName()`)

```java
public class ThreadExample2 {
    public static void main(String[] args) {

        Thread thread3 = new Thread(() -> 
                System.out.println("Get Thread Name")
        );
        
        thread3.start();
        thread3.setName("thread 3")
        System.out.println("thread3.getName() = " + thread3.getName());

        thread3.start();

    }
}
```

Thread 의 주소값을 얻는 `currentThread()` 는 static method 입니다.

```java
public class ThreadExample2 {
    public static void main(String[] args) {

        Thread thread3 = new Thread(() -> 
                System.out.println(Thread.currentThread())
        );
        
        thread3.start();
    }
}

//Thread[Thread-0,5,main]
```



## Thread 동기화

thread 가 같은 데이터를 공유하게 되면 문제가 발생할 수 있습니다. 프로세스의 데이터는 Heap, Stack, Data, Code 로 나눌 수 있는데, 개별 프로세스가 가지는 영역은 Stack 입니다. 

Heap 은 객체나 인스턴스의 변수, Dta 는 클래스의 정적 변수, Code 는 컴파일된 코드입니다. 이러한 영역은 모든 thread 가 공유됩니다.

다음과 같이 확인할 수 있습니다.

```java

public class Main {
    public static void main(String[] args) throws InterruptedException {

        Test test = new Test();

        Thread thread1 = new Thread(() ->{
                for(int i = 0; i < 10000; i++){
                    test.add();
                }
            }
        );

        Thread thread2 =  new Thread(() ->{
                for(int i = 0; i < 10000; i++){
                    test.sub();
                }
            }
        );

        thread1.start();
        thread2.start();

        thread1.join();
        thread2.join();

        System.out.println(test.sum);
    }
}

class Test{
    int sum = 10;

    void add() {
        int temp = this.sum;
        temp++;
        this.sum = temp;
    }

    void sub() {
        int temp = this.sum;
        temp--;
        this.sum = temp;
    }
}
```

- Thread1 과 Thread2 가 함께 동작하면서 test 인스턴스의 sum 이라는 멤버변수를 공유합니다. 
- 따라서 sum 값은 10 이 아닌 다른 값을 가지게 됩니다. (ex. -943, 123 등등...)

### 동기화 문제 해결

동기화 문제를 해결하기 위해선 먼저 임계 영역(Critical section) 과 락(Lock) 을 알아야 합니다. 임계 영역은 임계 영역은 오로지 하나의 스레드만 코드를 실행할 수 있는 코드 영역을 의미하며, 락은 임계 영역을 포함하고 있는 객체에 접근할 수 있는 권한을 의미합니다.

즉, 임계 영역에는 락을 얻은 뒤 1개의 스레드만 들어갈 수 있습니다.

이는 `synchronized` 키워드로 제어할 수 있습니다.

```java

public class Main {
    public static void main(String[] args) throws InterruptedException {

        Test test = new Test();

        Thread thread1 = new Thread(() ->{
                for(int i = 0; i < 10000; i++){
                    test.add();
                }
            }
        );

        Thread thread2 =  new Thread(() ->{
                for(int i = 0; i < 10000; i++){
                    test.sub();
                }
            }
        );

        thread1.start();
        thread2.start();

        thread1.join();
        thread2.join();

        System.out.println(test.sum);
    }
}

class Test{
    int sum = 10;

    void synchronized add() {
        int temp = this.sum;
        temp++;
        this.sum = temp;
    }

    void synchronized sub() {
        int temp = this.sum;
        temp--;
        this.sum = temp;
    }
}
```

`synchronized` 를 통해 메서드 전체를 임계 영역으로 지정하면 메서드가 호출되었을 때, 메서드를 실행할 thread 는 메서드가 포함된 객체의 락을 얻습니다.

## Thread 메서드

- `interrupt()` : `sleep()`, `wait()`, `join()`에 의해 `일시 정지` 상태에 있는 스레드들을 `실행 대기` 상태로 복귀시킵니다.

- `yield()` : 다른 스레드에 실행을 양보합니다.

  ```java
  public void run() {
  		while (true) {
  				if (example) {
  						...
  				}
  				else Thread.yield();
  		}
  }
  ```

  - example 이 false 일 때 while 반복문이 무의미하므로 `yield()` 를 통해 실행을 양보합니다.

- `join()` : `join()`은 특정 스레드가 작업하는 동안에 자신을 `일시 중지` 상태로 만드는 상태 제어 메서드입니다.

- `wait(), notify()` : 스레드 간 협업에 사용됩니다.

  - 스레드A와 스레드B가 공유 객체를 두고 협업하는 상황을 가정합니다.

  ```java
  public class ThreadExample5 {
      public static void main(String[] args) {
          WorkObject sharedObject = new WorkObject();
  
          ThreadA threadA = new ThreadA(sharedObject);
          ThreadB threadB = new ThreadB(sharedObject);
  
          threadA.start();
          threadB.start();
      }
  }
  
  class WorkObject {
      public synchronized void methodA() {
          System.out.println("ThreadA의 methodA Working");
          notify();
          try { wait(); } catch(Exception e) {}
      }
  
      public synchronized void methodB() {
          System.out.println("ThreadB의 methodB Working");
          notify();
          try { wait(); } catch(Exception e) {}
      }
  }
  
  class ThreadA extends Thread {
      private WorkObject workObject;
  
      public ThreadA(WorkObject workObject) {
          this.workObject = workObject;
      }
  
      public void run() {
          for(int i = 0; i < 10; i++) {
              workObject.methodA();
          }
      }
  }
  
  class ThreadB extends Thread {
      private WorkObject workObject;
  
      public ThreadB(WorkObject workObject) {
          this.workObject = workObject;
      }
  
      public void run() {
          for(int i = 0; i < 10; i++) {
              workObject.methodB();
          }
      }
  }
  ```

  - A 가 작업을 완료하면 `notify()` 를 호출하여 B 를 호출합니다. A 는 이후 `wait()` 를 호출하여 자기 자신을 일시정지 상태로 만듭니다.
  - B 도 마찬가지로 작업을 실행한 후 `notify()` 로 A 를 호출하고 `wait()` 로 일시정지됩니다.
  - 이 과정의 반복으로 두 thread 는 공유 객체에 대해 서로 배타적으로 접근할 수 있습니다.