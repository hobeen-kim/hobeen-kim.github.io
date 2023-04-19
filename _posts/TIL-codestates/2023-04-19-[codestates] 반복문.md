---
categories: "TIL-codestates"
tag: [ "codestates", "loop"]
---



# 반복문

반복문은 코드들이 반복적으로 실행되도록 할 때 사용됩니다.

## for loop

다음과 같은 형태입니다.

```java
public class Main {
  public static void main(String[] args) {
    int sum = 0;
    // for (초기화; 조건식; 증감식)
    for(int num = 0; num < 10; num++) {	
      sum += num;
    }
    System.out.println(sum); // 1~9의 합인 45가 출력됩니다.
  }
}
```

for 안에는 초기화, 조건식, 증감식으로 구성됩니다. 

- **초기화**는 `for`문이 시작할 때 최초 한 번만 수행되며, 사용할 변수의 초깃값을 정합니다.
- **조건식**은 계속 반복할지 여부를 결정하는 조건입니다. 조건식 안의 값이 `true`라면 실행문을 실행시키고, `false`라면 더 이상 블록을 실행하지 않고 끝납니다.
- **증감식**은 반복 횟수를 결정하는 규칙입니다. 변수에 값을 더하거나 곱하는 등 수행 방식을 지정합니다. `++` 은 반복문에서 자주 쓰는 증감연산자로, 피연산자의 값을 1 증가시킵니다.

## Enhanced for loop

향상된 for 문은 컬렉션 객체를 더 쉽게 처리할 목적으로 사용합니다. 다음과 같은 형태입니다.

```java
public class EnhancedForLoop {
  public static void main(String[] args) throws Exception {
    String[] names = {"kimcoding", "javalee", "ingikim"};
    for(String name : names) {
      System.out.println(name + "님은 자바를 공부중 입니다.");
    }
  }
}
/*
kimcoding님은 자바를 공부중 입니다.
javalee님은 자바를 공부중 입니다.
ingikim님은 자바를 공부중 입니다.
*/
```



## while loop

`while`문은 조건식이 `true`일 경우에 계속해서 반복합니다.

```java
int num = 0, sum = 0;
while(num <= 10) {
  sum += num;
  num++;
}
System.out.println(sum);
//output : 55
```



## do-while loop

do-while loop 문은 while 문과 동일하지만, 실행문을 1번은 실행시킨 뒤 그 결과에 따라 while 문을 반복 실행합니다.

```java
import java.util.Scanner;

public class Main {
  public static void main(String args[]){
    int input = 0, randomNum = 0;

      randomNum = (int)(Math.random() * 10) + 1; // 1 ~ 10 임의의 수를 생성
      Scanner scanner = new Scanner(System.in);

      do{
        System.out.println("1과 10 사이의 정수를 입력하세요");
        input = scanner.nextInt();

        if(input > randomNum) {
          System.out.println("더 작은 정수를 입력하세요");
        } else if (input < randomNum) {
          System.out.println("더 큰 정수를 입력하세요");
        }
      } while(input != randomNum);
      System.out.println(randomNum +" 정답입니다!");
  }
}
```



## break 문

`break`문은 반복문인 `for`문, `while`문, `do-while`문을 실행 중지할 때 사용됩니다. 

다음과 같이 반복문이 중첩되어 있을 경우 레이블을 사용하여 바깥쪽 반복문도 빠져나올 수 있습니다.

```java
public class Main {
    public static void main(String[] args) {
        Outer : for (int i = 3; i < 10; i++) {
            for (int j = 5; j > 0; j--) {
                System.out.println("i " + i + " j "+ j);
                if (i == 5) {
                    //Outer 문을 break
                    break Outer;
                }
            }
        }
    }
}
/*
i 3 j 5
i 3 j 4
i 3 j 3
i 3 j 2
i 3 j 1
i 4 j 5
i 4 j 4
i 4 j 3
i 4 j 2
i 4 j 1
i 5 j 5
*/
```



## continue 문

`continue`문은 반복문인 `for`문, `while`문, `do-while`문에서만 사용되는데, 블록 내부에서 `continue`문이 실행되면 `for`문의 증감문 혹은 `while`, `do-while`문의 조건식으로 이동하여 작동합니다. 

`continue`문과 `break`문의 차이점은 반복문 종료 여부입니다. `continue`문은 반복문을 종료하지 않고 다음 차례로 넘어가 계속 반복을 수행합니다.

다음과 같이 사용합니다.

```java
public class Main {
    public static void main(String[] args) throws Exception {
        for (int i = 0; i < 10; i++) {
            if (i % 2 == 0) { //나머지가 0일 경우는
                continue; //다음 반복으로 넘어간다.
            }
            System.out.println(i); //홀수만 출력
        }
    }
}
/*
1,3,5,7,9
*/
```

break 문과 마찬가지로 라벨을 통해 이중 for 문에서 바깥쪽 for 문으로 돌아갈 수 있습니다.

```java
public class Main {
    public static void main(String[] args) {
        Outer : for (int i = 0; i < 3; i++) {
           for(int j = 0; j < 3; j++) {
               if (i == j) {
                   continue Outer;
               }
               System.out.println(i + "," + j);
           }
        }
    }
}
/*
1,0
2,0
2,1
*/
```

