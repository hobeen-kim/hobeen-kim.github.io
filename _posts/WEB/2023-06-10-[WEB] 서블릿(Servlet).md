---
categories: "WEB"
tag: ["tomcat", "servlet"]
---

# Web Server 와 WAS(Web Application Server)

​	초기 웹 브라우저는 HTTP 프로토콜을 기반으로 해당 url path 에 맞게 정적인 파일:pencil:(HTML, CSS, JS, 이미지 등) 만 제공하는 목적이었습니다. 이를 **웹 서버**라고 합니다. Apache, Nginx 등이 웹 서버의 예시입니다.

​	반면 **WAS** 는 웹 서버와는 달리 동적 콘텐츠를 생성하고 제공하는 역할을 합니다. 데이터베이스와의 상호작용, 비즈니스 로직의 실행 등을 할 수 있습니다. **WAS는 클라이언트의 요청에 따라 실시간으로 콘텐츠를 생성하고, 이를 웹 서버를 통해 클라이언트에게 전달**합니다. Java EE, ASP.NET, PHP 등의 플랫폼에서 동작하는 Tomcat, JBoss, WebLogic 등이 WAS의 예시입니다.

​	물론 이 두 개념이 분리되어 운용되지 않습니다. 예를 들어 T**omcat 은 기본적으로 HTTP 서버 기능도 가지고 있어서, 웹 서버처럼 정적인 콘텐츠를 제공하는 역할도 수행할 수 있습니다**. 이는 Tomcat이 HTTP 요청을 받아서 처리하고 응답을 보낼 수 있기 때문입니다. 따라서 Tomcat은 웹 서버와 WAS의 기능을 모두 가지고 있다고 볼 수 있습니다.

​	**그러나 실제 대규모 프로덕션 환경에서는, 웹 서버(Apache HTTP Server, Nginx 등)와 WAS(Tomcat 등)를 분리하여 운영하는 경우가 많습니다**. 이는 각각의 서버가 최적화된 작업을 수행하게 하여 전체 시스템의 성능을 향상시키기 위한 것입니다. 웹 서버는 정적 콘텐츠를 빠르게 제공하고, 동적 콘텐츠가 필요한 경우에만 WAS에 요청을 전달하는 방식으로 작동합니다. 이렇게 하면 WAS는 복잡한 애플리케이션 로직을 처리하는데 집중할 수 있습니다. 

# 톰캣

​	Apache Tomcat 은 웹 서버 및 자바 서블릿 컨테이너로서, 자바 웹 애플리케이션을 실행하는데 필요한 환경을 제공하는 소프트웨어입니다. **웹 서버의 기능으로는 정적 컨텐츠를 제공하는 역할**을 수행하고, **서블릿 컨테이너의 역할로는 자바 코드를 실행하며, HTTP 요청에 따른 동적 컨텐츠를 생성하는 역할**을 수행합니다.

![image-20230613205139651](../../images/2023-06-10-[WEB] 서블릿(Servlet)/image-20230613205139651.png)

​	톰캣은 Coyote, Catalina, Jasper 로 이루어져있습니다.

- **Coyote** : Tomcat의 HTTP 커넥터 부분으로, 웹 브라우저와 같은 클라이언트로부터의 네트워크 연결을 처리합니다. Coyote 는 HTTP 프로토콜을 이해하고 HTTP 요청을 처리하여, 이를 "Catalina" 컴포넌트가 이해할 수 있는 형태(Request) 로 변환합니다. 그리고 Catalina 로부터의 응답(Response) 을 다시 HTTP 응답으로 변환하여 클라이언트에게 전달합니다. 
- **Catalina** : Tomcat의 Servlet 컨테이너 부분입니다. Catalina 는 Servlet과 JSP 페이지를 처리하며, 웹 애플리케이션의 생명주기를 관리합니다. 또한, 클라이언트의 요청을 적절한 웹 애플리케이션으로 라우팅하는 역할도 담당합니다. 이 과정에서는 Coyote 컴포넌트에서 전달받은 요청을 처리하고, 응답을 생성하여 다시 Coyote 컴포넌트로 보냅니다.
- **Jasper** :  Tomcat의 JSP 엔진 부분으로, JSP 페이지를 Servlet으로 변환하는 역할을 합니다. 이렇게 변환된 Servlet은 그 후 Catalina 에 의해 처리됩니다. (현재 JSP 는 잘 사용되지 않습니다.)

이러한 톰캣은 스프링부트에서 라이브러리로 내장되어 제공되고 있습니다. 

# 서블릿

![image-20230615151310531](../../images/2023-06-10-[WEB] 서블릿(Servlet)/image-20230615151310531.png)

​	서블릿은 동적인 페이지를 생성하는 WAS 서버를 위한 기술입니다. 웹 브라우저에서 요청을 하면 해당 기능을 수행한 후 웹 브라우저에 결과를 전송합니다.

1. 클라이언트가 HTTP 요청을 보냅니다. 이 요청은 먼저 톰캣의 Coyote 컴포넌트로 들어옵니다.
2. Coyote 컴포넌트는 이 HTTP 요청을 파싱하여 `org.apache.coyote.Request` 객체와 `org.apache.coyote.Response` 객체를 생성합니다.
3. 그 다음, `org.apache.coyote.Request` 객체와 `org.apache.coyote.Response` 객체는 서블릿 컨테이너인 Catalina 로 전달됩니다.
4. Catalina는 `org.apache.coyote.Request` 객체와 `org.apache.coyote.Response` 객체를 `javax.servlet.http.HttpServletRequest` 객체와 `javax.servlet.http.HttpServletResponse` 객체로 변환합니다.
5. 그 후, Catalina는 클라이언트의 요청을 처리할 적절한 서블릿을 찾아 이 `HttpServletRequest` 객체와 `HttpServletResponse` 객체를 해당 서블릿에 전달합니다.
6. 이렇게 전달받은 `HttpServletRequest` 객체와 `HttpServletResponse` 객체는 서블릿에서 사용되어 클라이언트의 요청을 처리하고, 처리된 결과를 `HttpServletResponse` 객체에 담아서 클라이언트에게 반환합니다.
7. 클라이언트에게 반환되기 전에 `HttpServletResponse` 객체는 다시 `org.apache.coyote.Response` 객체로 변환되어 Coyote 에게 전달되고, Coyote 는 이를 HTTP 응답 형식으로 변환하여 클라이언트에게 반환합니다.

## 서블릿 구조

​	서블릿의 구조는 개략적으로 아래와 같이 생겼습니다.

```java
public class MyServlet extends HttpServlet {
	public void init(ServletConfig config) throws ServletException{
		super.init();
	}
	
	public void destroy(){
		super.destroy();
	}
	
	protected void service(HttpServletRequest request, HttpServletReponse response){
		super.service(request, response);
	}
}
```

​	서블릿 컨테이너에서 특정 reqeust 를 받으면 해당 요청에 맞는 서블릿을 생성(init) 합니다. 그리고 service 메서드로 HttpServletRequest, HttpServletReponse 받아서 동작합니다.

​	아래는 실제 HttpServlet 의 service 메서드를 개략적으로 나타낸 것입니다.

```java
public abstract class HttpServlet extends GenericServlet {

	protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {

        String method = req.getMethod();

        if (method.equals(METHOD_GET)) {
            long lastModified = getLastModified(req);
            if (lastModified == -1) {
                // servlet doesn't support if-modified-since, no reason
                // to go through further expensive logic
                doGet(req, resp);
            } else {
                long ifModifiedSince;
                try {
                    ifModifiedSince = req.getDateHeader(HEADER_IFMODSINCE);
                } catch (IllegalArgumentException iae) {
                    // Invalid date header - proceed as if none was set
                    ifModifiedSince = -1;
                }
                if (ifModifiedSince < (lastModified / 1000 * 1000)) {
                    // If the servlet mod time is later, call doGet()
                    // Round down to the nearest second for a proper compare
                    // A ifModifiedSince of -1 will always be less
                    maybeSetLastModified(resp, lastModified);
                    doGet(req, resp);
                } else {
                    resp.setStatus(HttpServletResponse.SC_NOT_MODIFIED);
                }
            }

        } else if (method.equals(METHOD_HEAD)) {
            long lastModified = getLastModified(req);
            maybeSetLastModified(resp, lastModified);
            doHead(req, resp);

        } else if (method.equals(METHOD_POST)) {
            doPost(req, resp);

        } else if (method.equals(METHOD_PUT)) {
            doPut(req, resp);

        } else if (method.equals(METHOD_DELETE)) {
            doDelete(req, resp);

        } else if (method.equals(METHOD_OPTIONS)) {
            doOptions(req, resp);

        } else if (method.equals(METHOD_TRACE)) {
            doTrace(req, resp);

        } else {
            //
            // Note that this means NO servlet supports whatever
            // method was requested, anywhere on this server.
            //

            String errMsg = Strings.getString("http.method_not_implemented");
            Object[] errArgs = new Object[1];
            errArgs[0] = method;
            errMsg = MessageFormat.format(errMsg, errArgs);

            resp.sendError(HttpServletResponse.SC_NOT_IMPLEMENTED, errMsg);
        }
    }
}
```

​	조건문을 통해 `method.equals(METHOD_XXX)` 로 어떤 메서드 요청인지 확인해서 `doXXX(req, resp);` 를 호출합니다. 즉 Get 요청이 들어오면 doGet 을 호출하고, Post 요청이 들어오면 doPost 를 호출합니다.

## 서블릿 등록/호출

​	서블릿을 등록하는 방법은 그게 두 가지로, `web.xml`을 이용하는 전통적인 방법과 자바 기반의 구성을 사용하는 스프링 방식이 있습니다. 

**web.xml**

​	먼저 `web.xml` 을 간단하게 보겠습니다. 다음과 같이 서블릿을 생성하고 해당 서블릿을 특정 url 에 매핑해줍니다.

```xml
<web-app>
    <servlet>
        <servlet-name>myServlet</servlet-name>
        <servlet-class>com.example.MyServlet</servlet-class>
    </servlet>
    
    <servlet-mapping>
        <servlet-name>myServlet</servlet-name>
        <url-pattern>/my</url-pattern>
    </servlet-mapping>
</web-app>
```

`<servlet>` 태그를 통해 서블릿 이름과 클래스를 틍록하고, `<servlet-mapping>` 태그를 통해 url 과 서블릿을 매핑합니다.

그리고 서블릿을 정의해주면 되겠죠. 아래는 MyServlet 클래스입니다.

```java
public class MyServlet extends HttpServlet {
	
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		 resp.getWriter().println("test");
	}
}
```

해당 url 로 GET 메서드가 들어오면 `test` 를 출력합니다.



**스프링 방식**

​	스프링 방식으로 서블릿을 등록하는 방법은 2가지가 있는데요. `@WebServlet` 애노테이션을 사용하는 방식과 프로그래밍 방식이 있습니다. 여기서는 서블릿 등록방법을 알아보는 건 아니니 간단한 `@WebServlet` 방식만 확인해보겠습니다. 프로그래밍 방식은 [스프링 부트 활용 웹 서버와 서블릿 컨테이너](https://hobeen-kim.github.io/inflearn/스프링-부트-활용-웹-서버와-서블릿-컨테이너/) 포스팅을 확인해보세요.

```java
@WebServlet(urlPatterns = "/my")
public class MyServlet extends HttpServlet {
    
	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		 resp.getWriter().println("test");
	}
}
```

xml 형식의 파일이 없고, `@WebServlet(urlPatterns = "/my")` 을 통해 어느 url 을 사용할지 결정합니다. 해당 url 로 GET 메서드가 들어오면 `test` 를 출력합니다.

## DispatcherServlet

​	요청마다 servlet 을 정의하면 요청 처리 로직이 분산되고, 공통 로직을 처리하기 어려운 점이 있습니다. 따라서 프론트 컨트롤러 패턴을 구현하기 위해 DispatcherServlet 을 사용합니다. 이 패턴에서 모든 웹 요청은 단일 컨트롤러(여기서는 `DispatcherServlet`)를 통해 처리되며, 이 컨트롤러는 요청을 적절한 핸들러(컨트롤러 메소드)로 라우팅합니다. 이렇게 하면 요청 처리 로직이 분산되는 것을 방지하고 중앙에서 요청 처리를 조정할 수 있습니다.

![image-20230615002628976](../../images/2023-06-10-[WEB] 서블릿(Servlet)/image-20230615002628976.png)

​	간단하게 표현하면 위 그림처럼 표현할 수 있습니다.

​	또한 DispatcherServlet 을 사용하면 **스프링의 IoC(Inversion of Control) 컨테이너와 통합되어, 의존성 주입, 트랜잭션 관리, 보안 등 스프링의 핵심 기능을 사용할 수 있게 됩니다.**

![image-20230309173306041](../../images/2023-06-10-[WEB] 서블릿(Servlet)/image-20230309173306041.png)

​	위 흐름은 DispatcherServlet 이후 핸들러를 호출하고 로직을 처리해서 View 를 응답해는 SpringMVC 구조입니다. 여기서는 서블릿까지만 알아봤습니다.

# Ref.

- [Tomcat 구조](https://naeti.tistory.com/222)
- [[10분 테코톡] 🐶 코기의 Servlet vs Spring](https://www.youtube.com/watch?v=calGCwG_B4Y&t=65s)
- [[Servlet] 서블릿(Servlet)이란?](https://velog.io/@falling_star3/Tomcat-%EC%84%9C%EB%B8%94%EB%A6%BFServlet%EC%9D%B4%EB%9E%80)