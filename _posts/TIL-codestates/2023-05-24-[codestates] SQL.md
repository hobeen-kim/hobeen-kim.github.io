---
categories: "TIL-codestates"
tag: [ "database", "sql", "transaction", "ACID"]
---

# SQL

**Structured Query Language** (SQL)은 데이터베이스 언어로, 주로 관계형 데이터베이스에서 사용합니다. Query 란 데이터를 필터링하기 위한 질의문입니다.

### DB 생성

```MYSQL
CREATE DATABASE [DB 명]
```

### 데이터 베이스 사용

```MYSQL
USE [DB 명]
```

### 테이블 생성

```MYSQL
CREATE TABLE user (
  id int PRIMARY KEY AUTO_INCREMENT, 
  name varchar(255),
  email varchar(255)
);
```

### 테이블 정보 확인

```MYSQL
DESCRIBE user
```




## SQL 명령어

### SELECT + FROM

특정 테이블에서 특정 필드를 선택합니다.

```MYSQL
SELECT * FROM [TABLE 명] #TABLE 의 모든 필드를 가져옵니다.
SELECT NAME FROM [TABLE 명] #TABLE 에서 NAME 필드를 가져옵니다.
```

### WHERE

필터역할을 하는 쿼리문입니다.

```mysql
SELECT * FROM [TABLE 명] WHERE NAME="KIM" #TABLE 에서 NAME 필드가 "KIM" 인 모든 레코드를 가져옵니다.
SELECT * FROM [TABLE 명] WHERE NAME<>"KIM" #TABLE 에서 NAME 필드가 "KIM" 이 아닌 모든 레코드를 가져옵니다.
SELECT * FROM [TABLE 명] WHERE NOT NAME = "KIM" #TABLE 에서 NAME 필드가 "KIM" 이 아닌 모든 레코드를 가져옵니다. 위와 같습니다.
SELECT * FROM [TABLE 명] WHERE NAME LIKE "KIM%" #TABLE 에서 NAME 필드가 "KIM" 으로 시작하는 모든 레코드를 가져옵니다.
SELECT * FROM [TABLE 명] WHERE ID IN (1, 10) #TABLE 에서 ID 필드가 1 ~ 10 인 모든 레코드를 가져옵니다.
SELECT * FROM [TABLE 명] WHERE EMAIL IS NULL #TABLE 에서 EMAIL 필드가 NULL 값인 모든 레코드를 가져옵니다.
SELECT * FROM [TABLE 명] WHERE EMAIL IS NOT NULL #TABLE 에서 EMAIL 필드가 NULL 값이 아닌 모든 레코드를 가져옵니다.
```




### ORDER BY

데이터 출력하는 순서를 결정합니다.

```MYSQL
SELECT * FROM [TABLE 명] ORDER BY ID #TABLE 에서 모든 레코드를 ID 값의 오름차순으로 정렬하여 가져옵니다.
SELECT * FROM [TABLE 명] ORDER BY NAME #TABLE 에서 모든 레코드를 NAME 값의 오름차순으로 정렬하여 가져옵니다.
SELECT * FROM [TABLE 명] ORDER BY ID DESC #TABLE 에서 모든 레코드를 ID 값의 내림차순으로 정렬하여 가져옵니다.
SELECT * FROM [TABLE 명] ORDER BY ID, NAME #TABLE 에서 모든 레코드를 ID 값의 오름차순으로 정렬하고 같으면 NAME 값의 오름차순으로 정렬하여 가져옵니다.
```



### LIMIT

결과로 출력할 데이터의 개수를 정할 수 있습니다. LIMIT은 선택적으로 사용할 수 있습니다. 그리고 쿼리문에서 사용할 때에는 가장 마지막에 추가합니다.

```MYSQL
SELECT * FROM [TABLE 명] LIMIT 200 #TABLE 에서 200 개의 레코드를 가져옵니다.
```



### DISTINCT

특정 필드의 중복을 제거한 뒤 결과를 출력합니다. 아래는 USER 테이블입니다.

| ID   | NAME | EMAIL            |
| ---- | ---- | ---------------- |
| 1    | KIM  | EMAIL1@NAVER.COM |
| 2    | KIM  | EMAIL2@NAVER.COM |
| 3    | PARK | EMAIL2@NAVER.COM |

```MYSQL
SELECT DISTINCT NAME FROM USER # 1, 3번 아이디만 출력됩니다.
SELECT DISTINCT EMAIL FROM USER # 1, 2번 아이디만 출력됩니다.
SELECT DISTINCT NAME, EMAIL FROM USER # 1번 아이디만 출력됩니다.
```

### INNER JOIN

INNER JOIN 은 테이블을 병합하기 위해 사용합니다. DISTINCT 의 USER 테이블과 아래의  POST, REWARD 테이블을 함께 사용하겠습니다.

*POST TABLE*

| ID   | TITLE  | CONTENT  | USER_ID |
| ---- | ------ | -------- | ------- |
| 1    | TITLE1 | CONTENT1 | 1       |
| 2    | TITLE2 | CONTENT2 | 1       |
| 3    | TITLE3 | CONTENT3 | 2       |

*REWARD TABLE*

| ID   | REWARD | USER_ID |
| ---- | ------ | ------- |
| 1    | 1000   | 2       |
| 2    | 2000   | 3       |



```MYSQL
SELECT U.ID, P.TITLE, P.CONTENT FROM USER AS U JOIN POST AS P ON U.ID = P.USER_ID
```

JOIN 은 두 개 이상의 테이블을 결합하기 때문에 결합하는 테이블의 필드명이 중복될 수 있습니다. 따라서 위 쿼리문처럼 필드가 속한 테이블을 명시해줍니다. 위 쿼리문 시행 시 아래와 같은 결과를 얻습니다.

| U.ID | P.TITLE | P.CONTENT |
| ---- | ------- | --------- |
| 1    | TITLE1  | CONTENT1  |
| 1    | TITLE2  | CONTENT2  |
| 2    | TITLE3  | CONTENT3  |

다음은 삼중 JOIN 을 해보겠습니다.

```MYSQL
SELECT U.ID, P.TITLE, R.REWARD FROM USER AS U JOIN POST AS P ON U.ID = P.USER_ID JOIN REWARD AS R ON P.USER_ID = R.USER_ID
SELECT U.ID, P.TITLE, R.REWARD FROM USER AS U JOIN REWARD AS R ON U.ID = R.USER_ID JOIN POST AS P ON R.USER_ID = P.USER_ID
SELECT U.ID, P.TITLE, R.REWARD FROM USER AS U JOIN POST AS P ON U.ID = P.USER_ID JOIN REWARD AS R ON U.ID = R.USER_ID
SELECT U.ID, P.TITLE, R.REWARD FROM USER AS U JOIN REWARD AS R ON U.ID = R.USER_ID JOIN POST AS P ON U.ID = P.USER_ID
```

위 네 결과는 같습니다. USER 와 POST, RECORD 테이블이 모두 겹치는 경우만 출력합니다.

| U.ID | P.TITLE | R.REWARD |
| ---- | ------- | -------- |
| 2    | TITLE3  | CONTENT3 |



### OUTER JOIN 

외부 조인은 한쪽 테이블에만 내용이 있어도 결과가 검색이 됩니다. LEFT JOIN, RIGHT JOIN 과 같이 사용될 수 있는데, LEFT 는 첫번째 테이블은 모두 검색되어야 한다는 뜻이고, RIGHT 는 반대입니다.

```mysql
SELECT U.ID, P.TITLE FROM USER AS U LEFT JOIN POST AS P ON U.ID = P.USER_ID
```

| U.ID | P.TITLE |
| ---- | ------- |
| 1    | TITLE1  |
| 1    | TITLE2  |
| 2    | TITLE3  |
| 3    | NULL    |



# 트랜잭션

​	트랜잭션이란 여러 개의 작업을 하나로 묶은 실행 유닛입니다. 각 트랜잭션은 하나의 특정 작업으로 시작을 해 묶여 있는 모든 작업들을 다 완료해야 정상적으로 종료합니다. 반대로 한 작업이라도 실패한다면 이 트랙잭션에 속한 모든 작업을 실패한 것으로 간주합니다. 이러한 트랜잭션의 안전성을 보장하기 위해 ACID 라는 성질이 필요합니다.

**Atomicity (원자성)**

원자성은 하나의 트랜잭션에 속해있는 모든 작업이 **전부 성공하거나 전부 실패해서** 결과를 예측할 수 있어야 합니다. 

**Consistency (일관성)**

두 번째는 데이터베이스의 상태가 일관되어야 한다는 성질입니다. 하나의 트랜잭션 이전과 이후, **데이터베이스의 상태는 이전과 같이 유효해야 합니다.** 다시 말해, 트랜잭션이 일어난 이후의 데이터베이스는 데이터베이스의 제약이나 규칙을 만족해야 한다는 뜻입니다.

**Isolation(격리성, 고립성)**

Isolation(격리성) 은 **모든 트랜잭션은 다른 트랜잭션으로부터 독립되어야 한다** 는 뜻입니다. 예를 들어서 한 계좌에서 다른 계좌로 2번 송금을 하는 상황에서 동시에 트랜잭션을 실행하든, 연속적으로 실행하든 같은 결과가 나와야 합니다. 즉, 격리성을 지키는 각 트랜젝션은 철저히 독립적이기 때문에, 다른 트랜젝션의 작업 내용을 알 수 없습니다. 그리고 트랜잭션이 동시에 실행될 때와 연속으로 실행될 때의 데이터베이스 상태가 동일해야 합니다.

**Durability(지속성)**

Durability(지속성)는 하나의 트랜잭션이 성공적으로 수행되었다면, 해당 트랜잭션에 대한 로그가 남아야 합니다. 만약 런타임 오류나 시스템 오류가 발생하더라도, **해당 기록은 영구적이어야** 한다는 뜻입니다.

예를 들어 은행에서 계좌이체를 성공적으로 실행한 뒤에, 해당 은행 데이터베이스에 오류가 발생해 종료되더라도 계좌이체 내역은 기록으로 남아야 합니다.

# SQL DB vs NoSQL DB

SQL 과 NoSQL 에는 다음과 같은 차이점이 있습니다.

- **데이터 저장** : SQL 은 미리 작성된 스키마를 기반으로 테이블을 사용해 저장하는 반면 NoSQL 은 key-value, document, wide-column, graph 등의 방식으로 데이터를 저장합니다.
- **스키마** : SQL 은 필드를 만드는 등의 고정된 형식의 스키마가 있어야 합니다. 하지만 NoSQL 은 동적으로 스키마를 관리할 수 있습니다.
- **쿼리** : SQL 은 이름 그대로 구조화된 쿼리 언어로 질의합니다. 하지만 NoSQL 은 **데이터 그룹 자체**를 조회하는 것에 초점을 두고 있습니다. 그래서 구조화되지 않은 쿼리 언어로도 데이터 요청이 가능합니다.
- **확장성** : SQL 은 일반적으로 scale up 을 하고 NoSQL 은 scale out 을 합니다. SQL 도 scale out 이 가능하지만 여러 서버에 결쳐 관계를 정의하는 것은 매우 복잡하고 시간이 많이 소ㅗㅁ됩니다.

### SQL 기반의 RDMS 를 사용하는 경우

1. 데이터베이스의 ACID 성질을 준수해야 하는 경우
2. 소프트웨어에 사용되는 데이터가 구조적이고 일관적인 경우

**NoSQL 기반의 NonRDMS 를 사용하는 경우**

1. 데이터의 구조가 거의 또는 전혀 없는 대용량의 데이터를 저장하는 경우
2. 클라우드 컴퓨팅 및 저장공간을 최대한 활용하는 경우
3. **빠르게 서비스를 구축하는 과정에서 데이터 구조를 자주 업데이트 하는 경우**



