可以通过代码改变字节码的框架

读取方式大致为通过以下代码

```java
byte[] classByteArray = Files.readAllBytes("/字节码文件路径/xxxx.class")
```

获得class文件内容，并且通过框架使用输出被更改的byte[]格式的内容

## 主要应用场景

动态代理，aop，监控（SkyWalking，pinpoint），反编译，安全扫描，干不被发现情况删库

## 主要分类

### 源码编辑型

操作难度小，掌握java语言即可，功能少，性能略差，框架jar包体积较大

主要代表框架Javassist(hivernate的底层实现)

javassist使用方法：自己看官网[https://www.javassist.org/](https://www.javassist.org/)

### 指令编辑型

操作难度很大，需要了解class文件结构和指令，功能强大，可实现从方法中间插入逻辑，性能高，框架jar包体积小

主要代表框架ASM(java8 中lambda表达式的底层实现，bytebuddy底层实现，sping aop的部分底层实现)

asm使用方法：自己看官网[https://asm.ow2.io/asm4-guide.pdf](https://asm.ow2.io/asm4-guide.pdf)

## 其他类型

基于上面2种发展出来各种

bytebuddy

​  

具体框架使用不做具体教学，需要请查询各个官方网址

​