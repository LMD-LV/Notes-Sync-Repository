# 典型回答

  

场景题场景题，其实拆解一下就是八股文，这个问题归根结底，问你的就是如何实现分布式Session。

​  

[链接](https://www.yuque.com/hollis666/dkfgay/xbgu80vgxnhhb438)

​  

在上面这篇文章中我们介绍了很多分布式 Session的方案，其中**最常用的就是用 Redis 来保存了**。

​  

其实就是把用户的登录信息保存在 Redis 中，然后 A 服务器和 B 服务器都从这个 Redis 中读取 Session。主要的流程如下：

​  

```mermaid
sequenceDiagram
  participant User as 用户
  participant 浏览器 as 浏览器
  participant 服务器A as 服务器 A
  participant 服务器B as 服务器 B
  participant Redis as Redis
  User->>浏览器: 登录
  浏览器->>服务器A: 登录
  服务器A->>服务器A: 用户登录校验
  服务器A->>服务器A: 生成 token
  服务器A->>Redis: 保存 Session
  服务器A->>浏览器: token
  User->>浏览器: 访问页面
  浏览器->>服务器B: 访问页面（携带 token）
  服务器B->>Redis: 查询 Session
  服务器B->>服务器B: 获取到 Session，鉴权通过
  服务器B->>服务器B: 业务逻辑处理
  服务器B->>浏览器: 处理结果
```

![图表](assets/✅分布式系统,用户登录信息保存在服务器A上,服务器B如何获取到共享Session-1.svg)

  

除了用 Redis 以外，还可以用其他的第三方存储，比如MySQL，mongodb，等等的都可以的。

​  

除了用 Redis 以外，还有一些其他方案，在上面的文章中都提到了，就不展开说了，如客户端存储、粘性 Session、Session 复制等等