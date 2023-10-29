---
categories: "Kotlin"
tag: ["setter", "constructor"]
title: "[Kotlin] 코틀린과 JPA 를 함께 쓸 때 생각할 부분"
description: "setter, 생성자, data 클래스에 관한 내용입니다."
---

*[인프런 강의](https://www.inflearn.com/course/java-to-kotlin-2/dashboard) 내용 중 일부입니다.*

# setter

Java 에서 JPA Entity 사용 간, 필드에 대한 캡슐화를 위해서 Setter 는 닫아뒀습니다. Kotlin 에서도 비슷하게 구현할 수 있습니다.

## backing property

```kotlin
class User(
	private var _name: String
) {
	val name: String
		get() = this._name
}

```

실제 값인 `_name` 은 `private` 으로 접근을 막고, 읽기 전용으로 추가 프로퍼티 `name` 을 만듭니다.

## custom setter 사용

```kotlin
class User(
	name: String // 프로퍼티가 아닌, 생성자 인자로만 name을 받는다
) {
    var name = name
    private set
}
```

User의 생성자에서 name을 프로퍼티가 아닌, 생성자 인자로만 받고 이 name을 변경가능 한 name 프로퍼티로 넣어주되, name 프로퍼티에 private setter를 달아두는 방법입니다.

## setter 를 열어두되 사용하지 않는 방법

```kotlin
class User(
	var name: String
) {

}
```

위 두 방법도 괜찮지만 필드가 많아질 수록 번거롭고 코드가 복잡해진다는 단점이 있습니다. 따라서 setter 를 열어두되, 팀 내 컨벤션으로 setter 를 사용하지 않는 방법도 있습니다. (**Trade-off 의 영역**)

# 생성자 안의 프로퍼티, 클래스 body 안의 프로퍼티

```kotlin
@Entity
class User(
    var name: String,
    val age: Int?,
) {
	@OneToMany(mappedBy = "user", cascade = [CascadeType.ALL], orphanRemoval = true)
	val userLoanHistories: MutableList<UserLoanHistory> = mutableListOf(),

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	val id: Long? = null,
}
```

위 코드에서 프로퍼티는 생성자 안과 클래스의 body 안에 분산되어 있습니다. 어느 곳에 있든 동작은 합니다. 테스트를 하기 위한 객체를 만들어 줄 때도 정적 팩토리 메소드를 사용하다 보니 프로퍼티가 안에 있건, 밖에 있건 두 경우 모두 적절히 대응 할 수 있습니다.

하지만 명확한 가이드가 있다면 더 좋습니다. 예를 들어,

1. 모든 프로퍼티를 생성자에 넣기
2. 프로퍼티를 생성자 혹은 클래스 body 안에 구분해서 넣을 때 명확한 기준이 만들기

등의 팀 컨벤션이 있어야 합니다.

# TIP : Entity (Class) 가 생성되는 로직을 찾고 싶은 경우

```kotlin
@Entity
class User constructor(
    var name: String,
    val age: Int?,
)
```

, constructor 지시어를 명시적으로 작성하고 추적하면 생성자가 호출되는 곳만 추적된다.
