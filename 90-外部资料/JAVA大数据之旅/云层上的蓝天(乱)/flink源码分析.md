# flink源码分析

常用操作：

ctrl + n 查找 clifrontend类下的main方法

ctrl + 12 可查看类下的属性方法等

ctrl + h 可查看类的实现类（子类）

ctrl + alt 左右键 可进退

**​**  

![image.png](assets/flink源码分析-1.png)

**flink脚本顺序:**

1.  日志
2.  加载配置路径、及全局配置 config.sh
3.  包括java、hadoop、yarn、hbase等环境变量及配置
4.  flink-conf.yaml未指定的值的一些默认值等
5.  解析action参数

1.  run：指定并行度、jar包及类名、是否从状态恢复
2.  list： 列出不同模式（application、per-job、session、k8s等）正在运行的程序和计划调度的程序
3.  info：显示程序的优化执行计划（JSON）
4.  cancel：取消作业
5.  stop：停止作业 可做sp
6.  savepoint：做sp后停止
7.  \-h -v --help --version

6.  另外sql-client.sh 可以两种方式提交sql、本地flink集群embedded、或是远程连接集群gateway（该方式应该是dinky等flink二开sql开发平台的调用方式）
7.  判断执行模式、commonlines里的 generic、yarn（会判断是否存在yarnsession yarnId，然后根据参数判断是application、per-job等，没参数的话优先会识别yarn-session）、default 与命令行参数对比 isactive
8.  根据各种模式对应的参数不同，需要做进一步解析（如并行度、jm tm内存等等）
9.  封装有效配置

1.  获取jar包 、入口class
2.  获取配置 ha的id 并行度 内存等
3.  执行程序：用户代码类加载 -> invoke调用用户代码main方法

1.  环境读取
2.  获取streamGraph

1.  source
2.  transform
3.  sink

3.  execut方法中将 streamGraph转换为jobgraph

4.  集群描述器，读取yarn、flink等配置，初始化yarn 客户端并启动
5.  部署flink作业前检查、yarn队列资源

10.  启动APPmaster

1.  上传jar包、配置文件及参数到hdgs
2.  submit 到resourceManager
3.  创建disparcher
4.  创建jobmaster

**​**  

**​**  

![image.png](assets/flink源码分析-2.png)

  

  

  

![image.png](assets/flink源码分析-3.png)

  

  

![image.png](assets/flink源码分析-4.png)

  

  

![image.png](assets/flink源码分析-5.png)

  

  

  

**袋鼠云：**

![image.png](assets/flink源码分析-6.png)

  

![image.png](assets/flink源码分析-7.png)

![image.png](assets/flink源码分析-8.png)

  

![image.png](assets/flink源码分析-9.png)

  

![image.png](assets/flink源码分析-10.png)

  

![image.png](assets/flink源码分析-11.png)

  

![image.png](assets/flink源码分析-12.png)

  

  

![image.png](assets/flink源码分析-13.png)

  

![image.png](assets/flink源码分析-14.png)

  

![image.png](assets/flink源码分析-15.png)

![image.png](assets/flink源码分析-16.png)

  

![image.png](assets/flink源码分析-17.png)

  

![image.png](assets/flink源码分析-18.png)

![image.png](assets/flink源码分析-19.png)

  

![image.png](assets/flink源码分析-20.png)

![image.png](assets/flink源码分析-21.png)

  

![image.png](assets/flink源码分析-22.png)

  

  

**checkpoint：**

![image.png](assets/flink源码分析-23.png)