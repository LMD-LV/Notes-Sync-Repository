---
tags: [运维与部署, 概念]
created: 2026-08-02
domain: 运维与部署
source: 个人总结
---

1.  服务的基本执行方式

1.  nohup后台执行,常见的java服务就是这样的
2.  ./start.sh & 日志重定向输出到控制台
3.  screen tmux
4.  systemd 相当于系统的自己服务
5.  使用 setid 相当于启动一个新的会话保持执行
6.  disown 相当于从shell作业表中删除该作业,防止收到sighup信号

2.  代码变成可执行文件,就是编译, 编译时的依赖,顺序等操作 也就是构建, 构建需要被提供 makefile文件,其实相当于 maven,gradle中的配置文件
3.  wget指令，命令行下载，支持http和ftp，支持定时，越过缓存，断点等配置，可用于生成网站的镜像
4.  make指令，相当于maven，一种构建工具