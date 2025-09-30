---
title: "실행 계획으로 확인하는 Like 검색 최적화"
date: 2025-09-30
tags:
  - postgres
  - like
  - pg_trgm
description: "Like 검색 쿼리를 개선하기 위한 인덱싱 작업입니다."
---

<Header />

[[toc]]

> 예제 데이터는 [해당 사이트](https://www.kaggle.com/datasets/bharadwaj6/kindle-reviews)의 리뷰 데이터를 활용했다. (총 982618개)

# 1. 문제 상황

review 테이블에서 review_text 로 검색하는 쿼리는 다음과 같다. 이때 대소문자 구분없이 검색하기 위해 `lower()` 를 사용한다.

```sql 
select * from review
where lower(reviewtext) like '%good%';
```

아무런 인덱스나 설정이 없다면 full scan 을 하게 된다. 이 쿼리의 실행계획은 아래와 같다.

```
Gather  (cost=1000.00..83362.62 rows=7863 width=585)
  Workers Planned: 2
  ->  Parallel Seq Scan on review  (cost=0.00..81576.32 rows=3276 width=585)
        Filter: (lower(reviewtext) ~~ '%good%'::text)
```

- `Gather` 노드는 여러 워커 프로세스에서 처리한 결과를 모아주는 역할을 한다.
- `Workers Planned: 2` → 워커 2개를 띄워서 데이터를 병렬로 스캔한다.
- `Parallel Seq Scan on review` : 인덱스를 쓰지 않고 테이블 전체를 순차적으로 읽다. Parallel Seq Scan 은 테이블을 여러 프로세스가 나눠서 읽으므로 순차 스캔보다 빠를 수 있다.
- `Filter: (lower(reviewtext) ~~ '%good%'::text)` : ~~는 LIKE의 내부 연산자다.

## 1.2 B-tree 인덱스의 한계

<u>여기서 review_text 에 인덱스를 걸어보고 실행계획을 비교해보자.</u>

```sql
create index idx_reviewtext on review (reviewtext);
```

이 때 `[54000] ERROR: index row requires 10728 bytes, maximum size is 8191 Where: parallel worker` 라는 에러가 나온다. 이는 PostgreSQL의 B-tree 인덱스 한계때문이다.

- Postgres의 일반 B-tree 인덱스는 한 row의 인덱스 엔트리가 **최대 8191바이트(약 8KB)** 를 초과할 수 없다.
- `reviewtext` 컬럼이 긴 텍스트를 포함하고 있을 경우, 그대로 인덱스를 만들면 특정 row에서 이 제한을 초과하여 인덱스 생성에 실패하게 된다.

만약 B-tree 인덱스가 만들어진다고 해도 **`%good%` 이나` %good` 검색에는 활용될 수 없다.** B-tree 인덱스는 **정렬된 순서**를 유지하기 때문에 `WHERE reviewtext LIKE 'good%'`처럼 **접두어(prefix)** 가 고정된 검색에는 잘 동작한다. 그 이유는 `'good'`으로 시작하는 값들이 인덱스 상에서 **연속된 구간(range)** 을 이루기 때문이다. (인덱스 탐색 후 필요한 범위만 읽으면 된다.)

하지만 `%`가 앞에 붙어 있는 경우 `'good'`이 문자열 어디에 나올지 전혀 알 수 없다. 즉, <u>인덱스의 정렬 구조를 활용할 수 없어 모든 행을 확인해야 때문에 이 경우는 풀스캔을 피하기 어렵다.</u>

# 2. 문제 해결

문제를 해결을 위해 **Trigram 인덱스**와 **Full Text Search (FTS)** 를 찾았고 Trigram 인덱스를 사용하기로 결정했다. FTS 는 단어 단위 검색에 최적화되어있기 때문이다.

> **Trigram 인덱스 (`pg_trgm`)**
>
> - 문자열을 3글자 단위로 쪼개서 GIN 인덱스에 저장.  `%good%` 같은 부분 문자열 검색에도 인덱스를 활용할 수 있음.
>
> **Full Text Search (FTS)**
>
> - 단어 단위 검색에 최적화.  `%good%` 같은 단순 부분검색이 아니라 `"good"`이라 는 단어를 찾을 때 훨씬 효율적임

## 1. Trigram(tri-gram) 개념

**Trigram** 은 문자열을 **3글자 단위**로 쪼갠 조각을 의미한다. 예를 들어 `"good"`이라는 문자열이 있다면,

- 시작과 끝을 구분하기 위해 보통 padding(`␣`)을 붙여서 분리한다.
- `"  g"`, `" go"`, `"goo"`, `"ood"`, `"od "` 이런 식으로 3글자 단위 조각(trigram) 생성한다.
- 이렇게 쪼개진 trigrams 집합을 인덱스에 저장한다.


## 2. PostgreSQL에서의 `pg_trgm` 확장

PostgreSQL은 `pg_trgm` 확장을 통해 trigram 기반 검색을 지원한다. 아래와 같이 설치하고 인덱스를 생성한다.

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_review_reviewtext_trgm ON review USING gin (lower(reviewtext) gin_trgm_ops);
```

> **GIN**(Generalized Inverted Index)
>
> - 각 row의 값들을 **토큰/요소 단위로 분해해서 역색인(inverted index) 구조**로 저장
> - "이 값이 들어 있냐?"를 빠르게 판별
> - 예: 배열에 특정 값이 포함되어 있는지, 문자열에 특정 trigram이 있는지

## 3. 동작 원리

```sql
SELECT * FROM review WHERE lower(reviewtext) LIKE '%good%';
```

- 실행 과정

  1. 검색어 `"good"`을 trigram 집합으로 쪼갠다. (`"goo"`, `"ood"`)
  2. 인덱스에서 `"goo"` 또는 `"ood"`를 포함하는 row 후보군을 빠르게 찾는다.
  3. 후보군만 실제 문자열 비교로 최종 결과를 도출한다.


즉, **후보군을 빠르게 줄여주고 나머지 검증만 하기 때문에 성능이 크게 향상**된다.

## 4. 특징

**장점**

- **부분 문자열 검색 지원**
  
   - `%good%`, `%oo%`, `o%` 같은 검색에도 인덱스 활용 가능.
   
- **유사도 검색 지원** : 철자 오류나 오타 검색에 유용
  
  - `similarity()` 함수와 결합하면 `"god"` ≈ `"good"` 같은 fuzzy matching 이 가능하다.
  
  ```
  SELECT * FROM review 
  WHERE similarity(reviewtext, 'good') > 0.3;
  ```
  

**단점**

- 문자열을 trigram으로 쪼개서 저장하므로 인덱스가 커서 저장공간이 많이 든다.
- 문자열 변경 시 trigram 인덱스도 갱신해야 하므로 write 부하가 늘어나고 Insert/Update 성능이 저하된다.
- <u>정확히 prefix search (`good%`)만 필요하다면 B-tree 인덱스가 더 효율적이다.</u>

# 3. 해결 후 실행 계획 확인

```sql
CREATE INDEX idx_review_reviewtext_trgm ON review USING gin (lower(reviewtext) gin_trgm_ops);
```

해당 인덱스를 만들고 실행계획을 확인한다.

```sql
explain
select * from review
where lower(reviewtext) like '%good%';
```

아래와 같이 나온다.

```
Bitmap Heap Scan on review  (cost=87.80..23038.73 rows=7861 width=585)
  Recheck Cond: (lower(reviewtext) ~~ '%good%'::text)
  ->  Bitmap Index Scan on idx_review_reviewtext_trgm  (cost=0.00..85.83 rows=7861 width=0)
        Index Cond: (lower(reviewtext) ~~ '%good%'::text)
```

1.  `Bitmap Index Scan on idx_review_reviewtext_trgm`
   -   `lower(reviewtext) LIKE '%good%'` 로 탐색
   -  `idx_review_reviewtext_trgm` 인덱스로 조건을 만족할 가능성이 있는 row들의 위치(rowid = TID)를 비트맵 형태로 생성한다.
   -  인덱스만 탐색하기 때문에 비용이 매우 저렴함
2.  `Bitmap Heap Scan on review`
    - 인덱스에서 가져온 비트맵(rowid 집합)을 기반으로 실제 테이블(Heap)에서 데이터를 읽는다.
    - `Recheck Cond`
      - GIN 인덱스는 후보군을 빠르게 좁히지만 **정확히 매칭되는지는 다시 확인이 필요**하다.
      - 즉, 후보 row를 실제 데이터에서 다시 확인해서 `'good'`이 정말 들어있는지 체크한다. 이 과정을 **recheck**라고 부른다.

실행 계획은 다음과 같은 흐름이다.
1. `pg_trgm` 인덱스를 활용해 "good"이 포함될 가능성이 있는 row 후보를 모음 (`Bitmap Index Scan`)
2. 후보 row들을 테이블에서 읽고 실제 조건 재검증 (`Bitmap Heap Scan`)
3. 최종적으로 매칭되는 row 반환

# 4. 추가 개념: gin 인덱스

## 1. 기본 개념

- **GIN (Generalized Inverted Index)** 는 말 그대로 **역색인(inverted index)** 이다.
- RDBMS에서 보통 인덱스(B-tree)는 `값 → row 위치` 구조인데,
- **GIN은 `토큰(요소) → row 목록` 구조**로 저장한다.

즉,

- B-tree: `"홍길동"` → rowid=123
- GIN: `"홍"`, `"길"`, `"동"` 각각 → [rowid=123, rowid=456, …]

## 2. 인덱스 구조

GIN 인덱스는 크게 두 계층으로 나뉜다.

- **Entry Tree**
  - 인덱스의 "키"(= 토큰, trigram, 단어 등)를 관리하는 B-tree 구조
  - 예: `"goo"`, `"ood"`, `"app"` 같은 trigram 키
- **Posting List / Posting Tree**
  - 해당 키를 가진 row들의 목록(row TID)을 저장
  - row가 적으면 메모리에 바로 올릴 수 있는 **posting list** 형태
  - row가 많아지면 별도의 B-tree인 **posting tree**로 분리 저장

------

## 3. 쓰기(INSERT/UPDATE) 시 동작

1. 새 row 삽입하면 해당 컬럼 값이 토큰화된다.
   - 예: `"good"` → `"goo"`, `"ood"`
2. 각각의 토큰을 **Entry Tree**에서 찾아 위치를 확인한다.
3. 해당 키에 rowid를 **posting list**에 추가한다.
4. posting list가 너무 커지면 → posting tree로 분리한다.

이 때문에 GIN은 **쓰기 비용이 크다** (토큰 분해 + 여러 곳에 rowid 삽입)

------

## 4. 읽기(SELECT) 시 동작

1. 쿼리 조건을 토큰으로 분해
   - 예: `LIKE '%good%'` → `"goo"`, `"ood"`
   - FTS `"app & name"` → `"app"`, `"name"`
2. Entry Tree에서 해당 토큰을 찾아 posting list/tree 를 얻는다.
3. 교집합/합집합 연산으로 후보 rowid 집합을 생성
   - `"goo"`와 `"ood"` 둘 다 있어야 함 → 교집합
4. 후보 rowid에 대해 실제 데이터 확인( recheck ) → 최종 결과 반환

이 구조 덕분에 **부분 검색/포함 검색**이 빠르다.

## 5. 예시: LIKE '%good%'

1. `"good"` → `"goo"`, `"ood"`
2. Entry Tree에서 `"goo"`, `"ood"` 키를 찾음
3. 각 키가 가진 posting list에서 rowid 모음
   - `"goo"` → [1, 5, 8]
   - `"ood"` → [5, 8, 12]
4. 교집합 → [5, 8]
5. row 5, 8에서 실제 문자열 비교 후 최종 결과 확정

## 6. 장단점

- **장점**
  - 부분 문자열 검색, 배열 포함, JSONB 키 검색, Full Text Search에 강력
  - 후보군을 줄이는 데 최적화 → 큰 테이블에서 효과 극대화
- **단점**
  - 인덱스 크기가 큼 (토큰 단위로 쪼개 저장)
  - 쓰기 성능이 느림 (row 추가 시 많은 토큰 업데이트 필요)
  - 항상 recheck 과정이 필요 → 100% 인덱스만으로 끝나지 않음

- 읽기는 빠르지만, 쓰기는 무겁고 인덱스 크기도 크다
- 따라서 보통 **읽기 위주 workload** (검색, 로그 분석, 텍스트 검색 등)에 적합하다.

<Footer/>