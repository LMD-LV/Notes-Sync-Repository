---
tags: [Java与大数据, 概念]
created: 2026-09-06
status: 整理中
domain: Java与大数据
source: 个人总结
---
# Hadoop优化

### 多目录

DataNode设置多目录来存储不同的数据,

​  

磁盘间数据平衡问题,3.x出现的新特性,

​  

生成均衡计划 hdfs diskbalancer -plan

执行均衡计划 hdfs diskbalancer -execute

查看当前均衡任务的执行情况 hdfs diskbalancer

### 集群扩容及缩容

添加白名单 :白名单：表示在白名单的主机IP地址可以，用来存储数据。

企业中：配置白名单，可以尽量防止黑客恶意访问攻击。

​  

#### 服役新服务器

拷贝另一台服务器之后记得删除历史数据 data与log

将拷贝来的环境配置文件生效(source)

hdfs --daemon start datanode

yarn --daemon start nodemanager

在白名单中添加改服务器的信息

刷新namenode hdfs dfsadmin -refreshNodes

​  

#### 服务器间数据均衡

**开启数据均衡命令**

[atguigu@hadoop105 hadoop-3.1.3]$ sbin/start-balancer.sh -threshold 10

对于参数10，代表的是集群中各个节点的磁盘空间利用率相差不超过10%，可根据实际情况进行调整。

注意：由于HDFS需要启动单独的Rebalance Server来执行Rebalance操作，[所以尽量不要在NameNode上执行start-balancer.sh](http://xn--NameNodestart-balancer-sy68a2bx05ag98dux2afg9ay6af924fm2hzl3e.sh)，而是找一台比较空闲的机器。

#### 黑名单退役服务器

黑名单：表示在黑名单的主机IP地址不可以，用来存储数据。

企业中：配置黑名单，用来退役服务器。

​  

**第一次添加黑名单必须重启集群，不是第一次，只需要刷新NameNode节点即可**

hdfs dfsadmin -refreshNodes

​  

**检查Web浏览器，退役节点的状态为decommission in progress（退役中），说明数据节点正在复制块到其他节点**

**等待退役节点状态为decommissioned（所有块已经复制完成），停止该节点及节点资源管理器。注意：如果副本数是3，服役的节点小于等于3，是不能退役成功的，需要修改副本数后才能退役**

### 故障排除

NameNode挂掉了:NameNode进程挂了并且存储的数据也丢失了，如何恢复NameNode

拷贝2nn中的数据传到原NameNode存储数据目录

  

集群安全模式&磁盘恢复

安全模式:文件系统只接受读数据请求，而不接受删除、修改等变更请求

**进入安全模式场景**

Ø NameNode在加载镜像文件和编辑日志期间处于安全模式

Ø NameNode再接收DataNode注册时，处于安全模式

​  

**退出安全模式条件**

dfs.namenode.safemode.min.datanodes:最小可用datanode数量，默认0

dfs.namenode.safemode.threshold-pct:副本数达到最小要求的block占系统总block数的百分比，默认0.999f。（只允许丢一个块）

dfs.namenode.safemode.extension:稳定时间，默认值30000毫秒，即30秒

​  

​  

### 企业优化

### MapReduce优化

MapReduce优化方法主要从六个方面考虑：数据输入、Map阶段、Reduce阶段、IO传输、数据倾斜问题和常用的调优参数

​  

#### 数据输入端口

合并小文件:在执行MR任务前,将小文件合并,大量的小文件会产生大量的Map

增大了map的任务装载次数,任务的装载耗时,加大运行的时长

采用CombineTextInputFormat输入端解决了输入端大量小文件的场景

#### Map阶段

(1)减少溢写(Spill)次数 通过调整mapreduce.task.io.sort.mb以及mapreduce.map.sort.spill.percent参数值,增大触发Spill的内存上限,减少了spill的次数,减少了磁盘的IO

(2)减少合并(Merge)次数,通过调整mapreduce.task.io.sort.factor参数,

(3)在map之后,不影响业务逻辑前提下,先进行combine处理,减少I/O

​  

#### Reduce阶段

  

(1)合理设置Map与reduce的次数,太少,Task等待,延长处理时间 .

太多,map,reduce任务竞争,

(2)设置map.reduce共存,调整mapreduce.job.reduce.slowstart.completedmaps参数

,使得map运行到一定的程度之后,reduce开始运行,减少reduce的等待时间

(3)规避适应Reduce,reduce在连接数据集的时候会产生大量的网络消耗

(4)合理的设置Reduce端的Buffer:buffer与reduce不是直接关联的,通过设置参数来配置使得buffer的一部分数据可以直接输送到Reduce,来减少IO开销,mapreduce.reduce.input.percent,设置的值大于零的时候,会保留指定比例的内存读buffer的数据直接给Reduce使用

#### I/O传输

(1)采集数据压缩的方式,减少网络IO 的时间,安装压缩编码器

(2)使用SequeenceFile二进制文件

​  

#### 数据倾斜问题

数据倾斜的问题:数据倾斜现象,--------数据频率倾斜,数据大小倾斜

解决方法:(1)抽样和范围分区, 对原始数据抽样得到的结果集来预设分区边界值

(2)自定义分区

(3)Combiner

(4)采用mapjoin 避免reduce join

### 常用的调优参数

**资源相关参数**

（1）以下参数是在用户自己的MR应用程序中配置就可以生效（mapred-default.xml）

| 配置参数 | 参数说明 |
| --- | --- |
| mapreduce.map.memory.mb | 一个MapTask可使用的资源上限（单位:MB），默认为1024。如果MapTask实际使用的资源量超过该值，则会被强制杀死。 |
| mapreduce.reduce.memory.mb | 一个ReduceTask可使用的资源上限（单位:MB），默认为1024。如果ReduceTask实际使用的资源量超过该值，则会被强制杀死。 |
| mapreduce.map.cpu.vcores | 每个MapTask可使用的最多cpu core数目，默认值: 1 |
| mapreduce.reduce.cpu.vcores | 每个ReduceTask可使用的最多cpu core数目，默认值: 1 |
| mapreduce.reduce.shuffle.parallelcopies | 每个Reduce去Map中取数据的并行数。默认值是5 |
| mapreduce.reduce.shuffle.merge.percent | Buffer中的数据达到多少比例开始写入磁盘。默认值0.66 |
| mapreduce.reduce.shuffle.input.buffer.percent | Buffer大小占Reduce可用内存的比例。默认值0.7 |
| mapreduce.reduce.input.buffer.percent | 指定多少比例的内存用来存放Buffer中的数据，默认值是0.0 |

（2）应该在YARN启动之前就配置在服务器的配置文件中才能生效（yarn-default.xml）

| 配置参数 | 参数说明 |
| --- | --- |
| yarn.scheduler.minimum-allocation-mb | 给应用程序Container分配的最小内存，默认值：1024 |
| yarn.scheduler.maximum-allocation-mb | 给应用程序Container分配的最大内存，默认值：8192 |
| yarn.scheduler.minimum-allocation-vcores | 每个Container申请的最小CPU核数，默认值：1 |
| yarn.scheduler.maximum-allocation-vcores | 每个Container申请的最大CPU核数，默认值：32 |
| yarn.nodemanager.resource.memory-mb | 给Containers分配的最大物理内存，默认值：8192 |

（3）Shuffle性能优化的关键参数，应在YARN启动之前就配置好（mapred-default.xml）

| 配置参数 | 参数说明 |
| --- | --- |
| mapreduce.task.io.sort.mb | Shuffle的环形缓冲区大小，默认100m |
| mapreduce.map.sort.spill.percent | 环形缓冲区溢出的阈值，默认80% |

**2****）容错相关参数（****M****ap****R****educe****性能优化）**

| 配置参数 | 参数说明 |
| --- | --- |
| mapreduce.map.maxattempts | 每个Map Task最大重试次数，一旦重试次数超过该值，则认为Map Task运行失败，默认值：4。 |
| mapreduce.reduce.maxattempts | 每个Reduce Task最大重试次数，一旦重试次数超过该值，则认为Map Task运行失败，默认值：4。 |
| mapreduce.task.timeout | Task超时时间，经常需要设置的一个参数，该参数表达的意思为：如果一个Task在一定时间内没有任何进入，即不会读取新的数据，也没有输出数据，则认为该Task处于Block状态，可能是卡住了，也许永远会卡住，为了防止因为用户程序永远Block住不退出，则强制设置了一个该超时时间（单位毫秒），默认是600000（10分钟）。如果你的程序对每条输入数据的处理时间过长（比如会访问数据库，通过网络拉取数据等），建议将该参数调大，该参数过小常出现的错误提示是：“AttemptID:attempt_14267829456721_123456_m_000224_0 Timed out after 300 secsContainer killed by the ApplicationMaster.”。 |

### hadoop小文件问题

​  

HDFS的每个文件都要在NN上创建对应的元数据,每个占用150(byte),

这样当小文件比较多的时候，就会产生很多的元数据文件，一方面会大量占用NameNode的内存空间，另一方面就是元数据文件过多，使得寻址索引速度变慢。

小文件过多，在进行MR计算时，会生成过多切片，需要启动过多的MapTask。每个MapTask处理的数据量小，导致MapTask的处理时间比启动时间还小，白白消耗资源。

​  

#### 小文件优化的方案及其解决

(1) 数据采集--------Hadoop Archive

是一个高效的将小文件放入HDFS块中的文件存档工具，能够将多个小文件打包成一个HAR文件，从而达到减少NameNode的内存使用

(2)业务处理--------使用mapreduce程序对小文件进行合并

(3)mapreduce阶段-------combineTextInputFormat将多个小文件在切片过程中生成一个单独的切片或者少量的切片。

(4)uber阶段-------开启JVM重用 ,默认情况下，每个Task任务都需要启动一个JVM来运行，如果Task任务计算的数据量很小，我们可以让同一个Job的多个Task运行在一个JVM中，不必为每个Task都开启一个JVM.

​  

### Hadoop扩展

**1）scp实现两个远程主机之间的文件复制**

scp -r hello.txt [root@hadoop103:/user/atguigu/hello.txt](mailto:root@hadoop103:/user/atguigu/hello.txt) // 推push

scp -r [root@hadoop103:/user/atguigu/hello.txt  hello.txt](mailto:root@hadoop103:/user/atguigu/hello.txt%20%20hello.txt) // 拉 pull

scp -r [root@hadoop103:/user/atguigu/hello.txt](mailto:root@hadoop103:/user/atguigu/hello.txt) root@hadoop104:/user/atguigu //是通过本地主机中转实现两个远程主机的文件复制；如果在两个远程主机之间ssh没有配置的情况下可以使用该方式。

  

**2****）****采用****distcp****命令****实现****两个****Hadoop****集群之间的递归数据复制**

[atguigu@hadoop102 hadoop-3.1.3]$ bin/hadoop distcp hdfs://hadoop102:8020/user/atguigu/hello.txt hdfs://hadoop105:8020/user/atguigu/hello.txt

  

#### 小文件存档问题

![image.png](assets/Hadoop-29.png)

  

  

#### 回收站

开启回收站功能，可以将删除的文件在不超时的情况下，恢复原数据，起到防止误删除、备份等作用。

![image.png](assets/Hadoop-30.png)

  

# HA高可用

#### HA(High Availabilty)概述

（1）所谓HA（High Availablity），即高可用（7 \* 24小时不中断服务）。

（2）实现高可用最关键的策略是消除单点故障。HA严格来说应该分成各个组件的HA机制：HDFS的HA和YARN的HA。

（3）NameNode主要在以下两个方面影响HDFS集群

Ø NameNode机器发生意外，如宕机，集群将无法使用，直到管理员重启。

Ø NameNode机器需要升级，包括软件、硬件升级，此时集群也将无法使用。

HDFS HA功能通过配置多个NameNodes(Active/Standby)实现在集群中对NameNode的热备来解决上述问题。如果出现故障，如机器崩溃或机器需要升级维护，这时可通过此种方式将NameNode很快的切换到另外一台机器。

#### HDFS-HA核心问题

**1****）怎么保证三台****namenode****的数据一致**

（1）Fsimage：让一台nn生成数据，让其他机器nn同步。

（2）Edits：需要引进新的模块JournalNode来保证edtis的文件的数据一致性。

**2）****怎么让同时只有一台****nn****是****active****，其他所有是****standby****的**

（1）手动分配

（2）自动分配

**3****）****2nn****在****ha****架构中并不存在，定期合并****fsimage****和****edtis****的活谁来干**

​由standby的nn来干。

**4****）如果****nn****真的发生了问题，怎么让其他的****nn****上位干活**

（1）手动故障转移

（2）自动故障转移

  

#### HDFS-HA 自动模式

自动故障转移为HDFS部署增加了两个新组件：ZooKeeper和ZKFailoverController（ZKFC）进程，如图所示。ZooKeeper是维护少量协调数据，通知客户端这些数据的改变和监视客户端故障的高可用服务。

![image.png](assets/Hadoop-31.png)

#### HDFS-HA自动故障转移

详见配置文件

#### 连接不上JournalNode的问题

**<!-- NN连接JN重试次数，默认是10次-->**

**<!-- 重试时间间隔，默认1s -->**

也可以在core-site.xml里面适当调大上面的两个参数：

  

Yarn-HA配置

![image.png](assets/Hadoop-32.png)

  

**2）****核心问题**

**（****1****）如果当前****active rm****挂了，其他****rm****怎么将其他****standby rm****上位**

核心原理跟HDFS一样，利用了zk的临时节点。

**（****2****）当前****rm****上有很多的计算程序在等待运行，其他的****rm****怎么将这些程序接手过来接着跑**

rm会将当前的所有计算程序的状态存储在zk中，其他rm上位后会去读取，然后接着跑。

​  

​  

​  

​  

​  

![image.png](assets/Hadoop-33.png)