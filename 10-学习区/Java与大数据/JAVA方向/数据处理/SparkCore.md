---
tags: [Java与大数据, 概念]
created: 2025-11-17
status: 整理中
domain: Java与大数据
source: 个人总结
---

# SparkCore

> [!note] 拆分说明
> 2026-09-06 由 Spark.md 总集拆出(RDD 概述/编程/持久化/累加器/广播变量等),逐字搬运。

# SrarkCore

  

### RDD概述

RDD（Resilient Distributed Dataset）叫做弹性分布式数据集，是Spark中最基本的数据抽象。

![image.png](assets/Spark-4.png)

在Spark中创建RDD的创建方式可以分为三种：从集合中创建RDD、从外部存储创建RDD、从其他RDD创建。

注意：getSplits文件返回的是切片规划，真正读取是在compute方法中创建LineRecordReader读取的，有两个关键变量：start = split.getStart() end = start + split.getLength

1.分区数量的计算方式:

totalSize = 10

goalSize = 10 / 3 = 3(byte) 表示每个分区存储3字节的数据

分区数= totalSize/ goalSize = 10 /3 => 3,3,4

4子节大于3子节的1.1倍,符合hadoop切片1.1倍的策略,因此会多创建一个分区,即一共有4个分区 3,3,3,1

2. Spark读取文件，采用的是hadoop的方式读取，所以一行一行读取，跟字节数没有关系

3.数据读取位置计算是以偏移量为单位来进行计算的。

4.数据分区的偏移量范围的计算

0 => [0,3] 1@@ 012 0 => 1,2

1 => [3,6] 2@@ 345 1 => 3

2 => [6,9] 3@@ 678 2 => 4

3 => [9,9] 4 9 3 => 无

  

### RDD编程

#### Transformation转化算子

RDD整体上分为Value类型、双Value类型和Key-Value类型

value类型

map,mappartition,mappartitionwithIndex(),flatmap(),groupby,sortby,filter,distinct,coalesce,reparttion

双Vaule类型

zip(),substract(),union().intersection()

key_value类型

partitionby(),rducebykey(),foldbykey(),aggregateByKey(),combineByKey(),sortbykey(),cogroup(),join()

#### Action行动算子

collection,first,foreach,count,take,takeordered,countbykey,save

#### RDD序列化

在实际开发中我们往往需要自己定义一些对于RDD的操作，那么此时需要注意的是，初始化工作是在Driver端进行的，而实际运行程序是在Executor端进行的，这就涉及到了跨进程通信，是需要序列化的。

Driver：算子以外的代码都是在Driver端执行

Executor：算子里面的代码都是在Executor端执行

kryo序列化

Java的序列化能够序列化任何的类。但是比较重，序列化后对象的体积也比较大。

Spark出于性能的考虑，Spark2.0开始支持另外一种Kryo序列化机制。Kryo速度是Serializable的10倍。当RDD在Shuffle数据的时候，简单数据类型、数组和字符串类型已经在Spark内部使用Kryo来序列化。

#### RDD依赖关系

RDD只支持粗粒度转换，即在大量记录上执行的单个操作。将创建RDD的一系列Lineage（血统）记录下来，以便恢复丢失的分区。RDD的Lineage会记录RDD的元数据信息和转换行为，当该RDD的部分分区数据丢失时，它可以根据这些信息来重新运算和恢复丢失的数据分区。

####   

注意：要想理解RDDS是如何工作的，最重要的就是理解Transformations。

RDD之间的关系可以从两个维度来理解：一个是RDD是从哪些RDD转换而来，也就是 RDD的parent RDD(s)是什么(**血缘**); 另一个就是RDD依赖于parent RDD(s)的哪些Partition(s)，这种关系就是RDD之间的依赖(**依赖**)。

窄依赖表示每一个父RDD的Partition最多被子RDD的一个Partition使用(一对一or多对一)，窄依赖我们形象的比喻为独生子女。

宽依赖表示同一个父RDD的Partition被多个子RDD的Partition依赖(只能是一对多)，会引起Shuffle，总结：宽依赖我们形象的比喻为超生

  

具有宽依赖的*transformations*包括：*sort*、*reduceByKey*、*groupByKey*、*join*和调用*rePartition*函数的任何操作。

宽依赖对Spark去评估一个transformations有更加重要的影响，比如对性能的影响。

在不影响业务要求的情况下，要尽量避免使用有宽依赖的转换算子，因为有宽依赖,就一定会走shuffle，影响性能

  

DAG有向无环图

DAG（Directed Acyclic Graph）有向无环图是由点和线组成的拓扑图形，该图形具有方向，不会闭环。例如，DAG记录了RDD的转换过程和任务的阶段。

  

#### 任务划分

RDD任务切分中间分为：Application、Job、Stage和Task

（1）Application：初始化一个SparkContext即生成一个Application；

（2）Job：一个Action算子就会生成一个Job；

（3）Stage：Stage等于宽依赖的个数加1；

（4）Task：一个Stage阶段中，最后一个RDD的分区个数就是Task的个数。

注意：Application->Job->Stage->Task每一层都是1对n的关系。

  

#### RDD持久化

RDD通过Cache或者Persist方法将前面的计算结果缓存，默认情况下会把数据以序列化的形式缓存在JVM的堆内存中。但是并不是这两个方法被调用时立即缓存，而是触发后面的action算子时，该RDD将会被缓存在计算节点的内存中，并供后面重用。

缓存有可能丢失，或者存储于内存的数据由于内存不足而被删除，RDD的缓存容错机制保证了即使缓存丢失也能保证计算的正确执行。通过基于RDD的一系列转换，丢失的数据会被重算，由于RDD的各个Partition是相对独立的，因此只需要计算丢失的部分即可，并不需要重算全部Partition。

3）自带缓存算子

Spark会自动对一些Shuffle操作的中间数据做持久化操作（比如：reduceByKey）。这样做的目的是为了当一个节点Shuffle失败了避免重新计算整个输入。但是，在实际使用的时候，如果想重用数据，仍然建议调用persist或cache。

  

chectpoint检查点

检查点：是通过将RDD中间结果写入磁盘。

2）为什么要做检查点？

由于血缘依赖过长会造成容错成本过高，这样就不如在中间阶段做检查点容错，如果检查点之后有节点出现问题，可以从检查点开始重做血缘，减少了开销。

3）检查点存储路径：Checkpoint的数据通常是存储在HDFS等容错、高可用的文件系统

4）检查点数据存储格式为：二进制的文件

5）检查点切断血缘：在Checkpoint的过程中，该RDD的所有依赖于父RDD中的信息将全部被移除。

6）检查点触发时间：对RDD进行Checkpoint操作并不会马上被执行，必须执行Action操作才能触发。但是检查点为了数据安全，会从血缘关系的最开始执行一遍。

对RDD进行checkpoint操作并不会马上被执行,需等到Action操作才能被触发

  

  

### **缓存和检查点区别**

1）Cache缓存只是将数据保存起来，不切断血缘依赖。Checkpoint检查点切断血缘依赖。

2）Cache缓存的数据通常存储在磁盘、内存等地方，可靠性低。Checkpoint的数据通常存储在HDFS等容错、高可用的文件系统，可靠性高。

3）建议对checkpoint()的RDD使用Cache缓存，这样checkpoint的job只需从Cache缓存中读取数据即可，否则需要再从头计算一次RDD。

4）如果使用完了缓存，可以通过unpersist()方法释放缓存

  

  

#### 键值对RDD分区

Spark目前支持Hash分区、Range分区和用户自定义分区。Hash分区为当前的默认分区。分区器直接决定了RDD中分区的个数、RDD中每条数据经过Shuffle后进入哪个分区和Reduce的个数。

1）注意：

（1）只有Key-Value类型的RDD才有分区器，非Key-Value类型的RDD分区的值是None

（2）每个RDD的分区ID范围：0~numPartitions-1，决定这个值是属于那个分区的。

![image.png](assets/Spark-5.png)

  

![image.png](assets/Spark-6.png)

  

  

### 数据的读取与保存

Spark的数据读取及数据保存可以从两个维度来作区分：文件格式以及文件系统。

文件格式分为：Text文件、Sequence文件以及Object文件；

文件系统分为：本地文件系统、HDFS以及数据库。

### **Text** **文件**

1）基本语法

（1）数据读取：textFile(String)

（2）数据保存：saveAsTextFile(String)

SequenceFile文件是Hadoop用来存储二进制形式的key-value对而设计的一种平面文件(Flat File)。在SparkContext中，可以调用sequenceFile\[keyClass, valueClass\](path)。

object对象文件

对象文件是将对象序列化后保存的文件，采用hadoop的序列化机制。可以通过objectFile\[k,v\](path)函数接收一个路径，读取对象文件，返回对应的RDD，也可以通过调用saveAsObjectFile()实现对对象文件的输出。因为要序列化所以要指定类型。

  

Spark的整个生态系统与Hadoop是完全兼容的，所以对于Hadoop所支持的文件类型或者数据库类型，Spark也同样支持。另外，由于Hadoop的API有新旧两个版本，所以Spark为了能够兼容Hadoop所有的版本，也提供了两套创建操作接口。如TextInputFormat，新旧两个版本所引用分别是org.apache.hadoop.mapred.InputFormat、org.apache.hadoop.mapreduce.InputFormat(NewInputFormat)

  

### 累加器

累加器：分布式共享只写变量。（Executor和Executor之间不能读数据）

累加器用来把Executor端变量信息聚合到Driver端。在Driver中定义的一个变量，在Executor端的每个task都会得到这个变量的一份新的副本，每个task更新这些副本的值后，传回Driver端进行合并计算。

1）累加器使用

（1）累加器定义（SparkContext.accumulator(initialValue)方法）

val sum: LongAccumulator = sc.longAccumulator("sum")

（2）累加器添加数据（累加器.add方法）

sum.add(count)

（3）累加器获取数据（累加器.value）

注意：Executor端的任务不能读取累加器的值（例如：在Executor端调用sum.value，获取的值不是累加器最终的值）。因此我们说，累加器是一个分布式共享只写变量。

3）累加器要放在行动算子中

因为转换算子执行的次数取决于job的数量，如果一个spark应用有多个行动算子，那么转换算子中的累加器可能会发生不止一次更新，导致结果错误。所以，如果想要一个无论在失败还是重复计算时都绝对可靠的累加器，我们必须把它放在foreach()这样的行动算子中。

对于在行动算子中使用的累加器，Spark只会把每个Job对各累加器的修改应用一次。

  

可选择自定义累加器

自定义累加器步骤

（1）继承AccumulatorV2，设定输入、输出泛型

（2）重写6个抽象方法

（3）使用自定义累加器需要注册:：sc.register(累加器,"累加器名字")

  

### 广播变量

广播变量：分布式共享只读变量。

广播变量用来高效分发较大的对象。向所有工作节点发送一个较大的只读值，以供一个或多个Spark Task操作使用。比如，如果你的应用需要向所有节点发送一个较大的只读查询表，广播变量用起来会很顺手。在多个Task并行操作中使用同一个变量，但是Spark会为每个Task任务分别发送。

1）使用广播变量步骤：

（1）调用SparkContext.broadcast（广播变量）创建出一个广播对象，任何可序列化的类型都可以这么实现。

（2）通过广播变量.value，访问该对象的值。

（3）广播变量只会被发到各个节点一次，作为只读值处理（修改这个值不会影响到别的节点）。

  

### SparkCore实战

使用spark实现的四种方案
