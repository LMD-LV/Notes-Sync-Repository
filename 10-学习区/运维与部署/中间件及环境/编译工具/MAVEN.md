## 通识

1.  maven负责java项目的构建，依赖管理
2.  一个完整的过程，编译，测试，报告，打包，部署， 有的时候构建失败导致编译的不完整，清除后重新编译
3.  有的时候导入的依赖失败等，依赖下载到一半失败了，会出现一个最新的latest文件，删除并重新加载依赖
4.  项目构建是一个完整的过程，包括：

-   编译（.java -> .class）
-   资源处理（复制配置文件等）
-   依赖处理
-   打包（生成 jar/war）
-   单元测试
-   部署等

5.  maven的使用指令

-   clean： 清理命令，执行clean会删除target目录, 即清理掉上一次项目构建产生的文件
-   compile： 编译命令，作用是将 src/main/java 下的文件(正式的java文件)编译为class文件输出到target目录下
-   test： 测试命令，作用是执行 src/test/java 下的测试类，并编译为class文件输出到target目录下
-   package： 打包命令，打的是所有的正式代码(src/main) 对于java工程执行package打成jar包，对于web工程打成war包
-   install： 安装命令，将打好jar包或者war包安装到本地maven仓库
-   deploy： 部署命令，将打好的jar包或war包部署到私服中

6.  导入依赖的时候，通过scope来设置依赖的生效范围

-   compile： 默认依赖范围，作用域在编译、测试、运行时都有效。
-   test：作用域在测试时有效。编译和运行时不需要，比如：Junit。
-   provided：作用域在编译、测试时有效。运行时不需要，比如servlet-api被tomcat容器提供。
-   runtime：作用域在测试、运行时有效。编译时不需要，比如：jdbc的驱动包。

​