---
tags: [Java与大数据, 概念]
created: 2026-08-02
domain: Java与大数据
source: 个人总结
---

> [!note] 边界声明
> 本文讲 Spark Streaming 的背压等机制;Flink 反压见 [[Flink优化-反压机制]](同名概念,不同引擎实现)。

SparkStreaming用于流式处理数据

![image.png](assets/SparkStreaming-1.png)

Dstream

![image.png](assets/SparkStreaming-2.png)

  

![image.png](assets/SparkStreaming-3.png)

![image.png](assets/SparkStreaming-4.png)

#### 背压机制

Spark 1.5以前版本，用户如果要限制Receiver的数据接收速率,可 以通过设置静态配制参数“spark.streaming.receiver.maxRate”的值来实现，此举虽然可以通过限制接收速率，来适配当前的处理能力，防止内存溢出，但也会引入其它问题。比如：producer数据生产高于maxRate，当前集群处理能力也高于maxRate，这就会造成资源利用率下降等问题。

为了更好的协调数据接收速率与资源处理能力，1.5版本开始Spark Streaming可以动态控制数据接收速率来适配集群数据处理能力。背压机制（即Spark Streaming Backpressure）：根据JobScheduler反馈作业的执行信息来动态调整Receiver数据接收率。

通过属性“spark.streaming.backpressure.enabled”来控制是否启用背压机制，默认值false，即不启用。

  

wordcount案例实操

需求：使用netcat(黑客常用)工具向9999端口不断的发送数据，通过SparkStreaming读取端口数据并统计不同单词出现的次数

  

DStream是Spark Streaming的基础抽象，代表持续性的数据流和经过各种Spark算子操作后的结果数据流。在内部实现上，每一批次的数据封装成一个RDD，一系列连续的RDD组成了DStream。对这些RDD的转换是由Spark引擎来计算。DStream中批次与批次之间计算相互独立。如果批次设置时间小于计算时间会出现计算任务叠加情况，需要多分配资源。通常情况，批次设置时间要大于计算时间。

## 附:原 Spark 总集独有内容·SparkStreaming(2026-09-06 合并)

> 来自已转 MOC 的 Spark.md SparkStreaming 章,该子篇缺失的行逐字搬运。

# SparkSreaming
## 概述
SparkSreaming用于流式数据的处理,支持多数据输入源,例如;kafka,Flume,Hdfs
![image.png](assets/Spark-9.png)
#### 架构原理
![image.png](assets/Spark-10.png)
![image.png](assets/Spark-11.png)
![image.png](assets/Spark-12.png)
背压机制
Spark 1.5以前版本，用户如果要限制Receiver的数据接收速率，可以通过设置静态配制参数“spark.streaming.receiver.maxRate”的值来实现，此举虽然可以通过限制接收速率，来适配当前的处理能力，防止内存溢出，但也会引入其它问题。比如：producer数据生产高于maxRate，当前集群处理能力也高于maxRate，这就会造成资源利用率下降等问题。
DStream是Spark Streaming的基础抽象，代表持续性的数据流和经过各种Spark算子操作后的结果数据流。
在内部实现上，每一批次的数据封装成一个RDD，一系列连续的RDD组成了DStream。对这些RDD的转换是由Spark引擎来计算。
说明：DStream中批次与批次之间计算相互独立。如果批次设置时间小于计算时间会出现计算任务叠加情况，需要多分配资源。通常情况，批次设置时间要大于计算时
## 使用
自定义数据源接收器
需要继承Receiver，并实现onStart、onStop方法来自定义数据源采集。
Kafka数据源
![image.png](assets/Spark-13.png)
## DStream转换
DStream上的操作与RDD的类似，分为转换和输出两种，此外转换操作中还有一些比较特殊的原语，如：updateStateByKey()、transform()以及各种Window相关的原语。
无状态转化操作
无状态转化操作：就是把RDD转化操作应用到DStream每个批次上，每个批次相互独立，自己算自己的。
常规无状态转化操作
DStream的部分无状态转化操作列在了下表中，都是DStream自己的API。
注意，针对键值对的DStream转化操作，要添加import StreamingContext._才能在Scala中使用，比如reduceByKey()。
需要记住的是，尽管这些函数看起来像作用在整个流上一样，但事实上每个DStream在内部是由许多RDD批次组成，且无状态转化操作是分别应用到每个RDD(一个批次的数据)上的。
Window Operations可以设置窗口的大小和滑动窗口的间隔来动态的获取当前Streaming的允许状态。所有基于窗口的操作都需要两个参数，分别为窗口时长以及滑动步长。
- 窗口时长：计算内容的时间范围；
- 滑动步长：隔多久触发一次计算。
注意：这两者都必须为采集批次大小的整数倍。
reduceByKeyAndWindow（反向Reduce）
1）基本语法：
- reduceByKeyAndWindow(func, invFunc, windowLength, slideInterval, [numTasks]): 这个函数是上述函数的变化版本，每个窗口的reduce值都是通过用前一个窗的reduce值来递增计算。通过reduce进入到滑动窗口数据并“反向reduce”离开窗口的旧数据来实现这个操作。一个例子是随着窗口滑动对keys的“加”“减”计数。通过前边介绍可以想到，这个函数只适用于“可逆的reduce函数”，也就是这些reduce函数有相应的“反reduce”函数（以参数invFunc形式传入）。如前述函数，reduce任务的数量通过可选参数来配置。
window的其它操作
（1）countByWindow(windowLength, slideInterval): 返回一个滑动窗口计数流中的元素个数；
（2）reduceByWindow(func, windowLength, slideInterval): 通过使用自定义函数整合滑动区间流元素来创建一个新的离散化数据流；
## DStream输出
DStream通常将数据输出到，外部数据库或屏幕上。
DStream与RDD中的惰性求值类似，如果一个DStream及其派生出的DStream都没有被执行输出操作，那么这些DStream就都不会被求值。如果StreamingContext中没有设定输出操作，整个Context就都不会启动。
1）输出操作API如下：
- saveAsTextFiles(prefix, [suffix])：以text文件形式存储这个DStream的内容。每一批次的存储文件名基于参数中的prefix和suffix。“prefix-Time_IN_MS[.suffix]”。
- saveAsObjectFiles(prefix, [suffix])：以Java对象序列化的方式将DStream中的数据保存为 SequenceFiles 。每一批次的存储文件名基于参数中的为"prefix-TIME_IN_MS[.suffix]"。
- saveAsHadoopFiles(prefix, [suffix])：将Stream中的数据保存为 Hadoop files。每一批次的存储文件名基于参数中的为"prefix-TIME_IN_MS[.suffix]"。
注意：以上操作都是每一批次写出一次，会产生大量小文件，在生产环境，很少使用。
- print()：在运行流程序的驱动结点上打印DStream中每一批次数据的最开始10个元素。这用于开发和调试。
- foreachRDD(func)：这是最通用的输出操作，即将函数func用于产生DStream的每一个RDD。其中参数传入的函数func应该实现将每一个RDD中数据推送到外部系统，如将RDD存入文件或者写入数据库。
在企业开发中通常采用foreachRDD()，它用来对DStream中的RDD进行任意计算。这和transform()有些类似，都可以让我们访问任意RDD。在foreachRDD()中，可以重用我们在Spark中实现的所有行动操作(action算子)。比如，常见的用例之一是把数据写到如MySQL的外部数据库中。
在企业开发中通常采用foreachRDD()，它用来对DStream中的RDD进行任意计算。这和transform()有些类似，都可以让我们访问任意RDD。在foreachRDD()中，可以重用我们在Spark中实现的所有行动操作(action算子)。比如，常见的用例之一是把数据写到如MySQL的外部数据库中。
（1）连接不能写在Driver层面（序列化）
（2）如果写在foreach则每个RDD中的每一条数据都创建，得不偿失；
（3）增加foreachPartition，在分区创建（获取）。
#### 关闭方式
流式任务需要7\*24小时执行，但是有时涉及到升级代码需要主动停止程序，但是分布式程序，没办法做到一个个进程去杀死，所以配置优雅的关闭就显得至关重要了。
关闭方式：使用外部文件系统来控制内部程序关闭。
