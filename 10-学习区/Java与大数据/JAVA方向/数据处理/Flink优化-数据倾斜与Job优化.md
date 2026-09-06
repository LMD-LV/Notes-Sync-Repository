---
tags: [Java与大数据, 概念]
created: 2026-09-06
status: 整理中
domain: Java与大数据
source: 个人总结
---
# 数据倾斜

## 判断是否存在数据倾斜

相同 Task 的多个 Subtask 中，个别Subtask 接收到的数据量明显大于其他 Subtask 接收到的数据量，通过 Flink Web UI 可以精确地看到每个 Subtask 处理了多少数据，即可判断出 Flink 任务是否存在数据倾斜。通常，数据倾斜也会引起反压。

![image.png](assets/Flink优化-10.png)

另外， 有时Checkpoint detail 里不同 SubTask 的 State size 也是一个分析数据倾斜的有用指标。

## 解决数据倾斜

### keyby之前

如果 keyBy 之前就存在数据倾斜，上游算子的某些实例可能处理的数据较多，某些实例可能处理的数据较少，产生该情况可能是因为数据源的数据本身就不均匀，例如由于某些原因 Kafka 的 topic 中某些 partition 的数据量较大，某些 partition 的数据量较少。对于不存在 keyBy 的 Flink 任务也会出现该情况。

这种情况，需要让 Flink 任务强制进行shuffle。使用shuffle、rebalance 或 rescale算子即可将数据均匀分配，从而解决数据倾斜的问题。

### keyby之后聚合操作引起的数据倾斜

提交案例：

bin/flink run \\

\-t yarn-per-job \\

\-d \\

\-p 3 \\

\-Drest.flamegraph.enabled=true \\

\-Dyarn.application.queue=default \\

\-Djobmanager.memory.process.size=1024mb \\

\-Dtaskmanager.memory.process.size=2048mb \\

\-Dtaskmanager.numberOfTaskSlots=2 \\

\-c com.atguigu.flink.tuning.SkewDemo1 \\

/opt/module/flink-1.13.1/myjar/flink-tuning-1.0-SNAPSHOT.jar \\

\--local-keyby false

![image.png](assets/Flink优化-11.png)

​  

**为什么不能直接用二次聚合来处理**

Flink是实时流处理，如果keyby之后的聚合操作存在数据倾斜，且没有开窗口（没攒批）的情况下，简单的认为使用两阶段聚合，是不能解决问题的。因为这个时候Flink是来一条处理一条，且向下游发送一条结果，对于原来keyby的维度（第二阶段聚合）来讲，数据量并没有减少，且结果重复计算（非FlinkSQL，未使用回撤流），如下图所示

![image.png](assets/Flink优化-12.png)

​  

**2****）使用****LocalKeyBy****的思想**

在 keyBy 上游算子数据发送之前，首先在上游算子的本地对数据进行聚合后，再发送到下游，使下游接收到的数据量大大减少，从而使得 keyBy 之后的聚合操作不再是任务的瓶颈。类似MapReduce 中 Combiner 的思想，但是这要求聚合操作必须是多条数据或者一批数据才能聚合，单条数据没有办法通过聚合来减少数据量。从Flink LocalKeyBy 实现原理来讲，必然会存在一个积攒批次的过程，在上游算子中必须攒够一定的数据量，对这些数据聚合后再发送到下游。

**实现方式：**

Ø DataStreamAPI需要自己写代码实现

Ø SQL可以指定参数，开启miniBatch和LocalGlobal功能（推荐，后续介绍）

​  

### keyby之后窗口聚合引起的数据倾斜

因为使用了窗口，变成了有界数据（攒批）的处理，窗口默认是触发时才会输出一条结果发往下游，所以可以使用两阶段聚合的方式：

**1）实现思路：**

Ø 第一阶段聚合：key拼接随机数前缀或后缀，进行keyby、开窗、聚合

*注意：**聚合完不再是**WindowedStream，要获取WindowEnd作为窗口标记作为第二阶段分组依据，避免不同窗口的结果聚合到一起）*

Ø 第二阶段聚合：按照原来的key及windowEnd作keyby、聚合

​  

随机数范围，需要自己去测，因为keyby的分区器是（两次hash\*下游并行度/最大并行度）

# Job优化

## 1.1 **使用DataGen造数据**

开发完Flink作业，压测的方式很简单，先在kafka中积压数据，之后开启Flink任务，出现反压，就是处理瓶颈。相当于水库先积水，一下子泄洪。

数据可以是自己造的模拟数据，也可以是生产中的部分数据。造测试数据的工具：DataFactory、datafaker 、DBMonster、Data-Processer 、Nexmark、Jmeter等。

Flink从1.11开始提供了一个内置的DataGen 连接器，主要是用于生成一些随机数，用于在没有数据源的时候，进行流任务的测试以及性能测试等。

### DataStream的DataGenerator

### ​**SQL的DataGenerator**

## 1.1 **算子指定UUID**

对于有状态的 Flink 应用，推荐给每个算子都指定唯一用户ID（UUID）。 严格地说，仅需要给有状态的算子设置就足够了。但是因为 Flink 的某些内置算子（如 window）是有状态的，而有些是无状态的，可能用户不是很清楚哪些内置算子是有状态的，哪些不是。所以从实践经验上来说，我们建议每个算子都指定上 UUID。

默认情况下，算子UID是根据JobGraph自动生成的，JobGraph的更改可能会导致UUID改变。手动指定算子 UUID ，可以让 Flink 有效地将算子的状态从 savepoint 映射到作业修改后（拓扑图可能也有改变）的正确的算子上。比如替换原来的Operator实现、增加新的Operator、删除Operator等等，至少我们有可能与Savepoint中存储的Operator状态对应上。这是 savepoint 在 Flink 应用中正常工作的一个基本要素。

Flink 算子的 UUID 可以通过 uid(String uid) 方法指定，通常也建议指定name

​  

#算子.uid("指定uid")

.reduce((value1, value2) -> Tuple3.of("uv", value2.f1, value1.f2 + value2.f2))

.uid("uv-reduce").name("uv-reduce")

## 1.1 **链路延迟测量**

对于实时的流式处理系统来说，我们需要关注数据输入、计算和输出的及时性，所以处理延迟是一个比较重要的监控指标，特别是在数据量大或者软硬件条件不佳的环境下。Flink提供了开箱即用的LatencyMarker机制来测量链路延迟。开启如下参数：

metrics.latency.interval: 30000 #默认0，表示禁用，单位毫秒

监控的粒度，分为以下3档：

Ø single：每个算子单独统计延迟；

Ø operator（默认值）：每个下游算子都统计自己与Source算子之间的延迟；

Ø subtask：每个下游算子的sub-task都统计自己与Source算子的sub-task之间的延迟。

metrics.latency.granularity: operator #默认operator

一般情况下采用默认的operator粒度即可，这样在**Sink端观察到的latency metric就是我们最想要的全链路（端到端）延迟**。subtask粒度太细，会增大所有并行度的负担，不建议使用。

LatencyMarker不会参与到数据流的用户逻辑中的，而是直接被各算子转发并统计。为了让它尽量精确，有两点特别需要注意：

Ø 保证Flink集群内所有节点的时区、时间是同步的：ProcessingTimeService产生时间戳最终是靠System.currentTimeMillis()方法，可以用ntp等工具来配置。

Ø metrics.latency.interval的时间间隔宜大不宜小：一般配置成30000（30秒）左右。一是因为延迟监控的频率可以不用太频繁，二是因为LatencyMarker的处理也要消耗一定性能。

​  

端到端延迟的tag只有murmur hash过的算子ID（用uid()方法设定的），并没有算子名称，（[https://issues.apache.org/jira/browse/FLINK-8592](https://issues.apache.org/jira/browse/FLINK-8592)）并且官方暂时不打算解决这个问题，所以我们要么用最大值来表示，要么将作业中Sink算子的ID统一化。比如使用了Prometheus和Grafana来监控，效果如下：

![image.png](assets/Flink优化-13.png)

## 1.1 **开启对象重用**

![image.png](assets/Flink优化-14.png)

当调用了enableObjectReuse方法后，Flink会把中间深拷贝的步骤都省略掉，SourceFunction产生的数据直接作为MapFunction的输入，可以减少gc压力。但需要特别注意的是，这个方法不能随便调用，必须要确保下游Function只有一种，或者下游的Function均不会改变对象内部的值。否则可能会有线程安全的问题。

## 1.1 **细粒度滑动窗口优化**

**细粒度滑动的影响**

当使用细粒度的滑动窗口（窗口长度远远大于滑动步长）时，重叠的窗口过多，一个数据会属于多个窗口，性能会急剧下降。

![image.png](assets/Flink优化-15.png)

我们经常会碰到这种需求：以3分钟的频率实时计算App内各个子模块近24小时的PV和UV。我们需要用粒度为1440 / 3 = 480的滑动窗口来实现它，但是细粒度的滑动窗口会带来性能问题，有两点：

Ø 状态

对于一个元素，会将其写入对应的(key, window)二元组所圈定的windowState状态中。如果粒度为480，那么每个元素到来，更新windowState时都要遍历480个窗口并写入，开销是非常大的。在采用RocksDB作为状态后端时，checkpoint的瓶颈也尤其明显。

Ø 定时器

每一个(key, window)二元组都需要注册两个定时器：一是触发器注册的定时器，用于决定窗口数据何时输出；二是registerCleanupTimer()方法注册的清理定时器，用于在窗口彻底过期（如allowedLateness过期）之后及时清理掉窗口的内部状态。细粒度滑动窗口会造成维护的定时器增多，内存负担加重。

**2****）解决思路**

DataStreamAPI中，自己解决（[https://issues.apache.org/jira/browse/FLINK-7001](https://issues.apache.org/jira/browse/FLINK-7001)）。

我们一般使用**滚动窗口****+在线存储+读时聚合**的思路作为解决方案：

（1）从业务的视角来看，往往窗口的长度是可以被步长所整除的，可以找到窗口长度和窗口步长的最小公约数作为时间分片（一个滚动窗口的长度）；

（2）每个滚动窗口将其周期内的数据做聚合，存到下游状态或打入外部在线存储（内存数据库如Redis，LSM-based NoSQL存储如HBase）；

（3）扫描在线存储中对应时间区间（可以灵活指定）的所有行，并将计算结果返回给前端展示。

  

