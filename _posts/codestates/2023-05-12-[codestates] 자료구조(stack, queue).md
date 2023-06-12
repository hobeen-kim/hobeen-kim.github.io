---
categories: "codestates"
tag: [ "stack", "queue"]
---

# Stack

Stack 은 데이터를 순서대로 쌓는 자료 구조입니다. Stack 은 LIFO(Last In First Out) 으로, 나중에 들어온 데이터를 먼저 꺼낼 수 있습니다. Stack 에 데이터를 넣는 것을 push, 꺼내는 것을 pop 이라고 합니다. 따라서 stack 은 하나의 입출력 방향을 가지고 있습니다.

**Stack 의 장점**

1. 삽입과 삭제가 빠릅니다.

   스택은 LIFO구조이기 때문에 삽입, 삭제는 항상 스택 위에서 이루어집니다. 따라서 데이터의 위치를 변경할 필요가 없습니다. 

2. 자바는 Stack 을 기본 모듈로 제공합니다.

   ```java
   Stack<Integer> stack = new Stack<>();
   
   stack.push(1);
   stack.push(2);
   
   System.out.println(stack.pop()); //2
   System.out.println(stack.pop()); //1
   ```

**Stack 의 단점**

1. 크기 제한이 없습니다.

   스택은 크기 제한이 없어 메모리 사용량이 불필요하게 증가될 수 있습니다. 이를 위해서 스택의 크기를 미리 정해놓거나 동적으로 조절해야 합니다. 방법은 아래와 같습니다.

   ```java
   import java.util.Stack;
   
   //사이즈를 동적으로 변경해주는 custom Stack 클래스입니다.
   class DynamicSizeStack<E> extends Stack<E> {
       private int maxSize;
   
       public DynamicSizeStack() {
           super();
       }
   
       public void setMaxSize(int maxSize) {
           this.maxSize = maxSize;
       }
   
       public int getMaxSize() {
           return maxSize;
       }
   
       @Override
       public E push(E item) {
           if (size() < maxSize) {
               return super.push(item);
           } else {
               System.out.println("Stack is full. Cannot push more items.");
               return null;
           }
       }
   }
   
   public class Main {
       public static void main(String[] args) {
           DynamicSizeStack<Integer> stack = new DynamicSizeStack<>();
   
           // 사이즈를 정해줍니다.
           stack.setMaxSize(3);
           stack.push(1);
           stack.push(2);
           stack.push(3);
   
           // 크기가 3 이 초과되므로 무시됩니다.
           stack.push(4);
   
           // 사이즈를 늘립니다. (동적으로 변경 가능)
           stack.setMaxSize(4);
           //이제 정상적으로 저장됩니다.
           stack.push(4); 
   
           System.out.println(stack.pop()); //4
           System.out.println(stack.pop()); //3
           System.out.println(stack.pop()); //2
           System.out.println(stack.pop()); //1
       }
   }
   ```

2. Stack 클래스는 Vector 클래스를 상속받아 구현되어 있어, 크기를 동적으로 조정하지 않습니다. (Java 한정)

   스택에 저장되는 데이터의 개수가 배열의 크기를 초과하면 새로운 배열을 할당하고 기존 데이터를 복사합니다. 크기는 최초 10 에서 초과할 때마다 2배로 늘어납니다. 크기가 자주 변하면 그만큼 배열의 복사가 잦으므로 다른 자료 구조를 사용하는 것이 효율적일 수 있습니다.

   ```java
   //Vector 의 capacityIncrement 필드가 크기 초과 시 늘어나는 길이입니다. 기본 생성자에서 0 으로 지정됩니다.
   //0 이하의 값이면 2배씩 늘어납니다.
   
   /**
    * The amount by which the capacity of the vector is automatically
    * incremented when its size becomes greater than its capacity.  If
    * the capacity increment is less than or equal to zero, the capacity
    * of the vector is doubled each time it needs to grow.
    */
   protected int capacityIncrement;
   ```

3. Stack 클래스는 Vector 클래스를 상속받아 구현되어 있어, 중간에 데이터 삽입, 삭제가 가능합니다.

   하지만 이러한 구현 방식은 스택의 의도된 동작을 방해할 수 있습니다.

ArrayList 를 활용하여 custom Stack 클래스를 만들 수도 있습니다. 물론 Stack 클래스를 사용하면 구현하는 시간을 절약할 수 있지만요. 요는, **자료구조는 자료를 다루는 구조 그 자체를 뜻하며, 구현하는 방식에는 제약이 없다는 것입니다.**



# Queue

Queue 는 Stack 과 반대되는 개념으로, 선입선출(FIFO, First In, Last Out) 구조입니다. Queue 에서 데이터를 넣는 것을 enqueue, 꺼내는 것을 dequeue 라고 합니다. 넣는 방향과 꺼내는 방향이 다른 두개의 입출력 방향을 가집니다. 아래와 같이 사용합니다.

```java
Queue<Integer> queue = new LinkedList<>();

queue.add(1);
queue.add(2);
queue.offer(3);
queue.offer(4);

queue.peek()//1

queue.poll();//1
queue.poll();//2
queue.poll();//3
queue.poll();//4
```

- `add()` 와 `offer()` 메서드는 제일 뒤에 추가한다는 건 똑같으나, 크기가 가득 찬 queue 에서 `add()` 는 `IllegalStateException` 을 던지고, `offer()` 은 false 를 반환합니다. (e.g. `ArrayBlockingQueue` 클래스를 사용할 때)



**Queue 의 장점**

1. 자료를 먼저 넣은 순서대로 데이터를 꺼내서 처리할 수 있습니다.

   이러한 자료 구조의 특징으로 처리해야 할 작업이 여러 개일 경우, 효율적인 처리가 가능합니다. 예를 들어, 프린터의 인쇄 요청을 순서대로 처리하거나 채팅 시스템에서 메시지를 보내는 순서를 결정하는 경우 등이 있습니다.

2. 삽입과 삭제에서 다른 자료구조에 비해 빠릅니다.

   Queue 에서 삽입 연산은 Queue 끝단에서 새로운 원소를 추가하는 것으로 끝나며, 삭제 연산은 Queue 의 첫번째 원소를 삭제하는 것으로 끝납니다. 따라서 Queue 에서의 삽입과 삭제 연산은 단 한 번의 실행만으로 처리할 수 있습니다.

   - Queue 를 구현한 LinkedList<E> 에서 삭제연산은 다음과 같습니다.

   - ```java
     public E poll() {
         final Node<E> f = first;
         return (f == null) ? null : unlinkFirst(f);
     }
     ```

   - 즉, 제일 첫번째 요소의 link 를 끊어버립니다. 따로 순서를 조정할 필요가 없습니다.

     

**Queue 의 단점**

1. 중간에 있는 데이터를 조회하거나 수정하는 연산에 적합하지 않습니다.
2. 크기 제한이 없어서 메모리 낭비가 발생할 수 있습니다. (Stack 과 동일한 내용입니다.)
3. Queue 인터페이스는 `iterator()` 메서드를 지원하지 않습니다. 따라서 큐를 순회할 때는 `peek()`, `poll()` 을 사용하여 각각 데이터를 차례대로 가져와야 합니다.