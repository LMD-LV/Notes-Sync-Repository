---
tags: [Java与大数据, 概念]
created: 2026-08-02
domain: Java与大数据
source: 个人总结
---

## 概述

springboot的主要作用是整合框架，内嵌tomcat,使用的时候，先将spring-boot-starter-parent定义为父工程，然后根据使用到的场景，使用相应的starter，其starter的父项目是 spring-boot-dependencies

其中springboot整合了该场景中涉及的各种组件，想要实现对其中的组件，自定义版本号，可以使用maven的就近原则，更换具体组件的版本号，每个组件都有相应的配置类，使用默认的约定，设定了相关的配置，可以在 application.properties/yml (properties 优先级更高) 中修改相关的配置，组件会按照key读取具体的配置覆盖默认。

每个场景的starter都会导入一个spring-boot-starter，是基础starter，其又导入了一个spring-boot-autoconfigure，其中设定了各种场景的自动配置类，但是不是全部启用，导入了什么场景就会开启哪个配置类。springboot默认是不扫描其中指定好的配置类。

springboot中设定了main主类作为程序执行入口，所以需要spingboot自己的打包插件，该类上使用 @SpringBootApplication注释，改注释有指定修饰的类为配置的作用，其所在的平级和子集的文件都会被扫描到ioc容器中，但是sprinboot中指定了相关的配置类不会注定扫描到IOC中，需要手动添加

## 注释解读

#### 主程序

1.  `@SpringBootApplication`由三个注解组成`@SpringBootConfiguration`、`@EnableAutoConfiguratio`、`@ComponentScan`

-   `@ComponentScan` 确实扫描不到 spring-boot-autoconfigure 包中的配置类
-   但 `@EnableAutoConfiguration` 通过另一种方式（Import）把这些配置类加载进来了

2.  @ConditionalOnMissingClass || @ConditionalOnClass 是按照具体的条件确定类是否加载
3.  springboot中将bean注入ioc容器，可以使用 @Bean 的方式，导入第三方无法编辑的时候可以使用@Import 的方式注入，
4.  **@ConfigurationProperties： 声明组件的属性和配置文件哪些前缀开始项进行绑定@EnableConfigurationProperties：快速注册注解：**

-   **场景：**SpringBoot默认只扫描自己主程序所在的包。如果导入第三方包，即使组件上标注了 @Component、@ConfigurationProperties 注解，也没用。因为组件都扫描不进来，此时使用这个注解就可以快速进行属性绑定并把组件注册进容器

`@Component` 和 `@Bean` 的主要区别：

前者能修饰在TYPE类上，后者是方法和注释上

前者是修饰后通过类路径扫描自动装配，后者是 通过方法调用手动装配

前者的bean的名称是小写的类名，后者是小写的被修饰的方法名称

后者会更灵活，常见的场景是导入第三方的类

  

  

ConditionalOnClass

ConditionalOnBean

有什么本质的区别嘛

  

对象转化成json 和直接序列器 有什么区别

  

apifox的基本了解

  

dubbo

  

使用docke部署的kafka，在连接发送请求的时候，报错找不到kafka，说是因为host域名解析的问题，但是配置文件中不是已经确定了kafka的ip地址端口号了吗，docekr中的host的作用是什么

  

消费者将接受到的消息，序列化转成对象，存储

  

  

  

  

  

