---
tags: [Java与大数据, 概念]
created: 2026-09-06
status: 整理中
domain: Java与大数据
source: 个人总结
---

# 资源配置优化

Flink性能调优的第一步，就是为任务分配合适的资源，在一定范围内，增加资源的分配与性能的提升是成正比的，实现了最优的资源配置后，在此基础上再考虑进行后面论述的性能调优策略。

提交方式主要是yarn-per-job，资源的分配在使用脚本提交Flink任务时进行指定

###   

Ø标准的Flink任务提交脚本（Generic CLI 模式）

从1.11开始，增加了通用客户端模式，参数使用\-D <property=value>指定

bin/flink run \\

\-t yarn-per-job \\

\-d \\

\-p 3 \\ 指定并行度

\-Dyarn.application.queue=default \\ 指定yarn队列

\-Djobmanager.memory.process.size=1024mb \\ 指定JM的总进程大小

\-Dtaskmanager.memory.process.size=1024mb \\ 指定每个TM的总进程大小

\-Dtaskmanager.numberOfTaskSlots=2 \\ 指定每个TM的slot数

\-c com.atguigu.flink.tuning.UvDemo \\

/opt/module/flink-1.13.1/myjar/flink-tuning-1.0-SNAPSHOT.jar

参数列表：

[https://ci.apache.org/projects/flink/flink-docs-release-1.13/deployment/config.html](https://ci.apache.org/projects/flink/flink-docs-release-1.13/deployment/config.html)

### 内存设置

​  

​  

![image.png](assets/Flink优化-1.png)

​  

Task的内存=进程内存-JVM特有内存-网络内存-托管内存-框架内存(堆内,堆外)

​  

**1、内存模型详解**

**l** **JVM** **特定内存：**JVM本身使用的内存，包含JVM的metaspace和over-head

1）JVM metaspace：JVM元空间

taskmanager.memory.jvm-metaspace.size，默认256mb

2）JVM over-head执行开销：JVM执行时自身所需要的内容，包括线程堆栈、IO、编译缓存等所使用的内存。

taskmanager.memory.jvm-overhead.fraction，默认0.1

taskmanager.memory.jvm-overhead.min，默认192mb

taskmanager.memory.jvm-overhead.max，默认1gb

**总进程内存****\*fraction，如果小于****配置的****min****（或大于配置的****max****）****大小，则使用****min/max大小**

**l** **框架内存：**Flink框架，即TaskManager本身所占用的内存，**不计入****Slot的资源中。**

堆内：taskmanager.memory.framework.heap.size，默认128MB

堆外：taskmanager.memory.framework.off-heap.size，默认128MB

**l** **Task内存：**Task执行用户代码时所使用的内存

堆内：taskmanager.memory.task.heap.size，默认none，由Flink内存扣除掉其他部分的内存得到。

堆外：taskmanager.memory.task.off-heap.size，默认0，表示不使用堆外内存

**l** **网络内存：**网络数据交换所使用的堆外内存大小，如网络数据交换缓冲区

堆外：taskmanager.memory.network.fraction，默认0.1

taskmanager.memory.network.min，默认64mb

taskmanager.memory.network.max，默认1gb

**Flink内存\*fraction，如果小于****配置的****min****（或大于配置的****max****）****大小，则使用****min/max大小**

**l** **托管内存****：**用于RocksDB State Backend 的本地内存和批的排序、哈希表、缓存中间结果。

堆外：taskmanager.memory.managed.fraction，默认0.4

​taskmanager.memory.managed.size，默认none

**如果****size没指定，则等于Flink内存\*fraction**

**2、案例分析**

基于Yarn模式，一般参数指定的是总进程内存，taskmanager.memory.process.size，比如指定为4G，每一块内存得到大小如下：

（1）计算Flink内存

JVM元空间256m

JVM执行开销： 4g\*0.1=409.6m，在[192m,1g]之间，最终结果409.6m

Flink内存=4g\-256m\-409.6m\=3430.4m

（2）网络内存=3430.4m\*0.1=343.04m，在[64m,1g]之间，最终结果343.04m

（3）托管内存=3430.4m\*0.4=1372.16m

（4）框架内存，堆内和堆外都是128m

（5）Task堆内内存=3430.4m-128m-128m-343.04m-1372.16m=1459.2m

​  

![image.png](assets/Flink优化-2.png)

![image.png](assets/Flink优化-3.png)

所以进程内存给多大，每一部分内存需不需要调整，可以看内存的使用率来调整。

#### 1.1.1 生产资源配置示例

bin/flink run \\

\-t yarn-per-job \\

\-d \\

\-p 3 \\ 指定并行度

\-Dyarn.application.queue=default \\ 指定yarn队列

\-Djobmanager.memory.process.size=2048mb \\ JM2~4G足够

\-Dtaskmanager.memory.process.size=4096mb \\ 单个TM2~8G足够

\-Dtaskmanager.numberOfTaskSlots=2 \\ 与容器核数1core：1slot或1core：2slot

\-c com.atguigu.flink.tuning.UvDemo \\

/opt/module/flink-1.13.1/myjar/flink-tuning-1.0-SNAPSHOT.jar

Flink是实时流处理，关键在于资源情况能不能抗住高峰时期每秒的数据量，通常用QPS/TPS来描述数据情况。

### 合理使用CPU资源

Yarn的容量调度器默认情况下是使用“DefaultResourceCalculator”分配策略，只根据内存调度资源，所以在Yarn的资源管理页面上看到每个容器的vcore个数还是1。

可以修改策略为 DominantResourceCalculator，该资源计算器在计算资源的时候会综合考虑cpu和内存的情况。在capacity-scheduler.xml 中修改属性:

<property>

<name>yarn.scheduler.capacity.resource-calculator</name>

<!-- <value>org.apache.hadoop.yarn.util.resource.DefaultResourceCalculator</value> -->

<value>org.apache.hadoop.yarn.util.resource.DominantResourceCalculator</value>

</property>

#### 1.1.1 使用DefaultResourceCalculator 策略

bin/flink run \\

\-t yarn-per-job \\

\-d \\

\-p 3 \\

\-Dyarn.application.queue=default \\

\-Djobmanager.memory.process.size=1024mb \\

\-Dtaskmanager.memory.process.size=4096mb \\

\-Dtaskmanager.numberOfTaskSlots=2 \\

\-c com.atguigu.flink.tuning.UvDemo \\

/opt/module/flink-1.13.1/myjar/flink-tuning-1.0-SNAPSHOT.jar

可以看到一个容器只有一个vcore：

![image.png](assets/Flink优化-4.png)

#### 1.1.2 使用DominantResourceCalculator策略

修改后yarn配置后，分发配置并重启yarn，再次提交flink作业：

bin/flink run \\

\-t yarn-per-job \\

\-d \\

\-p 3 \\

\-Drest.flamegraph.enabled=true \\

\-Dyarn.application.queue=default \\

\-Djobmanager.memory.process.size=1024mb \\

\-Dtaskmanager.memory.process.size=4096mb \\

\-Dtaskmanager.numberOfTaskSlots=2 \\

\-c com.atguigu.flink.tuning.UvDemo \\

/opt/module/flink-1.13.1/myjar/flink-tuning-1.0-SNAPSHOT.jar

![image.png](assets/Flink优化-5.png)

  

#### 1.1.3 使用DominantResourceCalculator策略并指定容器vcore数

指定yarn容器的vcore数，提交：

bin/flink run \\

\-t yarn-per-job \\

\-d \\

\-p 3 \\

\-Drest.flamegraph.enabled=true \\

\-Dyarn.application.queue=default \\

\-Dyarn.containers.vcores=3 \\

\-Djobmanager.memory.process.size=1024mb \\

\-Dtaskmanager.memory.process.size=4096mb \\

\-Dtaskmanager.numberOfTaskSlots=2 \\

\-c com.atguigu.flink.tuning.UvDemo \\

/opt/module/flink-1.13.1/myjar/flink-tuning-1.0-SNAPSHOT.jar

![image.png](assets/Flink优化-6.png)

JobManager1个，占用1个容器，vcore=1

TaskManager2个，占用3个容器，每个容器vcore =3，总vcore=2\*3=6

### 并行度设置

#### 1.1.1 全局并行度计算

开发完成后，先进行压测。任务并行度给10以下，测试单个并行度的处理上限。然后 总QPS/单并行度的处理能力 = 并行度

开发完Flink作业，压测的方式很简单，先在kafka中积压数据，之后开启Flink任务，出现反压，就是处理瓶颈。相当于水库先积水，一下子泄洪。

不能只从QPS去得出并行度，因为有些字段少、逻辑简单的任务，单并行度一秒处理几万条数据。而有些数据字段多，处理逻辑复杂，单并行度一秒只能处理1000条数据。

最好根据高峰期的QPS压测，并行度\*1.2倍，富余一些资源。

#### 1.1.2 Source 端并行度的配置

数据源端是 Kafka，Source的并行度设置为Kafka对应Topic的分区数。

如果已经等于 Kafka 的分区数，消费速度仍跟不上数据生产速度，考虑下Kafka 要扩大分区，同时调大并行度等于分区数。

Flink 的一个并行度可以处理一至多个分区的数据，如果并行度多于 Kafka 的分区数，那么就会造成有的并行度空闲，浪费资源。

#### 1.1.3 Transform端并行度的配置

Ø Keyby之前的算子

一般不会做太重的操作，都是比如map、filter、flatmap等处理较快的算子，并行度可以和source保持一致。

Ø Keyby之后的算子 -\- keyGroup

如果并发较大，建议调整最大并行度并行度；

#### 1.1.4 Sink 端并行度的配置

Sink 端是数据流向下游的地方，可以根据 Sink 端的数据量及下游的服务抗压能力进行评估。如果Sink端是Kafka，可以设为Kafka对应Topic的分区数。

Sink 端的数据量小，比较常见的就是监控告警的场景，并行度可以设置的小一些。

Source 端的数据量是最小的，拿到 Source 端流过来的数据后做了细粒度的拆分，数据量不断的增加，到 Sink 端的数据量就非常大。那么在 Sink 到下游的存储中间件的时候就需要提高并行度。

另外 Sink 端要与下游的服务进行交互，并行度还得根据下游的服务抗压能力来设置，如果在 Flink Sink 这端的数据量过大的话，且 Sink 处并行度也设置的很大，但下游的服务完全撑不住这么大的并发写入，可能会造成下游服务直接被写挂，所以最终还是要在 Sink 处的并行度做一定的权衡。

​  

​  

