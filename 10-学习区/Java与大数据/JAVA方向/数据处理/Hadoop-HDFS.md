---
tags: [Java与大数据, 概念]
created: 2026-09-06
status: 整理中
domain: Java与大数据
source: 个人总结
---
# Hadoop之HDFS

​  

## HDFS概述

HDFS只是分布式文件管理系统中的一种。

一种系统来管理多台机器上的文件，这就是分布式文件管理系统

hdfs(Hadoop Distributed File System)用于存储文件的系统,通过目录树来定位文件,分布式的,由很多服务器联合起来实现其功能，集群中的服务器有各自的角色

​  

HDFS的使用场景：适合一次写入，多次读出的场景。一个文件经过创建、写入和关闭之后就不需要改变。

​  

#### 优缺点

(1)高容错-----------多副本机制,可自动恢复丢失的副本

(2)适合处理大数据-------数据规模可达PB级别,文件规模可达到百万规模以上

(3)可购建在廉价机器上,多副本机制提供可靠性

缺点

(1)不适合低延时的数据访问------做不到毫秒级别的数据存储

(2)无法高效的对大小文件进行存储---------小文件问题,占用NN的存储信息,寻址时间超过读取时间

寻址时间最佳为传输时间的1%,目前的磁盘传输效率普遍为100mb/s

(3)不支持并发写入,文件随机修改-------一文件仅能有一个写,不支持多个线程同时写,仅支持文件的追加写(append)

#### HDFS的组成架构

![image.png](assets/Hadoop-4.png)

NN(NAMENODE)作为master,主管,管理者,--------1,管理hdfs的名称空间2,配置副本策略3,管理数据块的映射信息4,处理客户端读写请求

DN(datanode)作为slave,worker,执行nn下达的操作,----------存储实际的数据块,执行数据块的读写操作

Client:客户端,----------1,切分上传hdfs的文件成Block后长传,2,与nn交互,获取文件的位置信息,3,与DN交互,读取或写入数据4,提供命令管理hdfs,例如格式化nn,访问hdfs,例如对hdfs增删改查

2NN(Secondary NameNode):当nn挂掉的时候不能马上替换nn并提供服务,----1,辅助nn,分担工作量, 2,紧急情况下,辅助恢复nn

#### HDFS文件块大小

在物理上是分块(Block)存储的,大小可以通配置参数(dfs.blocksize)来确定,在2.x之后默认是128m,1.x是64

![image.png](assets/Hadoop-5.png)

文件块大小要适宜,小了占据寻址时间,大了磁盘传输时间,处理速度

hfds的块文件的大小主要取决于磁盘的传输效率

## HDFS的shell操作

见常用组件及其命令

## HDFS的API操作

1,配置环境

2,写代码

## HDFS的读写流程

### 写流程

  

![image.png](assets/Hadoop-6.png)

（1）客户端通过Distributed FileSystem模块向NameNode请求上传文件，NameNode检查目标文件是否已存在，父目录是否存在。

（2）NameNode返回是否可以上传。

（3）客户端请求第一个 Block上传到哪几个DataNode服务器上。

（4）NameNode返回3个DataNode节点，分别为dn1、dn2、dn3。

（5）客户端通过FSDataOutputStream模块请求dn1上传数据，dn1收到请求会继续调用dn2，然后dn2调用dn3，将这个通信管道建立完成。

（6）dn1、dn2、dn3逐级应答客户端。

（7）客户端开始往dn1上传第一个Block（先从磁盘读取数据放到一个本地内存缓存），以Packet为单位，dn1收到一个Packet就会传给dn2，dn2传给dn3；dn1每传一个packet会放入一个应答队列等待应答。

（8）当一个Block传输完成之后，客户端再次请求NameNode上传第二个Block的服务器。（重复执行3-7步）。

#### 网络拓扑-节点距离计算

在HDFS写数据的过程中，NameNode会选择距离待上传数据最近距离的DataNode接收数据。那么这个最近距离怎么计算呢？

节点距离：两个节点到达最近的共同祖先的距离总和。

  

#### 机架感知

机架感知说明

（1）官方说明

[http://hadoop.apache.org/docs/r3.1.3/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html#Data\_Replication](#Data_Replication)

（2）源码说明

Crtl + n 查找BlockPlacementPolicyDefault，在该类中查找chooseTargetInOrder方法。

#### 副本选择

![image.png](assets/Hadoop-7.png)

​  

​  

### 读流程

![image.png](assets/Hadoop-8.png)

（1）客户端通过DistributedFileSystem向NameNode请求下载文件，NameNode通过查询元数据，找到文件块所在的DataNode地址。

（2）挑选一台DataNode（就近原则，然后随机）服务器，请求读取数据。

（3）DataNode开始传输数据给客户端（从磁盘里面读取数据输入流，以Packet为单位来做校验）。

（4）客户端以Packet为单位接收，先在本地缓存，然后写入目标文件。

## NN与2NN

#### 工作机制

因为经常需要进行随机访问，还有响应客户请求，元数据需要存放在内存中,一旦断电，元数据丢失，整个集群就无法工作了。因此产生在磁盘中备份元数据的FsImage。

当在内存中的元数据更新时，如果同时更新FsImage，就会导致效率过低，但如果不更新，就会发生一致性问题,一旦NameNode节点断电，就会产生数据丢失。因此，引入Edits文件（只进行追加操作，效率很高）。每当元数据有更新或者添加元数据时，修改内存中的元数据并追加到Edits中。

一旦NameNode节点断电，可以通过FsImage和Edits的合并，合成元数据。

如果长时间添加数据到Edits中，会导致该文件数据过大，效率降低，而且一旦断电，恢复元数据需要的时间过长。因此，需要定期进行FsImage和Edits的合并，如果这个操作由NameNode节点完成，又会效率过低。因此，引入一个新的节点SecondaryNamenode，专门用于FsImage和Edits的合并。

![image.png](assets/Hadoop-9.png)

**第一****阶段：****NameNode****启动**

（1）第一次启动NameNode格式化后，创建Fsimage和Edits文件。如果不是第一次启动，直接加载编辑日志和镜像文件到内存。

（2）客户端对元数据进行增删改的请求。

（3）NameNode记录操作日志，更新滚动日志。

（4）NameNode在内存中对元数据进行增删改。

**2****）第二****阶段：****Secondary NameNode****工作**

（1）Secondary NameNode询问NameNode是否需要CheckPoint。直接带回NameNode是否检查结果。

（2）Secondary NameNode请求执行CheckPoint。

（3）NameNode滚动正在写的Edits日志。

（4）将滚动前的编辑日志和镜像文件拷贝到Secondary NameNode。

（5）Secondary NameNode加载编辑日志和镜像文件到内存，并合并。

（6）生成新的镜像文件fsimage.chkpoint。

（7）拷贝fsimage.chkpoint到NameNode。

（8）NameNode将fsimage.chkpoint重新命名成fsimage。

#### Fsimage和Edits解析

![image.png](assets/Hadoop-10.png)

**oiv****查看****Fsimage****文件**

（1）查看oiv和oev命令

[atguigu@hadoop102 current]$ hdfs

**oiv** apply the offline fsimage viewer to an fsimage

**oev** apply the offline edits viewer to an edits file

​  

（2）基本语法

hdfs oiv -p 文件类型 \-i镜像文件 \-o 转换后文件输出路径

（3）案例实操

[atguigu@hadoop102 current]$ pwd

/opt/module/hadoop-3.1.3/data/dfs/name/current

​  

[atguigu@hadoop102 current]$ hdfs oiv -p XML -i fsimage\_0000000000000000025 -o /opt/module/hadoop-3.1.3/fsimage.xml

​  

[atguigu@hadoop102 current]$ cat /opt/module/hadoop-3.1.3/fsimage.xml

**oev****查看****Edits****文件**

（1）基本语法

hdfs oev -p 文件类型 \-i编辑日志 \-o 转换后文件输出路径

（2）案例实操

[atguigu@hadoop102 current]$ hdfs oev -p XML -i edits\_0000000000000000012-0000000000000000013 -o /opt/module/hadoop-3.1.3/edits.xml

​  

[atguigu@hadoop102 current]$ cat /opt/module/hadoop-3.1.3/edits.xml

​  

#### checkpoint时间设置

1）通常情况下，SecondaryNameNode每隔一小时执行一次

**一分钟****检查一次操作次数，当操作次数达到****1****百万****时，****SecondaryNameNode****执行****一次。**

<property>

​<name>dfs.namenode.checkpoint.txns</name>

​<value>1000000</value>

<description>操作动作次数</description>

</property>

​  

<property>

​<name>dfs.namenode.checkpoint.check.period</name>

​<value>60s</value>

<description> 1分钟检查一次操作次数</description>

</property>

## DN

#### DataNode工作机制

![image.png](assets/Hadoop-11.png)

（1）一个数据块在DataNode上以文件形式存储在磁盘上，包括两个文件，一个是数据本身，一个是元数据包括数据块的长度，块数据的校验和，以及时间戳。

（2）DataNode启动后向NameNode注册，通过后，周期性（6小时）的向NameNode上报所有的块信息。

#### 心跳机制

心跳是每3秒一次，心跳返回结果带有NameNode给该DataNode的命令如复制块数据到另一台机器，或删除某个数据块。如果超过10分钟没有收到某个DataNode的心跳，则认为该节点不可用。

#### 数据完整性

如下是DataNode节点保证数据完整性的方法。

（1）当DataNode读取Block的时候，它会计算CheckSum。

（2）如果计算后的CheckSum，与Block创建时值不一样，说明Block已经损坏。

（3）Client读取其他DataNode上的Block。

（4）常见的校验算法crc（32），md5（128），sha1（160）。

（5）DataNode在其文件创建后周期验证CheckSum。

![image.png](assets/Hadoop-12.png)

#### 掉线时限参数设置

![image.png](assets/Hadoop-13.png)

需要注意的是hdfs-site.xml 配置文件中的heartbeat.recheck.interval的单位为毫秒，dfs.heartbeat.interval的单位为秒。

