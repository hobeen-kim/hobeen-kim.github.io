---
title: "lateral join 을 사용해보자"
date: 2025-04-20
tags:
  - lateral join
description: "Lateral Join 에 대한 간단한 정리입니다."
---

# 1. LATERAL 조인이란?

LATERAL 조인은 PostgreSQL 9.3 버전에서 도입된 고급 조인 기법으로, 메인 쿼리의 각 행에 대해 서브쿼리를 실행할 수 있게 해주는 기능입니다. 일반적인 서브쿼리와 달리, LATERAL 서브쿼리는 메인 쿼리(왼쪽 테이블)의 컬럼을 참조할 수 있어 동적인 서브쿼리 실행이 가능합니다.

간단히 말해, LATERAL 조인은 메인 쿼리의 각 행마다 서브쿼리를 개별적으로 평가하여 그 결과와 조인하는 방식입니다. 이는 마치 프로그래밍에서 중첩 루프와 유사한 동작을 SQL에서 구현한 것이라고 볼 수 있습니다.

## 중첩 루프 개념

프로그래밍에서 중첩 루프는 한 루프 내부에 다른 루프가 있는 구조입니다.

```kotlin
for (i in 1..3) {
    // 외부 루프: 1, 2, 3을 순회
    for (j in 1..2) {
        // 내부 루프: 각 i 값에 대해 1, 2를 순회
        println("i=$i, j=$j")
    }
}
```

이 코드의 출력은 다음과 같습니다.

```
i=1, j=1
i=1, j=2
i=2, j=1
i=2, j=2
i=3, j=1
i=3, j=2
```

여기서 중요한 점은 **내부 루프가 외부 루프의 각 항목마다 새롭게 실행**되며, **내부 루프는 외부 루프의 현재 변수(i)에 접근**할 수 있다는 것입니다.

## LATERAL JOIN의 유사성

LATERAL JOIN은 이와 매우 유사하게 동작합니다.

1. 메인 쿼리(외부 루프)의 각 행에 대해
2. LATERAL 서브쿼리(내부 루프)가 개별적으로 실행됨
3. 서브쿼리는 메인 쿼리의 현재 행 값을 참조할 수 있음

# 2. LATERAL 조인을 사용하는 경우와 이유

LATERAL 조인은 다음과 같은 상황에서 특히 유용합니다.

1. **행별 Top-N 쿼리**: 각 그룹/행별로 특정 조건에 따른 상위 N개의 행을 선택해야 할 때
2. **행별 집계**: 메인 쿼리의 각 행에 대해 관련된 다른 테이블의 데이터를 집계해야 할 때
3. **동적 필터링**: 메인 쿼리의 각 행마다 다른 조건으로 필터링해야 할 때
4. **복잡한 계산**: 메인 쿼리의 값을 기반으로 복잡한 계산이나 함수 결과를 조인해야 할 때

일반 JOIN과 GROUP BY, 윈도우 함수로도 유사한 결과를 얻을 수 있는 경우가 많지만, LATERAL 조인은 더 명확하고 직관적인 쿼리 작성을 가능하게 하며, 때로는 성능 이점도 제공합니다.

# 3. LATERAL 조인 예시

실생활에서 이해하기 쉬운 예시를 통해 LATERAL JOIN의 활용법을 알아봅시다. 학생과 수강 과목에 관한 테이블을 생성해 보겠습니다.

```sql
-- 테이블 생성
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    grade INT
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    title VARCHAR(100),
    difficulty INT
);

CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    score INT,
    PRIMARY KEY (student_id, course_id)
);

-- 샘플 데이터 삽입
INSERT INTO students VALUES
(1, '김철수', 3),
(2, '이영희', 2),
(3, '박민수', 3);

INSERT INTO courses VALUES
(101, '데이터베이스', 4),
(102, '프로그래밍 기초', 2),
(103, '알고리즘', 5),
(104, '운영체제', 4),
(105, '네트워크', 3);

INSERT INTO enrollments VALUES
(1, 101, 85),
(1, 103, 92),
(1, 105, 78),
(2, 102, 95),
(2, 104, 88),
(2, 105, 91),
(3, 101, 79),
(3, 102, 88),
(3, 103, 94);
```

이제 각 학생별로 성적이 가장 높은 2개 과목을 조회하는 쿼리를 LATERAL JOIN으로 구현해 보겠습니다.

```sql
SELECT s.name, x.title, x.score
FROM students s,
     LATERAL (
         SELECT c.title, e.score
         FROM enrollments e
         JOIN courses c ON e.course_id = c.course_id
         WHERE e.student_id = s.student_id  -- 메인 쿼리의 현재 학생 참조
         ORDER BY e.score DESC
         LIMIT 2
     ) AS x
ORDER BY s.name, x.score DESC;
```

## 동작 원리 설명

이 쿼리가 실행되는 과정을 단계별로 살펴보겠습니다.

1. 메인 쿼리는 students 테이블에서 학생들을 한 명씩 가져옵니다.
2. 각 학생에 대해 LATERAL 서브쿼리가 실행됩니다.
   - 서브쿼리는 `s.student_id`를 참조하여 현재 학생의 수강 정보를 필터링합니다.
   - 성적(score)을 기준으로 내림차순 정렬합니다.
   - 상위 2개 과목만 선택합니다.
3. 메인 쿼리의 각 학생 행과 해당 학생의 서브쿼리 결과가 조인됩니다.

이 SQL의 동작을 Kotlin 코드로 표현하면 다음과 같습니다.

```kotlin
val results = mutableListOf<ResultRow>()

// 외부 루프: 모든 학생 순회
for (student in students) {
    // 내부 루프: 현재 학생의 수강 정보 처리
    val topCourses = enrollments
        .filter { it.studentId == student.id }  // 현재 학생의 수강 정보만 필터링
        .sortedByDescending { it.score }        // 성적 기준 정렬
        .take(2)                                // 상위 2개만 선택
        .map { enrollment ->
            val course = courses.find { it.id == enrollment.courseId }
            Triple(student.name, course?.title, enrollment.score)
        }
    
    // 결과에 추가
    results.addAll(topCourses)
}

// 결과 정렬
results.sortWith(compareBy({ it.first }, { -it.third }))
```

## 실행 결과

이 쿼리의 결과는 다음과 같습니다.

```
   name   |      title       | score
----------+------------------+-------
 김철수   | 알고리즘         |    92
 김철수   | 데이터베이스     |    85
 박민수   | 알고리즘         |    94
 박민수   | 프로그래밍 기초  |    88
 이영희   | 프로그래밍 기초  |    95
 이영희   | 네트워크         |    91
```

## 다른 LATERAL JOIN 활용 예시

앞서 본 예시를 확장하여, 이번에는 각 학생이 수강 중인 과목 중 난이도(difficulty)가 학생의 학년(grade)보다 높은 과목들 중 가장 어려운 2개 과목을 찾아보겠습니다.

```sql
SELECT s.name, s.grade, x.title, x.difficulty
FROM students s,
     LATERAL (
         SELECT c.title, c.difficulty
         FROM courses c
         JOIN enrollments e ON e.course_id = c.course_id
         WHERE e.student_id = s.student_id
         AND c.difficulty > s.grade
         ORDER BY c.difficulty DESC
         LIMIT 2
     ) AS x
ORDER BY s.name, x.difficulty DESC;
```

이 쿼리는 각 학생에 대해 수강 중인 과목 중에서 자신의 학년보다 난이도가 높은 과목들을 찾고, 그 중 난이도가 가장 높은 2개 과목을 선택합니다.

# 4. 일반 조인과의 차이점

LATERAL JOIN과 일반 조인의 주요 차이점은 **상관 관계(correlation)** 입니다.

1. **일반 조인**: 조인되는 두 테이블은 독립적으로 평가됩니다. 서브쿼리는 메인 쿼리와 독립적으로 한 번만 실행됩니다.
2. **LATERAL 조인**: 서브쿼리는 메인 쿼리의 각 행에 대해 개별적으로 실행됩니다. 서브쿼리는 메인 쿼리의 현재 행 값을 참조할 수 있습니다.

일반 조인으로는 "각 학생별 상위 2개 과목"과 같은 요구사항을 직접적으로 표현하기 어렵습니다. 이런 경우 윈도우 함수를 사용한 추가적인 작업이 필요하지만, LATERAL JOIN을 사용하면 더 직관적으로 표현할 수 있습니다.

# 5. EXPLAIN으로 성능 비교

LATERAL 조인과 대안 방식의 성능을 비교해봅시다. 대안으로는 윈도우 함수(ROW_NUMBER)를 사용한 방식을 살펴보겠습니다.

## LATERAL 조인 사용 (원본 쿼리)

```sql
EXPLAIN ANALYZE
SELECT s.name, x.title, x.score
FROM students s,
     LATERAL (
         SELECT c.title, e.score
         FROM enrollments e
         JOIN courses c ON e.course_id = c.course_id
         WHERE e.student_id = s.student_id
         ORDER BY e.score DESC
         LIMIT 2
     ) AS x
ORDER BY s.name, x.score DESC;
```

## 윈도우 함수 사용 (대안 방식)

```sql
EXPLAIN ANALYZE
WITH ranked_courses AS (
    SELECT 
        s.name,
        c.title,
        e.score,
        ROW_NUMBER() OVER (PARTITION BY s.student_id ORDER BY e.score DESC) AS row_num
    FROM 
        students s
    JOIN 
        enrollments e ON e.student_id = s.student_id
    JOIN 
        courses c ON c.course_id = e.course_id
)
SELECT 
    name,
    title,
    score
FROM 
    ranked_courses
WHERE 
    row_num <= 2
ORDER BY 
    name, score DESC;
```

## LATERAL JOIN과 윈도우 함수 실행 계획 비교

### LATERAL JOIN 실행 계획

```
Sort  (cost=9350.63..9352.23 rows=640 width=440) (actual time=0.203..0.205 rows=6 loops=1)
"  Sort Key: s.name, e.score DESC"
  Sort Method: quicksort  Memory: 25kB
  ->  Nested Loop  (cost=29.06..9320.80 rows=640 width=440) (actual time=0.139..0.167 rows=6 loops=1)
        ->  Seq Scan on students s  (cost=0.00..13.20 rows=320 width=222) (actual time=0.018..0.019 rows=3 loops=1)
        ->  Limit  (cost=29.06..29.07 rows=2 width=222) (actual time=0.046..0.046 rows=2 loops=3)
              ->  Sort  (cost=29.06..29.09 rows=10 width=222) (actual time=0.045..0.045 rows=2 loops=3)
                    Sort Key: e.score DESC
                    Sort Method: quicksort  Memory: 25kB
                    ->  Hash Join  (cost=14.91..28.96 rows=10 width=222) (actual time=0.039..0.040 rows=3 loops=3)
                          Hash Cond: (c.course_id = e.course_id)
                          ->  Seq Scan on courses c  (cost=0.00..13.20 rows=320 width=222) (actual time=0.002..0.003 rows=5 loops=3)
                          ->  Hash  (cost=14.79..14.79 rows=10 width=8) (actual time=0.027..0.027 rows=3 loops=3)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                ->  Bitmap Heap Scan on enrollments e  (cost=4.23..14.79 rows=10 width=8) (actual time=0.010..0.011 rows=3 loops=3)
                                      Recheck Cond: (student_id = s.student_id)
                                      Heap Blocks: exact=3
                                      ->  Bitmap Index Scan on enrollments_pkey  (cost=0.00..4.23 rows=10 width=0) (actual time=0.006..0.006 rows=3 loops=3)
                                            Index Cond: (student_id = s.student_id)
Planning Time: 0.221 ms
Execution Time: 0.273 ms
```

#### LATERAL JOIN 실행 계획 분석

1. **학생별 처리 방식**
   - `Seq Scan on students s`로 먼저 3명의 학생을 가져옵니다
   - `loops=3`은 이후 작업이 각 학생마다 반복됨을 의미합니다
   - 각 학생에 대해 `Bitmap Index Scan`으로 해당 학생의 수강 정보를 인덱스를 통해 빠르게 필터링합니다
   - 각 학생별로 평균 3개의 수강 정보만 처리합니다 (`rows=3`)
2. **효율적인 필터링**
   - `student_id = s.student_id` 조건으로 각 학생별로 필요한 데이터만 가져옵니다
   - 각 학생마다 성적 기준 정렬 후 바로 상위 2개만 선택합니다 (`Limit rows=2`)
   - 불필요한 데이터는 처리하지 않습니다
3. **중요한 성능 지표**
   - 실행 시간이 매우 짧습니다 (0.273ms)
   - 각 단계에서 처리하는 행 수가 적습니다
   - 메모리 사용량이 적습니다 (25kB)

### 윈도우 함수 실행 계획

```
Sort  (cost=361.13..366.23 rows=2040 width=440) (actual time=0.448..0.449 rows=6 loops=1)
"  Sort Key: ranked_courses.name, ranked_courses.score DESC"
  Sort Method: quicksort  Memory: 25kB
  ->  Subquery Scan on ranked_courses  (cost=187.81..248.99 rows=2040 width=440) (actual time=0.316..0.322 rows=6 loops=1)
        ->  WindowAgg  (cost=187.81..228.59 rows=2040 width=452) (actual time=0.316..0.320 rows=6 loops=1)
              Run Condition: (row_number() OVER (?) <= 2)
              ->  Sort  (cost=187.79..192.89 rows=2040 width=444) (actual time=0.296..0.297 rows=9 loops=1)
"                    Sort Key: s.student_id, e.score DESC"
                    Sort Method: quicksort  Memory: 25kB
                    ->  Hash Join  (cost=34.40..75.64 rows=2040 width=444) (actual time=0.248..0.252 rows=9 loops=1)
                          Hash Cond: (e.course_id = c.course_id)
                          ->  Hash Join  (cost=17.20..53.02 rows=2040 width=230) (actual time=0.074..0.077 rows=9 loops=1)
                                Hash Cond: (e.student_id = s.student_id)
                                ->  Seq Scan on enrollments e  (cost=0.00..30.40 rows=2040 width=12) (actual time=0.027..0.028 rows=9 loops=1)
                                ->  Hash  (cost=13.20..13.20 rows=320 width=222) (actual time=0.027..0.027 rows=3 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      ->  Seq Scan on students s  (cost=0.00..13.20 rows=320 width=222) (actual time=0.015..0.015 rows=3 loops=1)
                          ->  Hash  (cost=13.20..13.20 rows=320 width=222) (actual time=0.148..0.148 rows=5 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                ->  Seq Scan on courses c  (cost=0.00..13.20 rows=320 width=222) (actual time=0.105..0.106 rows=5 loops=1)
Planning Time: 2.083 ms
Execution Time: 1.170 ms
```

#### 윈도우 함수 실행 계획 분석

1. **전체 테이블 선처리**
   - 모든 테이블을 먼저 순차 스캔합니다 (`Seq Scan`)
   - 모든 학생(3명), 모든 수강 정보(9개), 모든 과목(5개)을 가져옵니다
   - 전체 데이터를 조인한 후에야 필터링을 시작합니다
2. **복잡한 처리 단계**
   - 전체 조인 결과(9개 행)를 학생 ID와 성적으로 정렬합니다
   - 윈도우 집계 함수를 적용하여 각 학생별 순위를 계산합니다
   - 그 후에야 순위 조건으로 필터링합니다
   - 마지막으로 결과를 다시 정렬합니다
3. **성능 지표**
   - 실행 시간이 LATERAL JOIN보다 4배 이상 깁니다 (1.170ms)
   - 계획 시간도 9배 이상 깁니다 (2.083ms)
   - 중간 단계에서 더 많은 행을 처리합니다

### 두 방식의 핵심 차이

1. **처리 순서의 차이**
   - LATERAL JOIN은 학생마다 필터링 → 조인 → 정렬 → LIMIT 적용
   - 윈도우 함수는 전체 조인 → 전체 정렬 → 윈도우 계산 → 필터링
2. **처리하는 데이터량**
   - LATERAL JOIN은 필요한 데이터만 처리 (학생당 평균 3개 행)
   - 윈도우 함수는 모든 데이터를 처리 (총 9개 행)
3. **성능 차이**
   - LATERAL JOIN이 윈도우 함수보다 약 4배 빠름
   - 데이터 크기가 커질수록 이 차이는 더 극명해짐

대규모 데이터에서 LATERAL JOIN은 필터링을 먼저 적용하고 필요한 데이터만 처리하기 때문에 훨씬 효율적입니다. 예를 들어 학생 1,000명, 학생당 과목 20개인 경우 LATERAL JOIN은 최대 2,000개 행만 생성하지만, 윈도우 함수는 20,000개 행을 모두 처리해야 합니다.

### 성능 비교 분석

**LATERAL 조인의 장점**

1. **선택적 스캔**: LATERAL 조인은 각 학생에 대해 조건을 만족하는 과목을 찾은 후 바로 LIMIT을 적용하므로, 불필요한 행을 처리하지 않습니다.
2. **메모리 효율성**: 각 학생마다 최대 2개의 과목만 메모리에 유지하므로, 학생 수에 비례하는 메모리만 사용합니다.
3. **조기 종료**: 각 학생에 대해 성적이 가장 높은 2개 과목을 찾자마자 해당 학생에 대한 검색을 중단합니다.

**윈도우 함수 방식의 단점**

1. **전체 조인 필요**: 모든 학생과 그들의 모든 수강 과목을 먼저 조인한 후에 필터링하므로, 중간 결과가 매우 클 수 있습니다.
2. **추가 정렬 작업**: 윈도우 함수가 정렬을 수행하고, 그 이후에 다시 최종 결과를 정렬해야 합니다.
3. **메모리 사용량 증가**: 전체 조인 결과를 메모리에 보관해야 하므로, 대용량 데이터에서 메모리 사용량이 크게 증가할 수 있습니다.

대규모 데이터셋에서는 이러한 차이가 더욱 두드러집니다. 예를 들어, 학생이 1,000명이고 각 학생당 평균 10개의 수강 과목이 있다면,

- LATERAL 조인: 최악의 경우에도 2,000개의 행만 처리 (1,000 × 2)
- 윈도우 함수: 모든 학생과 수강 과목의 조인 결과인 10,000개의 행을 모두 처리한 후 필터링

## 6. 결론

LATERAL JOIN은 SQL에서 프로그래밍 언어의 중첩 루프와 유사한 패턴을 구현할 수 있게 해주는 강력한 도구입니다. 각 행별로 동적인 서브쿼리 처리가 필요한 상황에서 특히 유용하며, 복잡한 비즈니스 로직을 더 직관적으로 표현할 수 있게 해줍니다.

살펴본 학생별 최고 성적 과목을 찾는 시나리오처럼, 행별 Top-N 쿼리에서 LATERAL 조인은 성능과 메모리 사용 측면에서 상당한 이점을 제공합니다. EXPLAIN 분석 결과에서도 확인했듯이, 윈도우 함수를 사용한 방식보다 LATERAL JOIN이 약 4배 이상 빠른 성능을 보여주었습니다.
