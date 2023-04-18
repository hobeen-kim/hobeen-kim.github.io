---
categories: "TIL-codestates"
tag: [ "codestates", "conditionalstate"]
---



# 연산자

연산자란, 하나의 값 또는 여러 개의 값을 피연산자로 하여 새로운 값을 만들어내는 기호를 의미합니다. 

- 산술연산자 : `+, -< *, /, %, //`
- 비교연산자 : `<, >, ==, !=`
- 논리연산자 : `&&, ||, !`

연산자 우선 순위는 다음과 같습니다.

| 우선순위 | 연산자            | 내용                 |
| -------- | ----------------- | -------------------- |
| 1        | (), []            | 괄호 / 대괄호        |
| 2        | !, ~, ++, --      | 부정/ 증감 연산자    |
| 3        | *, /, %           | 곱셈 / 나눗셈 연산자 |
| 4        | <, <=, >, >=      | 대소 비교 연산자     |
| 5        | &&                | AND 연산자           |
| 6        | \|\|              | OR 연산자            |
| 7        | ? :               | 조건 연산자          |
| 8        | =, +=, -=, /=, %= | 대입/할당 연산자     |



## 콘솔 입출력(I/O)

**출력**

- 출력하기 : System.out.print()

- 출력하고 줄 바꾸기 : System.out.println()

- 형식대로 출력하기 System.out.printf()

  - | 지시자 | 출력 포맷 |
    | ------ | --------- |
    | %b     | 불리언    |
    | %d     | 10진수    |
    | %o     | 8진수     |
    | %x, %X | 16진수    |
    | %c     | 문자      |
    | %s     | 문자열    |
    | %n     | 줄 바꿈   |

  - 다음과 같이 사용합니다.

  - ```java
    System.out.printf("%s%n", "Hello JAVA"); // 줄 바꿈이 됩니다.
    System.out.printf("%s%n", "Kim" + "Coding");
    System.out.printf("%d%n", 3+6); 
    System.out.printf("지금은 %s입니다", 2022 + "year"); // 자동 타입 변환이 일어납니다.
    System.out.printf("나는 %c%s입니다", '김', "코딩"); //여러 개의 인자를 넣을 수 있습니다.
    ```



**입력**

다음과 같이 Scanner 클래스로 입력을 받습니다.

```java
import java.util.Scanner;                 // Scanner 클래스를 가져옵니다.

Scanner scanner = new Scanner(System.in); // Scanner 클래스의 인스턴스를 생성합니다.
String inputValue = scanner.nextLine();   // 입력한 내용이 inputValue에 저장됩니다.

System.out.println(inputValue);           // 입력한 문자열이 출력됩니다.
```

- `nextLine()` : 콘솔을 통해 문자열 데이터를 입력받는 기능을 수행합니다. 입력받은 타입이 정수형일 때는 `nextInt()`, 실수형일 때는 `nextFloat()` 등을 사용할 수 있습니다.



# 조건문

## Switch 문

switch 문은 다음과 같이 사용합니다.

```java
public class Main {
    static Scanner myInput = new Scanner(System.in);
    public static void main(String[] args) {
        String dice = myInput.nextLine(); //주사위 번호 입력

        switch (dice) {
            case "1":
                System.out.println("1번");
                break; //다음 case를 실행하지 않고, switch문 탈출!
            case "2":
                System.out.println("2번");
                break;
            case "3":
                System.out.println("3번");
                break;
            case "4":
                System.out.println("4번");
                break;
            case "5":
                System.out.println("5번");
                break;
            case "6":
                System.out.println("6번");
                break;
            default: //switch문의 괄호 안 값과 같은 값이 없으면, 여기서 실행문 실행
                System.out.println("없는 숫자! " + dice);
                break;
        }
    }
}
```

- switch 문의 조건에는 `int`, `char`, `String` 타입의 변수가 올 수 있습니다.