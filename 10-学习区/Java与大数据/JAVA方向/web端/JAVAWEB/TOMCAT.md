---
tags: [Java与大数据, 概念]
created: 2026-08-02
domain: Java与大数据
source: 个人总结
---

-   static 通常用于存放静态资源 WEB-INF 通常用于存放受保护的资源（不允许通过url直接访问）
-   lib存放依赖包，classes下的src存放源码
-   部署方式

-   编译好的项目直接放.
-   放置war包，启动后自动解压
-   放置任意指定地点，通过server.xml指定路径启动

-   application context 即为项目的上下文路径
-   idea开发时，是将tomcat复制一个副本，副本中仅有相关的配置文件，实际通过配置文件的实现部署
-   tomcat中的 war ，和war exploded 的区别，后者常用于开发的时候热部署，尤其是修改静态资源的时候，能快速看到效果，同时 war相当于将包打到tomcat中运行 读取的上下文的路径就是 tomcat所在的路径，war exploded 的路径是开发时代代码的路径

​  

​  

  

​