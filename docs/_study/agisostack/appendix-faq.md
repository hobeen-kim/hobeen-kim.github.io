---
title: "부록 A. FAQ·릴리스·라이선스"
description: "AgIsoStack++ 공식 FAQ 3문항, 릴리스 정책, MIT 라이선스와 특허 관련 법적 주의사항, 그리고 실전 트러블슈팅 표."
date: 2026-07-20
tags: [AgIsoStack, ISOBUS, FAQ, 라이선스]
---

# 부록 A. FAQ·릴리스·라이선스

## 공식 FAQ

### 전송 프로토콜로 큰 CAN 메시지를 보내면 현재 스레드가 블로킹되나?

<strong>아니다.</strong> 모든 송신은 비동기다.

`send_can_message()`는 메시지를 큐에 넣고 곧바로 반환한다. 실제 프레임 분할과 전송은 [CH17](/study/agisostack/17-hardware-interface)에서 본 주기 스레드가 담당한다. 그래서 1785바이트짜리 TP 메시지를 보내든 오브젝트 풀 전체를 올리든 호출한 스레드가 멈춰 있지는 않는다.

이 말은 반대로, <strong>반환값이 "전송 성공"을 의미하지 않는다</strong>는 뜻이기도 하다. `send_can_message()`가 `true`를 돌려줬다는 건 세션이 시작됐다는 것이지 상대가 받았다는 것이 아니다. 진행 상황이나 완료 여부가 필요하면 [CH19](/study/agisostack/19-api-reference)에서 정리한 `get_active_transport_protocol_sessions()`로 세션을 조회하거나, 애플리케이션 계층 인터페이스가 제공하는 콜백을 쓴다.

### `undefined reference to 'pthread_create'` 오류가 나면?

빌드 마지막 링크 단계에서 이런 형태의 에러가 난다면,

```text
/usr/bin/ld: AgIsoStack-plus-plus/socket_can/libSocketCANInterface.so: undefined reference to `pthread_create'
collect2: error: ld returned 1 exit status
make[2]: *** [CMakeFiles/isobus_hello_world.dir/build.make:86: isobus_hello_world] Error 1
make[1]: *** [CMakeFiles/Makefile2:285: CMakeFiles/isobus_hello_world.dir/all] Error 2
make: *** [Makefile:130: all] Error 2
```

CMake가 스레드 라이브러리를 실행 파일에 링크하도록 해 주면 된다.

```cmake
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads)

target_link_libraries(<your executable name> PRIVATE isobus::Isobus isobus::HardwareIntegration Threads::Threads)
```

원인은 단순하다. 스택은 수신 스레드와 주기 스레드를 돌리기 때문에 pthread에 의존하는데, 최종 실행 파일이 `Threads::Threads`를 링크하지 않으면 심볼이 해결되지 않는다. `find_package(Threads)`만 하고 `target_link_libraries`에 넣지 않는 실수가 가장 흔하다.

### 그 밖의 문제는 어디에 물어보나?

프로젝트 GitHub의 이슈 페이지에 이슈를 등록하면 된다.

```text
https://github.com/Open-Agriculture/AgIsoStack-plus-plus/issues
```

## 릴리스

원문 Releases 문서는 현재 한 줄이다. <strong>"첫 정식 안정 릴리스를 준비 중이니 나중에 다시 확인하라(Check back soon for our first stable release!)"</strong>.

즉 이 글을 쓰는 시점 기준으로 공식 문서가 안내하는 안정 릴리스 버전 번호는 없다. 실무에서 버전을 고정해야 한다면 이렇게 접근한다.

| 방법 | 어떻게 | 비고 |
| --- | --- | --- |
| GitHub Releases / 태그 확인 | 저장소의 Releases·Tags 페이지 | 문서보다 저장소 쪽이 항상 최신이다 |
| 커밋 해시로 고정 | `FetchContent` 또는 서브모듈에서 `GIT_TAG`에 커밋 해시 지정 | 재현 가능한 빌드를 원하면 이 방법이 가장 안전하다 |
| `main` 추적 | `GIT_TAG main` | 최신 기능은 빠르게 받지만 깨질 위험이 있다 |
| Arduino Library Manager | `AgIsoStack-Arduino` 저장소가 버전 관리를 한다 | Arduino 생태계에 맞춰 별도 배포된다 |

::: tip 프로젝트 통합 시 권장
[CH5. 설치와 프로젝트 통합](/study/agisostack/05-installation)에서 다룬 `FetchContent` 방식을 쓰되, `GIT_TAG`에는 브랜치 이름이 아니라 <strong>커밋 해시</strong>를 박아 두는 편이 좋다. 안정 릴리스 태그가 아직 없는 상태에서 `main`을 그대로 추적하면 어느 날 갑자기 빌드가 깨져도 원인을 특정하기 어렵다.
:::

## 라이선스

AgIsoStack++는 <strong>MIT 라이선스</strong>다.

```text
MIT License

Copyright (c) 2022-2024 The Open-Agriculture Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

정리하면 상업적 이용, 수정, 배포, 재라이선스, 판매 전부 허용된다. 조건은 저작권 고지와 라이선스 전문을 사본 또는 실질적 부분에 포함시키는 것 하나다. 그리고 소프트웨어는 <strong>어떤 보증도 없이 "있는 그대로"</strong> 제공된다. 조향이나 살포처럼 사람과 재산에 직접 영향을 주는 기능을 구현한다면 이 문장의 무게를 가볍게 보면 안 된다.

## 기타 법적 사항

::: warning 원문 "Other Legal Stuff"의 특허 관련 고지
<strong>ISO 11783 준수에는 CAN 프로토콜에 관한 특허의 사용이 관련될 수 있다는 주장이 제기되어 있다.</strong> 여기서 말하는 CAN 프로토콜은 이 프로젝트 전반과 ISO 11783 / J1939 표준에서 다루는 그 CAN이다.

<strong>Adrian Del Grosso를 비롯한 이 프로젝트의 어떤 기여자도 해당 특허의 증거·유효성·범위에 대해 어떠한 입장도 취하지 않는다.</strong>

<strong>ISO 11783과 J1939의 일부 요소는 위에서 언급한 특허 외의 다른 특허권의 대상일 수 있다. 이 프로젝트의 어떤 구성원도 그러한 특허권을 식별할 책임을 지지 않는다.</strong>
:::

이 고지가 실무에서 의미하는 바를 몇 가지로 풀면 이렇다.

- <strong>라이선스와 표준 준수는 별개다.</strong> MIT 라이선스는 이 <strong>코드</strong>를 쓸 권리를 준다. ISO 11783 <strong>표준 자체</strong>를 구현·판매할 때 발생할 수 있는 특허·인증 문제까지 해결해 주지 않는다.
- <strong>ISO 11783 표준 문서는 유료다.</strong> 이 라이브러리가 무료라고 해서 표준 원문이 무료가 되는 것은 아니다. 정확한 규격이 필요하면 ISO에서 구매해야 한다.
- <strong>AEF 인증은 별도 절차다.</strong> AgIsoStack++를 쓴다고 해서 AEF 적합성 인증을 받은 제품이 되는 것이 아니다. 프로젝트는 AEF와 무관하며 AEF의 승인을 받은 적도 없다. 상업 제품이라면 인증 트랙을 따로 밟아야 한다.
- <strong>제조사 코드를 빌려 쓰는 데도 조건이 있다.</strong> 프로젝트는 자신들의 SAE/ISOBUS 제조사 코드 <strong>1407(십진)</strong>을 비영리 목적이면 써도 좋다고 허용한다. 다만 영리 목적으로 판매하는 제품이라면 SAE에서 <strong>직접 제조사 코드를 발급받으라</strong>고 요청하고 있다.

## 실전 트러블슈팅

앞 챕터들에서 다룬 범위 안에서, 실제로 자주 부딪히는 증상들을 정리했다.

### 빌드·링크 단계

| 증상 | 흔한 원인 | 확인할 것 |
| --- | --- | --- |
| `undefined reference to 'pthread_create'` | 실행 파일에 `Threads::Threads` 미링크 | 위 FAQ 항목의 CMake 3줄 |
| `isobus/isobus/can_network_manager.hpp` 를 못 찾음 | 타겟 링크 누락 또는 include 경로 문제 | `target_link_libraries`에 `isobus::Isobus`가 있는지 |
| SocketCAN 관련 심볼 미해결 | `isobus::HardwareIntegration` 미링크 | 하드웨어 플러그인은 별도 타겟이다 |
| 원하는 CAN 드라이버 클래스가 없음 | CMake `CAN_DRIVER` 설정과 불일치 | `-DCAN_DRIVER=...` 값, `available_can_drivers.hpp` 확인 |

### 버스 연결과 주소 클레임

| 증상 | 흔한 원인 | 확인할 것 |
| --- | --- | --- |
| `CANHardwareInterface::start()`가 실패 | 인터페이스 미기동, 권한 부족, 채널 수 미설정 | `set_number_of_can_channels()`를 `start()` 전에 불렀는지, `canDriver->get_is_valid()` 반환값 |
| 드라이버는 valid인데 프레임이 안 들어옴 | 비트레이트 불일치, 종단 저항 문제 | 물리 계층부터 점검. ISOBUS는 250 kbit/s가 기본이다 |
| `get_address_valid()`가 계속 false | 주소 클레임이 완료되지 않음 | 스택이 주기적으로 돌고 있는지, NAME이 버스 위 다른 장치와 충돌하지 않는지 |
| 주소가 자꾸 바뀜 | 동일 NAME 중복 또는 우선순위 경쟁 | Identity Number를 장치마다 유일하게 부여했는지 |

### 파트너 매칭

| 증상 | 흔한 원인 | 확인할 것 |
| --- | --- | --- |
| 파트너를 영원히 못 찾음 | `NAMEFilter` 조건이 너무 빡빡함 | 필터를 하나씩 빼 보며 어느 조건에서 걸리는지 좁힌다 |
| 엉뚱한 장치와 매칭됨 | 필터가 너무 느슨함 | Function, Device Class, 제조사 코드 등을 추가해 조인다 |
| 파트너는 잡혔는데 응답이 없음 | 상대가 해당 PGN을 지원하지 않음 | 디버그 로깅([CH12](/study/agisostack/12-debug-logging))을 켜고 실제 트래픽을 확인 |

### Virtual Terminal

| 증상 | 흔한 원인 | 확인할 것 |
| --- | --- | --- |
| VT 서버를 찾지 못함 | 버스에 VT가 없거나 주소 클레임 미완료 | 클라이언트 상태 기계가 어느 단계에서 멈췄는지 로그로 확인 |
| 오브젝트 풀 업로드가 실패 | IOP 버전과 VT 지원 버전 불일치, 풀 크기 초과 | VT가 보고하는 소프트키/데이터마스크 크기와 지원 버전 |
| 업로드는 되는데 화면이 이상함 | 마스크 해상도 가정과 실제 VT 해상도 차이 | VT가 알려 주는 해상도에 맞춘 풀을 쓰는지 |
| ISB를 받는데 인증에서 지적당함 | 알람·아이콘 미구현 | [CH16](/study/agisostack/16-implement-messages)의 ISB 요구사항 재확인 |

### 전송 프로토콜

| 증상 | 흔한 원인 | 확인할 것 |
| --- | --- | --- |
| TP 세션이 abort로 끝남 | 상대의 수신 버퍼 부족, 타임아웃, 중복 세션 | 같은 송수신 쌍으로 동시에 여러 세션을 열려 하지 않는지 |
| 큰 메시지가 아예 안 나감 | 목적지 지정 없이 TP를 쓰려 함 | TP는 목적지 지정 통신이 전제다([CH9](/study/agisostack/09-adding-destination), [CH10](/study/agisostack/10-transport-layer)) |
| 전송이 끝났는지 알 수 없음 | 반환값을 완료로 오해 | 모든 송신은 비동기다. 세션 조회나 콜백으로 확인한다 |
| 진행률이 멈춰 있음 | 주기 스레드가 안 돌고 있음 | `CANHardwareInterface::start()` 성공 여부, 직접 이식이라면 `update()` 호출 주기 |

### Task Controller

| 증상 | 흔한 원인 | 확인할 것 |
| --- | --- | --- |
| TC 서버에 연결되지 않음 | 버스에 TC가 없거나 버전 불일치 | 서버가 보고하는 TC 버전(3 / 4)과 클라이언트 설정 |
| DDOP 업로드가 거부됨 | DDOP 구조 오류, 오브젝트 ID 충돌 | DDOP 생성 단계에서의 검증 결과([CH14](/study/agisostack/14-tc-ddop)) |
| 값이 갱신되지 않음 | 프로세스 데이터 요소 등록 누락 | 클라이언트에 등록한 DDI와 요소 번호가 DDOP와 일치하는지 |

::: info 어느 표에도 없는 문제라면
먼저 [CH12. 디버그 로깅](/study/agisostack/12-debug-logging)의 로깅을 최대 상세도로 켜고 실제 버스 트래픽을 본다. 그래도 원인을 못 잡으면 재현 가능한 최소 예제와 로그를 첨부해서 GitHub 이슈로 올리는 게 공식 안내다.
:::

## 정리

::: tip 핵심 정리
- 전송 프로토콜 송신은 전부 비동기다. 호출 스레드는 블로킹되지 않고, 반환값도 "전송 완료"가 아니라 "세션 시작"을 뜻한다.
- `pthread_create` 링크 에러는 `set(THREADS_PREFER_PTHREAD_FLAG ON)` + `find_package(Threads)` + `Threads::Threads` 링크로 해결한다.
- 공식 안정 릴리스는 아직 없다. 재현 가능한 빌드를 원하면 커밋 해시로 고정하는 게 안전하다.
- 코드는 MIT지만, ISO 11783 준수에는 CAN 관련 특허가 얽힐 수 있고 프로젝트는 그에 대해 어떤 입장도 취하지 않는다. 표준 문서 구매, AEF 인증, 제조사 코드 발급은 전부 사용자 몫이다.
- 제조사 코드 1407은 비영리 사용에만 허용된다. 영리 제품이라면 SAE에서 직접 발급받아야 한다.
:::

## 다음 문서

[참고 자료](/study/agisostack/appendix-references)
