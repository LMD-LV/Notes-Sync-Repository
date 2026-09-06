spirngmvc核心做的事情，封装了 对request ，response的处理

param参数和 json参数

混合开发，返回的是一个具体的页面(html+java数据)，只能被浏览器访问，例如 android就使用不了

前后端分离

​  

thymeleaf

​  

responseBody

​  

web中讲到，重定向中不能访问web-inf下的资源，但是为什么使用springmvc提哦的重定向就可以？静态不行？

  

delete，get没有请求体

​  

filter在sprnigmvc之外拦截，handleerInterceptor在内部，可以作用于handle之前之后，及视图解析器之后

​  

spring中的两个ioc容器是什么

​  

sql中的limit的后两个参数的使用。limit 2，3；

​  

完成mvc的接口的测试，尤其是对象和json接受返回部分，

完成前端的项目部署，

ssm整合的代码注释

​  

在配置类中声明bean，和别的类中有什么区别吗

​  

### 简介

1.  将整体的架构分成

1.  controller 作用相当于servlet ，接受请求，返回数据
2.  model 处理数据，数据处理模块，和数据库对应的实体类，存储对象，数据逻辑，业务处理
3.  view 视图层 展示数据，数据交互，视图，存放前端文件，现已经可以独立衍生出去，前端工程化

2.  流程为 controller接受数据，调用相关的modole，获取处理结束的数据，并调用相关的view视图渲染数据后响应给浏览器，controller对每个请求涉及的不同类，不同的处理过程 定义不同的请求的方法 也就是控制器方法
3.  springmvc在原生的servlet的基础上，出现了dispatcherservlet，用于处理请求和响应
4.  导入springmvc的时候需要先导入 javax.servlet-api 依赖
5.  使用springmvc中的dispatcherservlet需要先在webxml中配置servlet-name，然后使用servlet-mapping，url-pattern中定义dispatcherservlet处理的请求路径，当url-pattern 定义/的时候，无法拦截jsp请求路径（这是为什么，jsp动态有什么特性？已经遗忘了）

1.  可以通过load-on-startup来定义启动的次序，可以提早启动加速请求速度

6.  通过将控制方法定义为一个控制层组件，交给ioc管理，dispatcher才知道其存在
7.  springmvc的配置文件中定义。扫描的包的路径(读取控制层组件)，配置的视图解析器的名称，处理静态资源的默认配置，注解驱动的配置，如果不配置注解驱动，此时只能访问静态资源
8.  视图解析器返回的是字符串形式的视图名称，需要在视图解析器中定义好视图的路径，
9.  sprinhMVC中常见的组件有，dispatcherServlet，handlerMapping（处理器映射），Handler，HandlerAdapater，viewResolver，view

### ReuqestMapping的属性

1.  该注释用于映射请求路径 和 处理请求的控制方法的映射关系，一般使用在controller中，该注释方法可以修饰类，方法，当类和类中的方法同时被修饰的时候，请求该方法的实际路径是 类路径+方法的路径
2.  value参数，字符串类型，支持数组的方式，可同时映射多个请求路径，当只有一个请求路径的时候，value标识可以省略
3.  method参数，用于限定请求方法的请求参数，支持匹配多种请求方式

1.  对于不同的请求方法有在requestmapping衍生类，getmapping，postmapping，putmapping，deletemapping
2.  使用浏览器发送的请求方式只有，post，get方式，如果设置了其余的方式，会被按照默认的get方式来处理，除非使用hiddenhttpmethodfilter过滤器来处理，使用该过滤器的前提是 发送的请求方式一定是post，该请求一定得传输请求参。

4.  params参数，通过设置param参数匹配其请求方法的请求参数 ，支持四种表达式匹配

1.  "param"：要求请求映射所匹配的请求必须携带param请求参数
2.  "!param"：要求请求映射所匹配的请求必须不能携带param请求参数
3.  "param=value"：要求请求映射所匹配的请求必须携带param请求参数且param=value
4.  "param!=value"：要求请求映射所匹配的请求必须携带param请求参数但是param!=value

例如 params = {"username","password!=123456"} ，就是要求必须有username，password参数，且password不能为123456

5.  同理，header参数，用于匹配请求方法的请求头，支持的表达式和语法与params一样，只是将key的名称换成header
6.  支持ant的风格，支持使用的语法 有

1.  ？：表示任意的单个字符
2.  \*：表示任意的0个或多个字符
3.  \*\*：表示任意的一层或多层目录 注意：在使用\*\*时，只能使用/\*\*/xxx的方式

7.  支持解析resulttful风格的请求方法，resultful风格就是将psot请求体中的？ 替换成/，springmvc通过requestmaping中的value {params的名称}，定义好该位置实际的key，然后通过@PathVariable注解，将占位符所表示的数据赋值给控制器方法的形参

```plain
@RequestMapping("/testRest/{id}/{username}")
public String testRest(@PathVariable("id") String id, @PathVariable("username") String username){
    System.out.println("id:"+id+",username:"+username);
    return "success";
}
//最终输出的内容为-->id:1,username:admin
```

#### 控制方法获取请求方法参数的方式

1.  形参定义为HttpServletRequest，通过这样的方式获取请求报文的对象，按照key解析出参数的值
2.  在控制方法的形参中定义和请求参数同名的方式，通过dispatcherservlet的方式获取到参数的值

1.  当出现了多个同名的请求参数的时候，将控制方法的形参定义为 数组 字符串（会按照 ， 分割 数据)的方式 获取到请求参数的值

3.  通过requestparam的方式，该注释通过 value属性，定义给行参赋值的请求参数的名称，还有required，defaultvalue属性
4.  requestHeader注释使用方式同requestParam，获取请求头信息赋值给行参
5.  CookieValue同理，将cookie数据和控制器方法的形参创建映射关系，属性同上面的两个
6.  还可以通过控制方法的行参定义个实体类，如果发送来的请求参数的名称和实体类的属性名一致，会被自动赋值
7.  处理获取的请求方法的值是乱码问题，声明一个编码过滤器，CharacterEncodingFilter，在webxml中注释下，然后在所有的拦截器之前执行，其方法setCharacterEncoding方法要求前不能有任何获取请求参数的动作

### 域对象共享数据

1.  可以通过servletAPI的方式将数据共享到request域，session域，application域，setAttribute
2.  ModelAndView的方式共享数据同时实现设置视图，实现页面跳转（其实就是一面返回数据，一面返回可以被视图解析器解析的字符串）
3.  此外还有module，map，moduleMap的方式返回值

### springmvc中的视图解析器

1.  视图的作用是渲染数据，将model中的数据展示出来，默认的有转发视图，重定向视图
2.  springmvc中支持多种实现视图的技术，当控制方法的视图名称没有前缀的时候，视图被mvc配置文件中配置好的视图解析器所解析，拼接前缀后缀之后，通过转发的方式实现
3.  当控制方法中设置的视图名称有前缀的时候，相当于按照spring中默认的处理这种前缀的视图解析器去解析，无视配置文件中配置的，常见的有

1.  转发视图，以forward作为前缀，为转发视图，默认解析器为 internalResourceView，例如forward:/testHello
2.  重定向视图，以redirect作为前缀，为重定向视图，默认解析器为RedirectView，例如 redirect:/testHello

4.  当配置文件中定义了<mvc:view-controller> 来修饰控制器方法，此时可以实现页面跳转，但是其余所有的请求映射将全部失效，除非配置 开启mvc注解驱动的标签，<mvc:annotation-driven>

### springmvc中的HttpMessageConverter

1.  httpmessageconverter用于将请求报文和java对象相互转化，提供对请求和响应的处理
2.  常用的注解和类型有

1.  @requestBody，用于控制方法的形参，该形参就是请求体
2.  @requestBody，修饰方法上，用于将方法的返回值作为响应报文响应到浏览器
3.  RestController，一个复合注解，修饰类上，作用相当于为类添加了@Controller注解，并且为其中的每个方法添加了@ResponseBody注解
4.  requestEntity，一种封装报文的类型，在控制器方法中设置为形参的类型，会自动获取请求报文的值，然后可以通过形参的 getHeaders()，getBody() 获取具体的值
5.  responseEntity，用于定义响应数据的类型

3.  springmvc中导入jackjson的依赖，配置<mvc:annotation-driven />，HandlerAdaptor中会自动装配一个消息转换器：MappingJackson2HttpMessageConverter，可以将响应到浏览器的Java对象转换为Json格式的字符串，在处理器方法上使用@ResponseBody注解进行标识，就可以实现 java对象返回到浏览器后自动转化为json格式的数据

### springMVC中的拦截器，异常处理器

1.  拦截器用于拦截控制方法的执行，需要实现HandlerInterceptor，

1.  重写三个抽象方法，

1.  prehandle，boolean类型用于判断方法是否放行
2.  posthandle，在控制器方法执行之后执行
3.  aftercompaltion，在处理完视图和模型数据后执行

2.  在配置的时候，可以使用mvc：mapping设置需要拦截的请求，exclude设置不需要拦截的请求
3.  当同时匹配了多个拦截器的时候，按照顺序，方法的执行顺序 链式执行，注意posthandle在链式过程中遇到了任意一环为false后，设计的链上的都不会再被执行。
4.  mvc中提供了处理 控制方法执行过程中出现了异常时 的处置接口。handlerExceptionResolver，其实现类有 DefaultHandlerExceptionResolver和SimpleMappingExceptionResolver，可以通过配置文件，注释来使用，使用注释的时候

1.  在类上使用 @ControllerAdvice 将当前类标记为处置异常的组件
2.  在控制方法中 使用 @ExceptionHandler（异常类类型）的方式捕获异常 ，例如 @ExceptionHandler(ArithmeticException.class)

### 使用配置类，注释实现替代spring-mvc.xml

首先定义一个实现 了 AbstractAnnotationConfigDispatcherServletInitializer 的类 ，用于ioc容器发现并配置servlet上下文，

然后定义spring的配置类，在其中定义了springConfig配置类