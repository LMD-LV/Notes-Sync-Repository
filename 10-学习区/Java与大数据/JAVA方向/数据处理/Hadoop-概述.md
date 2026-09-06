---
tags: [Java与大数据, 概念]
created: 2026-09-06
status: 整理中
domain: Java与大数据
source: 个人总结
---

  

# Hadoop概述

Hadoop是一个分布式系统基础架构

解决海量数据存储与分析计算

是一个生态圈

  

#### Hadoop发行版本

Apache,Cloudera,Hortonworks,

#### Hadoop优势

高可靠, 底层维护多个副本,即使某个计算元素或存储出现问题,不会导致数据的丢失

高扩展, 可拓展多节点

高效性,MapReduce加快了任务的处理速度

高容错;失败的任务可以重新分配

#### Hadoop的组成

MapReduce(计算) ,Yarn(资源调度),HDFS(数据存储),Common(辅助工具)

2.x新增的Yarn

  

#### HDFS概述:

Hadoop Distributed File System简称HDFS,分布式文件系统

由NN(NameNode):存储文件的元数据,文件名,文件目录结构,文件属性(生成时间,副本数,文件权限),以及块列表,和块所在的DataNode等

.DN(DateNode),:在本地文件系统存储文件块数据,以及块数据的校验和

2NN(Secondary NameNode):每隔一段时间堆Namenode元数据备份

  

#### Yarn构架概述

Yet Another Resource Negotiator简称YARN,资源协调者,是Hadoop的资源管理器

![image.png](assets/Hadoop-1.png)

  

  

#### Mapreduce架构概述

将计算过程分为两个阶段:Map与Reduce

map阶段进行并行处理输出数据

redece阶段对Map结果进行汇总

  

#### 三者的关系

![image.png](assets/Hadoop-2.png)

  

![image.png](assets/Hadoop-3.png)

  

图中涉及的技术名词解释如下：

（1）Sqoop：Sqoop是一款开源的工具，主要用于在Hadoop、Hive与传统的数据库（MySQL）间进行数据的传递，可以将一个关系型数据库（例如：MySQL，Oracle 等）中的数据导进到Hadoop的HDFS中，也可以将HDFS的数据导进到关系型数据库中。

（2）Flume：Flume是一个高可用的，高可靠的，分布式的海量日志采集、聚合和传输的系统，Flume支持在日志系统中定制各类数据发送方，用于收集数据；

（3）Kafka：Kafka是一种高吞吐量的分布式发布订阅消息系统；

（4）Spark：Spark是当前最流行的开源大数据内存计算框架。可以基于Hadoop上存储的大数据进行计算。

（5）Flink：Flink是当前最流行的开源大数据内存计算框架。用于实时计算的场景较多。

（6）Oozie：Oozie是一个管理Hadoop作业（job）的工作流程调度管理系统。

（7）HBase：HBase是一个分布式的、面向列的开源数据库。HBase不同于一般的关系数据库，它是一个适合于非结构化数据存储的数据库。

（8）Hive：Hive是基于Hadoop的一个数据仓库工具，可以将结构化的数据文件映射为一张数据库表，并提供简单的SQL查询功能，可以将SQL语句转换为MapReduce任务进行运行。其优点是学习成本低，可以通过类SQL语句快速实现简单的MapReduce统计，不必开发专门的MapReduce应用，十分适合数据仓库的统计分析。

（9）ZooKeeper：它是一个针对大型分布式系统的可靠协调系统，提供的功能包括：配置维护、名字服务、分布式同步、组服务等。

  

### Hadoop序列化

**什么是序列化**

**序列化**就是把内存中的对象，转换成字节序列（或其他数据传输协议）以便于存储到磁盘（持久化）和网络传输。

**反序列化**就是将收到字节序列（或其他数据传输协议）或者是磁盘的持久化数据，转换成内存中的对象。

序列化作用于保存数据,发送数据

**为什么不用** **Java** **的序列化**

Java的序列化是一个重量级序列化框架（Serializable），一个对象被序列化后，会附带很多额外的信息（各种校验信息，Header，继承体系等），不便于在网络中高效传输。所以，Hadoop自己开发了一套序列化机制（Writable）

**Hadoop** **序列化特点**

**Ø** **紧凑** **：**高效使用存储空间。

**Ø** **快速：**读写数据的额外开销小。

**Ø 互操作：**支持多语言的交互

  

#### 自定义bean对象实现序列化接口(writable)

在企业开发中往往常用的基本序列化类型不能满足所有需求，比如在Hadoop框架内部传递一个bean对象，那么该对象就需要实现序列化接口。

  

具体实现bean对象序列化步骤如下7步。

（1）必须实现Writable接口

（2）反序列化时，需要反射调用空参构造函数，所以必须有空参构造

（3）重写序列化方法

（4）重写反序列化方法

（5）注意反序列化的顺序和序列化的顺序完全一致。

（6）要想把结果显示在文件中，需要重写toString()，可用"\\t"分开，方便后续用。

（7）如果需要将自定义的bean放在key中传输，则还需要实现Comparable接口，因为MapReduce框中的Shuffle过程要求对key必须能排序。

  

  

#### 案例实操

  

### Hadoop数据压缩

压缩的优点：以减少磁盘IO、减少磁盘存储空间。

压缩的缺点：增加CPU开销。

原则:

1）运算密集型的Job，少用压缩。

（2）IO密集型的Job，多用压缩。

#### 支持的压缩

1）压缩算法对比介绍

| 压缩格式 | Hadoop自带？ | 算法 | 文件扩展名 | 是否可切片 | 换成压缩格式后，原来的程序是否需要修改 |
| --- | --- | --- | --- | --- | --- |
| DEFLATE | 是，直接使用 | DEFLATE | .deflate | 否 | 和文本处理一样，不需要修改 |
| Gzip | 是，直接使用 | DEFLATE | .gz | 否 | 和文本处理一样，不需要修改 |
| bzip2 | 是，直接使用 | bzip2 | .bz2 | 是 | 和文本处理一样，不需要修改 |
| LZO | 否，需要安装 | LZO | .lzo | 是 | 需要建索引，还需要指定输入格式 |
| Snappy | 是，直接使用 | Snappy | .snappy | 否 | 和文本处理一样，不需要修改 |

2）压缩性能的比较

| 压缩算法 | 原始文件大小 | 压缩文件大小 | 压缩速度 | 解压速度 |
| --- | --- | --- | --- | --- |
| gzip | 8.3GB | 1.8GB | 17.5MB/s | 58MB/s |
| bzip2 | 8.3GB | 1.1GB | 2.4MB/s | 9.5MB/s |
| LZO | 8.3GB | 2.9GB | 49.3MB/s | 74.6MB/s |

[http://google.github.io/snappy/](http://google.github.io/snappy/)

Snappy is a compression/decompression library. It does not aim for maximum compression, or compatibility with any other compression library; instead, it aims for very high speeds and reasonable compression. For instance, compared to the fastest mode of zlib, Snappy is an order of magnitude faster for most inputs, but the resulting compressed files are anywhere from 20% to 100% bigger.On a single core of a Core i7 processor in 64-bit mode, Snappy compresses at about 250 MB/sec or more and decompresses at about 500 MB/sec or more.

  

压缩方式选择时重点考虑：压缩/解压缩速度、压缩率（压缩后存储大小）、压缩后是否可以支持切片。

  

Gzip压缩

优点：压缩率比较高。

缺点：不支持Split；压缩/解压速度一般。

Bzip2压缩

优点：压缩率高；支持Split。

缺点：压缩/解压速度慢。

Lzo压缩

优点：压缩/解压速度比较快；支持Split。

缺点：压缩率一般；想支持切片需要额外创建索引。

Snappy压缩

优点：压缩和解压缩速度快。

缺点：不支持Split；压缩率一般。

#### 压缩位置选择

压缩可以在MapReduce作用的任意阶段启用。

#### 压缩参数配置

1）为了支持多种压缩/解压缩算法，Hadoop引入了编码/解码器

| 压缩格式 | 对应的编码/解码器 |
| --- | --- |
| DEFLATE | org.apache.hadoop.io.compress.DefaultCodec |
| gzip | org.apache.hadoop.io.compress.GzipCodec |
| bzip2 | org.apache.hadoop.io.compress.BZip2Codec |
| LZO | com.hadoop.compression.lzo.LzopCodec |
| Snappy | org.apache.hadoop.io.compress.SnappyCodec |

2）要在Hadoop中启用压缩，可以配置如下参数

| 参数 | 默认值 | 阶段 | 建议 |
| --- | --- | --- | --- |
| io.compression.codecs<br>（在core-site.xml中配置） | 无，这个需要在命令行输入hadoop checknative查看 | 输入压缩 | Hadoop使用文件扩展名判断是否支持某种编解码器 |
| mapreduce.map.output.compress（在mapred-site.xml中配置） | false | mapper输出 | 这个参数设为true启用压缩 |
| mapreduce.map.output.compress.codec（在mapred-site.xml中配置） | org.apache.hadoop.io.compress.DefaultCodec | mapper输出 | 企业多使用LZO或Snappy编解码器在此阶段压缩数据 |
| mapreduce.output.fileoutputformat.compress（在mapred-site.xml中配置） | false | reducer输出 | 这个参数设为true启用压缩 |
| mapreduce.output.fileoutputformat.compress.codec（在mapred-site.xml中配置） | org.apache.hadoop.io.compress.DefaultCodec | reducer输出 | 使用标准工具或者编解码器，如gzip和bzip2 |

  

### 压缩实操案例

#### 4.5.1 Map输出端采用压缩

即使你的MapReduce的输入输出文件都是未压缩的文件，你仍然可以对Map任务的中间结果输出做压缩，因为它要写在硬盘并且通过网络传输到Reduce节点，对其压缩可以提高很多性能，这些工作只要设置两个属性即可，我们来看下代码怎么设置。

#### reduce输出端采用压缩

