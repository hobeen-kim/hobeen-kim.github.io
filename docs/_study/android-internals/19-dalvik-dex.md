---
title: "CH19. Dalvik과 DEX"
description: "레지스터 기반 Dalvik VM이 스택 기반 JVM과 무엇이 다른지, DEX 파일 포맷의 헤더와 인덱스 테이블·code_item 구조, 65536 메서드 한계와 multidex, 그리고 DEX 바이트코드와 smali를 손으로 읽는 법까지 안드로이드 실행 포맷의 근본을 파고든다."
date: 2026-07-13
tags: [android, aosp, dalvik, dex, bytecode]
---

# CH19. Dalvik과 DEX

Dalvik VM 자체는 [ART](/study/android-internals/20-art-internals)로 대체돼 역사 속으로 사라졌지만, 그 유산인 <strong>DEX 파일 포맷</strong>은 지금도 모든 안드로이드 앱의 실행 단위로 그대로 남아 있다. 이 챕터는 역사보다 현재도 유효한 DEX 포맷에 비중을 둔다. 레지스터 기반 설계가 왜 나왔는지, DEX 파일이 어떻게 생겼는지, 그리고 바이트코드를 손으로 읽는 법을 익힌다. 디컴파일·최적화·보안 분석의 바닥에 깔린 지식이다.

## 학습 목표

- 레지스터 기반 Dalvik과 스택 기반 JVM의 차이, 그리고 별도 VM을 만든 이유를 이해한다.
- DEX 파일 포맷의 header·인덱스 테이블·code_item 구조를 파악한다.
- 65536 메서드 한계가 어디서 오는지와 multidex 해법을 안다.
- 주요 DEX opcode와 smali 문법으로 간단한 메서드를 읽는다.
- dexdump/dexlayout 같은 도구로 DEX를 검사하는 법을 익힌다.

## Dalvik vs JVM

Dalvik은 2008년 안드로이드와 함께 등장한 가상 머신이다. 자바 소스를 컴파일한 `.class`(JVM 바이트코드)를 그대로 쓰지 않고, `dx`(현재는 `d8`)로 변환한 <strong>DEX(Dalvik Executable)</strong>를 실행했다. 왜 굳이 별도 VM과 포맷을 만들었을까.

가장 근본적인 차이는 <strong>레지스터 기반 vs 스택 기반</strong>이다.

![스택 기반 JVM과 레지스터 기반 DEX의 바이트코드 대비 — 같은 덧셈을 스택은 4개 명령으로 레지스터는 1개 명령으로 표현](/images/study-android-internals/19-register-vs-stack-light.png)
![스택 기반 JVM과 레지스터 기반 DEX의 바이트코드 대비 — 같은 덧셈을 스택은 4개 명령으로 레지스터는 1개 명령으로 표현](/images/study-android-internals/19-register-vs-stack-dark.png)

JVM은 <strong>스택 기반</strong>이다. `a = b + c`를 하려면 b를 스택에 push(`iload`), c를 push(`iload`), 더해서(`iadd`) 결과를 스택에 남기고, 다시 변수에 저장(`istore`)한다—명령 4개. 각 명령은 짧지만 피연산자를 스택에서 매번 넣고 빼야 해 명령 수가 많고, 그만큼 명령 인출(fetch/decode) 오버헤드가 크다.

Dalvik은 <strong>레지스터 기반</strong>이다. 메서드마다 여러 가상 레지스터(`v0`, `v1`, ...)가 있고, `add-int v0, v1, v2`처럼 피연산자와 목적지를 명령 하나에 직접 담는다—명령 1개. 명령 수가 줄고 명령당 정보량이 많아, 인터프리터가 명령을 인출·디코드하는 횟수가 줄어든다. 초기 모바일처럼 인터프리터 오버헤드가 크리티컬한 환경에서 유리한 선택이었다.

DEX를 만든 다른 이유는 <strong>크기와 공유</strong>다. 앱은 여러 `.class`로 나뉘지만 DEX는 모든 클래스를 <strong>하나의 파일</strong>로 묶고, 문자열·타입·메서드 이름 같은 상수를 <strong>공유 풀</strong>에 한 번만 저장한다. 여러 `.class`가 각자 상수 풀을 갖는 JVM 대비 중복이 크게 줄어 APK 크기가 작아진다.

<strong>Dalvik에서 ART로의 전환</strong>은 간결히만 짚는다. Dalvik은 JIT(Just-In-Time) 인터프리터였다. Android 4.4에서 실험적으로 ART가 등장하고, <strong>5.0에서 ART가 Dalvik을 완전히 대체</strong>했다. ART는 초기엔 순수 AOT(설치 시 전체 컴파일)였다가 7.0에서 다시 인터프리터+JIT+프로파일 기반 AOT 하이브리드로 진화한다. 이 이야기는 [CH20](/study/android-internals/20-art-internals)에서 다룬다. 중요한 것은 <strong>실행 엔진은 바뀌었어도 입력 포맷인 DEX는 그대로</strong>라는 점이다.

## DEX 파일 포맷 심층

`classes.dex`는 잘 정의된 바이너리 구조다. 크게 <strong>header → 인덱스 테이블들 → data</strong> 순으로 배치된다.

![classes.dex의 섹션 순서(header·string_ids·type_ids·proto_ids·field_ids·method_ids·class_defs·data)와 method_id가 type_id·proto_id·string_id를 참조하는 관계](/images/study-android-internals/19-dex-format-light.png)
![classes.dex의 섹션 순서(header·string_ids·type_ids·proto_ids·field_ids·method_ids·class_defs·data)와 method_id가 type_id·proto_id·string_id를 참조하는 관계](/images/study-android-internals/19-dex-format-dark.png)

- <strong>header</strong>는 파일 시작에 온다. 매직(`dex\n035\0` 등 버전), 파일 전체의 Adler-32 <strong>checksum</strong>, SHA-1 <strong>signature</strong>, 파일 크기, 그리고 뒤따르는 각 섹션의 개수와 오프셋이 담긴다. 런타임은 checksum·signature로 무결성을 먼저 확인한다.
- <strong>string_ids</strong>는 파일 안 모든 문자열 상수(클래스명·메서드명·리터럴)의 인덱스다. 실제 문자열 바이트는 data 영역에 있고 여기엔 오프셋만 있다.
- <strong>type_ids</strong>는 타입(클래스·인터페이스·기본형)의 인덱스로, 각 항목은 string_ids를 가리켜 타입 이름을 참조한다.
- <strong>proto_ids</strong>는 메서드 <strong>시그니처(프로토타입)</strong>—반환 타입과 파라미터 타입 목록—의 인덱스다.
- <strong>field_ids</strong>는 필드(정의 클래스·타입·이름)의 인덱스, <strong>method_ids</strong>는 메서드(정의 클래스·시그니처·이름)의 인덱스다. 그림처럼 method_id 하나가 type_id(정의 클래스)·proto_id(시그니처)·string_id(메서드명)를 동시에 참조한다.
- <strong>class_defs</strong>는 클래스 정의다. 슈퍼클래스, 구현 인터페이스, 필드·메서드 목록, 그리고 각 메서드의 코드로 이어지는 링크를 담는다.
- <strong>data / code_item</strong>은 실제 본문이다. 문자열 바이트, 그리고 각 메서드의 <strong>code_item</strong>—사용 레지스터 수, 인자 개수, 바이트코드 명령 배열, try/catch 정보, 디버그 정보—이 여기 들어간다.

이 구조 덕에 여러 DEX가 문자열·타입 풀을 공유하는 효과를 내고, 인덱스 참조로 중복을 없앤다. 포맷을 눈으로 확인하려면 `dexdump`를 쓴다.

```bash
# APK에서 DEX 추출
unzip app.apk classes.dex

# 헤더·클래스·메서드 덤프
dexdump -f classes.dex | sed -n '1,30p'     # 헤더(-f)
dexdump -d classes.dex | sed -n '1,60p'     # 바이트코드 디스어셈블(-d)

# dexlayout: 프로파일 기반 재배치·통계
dexlayout -o /tmp -w /tmp classes.dex
```

`dexlayout`은 DEX를 재배치(hot 메서드를 앞으로 모으는 등)하거나 구조 통계를 뽑는 도구로, ART의 CDEX 최적화와도 관련된다.

## 65536 메서드 한계와 multidex

DEX에서 method_ids를 참조하는 명령(`invoke-*`)의 메서드 인덱스는 <strong>16비트</strong>다. 그래서 하나의 DEX가 참조할 수 있는 메서드는 <strong>2^16 = 65536개</strong>가 상한이다. 이 숫자는 앱이 <em>정의한</em> 메서드뿐 아니라 <strong>참조하는 모든 메서드</strong>(프레임워크·라이브러리 포함)를 합친 값이라, 의존성이 많은 앱은 의외로 쉽게 넘어선다. 넘으면 빌드가 그 유명한 `Too many field/method references` 오류로 실패한다.

해법이 <strong>multidex</strong>다. 클래스를 여러 DEX 파일(`classes.dex`, `classes2.dex`, `classes3.dex`, ...)로 나눠 각 DEX가 자신의 64K 한계를 따로 갖게 한다. 각 DEX가 자체 인덱스 공간을 가지므로 전체 메서드 수는 사실상 제한이 없어진다.

```
app.apk
 ├─ classes.dex     ← 첫 64K 메서드 참조
 ├─ classes2.dex    ← 다음 묶음
 └─ classes3.dex    ← ...
```

Android 5.0(ART) 이상에서는 런타임이 모든 `classesN.dex`를 기본으로 로드하므로 multidex가 투명하게 동작한다. 5.0 이전 Dalvik에서는 부팅 시 첫 DEX만 자동 로드돼, `MultiDex.install()`을 앱 초기화에서 명시적으로 불러 나머지를 로드해야 했다. `field_ids` 참조도 같은 16비트 제약을 받는다.

## DEX 바이트코드 읽기

바이트코드를 직접 읽을 수 있으면 디컴파일 결과를 검증하고 최적화·난독화를 이해하는 데 큰 도움이 된다. 사람이 읽기 쉬운 형태가 <strong>smali</strong>(baksmali가 만드는 어셈블리 표기)다.

먼저 자주 보는 opcode 부류를 알아둔다.

- <strong>이동/상수:</strong> `move v0, v1`(레지스터 복사), `const/4 v0, 0x1`·`const-string v0, "hi"`(상수 로드).
- <strong>연산:</strong> `add-int v0, v1, v2`, `mul-int/lit8 v0, v1, 0x2`(리터럴 곱), `sub-int` 등. 접미사(`-int`, `-long`, `-float`)가 타입을 지정한다.
- <strong>필드 접근:</strong> `iget`/`iput`(인스턴스 필드), `sget`/`sput`(정적 필드).
- <strong>메서드 호출:</strong> `invoke-virtual`(가상 디스패치), `invoke-static`, `invoke-direct`(생성자·private), `invoke-super`. 반환값은 뒤이은 `move-result`로 받는다.
- <strong>분기/반환:</strong> `if-eqz v0, :label`(0이면 점프), `goto`, `return-void`, `return v0`.

이제 간단한 메서드를 smali로 읽어보자. 자바 원본은 다음과 같다.

```java
int square(int x) {
    return x * x;
}
```

이를 baksmali로 풀면 대략 이렇게 나온다.

```
.method square(I)I
    .registers 3            # v0, v1(=this는 p0), 파라미터 포함 총 3개 레지스터
    .param p1, "x"          # p1 = 첫 번째 파라미터 x

    mul-int v0, p1, p1      # v0 = x * x
    return v0               # v0 반환
.end method
```

읽는 요령은 이렇다. `.registers`는 이 메서드가 쓰는 레지스터 총수이고, `p0`는 인스턴스 메서드의 `this`, `p1`부터가 실제 파라미터다(파라미터 레지스터 `pN`은 지역 레지스터 `vN` 뒤에 매핑된다). `mul-int v0, p1, p1`은 "p1과 p1을 곱해 v0에 넣어라", `return v0`은 v0을 반환하라는 뜻이다. 시그니처 `(I)I`는 proto—`int` 하나를 받아 `int`를 반환—를 나타낸다.

조금 더 복잡한 조건 분기도 패턴은 같다.

```
.method isPositive(I)Z
    .registers 2
    if-lez p1, :not_pos     # p1 <= 0 이면 :not_pos로 점프
    const/4 v0, 0x1         # v0 = true
    return v0
    :not_pos
    const/4 v0, 0x0         # v0 = false
    return v0
.end method
```

`if-lez`(less-than-or-equal-zero)로 분기하고, 레이블(`:not_pos`)로 흐름이 갈린다. 이 정도 문법만 익혀도 jadx가 자바로 복원하지 못한 난독화 코드나 최적화 흔적을 바이트코드 수준에서 따라갈 수 있다. smali를 만들고 되돌리는 도구는 [CH18의 디컴파일 절](/study/android-internals/18-app-anatomy)에서 소개한 apktool/baksmali다.

## Dalvik JNI와 레거시

Dalvik 시절의 [JNI](/study/android-internals/18-app-anatomy) 구현도 간결히만 언급한다. Dalvik은 네이티브 메서드 호출 시 인디렉트 레퍼런스 테이블로 로컬/글로벌 레퍼런스를 관리했고, 이 기본 규약은 ART에서도 이어진다. Dalvik 고유의 `dexopt`(설치 시 DEX를 최적화한 `odex` 생성)와 verification 단계는 ART의 dex2oat·VDEX로 대체됐다. 즉 <strong>개념적 뼈대는 유지되고 구현이 현대화</strong>됐다고 보면 된다. 오늘날 실무에서 순수 Dalvik을 만날 일은 없지만, DEX 포맷과 JNI 규약이라는 유산은 여전히 매일 마주치는 대상이다.

::: tip 핵심 정리
- Dalvik은 레지스터 기반 VM으로, 스택 기반 JVM보다 명령 수가 적어 인터프리터 오버헤드를 줄이려는 설계였고, DEX는 상수 풀 공유로 앱 크기를 줄인다.
- DEX는 header → string/type/proto/field/method_ids → class_defs → data(code_item) 구조이며, method_id가 type/proto/string_id를 참조한다.
- invoke 명령의 메서드 인덱스가 16비트라 DEX당 65536 메서드 한계가 생기고, multidex(classesN.dex)로 이를 넘는다.
- DEX 바이트코드는 레지스터 명령(add-int v0, v1, v2 등)이며, smali 표기로 .registers·pN·invoke-*·if-* 패턴을 읽을 수 있다.
- dexdump/dexlayout으로 DEX 구조를 검사하며, Dalvik의 dexopt·JNI 규약은 ART에서 현대화돼 이어진다.
:::

## 다음 챕터

[CH20. ART 내부 구조](/study/android-internals/20-art-internals)에서는 com.android.art APEX 구성, OAT/ART/VDEX/CDEX 파일의 역할, dex2oat 컴파일 전략과 compiler filter, JIT·프로파일·CC GC, 그리고 임베디드 기기의 first-boot dexopt 최적화를 다룬다.
