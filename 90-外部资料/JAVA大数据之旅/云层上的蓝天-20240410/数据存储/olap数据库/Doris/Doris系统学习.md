# 简介

## 能力介绍

Apache Doris 是一款基于 MPP 架构的高性能、实时的分析型数据库，以高效、简单、统一的特点被人们所熟知，仅需亚秒级响应时间即可返回海量数据下的查询结果，不仅可以支持**高并发的点查询**场景，也能支持**高吞吐的复杂分析**场景。基于此，Apache Doris 能够较好的满足报表分析、即席查询、统一数仓构建、数据湖联邦查询加速等使用场景，用户可以在此之上构建大屏看板、用户行为分析、AB 实验平台、日志检索分析、用户画像分析、订单分析等应用。

## 定位

多功能olap数据库，能简化kafka+flink、hadoop+hive等复杂架构，缩短链路与使用难度；

适用于报表分析、即席查询、统一数仓构建、数据湖联邦查询加速等使用场景。

![](assets/Doris系统学习-1.png)

## 架构及技术特点

![](assets/Doris系统学习-2.png)

**FE（Frontend）**：存储、维护集群**元数据**；负责接收、解析查询请求，规划查询计划，调度查询执行，返回查询结果。主要有三个角色：

（1）Leader 和Follower：主要是用来达到元数据的高可用，保证单节点宕机的情况下，元数据能够实时地在线恢复，而不影响整个服务。

（2）Observer：用来扩展查询节点，同时起到元数据备份的作用。如果在发现集群压力非常大的情况下，需要去扩展整个查询的能力，那么可以加observer 的节点。observer 不参与任何的写入，只参与读取，同时备份master节点的元数据。

**BE（Backend）**：负责**物理数据的存储和计算**；依据FE 生成的物理计划，分布式地执行查询。

数据的可靠性由BE 保证，BE 会对整个数据存储多副本或者是三副本。副本数可根据需求动态调整。

**MySQL Client**

Doris借助MySQL协议，用户使用任意MySQL的ODBC/JDBC以及MySQL的客户端，都可以直接访问Doris。

**Broker**

Broker为一个独立的无状态进程。封装了文件系统接口，提供Doris读取远端存储系统中文件的能力，包括HDFS，S3，BOS等。

## 架构原理

### 基本概念

**FE：**Frontend，即 Doris 的前端节点。主要负责接收和返回客户端请求、元数据以及集群管理、查询计划生成等工作。

**BE：**Backend，即 Doris 的后端节点。主要负责数据存储与管理、查询计划执行等工作。

**BDBJE：**Oracle Berkeley DB Java Edition， 在 Doris 中，使用 BDBJE 完成元数据操作日志的持久化、FE 高可用等功能。

**Tablet：**Tablet是一张实际的物理存储单元，一张表按照分区和分桶后在BE构成分布式存储层以Tablet为单位进行存储，每个Tablet包括元信息及若干个连续的RowSet。

**RowSet：**RowSet是Tablet中一次数据变更的数据集合，数据变更包括了数据导入、删除、更新等。RowSet按版本信息进行记录。每次变更会生成一个版本。

**Version：**由Start、End两个属性构成，维护数据变更的记录信息。通常用来表示RowSet的版本范围，在一次新导入后生成一个Start、End 相等的RowSet，在Compaction后生成一个带范围的RowSet版本。

**Segment：**表示RowSet中的数据分段，多个Segment构成一个RowSet。

**Compaction：**连续版本的RowSet合并的过程称为Compaction，合并过程中会对数据进行压缩操作。

**Key 列、Value 列：**在 Doris 中，数据以表（Table）的形式进行逻辑上的描述。一张表包括行（Row）和列（Column），Row 即用户的一行数据，Column 用于描述一行数据中不同的字段。Column可以分为两大类：Key 和 Value。从业务角度看，Key 和 Value 可以分别对应的维度列和指标列。Doris 的 Key 列是建表语句中指定的列，建表语句中的关键字 unique key 或 aggregate key 或 duplicate key 后面的列就是 Key 列，除了 Key 列剩下的就是 Value 列。

**数据模型：**Doris的数据模型主要分为3类：Duplicate、Aggregate、Unique。

**Base表：** Doris 中，将用户通过建表语句创建出来的表称为 Base 表（Base Table），Base 表中保存着按用户建表语句指定方式存储的基础数据。

**ROLLUP 表：**在 Base 表之上，用户可以创建任意多个 ROLLUP 表。这些 ROLLUP 的数据是基于 Base 表产生的，并且在物理上是独立存储的。ROLLUP 表的基本作用，在于在 Base 表的基础上，获得更粗粒度的聚合数据，类似于物化视图。

### Doris 的存储结构

Doris 通过 storage\_root\_path 进行存储路径配置，Segment 文件存放在 tablet\_id 目录下按 SchemaHash 管理。Segment 文件可以有多个，一般按照大小进行分割，默认为256M。存储目录以及Segment文件命名规则为： ${storage\_root\_path}/data/${shard}/${tablet\_id}/${schema\_hash}/${rowset\_id}\_${segment\_id}.dat

![](assets/Doris系统学习-3.png)

**${shard}：**即上图中的 0、1。是存储目录下 BE 自动创建的，是随机的。会随着数据的增多而增多。

**${tablet\_id}：**即上图中的 15123、27003 等，即上面提到的 Bucket 的 ID。

**${schema\_hash}：**即上图中的 727041558、1102328406 等。因为一个表的结构可能会被变更，所以对每个 Schema 的版本生成一个 SchemaHash，来标识该版本下的数据。

**${segment\_id}.dat：**其中前面的为 rowset\_id，即上图中的 02000000000000e3ba4924368a21695d8cc3cf8525f80789；${segment\_id} 为当前 RowSet 的 segment\_id，从 0 开始递增。

### Segment 文件的存储格式:

Segment 整体的文件格式分为数据区域、索引区域、Footer三个部分，如下图所示：

![](assets/Doris系统学习-4.png)

**Data Region：** 用于存储各个列的数据信息，这里的数据是按需分Page加载的，其中 Page 中包含了列的数据，每个Page为 64k。

**Index Region：**Doris 中将各个列的 Index 数据统一存储在 Index Region，这里的数据会按照列粒度进行加载，所以跟列的数据信息分开存储。

**Footer 信息：**包含文件的元数据信息、内容的 Checksum 等。

### compaction /merge合并

当有insert、upsert、delete操作时，每一次操作会先生成数据key对应的tablet的rowset，数据量大时会生成多个segment存储数据和索引。每次操作会先在memtable中记录相关变化，一次操作将会有一个或多个rowset生成，rowset变多，小文件自然就多，doris会根据相应的策略来合并多个rowset到第一个rowset（start\_version为0的），或者将多个rowset先合并到一个临时的较大的rowset后再合并到第一个rowset。

合并过程主要是将tablet中数据按照排序key合并为有序的数据，这样在查询时能少了扫描很多小文件归并的操作。

合并中涉及三个概念：

base compaction：基础版本合并，合并后的rowset[0，x]，一般多次增量合并后会有一次基础合并

cumulative compaction：增量版本合并，合并后的rowset[x，x+n]

cumulative point：用于分割哪些rowset只能做base compaction，哪些能cumulative compaction，base合并后point会增加

![](assets/Doris系统学习-5.png)

[https://mp.weixin.qq.com/mp/appmsgalbum?\_\_biz=Mzg5MDEyODc1OA==&action=getalbum&album\_id=1507526553017090049&scene=126&sessionid=-1864583965&uin=&key=&devicetype=Windows+10+x64&version=63090a13&lang=zh\_CN&ascene=0](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzg5MDEyODc1OA==&action=getalbum&album_id=1507526553017090049&scene=126&sessionid=-1864583965&uin=&key=&devicetype=Windows+10+x64&version=63090a13&lang=zh_CN&ascene=0)

### 写入流程

写入数据时会先创建每个Segment的主键索引，再更新 Delete Bitmap。

![](assets/Doris系统学习-6.png)

### 读取流程

![](assets/Doris系统学习-7.png)

一个请求了版本 7 的 Query，只会看到版本 7 对应的数据

读取 RowSet5 的数据时，会将 V6 和 V7 对它的修改产生的 Bitmap 合并在一起，得到 Version7 对应的完整 DeleteBitmap，用来过滤数据

在上图的示例中，版本 8 的导入覆盖了 RowSet1 的 Segment2 一条数据，但请求版本 7 的 Query 仍然能读到该条数据

### Merge on Write(写时合并)的处理流程是：

对于每一条Key，查找它在 Base 数据中的位置（RowSetid + Segmentid + 行号）【内存中维护了 Segment 级别的主键区间树，加速查询】

如果 Key存在，则将该行数据标记删除。标记删除的信息记录在 Delete Bitmap 中，其中每个 Segment 都有一个对应的Delete Bitmap。

将更新的数据写入新的RowSet 中，完成事务，让新数据可见，即能够被用户查询到。

查询时，读取 Delete Bitmap，将被标记删除的行过滤掉，只返回有效的数据【对于命中的所有Segment，按照版本从高到低进行查询】

### insert

#### aggregate模型：

Insert 阶段将增量的数据按照 Append 的方式写到 RowSet，查询阶段采用 Merge on Read 的方式进行进行合并。也就是说数据在导入时先写入一个新的 RowSet，写入后并不会执行去重，只有在发起查询时才会做多路并发排序，在进行多路归并排序时，会将重复的 Key 排在一起，并进行聚合操作。其中高版本 Key 的会覆盖低版本的 Key，最终只返回给用户版本最高的那一条记录。

#### duplicate模型：

该模型写入与上述类似，读取阶段不会有任何聚合操作。

#### unique模型：

在 1.2 版本之前，该模型本质上是聚合模型的一个特例，行为与aggregate模型一致。由于聚合模型的实现方式是读时合并（Merge on Read），因此在一些聚合查询上性能不佳。Doris 在 1.2 版本后引入了 unique模型新的实现方式，写时合并（Merge on Write），通过在写入时将被覆盖和被更新的数据进行标记删除，在查询的时候，所有被标记删除的数据都会在文件级别被过滤掉，读取出来的数据就都是最新的数据，消除掉了读时合并中的数据聚合过程，并且能够在很多情况下支持多种谓词的下推。

在 1.2 版本之前，该模型本质上是聚合模型的一个特例，行为与aggregate模型一致。由于聚合模型的实现方式是读时合并（Merge on Read），因此在一些聚合查询上性能不佳。Doris 在 1.2 版本后引入了 unique模型新的实现方式，写时合并（Merge on Write），通过在写入时将被覆盖和被更新的数据进行标记删除，在查询的时候，所有被标记删除的数据都会在文件级别被过滤掉，读取出来的数据就都是最新的数据，消除掉了读时合并中的数据聚合过程，并且能够在很多情况下支持多种谓词的下推。

### update

UNIQUE模型Update过程本质上是 Select+Insert。

Update利用查询引擎自身的where过滤逻辑，从待更新表中筛选出需要被更新的行，基于此维护 Delete Bitmap 以及生成新插入的数据。

接着再执行Insert 逻辑，具体流程跟上述的UNIQUE模型写入逻辑类似。

### delete

Doris 的Delete也是会生成一个RowSet，Delete模式下没有对数据进行实际删除操作，而是对数据删除条件进行了记录，存储在Meta 信息中。当执行Base Compaction（基线合并）时删除条件会一起会被合并到Base版本中

Doris 在 unique key模型下也支持了 load\_delete，实现了通过批量导入删除的key对数据进行删除，能够支持大量数据删除能力。整体思路是在数据记录中加入删除状态标识，在Compaction流程中会对删除的key进行压缩。Compaction负责将多个RowSet版本进行合并。

### 索引

内建的智能索引，包括前缀索引和 ZoneMap 索引。

用户手动创建的二级索引，包括倒排索引、 Bloomfilter 索引、 Ngram Bloomfilter 索引 和 Bitmap 索引。

其中ZoneMap索引是在列存格式上，对每一列自动维护的索引信息，包括 Min/Max，Null 值个数等等。这种索引对用户透明。

### 集群间迁移

为了实现跨集群数据复制功能，Doris 引入了 Binlog机制。通过 Binlog 机制自动记录数据修改记录和操作，以实现数据的可追溯性，同时还可以基于Binlog回放机制来实现数据的重放和恢复。

在开启 Binlog属性后，FE 和 BE 会将 DDL/DML 操作的修改记录持久化成 Meta Binlog 和 Data Binlog。

### Doris 的表是多副本的，写入阶段怎么保证多副本的，是否有主从概念？需要 Majority 后再返回写入成功吗？

Doris BE的3副本没有主从的概念，采用 Quorum 算法保证多副本写入。

在写入过程中，FE 会判断每一个 Tablet 成功写入数据的副本数量是否超过了 Tablet 副本总数的一半，如果每一个 Tablet 成功写入数据的副本数量都超过 Tablet 副本总数的一半（多数成功），则 Commit Transaction 成功，并将事务状态设置为 COMMITTED；COMMITTED 状态表示数据已经成功写入，但是数据还不可见，需要继续执行 Publish Version 任务，此后，事务不可被回滚。

FE 会有一个单独的线程对 Commit 成功的 Transaction 执行 Publish Version，FE 执行 Publish Version 时会通过 Thrift RPC 向 Transaction 相关的所有 Executor BE 节点下发 Publish Version 请求，Publish Version 任务在各个 Executor BE 节点异步执行，将数据导入生成的 RowSet 变为可见的数据版本。

  

为什么会有 publish 机制?：类似于mvcc，如果没有 publish 机制，用户可能读到还没有提交的数据。

如果表为3副本，只写入成功 1 个副本会怎样：这个时候事务会aborted

如果表为3副本，只写入成功 2 副本会怎样：这个时候事务会 committed，doris fe 会定期执行 tablet 监控巡检，如果发现 tablet 副本异常，会生成 clone 任务，clone 一个新的副本。

为什么用户执行完 insert into，立即执行查询，结果可能为空呢：原因是事务还没有 publish

### Doris 的FE怎么保证高可用的？

元数据层面，Doris 采用 Paxos 协议以及 Memory + Checkpoint + Journal 的机制来确保元数据的高性能及高可靠。

![](assets/Doris系统学习-8.png)

元数据的数据流具体过程如下：

只有 Leader FE 可以对元数据进行写操作。写操作在修改 Leader 的内存后，会序列化为一条 Log，按照 key-value 的形式写入 BDBJE。其中 Key 为连续的整型，作为 log id，Value 即为序列化后的操作日志。

日志写入 BDBJE 后，BDBJE 会根据策略（写多数/全写），将日志复制到其他 Non-Leader 的 FE 节点。Non-Leader FE 节点通过对日志回放，修改自身的元数据内存镜像，完成与 Leader 节点的元数据同步。

Leader 节点的日志条数达到阈值（默认 10w 条）并且满足 Checkpoint 线程执行周期（默认六十秒）。Checkpoint 会读取已有的 Image 文件，和其之后的日志，重新在内存中回放出一份新的元数据镜像副本。然后将该副本写入到磁盘，形成一个新的 Image。之所以是重新生成一份镜像副本，而不是将已有镜像写成 Image，主要是考虑写 Image 加读锁期间，会阻塞写操作。所以每次 Checkpoint 会占用双倍内存空间。

Image 文件生成后，Leader 节点会通知其他 Non-Leader 节点新的 Image 已生成。Non-Leader 主动通过 HTTP 拉取最新的 Image 文件，来更换本地的旧文件。

BDBJE 中的日志，在 Image 做完后，会定期删除旧的日志。

解释：

元数据的每次更新，都首先写入到磁盘的日志文件中，然后再写到内存中，最后定期 Checkpoint 到本地磁盘上。

相当于是一个纯内存的一个结构，也就是说所有的元数据都会缓存在内存之中，从而保证 FE 在宕机后能够快速恢复元数据，而且不丢失元数据。

Leader、Follower 和 Observer 它们三个构成一个可靠的服务，单机的节点故障的时候其实基本上三个就够了，因为 FE 节点毕竟它只存了一份元数据，它的压力不大，所以如果 FE 太多的时候它会去消耗机器资源，所以多数情况下三个就足够了，可以达到一个很高可用的元数据服务。

用户可以使用 MySQL 连接任意一个 FE 节点进行元数据的读写访问。如果连接的是 Non-Leader 节点，则该节点会将写操作转发给 Leader 节点。

# 安装部署

① netstate -tunlp | grep fe端口和be使用到的各个端口，确保无已被占用情况。且验证操作系统的一些情况

```plain
# 验证各端口占用情况
netstate -tunlp | grep 9030
netstate -tunlp | grep 8030
.........
# 验证机器支持AVX2指令集（有输出结果），若不支持需使用no avx2的安装包
cat /proc/cpuinfo | grep avx2
# 关闭swap分区
swapoff -a 
# 永久关闭可使用 Linux root 账户，注释掉 /etc/fstab 中的 swap 分区，然后重启即可彻底关闭 swap 分区。
# 配置ntp服务，确保集群时间同步

```

② fe的conf中添加修改JAVA\_HOME、meta\_data目录、端口、priority\_networks = **10.1.3**.0/24、日志目录建议配置个大的盘。lower\_case\_table\_names大小写敏感配置，只有首次安装时配置生效，以后不可改；JAVA\_OPTS 参数配置相应内存，默认最大堆内存8G，生产肯定不够。

③ be的conf中添加修改storage\_root\_path目录（大的盘）、log目录（大的盘）、端口、priority\_networks = 10.1.3.0/24

④ 其他需要调优参数参考如下：

fe.conf: [https://doris.apache.org/zh-CN/docs/admin-manual/config/fe-config](https://doris.apache.org/zh-CN/docs/admin-manual/config/fe-config)

be.conf: [https://doris.apache.org/zh-CN/docs/admin-manual/config/be-config](https://doris.apache.org/zh-CN/docs/admin-manual/config/be-config)

⑤ 若需要链接hdfs、hive、kerberos认证等，可将相关配置加入be和fe的conf目录下（默认读取）

⑥ 启动 fe、be，第一个启动的fe将成为集群的leader，使用MySQL客户端连接该fe ip:9030，首次连接使用该fe节点上的的mysql（或者ip:8030访问网页操作）连接admin用户无需密码。连接上后可为admin、root设置密码方便后续其他mysql客户端连接。bin/start\_fe.sh --daemon bin/start\_be.sh --daemon

⑦ 加入fe节点

```sql
ALTER SYSTEM ADD FOLLOWER "<fe_ip_address>:<fe_edit_log_port>"
show frontends   -- alive 为 ture
```

⑧ 加入be节点

```sql
ALTER SYSTEM ADD BACKEND "<be_ip_address>:<be_heartbeat_service_port>"
show backends;	-- alive 为 ture
```

⑨ fe负载均衡

jdbc的自动重试可达到高可用效果：

```sql
jdbc:mysql:loadbalance://[host:port],[host:port].../[database][?propertyName1][=propertyValue1][&propertyName2][=propertyValue
```

ProxySQL 方式

nginx TCP方向代理方式

Haproxy方式

# 数据表设计

## 数据类型

| **类型名** | **字节数** | **描述** |
| --- | --- | --- |
| BOOLEAN | 1 | 布尔值，0 代表 false，1 代表 true。 |
| TINYINT | 1 | 有符号整数，范围 [-128, 127]。 |
| SMALLINT | 2 | 有符号整数，范围 [-32768, 32767]。 |
| INT | 4 | 有符号整数，范围 [-2147483648, 2147483647] |
| BIGINT | 8 | 有符号整数，范围 [-9223372036854775808, 9223372036854775807]。 |
| LARGEINT | 16 | 有符号整数，范围 [-2^127 + 1 ~ 2^127 - 1]。 |
| FLOAT | 4 | 浮点数，范围 [-3.4*10^38 ~ 3.4*10^38]。 |
| DOUBLE | 8 | 浮点数，范围 [-1.79*10^308 ~ 1.79*10^308]。 |
| DECIMAL | 2004/8/16 | 高精度定点数，格式：DECIMAL(M[,D])。其中，M 代表一共有多少个有效数字（precision），D 代表小数位有多少数字（scale）。有效数字 M 的范围是 [1, 38]，小数位数字数量 D 的范围是 [0, precision]。<br>0 < precision <= 9 的场合，占用 4 字节。<br>9 < precision <= 18 的场合，占用 8 字节。<br>16 < precision <= 38 的场合，占用 16 字节。 |
| DATE | 16 | 日期类型，目前的取值范围是 ['0000-01-01', '9999-12-31']，默认的打印形式是 'yyyy-MM-dd'。 |
| DATETIME | 16 | 日期时间类型，格式：DATETIME([P])。可选参数 P 表示时间精度，取值范围是 [0, 6]，即最多支持 6 位小数（微秒）。不设置时为 0。<br>取值范围是 ['0000-01-01 00:00:00[.000000]', '9999-12-31 23:59:59[.999999]']。打印的形式是 'yyyy-MM-dd HH:mm:ss.SSSSSS'。 |
| CHAR | M | 定长字符串，M 代表的是定长字符串的字节长度。M 的范围是 1-255。 |
| VARCHAR | M | 变长字符串，M 代表的是变长字符串的字节长度。M 的范围是 1-65533。变长字符串是以 UTF-8 编码存储的，因此通常英文字符占 1 个字节，中文字符占 3 个字节。 |
| STRING | / | 变长字符串，默认支持 1048576 字节（1MB），可调大到 2147483643 字节（2GB）。可通过 BE 配置 string_type_length_soft_limit_bytes 调整。String 类型只能用在 Value 列，不能用在 Key 列和分区分桶列。 |
| HLL | / | HLL 是模糊去重，在数据量大的情况性能优于 Count Distinct。HLL 的误差通常在 1% 左右，有时会达到 2%。HLL 不能作为 Key 列使用，建表时配合聚合类型为 HLL_UNION。<br>用户不需要指定长度和默认值。长度根据数据的聚合程度系统内控制。HLL 列只能通过配套的 hll_union_agg、hll_raw_agg、hll_cardinality、hll_hash 进行查询或使用。 |
| BITMAP | / | BITMAP 类型的列可以在 Aggregate 表或 Unique 表中使用。在 Unique 表中使用时，其必须作为非 Key 列使用。在 Aggregate 表中使用时，其必须作为非 Key 列使用，且建表时配合的聚合类型为 BITMAP_UNION。<br>用户不需要指定长度和默认值。长度根据数据的聚合程度系统内控制。BITMAP 列只能通过配套的 bitmap_union_count、bitmap_union、bitmap_hash、bitmap_hash64 等函数进行查询或使用。 |
| QUANTILE_STATE | / | QUANTILE_STATE 是一种计算分位数近似值的类型，在导入时会对相同的 Key，不同 Value 进行预聚合，当 value 数量不超过 2048 时采用明细记录所有数据，当 Value 数量大于 2048 时采用 TDigest 算法，对数据进行聚合（聚类）保存聚类后的质心点。QUANTILE_STATE 不能作为 Key 列使用，建表时配合聚合类型为 QUANTILE_UNION。<br>用户不需要指定长度和默认值。长度根据数据的聚合程度系统内控制。QUANTILE_STATE 列只能通过配套的 QUANTILE_PERCENT、QUANTILE_UNION、TO_QUANTILE_STATE 等函数进行查询或使用。 |
| ARRAY | / | 由 T 类型元素组成的数组，不能作为 Key 列使用。目前支持在 Duplicate 和 Unique 模型的表中使用。 |
| MAP | / | 由 K, V 类型元素组成的 map，不能作为 Key 列使用。目前支持在 Duplicate 和 Unique 模型的表中使用。 |
| STRUCT | / | 由多个 Field 组成的结构体，也可被理解为多个列的集合。不能作为 Key 使用，目前 STRUCT 仅支持在 Duplicate 模型的表中使用。一个 Struct 中的 Field 的名字和数量固定，总是为 Nullable。 |
| JSON | / | 二进制 JSON 类型，采用二进制 JSON 格式存储，通过 JSON 函数访问 JSON 内部字段。默认支持 1048576 字节（1MB），可调大到 2147483643 字节（2GB）。可通过 BE 配置 jsonb_type_length_soft_limit_bytes 调整。 |
| AGG_STATE | / | 聚合函数，只能配合 state/merge/union 函数组合器使用。AGG_STATE 不能作为 key 列使用，建表时需要同时声明聚合函数的签名。用户不需要指定长度和默认值。实际存储的数据大小与函数实现有关。 |

您也可通过SHOW DATA TYPES; 语句查看 Doris 支持的所有数据类型。

## 数据模型

### 主键模型 Unique

```sql
CREATE TABLE `mtpplcczs_mtpplcczs_plcc_case_division_result_A` (
  `id_case_division_result` BIGINT NOT NULL COMMENT '主键',	-- key（分区、分桶都算key，需排前面）
  `partition_key` DATE NOT NULL COMMENT '目标表分区字段',		-- 上游创建时间解析而来yyyy-mm-dd
  `case_no` TEXT NULL COMMENT '案件号',
  `business_code` TEXT NULL COMMENT '业务线编码-待删除',
  `task_no` TEXT NULL COMMENT '策略中心分案批次号',
  `stgy_code` TEXT NULL COMMENT '策略编码',
  `company_id` TEXT NULL COMMENT '受托公司ID(OCA)',
  `company_name` TEXT NULL COMMENT '受托公司名(OCA)',
  `entrust_begin_date` DATETIME NULL COMMENT '委托开始日期-待删除',
  `entrust_end_date` DATETIME NULL COMMENT '委托结束日期-待删除',
  `user_id` TEXT NULL COMMENT '业务员',
  `entrust_capital` DECIMAL(38, 10) NULL COMMENT '分案时委托金额-待删除',
  `is_deleted` BIGINT NULL COMMENT '逻辑删除，1表示删除',
  `updated_date` DATETIME NULL COMMENT '更新时间',
  `updated_by` TEXT NULL COMMENT '更新人',
  `created_date` DATETIME NULL COMMENT '创建时间',
  `created_by` TEXT NULL COMMENT '创建人',
  `queue` TEXT NULL COMMENT '队列-待删除',
  `division_date` DATETIME NULL COMMENT '分案时间',
  `relation_key` TEXT NULL COMMENT '关联唯一键：委案信息-分案结果-案件流转-待删除',
  `id_case_entrust_info` BIGINT NULL COMMENT '委案信息主键-待删除',
  `ext_id` TEXT NULL COMMENT '业务主键',
  `entrust_ext_id` TEXT NULL COMMENT '委案信息业务主键',
  `company_type` TEXT NULL COMMENT '公司类型，01：主催，02：协催',
  `oca_ext_id` TEXT NULL COMMENT '主催委案业务主键'
) ENGINE=OLAP		-- 内表
UNIQUE KEY(`id_case_division_result`, `partition_key`)	-- 主键排序列
COMMENT '分案结果表'
PARTITION BY RANGE(`partition_key`)()										-- range分区
DISTRIBUTED BY HASH(`id_case_division_result`) BUCKETS 1	-- 分桶
PROPERTIES (
"replication_allocation" = "tag.location.default: 3",			-- 默认3副本
"min_load_replica_num" = "-1",		-- 写入数据落盘两副本相应成功，可设置为1来增强性能，但是丢数
"is_being_synced" = "false",			
"dynamic_partition.enable" = "true",			-- 动态分区
"dynamic_partition.time_unit" = "MONTH",	-- 动态分区单位
"dynamic_partition.time_zone" = "Asia/Shanghai",	-- 分区参照系统时区
"dynamic_partition.start" = "-1000",			-- 保留多少个历史分区
"dynamic_partition.end" = "1",						-- 预建多少分区
"dynamic_partition.prefix" = "p",					-- 分区名前缀，如p20240519
"dynamic_partition.replication_allocation" = "tag.location.default: 3",  -- 副本数
"dynamic_partition.buckets" = "1",				-- 分桶数，alter...set后可对新分区生效
"dynamic_partition.create_history_partition" = "true",		-- 是否创建历史分区
"dynamic_partition.history_partition_num" = "60",					-- 创建多少个历史分区
"dynamic_partition.hot_partition_num" = "0",							-- 冷热分离相关
"dynamic_partition.reserved_history_periods" = "NULL",		-- 保留历史分区的时间范围，防止被自动删
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",		-- 控制分区开始结束范围
"storage_medium" = "hdd",			-- 存储介质类型
"storage_format" = "V2",			
"inverted_index_storage_format" = "V1",
"compression" = "LZ4",				-- 压缩，默认lz4，zstd压缩比会更高
"enable_unique_key_merge_on_write" = "true",		-- 写时合并
"light_schema_change" = "true",									-- 是否可修改列名、点查询优化相关
"function_column.sequence_col" = "updated_date",		-- 相同key数据更新逻辑，比大小字段
"disable_auto_compaction" = "false",								-- 自动合并
"enable_single_replica_compaction" = "false",				-- 单副本写入，性能更高，但be挂可能丢数
"group_commit_interval_ms" = "10000"								-- 默认10s、64MB提交数据
);
```

注意：delete语句需要where 条件作用在key上

### 明细模型 Duplicate

```sql
CREATE TABLE `mtpplcczs_mtpplcczs_plcc_case_division_result_A` (
  `id_case_division_result` BIGINT NOT NULL COMMENT '主键',	-- key（分区、分桶都算key，需排前面）
  `partition_key` DATE NOT NULL COMMENT '目标表分区字段',		-- 上游创建时间解析而来yyyy-mm-dd
  `case_no` TEXT NULL COMMENT '案件号',
  `business_code` TEXT NULL COMMENT '业务线编码-待删除',
  `task_no` TEXT NULL COMMENT '策略中心分案批次号',
  `stgy_code` TEXT NULL COMMENT '策略编码',
  `company_id` TEXT NULL COMMENT '受托公司ID(OCA)',
  `company_name` TEXT NULL COMMENT '受托公司名(OCA)',
  `entrust_begin_date` DATETIME NULL COMMENT '委托开始日期-待删除',
  `entrust_end_date` DATETIME NULL COMMENT '委托结束日期-待删除',
  `user_id` TEXT NULL COMMENT '业务员',
  `entrust_capital` DECIMAL(38, 10) NULL COMMENT '分案时委托金额-待删除',
  `is_deleted` BIGINT NULL COMMENT '逻辑删除，1表示删除',
  `updated_date` DATETIME NULL COMMENT '更新时间',
  `updated_by` TEXT NULL COMMENT '更新人',
  `created_date` DATETIME NULL COMMENT '创建时间',
  `created_by` TEXT NULL COMMENT '创建人',
  `queue` TEXT NULL COMMENT '队列-待删除',
  `division_date` DATETIME NULL COMMENT '分案时间',
  `relation_key` TEXT NULL COMMENT '关联唯一键：委案信息-分案结果-案件流转-待删除',
  `id_case_entrust_info` BIGINT NULL COMMENT '委案信息主键-待删除',
  `ext_id` TEXT NULL COMMENT '业务主键',
  `entrust_ext_id` TEXT NULL COMMENT '委案信息业务主键',
  `company_type` TEXT NULL COMMENT '公司类型，01：主催，02：协催',
  `oca_ext_id` TEXT NULL COMMENT '主催委案业务主键'
) ENGINE=OLAP		-- 内表
duplicate KEY(`id_case_division_result`, `partition_key`)	-- 明细排序列
COMMENT '分案结果表'
PARTITION BY RANGE(`partition_key`)()										-- range分区
DISTRIBUTED BY HASH(`id_case_division_result`) BUCKETS 1	-- 分桶
PROPERTIES (
"replication_allocation" = "tag.location.default: 3",			-- 默认3副本
"min_load_replica_num" = "-1",		-- 写入数据落盘两副本相应成功，可设置为1来增强性能，但是丢数
"is_being_synced" = "false",			
"dynamic_partition.enable" = "true",			-- 动态分区
"dynamic_partition.time_unit" = "MONTH",	-- 动态分区单位
"dynamic_partition.time_zone" = "Asia/Shanghai",	-- 分区参照系统时区
"dynamic_partition.start" = "-1000",			-- 保留多少个历史分区
"dynamic_partition.end" = "1",						-- 预建多少分区
"dynamic_partition.prefix" = "p",					-- 分区名前缀，如p20240519
"dynamic_partition.replication_allocation" = "tag.location.default: 3",  -- 副本数
"dynamic_partition.buckets" = "1",				-- 分桶数，alter...set后可对新分区生效
"dynamic_partition.create_history_partition" = "true",		-- 是否创建历史分区
"dynamic_partition.history_partition_num" = "60",					-- 创建多少个历史分区
"dynamic_partition.hot_partition_num" = "0",							-- 冷热分离相关
"dynamic_partition.reserved_history_periods" = "NULL",		-- 保留历史分区的时间范围，防止被自动删
"dynamic_partition.storage_policy" = "",
"dynamic_partition.start_day_of_month" = "1",		-- 控制分区开始结束范围
"storage_medium" = "hdd",			-- 存储介质类型
"storage_format" = "V2",			
"inverted_index_storage_format" = "V1",
"compression" = "LZ4",				-- 压缩，默认lz4，zstd压缩比会更高
"light_schema_change" = "true",									-- 是否可修改列名、点查询优化相关
"disable_auto_compaction" = "false",								-- 自动合并
"enable_single_replica_compaction" = "false",				-- 单副本写入，性能更高，但be挂可能丢数
"group_commit_interval_ms" = "10000"								-- 默认10s、64MB提交数据
);
```

### 聚合模型 Aggregate

```sql
CREATE TABLE IF NOT EXISTS example_tbl_agg1
(
    `user_id` LARGEINT NOT NULL COMMENT "用户id",
    `date` DATE NOT NULL COMMENT "数据灌入日期时间",
    `city` VARCHAR(20) COMMENT "用户所在城市",
    `age` SMALLINT COMMENT "用户年龄",
    `sex` TINYINT COMMENT "用户性别",
    `last_visit_date` DATETIME REPLACE DEFAULT "1970-01-01 00:00:00" COMMENT "用户最后一次访问时间",
    `cost` BIGINT SUM DEFAULT "0" COMMENT "用户总消费",
    `max_dwell_time` INT MAX DEFAULT "0" COMMENT "用户最大停留时间",
    `min_dwell_time` INT MIN DEFAULT "99999" COMMENT "用户最小停留时间"
)
AGGREGATE KEY(`user_id`, `date`, `city`, `age`, `sex`)
DISTRIBUTED BY HASH(`user_id`) BUCKETS 1
PROPERTIES (
"replication_allocation" = "tag.location.default: 1"
);
```

注意：delete语句需要where 条件作用在key上

## 分区分桶

### 分区

**手动分区：**range、list、null分区

**动态分区：**只支持在 DATE/DATETIME 列上进行 Range 类型的分区。

常用形式：可配置删除历史过期分区，可预见未来分区，从小时到年各种粒度

不同模型分区正常用什么字段？created\_date、updated\_date、current\_date？

unique 模型使用created\_date分区，只保留3个月数据，但是有数据更新三个月前数据，导致插入数据找不到分区怎么办？特殊分区（关闭动态分区->手动添加特殊分区->开启动态分区）

**自动分区：**支持range和list

目前还不大稳，不建议用

### 分桶

**手动分桶：**500MB-3GB 一个桶原则，根据导入数据大小来推算

**自动分桶：**不推荐使用，产生大量小文件

**注：**分桶键应选择基数较大的列，如主键、或其他常用查询过滤列

## 索引

### 索引使用

#### 排序列：

key即排序列，查询时带上排序列，能快速二分查找想要数据。

#### 前缀索引：

key的前36个字节，遇到varchar会截断，即使varchar没有36个字节。原理是稀疏索引，即给数据分块。

#### ZoneMap索引：

对每一列自动维护的索引信息，包括 Min/Max，Null 值个数等等。

#### 倒排索引：

对列值切分为词，将词排序编号建立索引，查询时根据命中的词定位相关数据。分词的情况下等值查询不能命中索引，范围查询可以。

关键词匹配，通过 MATCH\_ANY、MATCH\_ALL 完成（会忽略大小写），like不会忽略大小写。

```sql
CREATE DATABASE test_inverted_index;

USE test_inverted_index;

-- 创建表的同时创建了 comment 的倒排索引 idx_comment
--   USING INVERTED 指定索引类型是倒排索引
--   PROPERTIES("parser" = "english") 指定采用 "english" 分词，还支持 "chinese" 中文分词和 "unicode" 中英文多语言混合分词，如果不指定 "parser" 参数表示不分词

CREATE TABLE hackernews_1m
(
    `id` BIGINT,
    `deleted` TINYINT,
    `type` String,
    `author` String,
    `timestamp` DateTimeV2,
    `comment` String,
    `dead` TINYINT,
    `parent` BIGINT,
    `poll` BIGINT,
    `children` Array<BIGINT>,
    `url` String,
    `score` INT,
    `title` String,
    `parts` Array<INT>,
    `descendants` INT,
    INDEX idx_comment (`comment`) USING INVERTED PROPERTIES("parser" = "english") COMMENT 'inverted index for comment'
)
DUPLICATE KEY(`id`)
DISTRIBUTED BY HASH(`id`) BUCKETS 10
PROPERTIES ("replication_num" = "1");

-- 建表后添加的倒排索引需要build之后才能对全量数据生效，否则只是增量数据
CREATE INDEX idx_timestamp ON hackernews_1m(timestamp) USING INVERTED;
BUILD INDEX idx_timestamp ON hackernews_1m;
-- 查看索引构建是否完成
SHOW BUILD INDEX;

```

#### Bloomfilter 索引：

二进制数组+哈希函数，所有的值会被hash函数（多个）映射到数组相应位值（多个位置），有该数据则是1，没有就是0。在查询数据时若映射的位置上有0，则这个数据一定不存在；若是位置上全是1，则说明数据可能存在（1可能是其他数据映射的），这也称为假阳性。

```sql
-- 建表时添加索引
"bloom_filter_columns"="saler_id,category_id"
-- 删除索引
ALTER TABLE table_name SET ("bloom_filter_columns" = "");
-- 修改
ALTER TABLE table_name SET ("bloom_filter_columns" = "k1,k3");
```

### Doris有哪些索引（网上找的一篇文章，待整理）

目前 Doris 主要支持两类索引：

内建的智能索引，包括前缀索引和 ZoneMap 索引。

用户手动创建的二级索引，包括倒排索引、 Bloomfilter 索引、 Ngram Bloomfilter 索引 和 Bitmap 索引。

​  

其中ZoneMap索引是在列存格式上，对每一列自动维护的索引信息，包括 Min/Max，Null 值个数等等。这种索引对用户透明。

​  

索引是什么级别?

现在 Doris 里所有索引都是BE级别Local 的，例如：倒排索引、 Bloomfilter 索引、 Ngram Bloomfilter 索引 和 Bitmap 索引、前缀索引和 ZoneMap 索引等

Doris 没有 Global Index。广义理解上，分区间+分桶键 这些也能算是 Global 的，但是比较粗粒度。

索引的存储格式是怎样的？

doris 中将各个列的index数据统一存储在 segment文件的 index region，这里的数据会按照列粒度进行加载，所以跟列的数据信息分开存储。这里以short key index 前缀索引为例进行介绍。

​  

short key index 前缀索引，是在key（aggregate key、uniq key 和 duplicate key）排序的基础上，实现的一种根据给定前缀列，快速查询数据的索引方式。这里 short key index 前缀索引也采用了稀疏索引结构，在数据写入过程中，每隔一定行数，会生成一个索引项。这个行数为索引粒度默认为 1024 行，可配置。该过程如下图所示：

![](assets/Doris系统学习-9.png)

其中，KeyBytes 中存放了索引项数据，OffsetBytes 存放了索引项在 KeyBytes 中的偏移。

Short Key Index 采用了前 36 个字节，作为这行数据的前缀索引。当遇到 VARCHAR 类型时，前缀索引会直接截断。 Short Key Index 采用了前 36 个字节，作为这行数据的前缀索引。当遇到 VARCHAR 类型时，前缀索引会直接截断。

​  

读的过程如何命中索引？

在查询一个 Segment 中的数据时，根据执行的查询条件，会对首先根据字段加索引的情况对数据进行过滤。然后在进行读取数据，整体的查询流程如下：

![](assets/Doris系统学习-10.png)

首先，会按照Segment的行数构建了一个row\_bitmap，表示记录哪些数据需要进行读取。没有使用任务索引的情况下，需要读取所有数据。

当查询条件中按前缀索引规则使用到了Key 时，会先进行 ShortKey Index的过滤，可以在ShortKey Index中匹配到的Ordinal行号范围，合入到 row\_bitmap 中。

当查询条件中列字段存在 BitMap Index 索引时，会按照 BitMap索引直接查出符合条件的 Ordinal 行号，与 row\_bitmap 求交过滤。这里的过滤是精确的，之后去掉该查询条件，这个字段就不会再进行后面索引的过滤。

当查询条件中列字段存在 BloomFilter 索引并且条件为等值（eq，in，is）时，会按 BloomFilter 索引过滤，这里会走完所有索引，过滤每一个 Page 的 BloomFilter，找出查询条件能命中的所有 Page。将索引信息中的 Ordinal 行号范围与 row\_bitmap 求交过滤。

当查询条件中列字段存在 ZoneMap 索引时，会按 ZoneMap索引过滤，这里同样会走完所有索引，找出查询条件能与 ZoneMap 有交集的所有 Page。将索引信息中的 Ordinal 行号范围与 row\_bitmap求交过滤。

生成好 row\_bitmap 之后，批量通过每个Column 的 OrdinalIndex 找到到具体的 Data Page。

批量读取每一列的 Column Data Page 的数据。在读取时，对于有 Null 值的Page，根据 Null 值位图判断当前行是否是Null，如果为Null 进行直接填充即可。

## schema变更

表的 Schema，主要包括对列的修改和索引的改动。

-   Base Table：基表。每一个表被创建时，都对应一个基表。
-   Rollup：基于基表或者其他 Rollup 创建出来的上卷表。
-   Index：物化索引。Rollup 或 Base Table 都被称为物化索引。
-   Transaction：事务。每一个导入任务都是一个事务，每个事务有一个唯一递增的 Transaction ID。

变更分为key列和value列

**key列变更：**增删列、改属性都是比较重的操作，需要将数据读出、重新排序、再次写入。

**value列变更：**Light Schema Change 使得增减 Value 列可以在毫秒级完成；若是更改数据属性，则需读取数据、重新写入，但是不用排序。

## 冷热数据分层

将对数据新鲜度要求较高的数据存储在本地，将不再新鲜的数据放入hdfs、s3等对象存储器。

## 自增列

1.  仅 Duplicate 模型表和 Unique 模型表可以包含自增列。
2.  一张表最多只能包含一个自增列。
3.  自增列的类型必须是 BIGINT 类型，且必须为 NOT NULL。
4.  自增列手动指定的起始值必须大于等于 0。

**可用于做字典码值：**如用户ID

**可用于高效分页：**直接过滤指定的数据，而不需所有数据读入内存后显示部分数据。

## 规范(数仓)

### 准入：

① doris虽能实现流批一体，但对于时效要求极高的场景，并不能胜任，仍需走flink、spark streaming

② doris数据写入需异步线程compaction，需控制每次写入数据量+间隔，若是过于频繁且小数据量写入，则不利于compaction，会消耗大量cpu和磁盘io性能。故数据写入需攒批，无法攒批的频繁小数据量插入更新场景不易使用。

③ doris支持高效点查，但是高并发点查只针对于 key 列的等值查询，且查询中不能包含 join，嵌套子查询。故点查场景不推荐使用doris。

④ doris支持多种catalog外表联邦查询，但是外表查询当前只有hive外表支持统计信息（字段的min、max、count等信息），因此对于频繁点查点更新不推荐使用。

**综上：**

**doris不适用于时效性要求高；小批量频繁插入更新情况；高并发点查；**

**doris适用于数仓构建、日志检索、即席查询、实时看榜等场景，分钟/小时级链路延迟。**

### 命名：

**库名表名，命名统一小写，doris表名大小写敏感**

**库：子公司\_层级\_部门\_drs**

**表：层级\_[源库名]\_[源属主]\_[数据主题域]\_[业务过程]\_[粒度]\_源表名\_[周期]**

[]为可选项

ods：贴源层

不建议做过多的数据清洗工作，原封不动地接入**原始数据**即可，ods层数据可选压缩比较高算法，如zstd，其他层查询频率较高可选用解压缩快的lz4算法（hive常用）。数仓面向分析，doris默认列式存储，hive则可使用orc，统计分析查询性能会更好。

dwd：明细层

将 ODS 层的数据按照主题域、业务过程划分，提高事实表**易用性**，并且保证**数据质量**。如数据清理、整合、规范化、脏数据、垃圾数据、规范不一致的、状态定义不一致的、命名不规范的数据都会被处理，如时间格式、重复数据、脏数据、性别/状态等码值统一映射；另外事实表可将常用小维表字段退化至事实表。

dim：维表 **尽可能通用**

将ods层相关维表，区分主维表与相关维表整合为易用维表，如小额贷的产品表、产品属性、产品分类表可整合为产品粒度的一张维表即可；也可将用户的信息、关联设备、账号信息等整合。提升了维表的属性丰富度和减少join操作，达到易用。

高基数：用户、商品等千万级及以上数据，数据可使用主键模型（hive用拉链表实现）

低基数：配置表、码表等（每日全量同步覆盖即可）

dws：业务过程轻度公共汇总层

根据业务过程根据指标体系建设原理拆分指标为派生、衍生、原子指标，将原子指标沉淀为常用的、不同粒度的、按照不同周期轻度聚合的**通用性大宽表**。当一个公司业务场景充分多时，新需求，可直接由dws表+维表/dws表+dws表得到结果。

dwm层：多业务过程轻度汇总公共层

ads：结果层/应用层

满足客户不同统计分析要求，一般每一次需求即对应多个ads表。

**字段类型：**

上游数据统一转换为：date、datetime、decimal（38,10）、varchar几个类型，特殊字段另算。

### 元数据信息

**表名注释：**

表名、粒度、表义

**字段名：**

见名知意

creaed\_date、updated\_date等字段应全局统一，方便使用

新增表负责人字段，方便找人/告警处理。

### 开发规范

**主题域划分：**

可按照业务线或业务过程划分（常用）；也可根据数据域划分。

**模型设计：**

高内聚低耦合；核心与扩展模型分离；公共处理逻辑下沉及单一到dws层；适当冗余换取少join，但也不可过度冗余；数据可重跑。

结果层不可跨层调用ods、禁止反向依赖

指标口径统一

select \* 禁止

where 条件合理命中分区，尽可能提前过滤

禁止delete from where ...

doris 尽可能不适用 insert overwrite（性能差），hive可行。

字段类型转换统一，避免隐式转换精度丢失、或join笛卡尔积

sql注释

根据数据量，显示指定join 类型

数据倾斜警觉

**突发问题处理预案：**

跑的慢：

单表group by、多表join出现 数据倾斜，如何定位，处理？

非倾斜：资源不够？

跑太快：查崩上游、撑死下游，如何处理？

作业失败：

偶发失败：重启完事

逻辑问题：影响范围评估、通知被影响方、评估恢复时效、修改、重新上线、刷数。

数据不准：

逻辑、脏数据：影响范围评估、通知被影响方、评估恢复时效、刷数。

无法预期产出数据：

临时使用上一批次数据

告知被影响方，尽快恢复，写报告定责。

### 流程：

**需求评审：平台组+数仓组+业务产品+信创工具组**

业务场景、数据量、接入方式（flink、doris、hive/impala）、用途、时效性、上线日期、工作量评估等

评估已有表、已有模型是否能满足需求

**ods层接入表梳理：平台组**

涉密字段处理：禁止准入、或是加密，一般是接入非明文数据

数据全增量评估：评估对时效、集群的影响

数据接入：cdc工具实时同步、datax等跑批接入

**模型层：数仓组**

根据事实维度模型建模处理数据（dwd、dim、dws、dwm）

**上线评审：平台组+数仓组**

评估数仓开发模型合理性、链路依赖配置合理性、sql准确性、SQL注释、试跑资源消耗情况、SQL调优、参数限制、监控配置情况（数据延迟、数据量核对、数据唯一性、空值率、链路异常）等。

**数据应用：客户**

fineBI等系统接入数据，出报表

数据对账等

**其他相关：**

数据血缘、监控告警处理机制，代码库维护，数据资产维护，自助分析平台。

# 数据操作

## 数据导入

### 按场景划分

| **数据源** | **导入方式** |
| --- | --- |
| 对象存储（s3）,HDFS | [使用 Broker 导入数据](https://doris.apache.org/zh-CN/docs/data-operate/import/broker-load-manual) |
| 本地文件 | [Stream Load](https://doris.apache.org/zh-CN/docs/data-operate/import/stream-load-manual)<br>, [MySQL Load](https://doris.apache.org/zh-CN/docs/data-operate/import/mysql-load-manual) |
| Kafka | [订阅 Kafka 数据](https://doris.apache.org/zh-CN/docs/data-operate/import/routine-load-manual)、Routine Load |
| Mysql、PostgreSQL，Oracle，SQLServer | [通过外部表同步数据](https://doris.apache.org/zh-CN/docs/data-operate/import/insert-into-manual) |
| 通过 JDBC 导入 | [使用 JDBC 同步数据](https://doris.apache.org/zh-CN/docs/lakehouse/database/jdbc) |
| 导入 JSON 格式数据 | [JSON 格式数据导入](https://doris.apache.org/zh-CN/docs/data-operate/import/load-json-format) |

### 按导入方式划分

| **导入方式名称** | **使用方式** | **​** |
| --- | --- | --- |
| Broker Load | [通过 Broker 导入外部存储数据](https://doris.apache.org/zh-CN/docs/data-operate/import/broker-load-manual) | 适用于**拉取**远程存储，且**数据量较大**的场景、如：**hdfs、s3**等 |
| Stream Load | [流式导入数据 (本地文件及内存数据)](https://doris.apache.org/zh-CN/docs/data-operate/import/stream-load-manual) | 客户端http方式post数据到doris be、适合10GB以下，流批导入均可。 |
| Routine Load | [导入 Kafka 数据](https://doris.apache.org/zh-CN/docs/data-operate/import/routine-load-manual) | 持续消费kafka，task被视为stream load |
| Insert Into | [外部表通过 INSERT 方式导入数据](https://doris.apache.org/zh-CN/docs/data-operate/import/insert-into-manual) | 以hms、es、jdbc的方式创建hive、es、mysql、Oracle、postgresql、clickhouse、SQLserver、saphana、trino、OceanBase的catalog。通过查询catalog数据insert into doris。 |
| MySQL Load | [MySQL 客户端导入本地数据](https://doris.apache.org/zh-CN/docs/data-operate/import/mysql-load-manual) | 使用 MySQL 标准的 [LOAD DATA](https://dev.mysql.com/doc/refman/8.0/en/load-data.html) 语法导入本地文件，包含stream load 的能力 |

BROKER LOAD 和 ROUTINE LOAD支持前置过滤。

### 支持的数据格式

不同的导入方式支持的数据格式略有不同。

| **导入方式** | **支持的格式** |
| --- | --- |
| Broker Load | parquet、orc、csv、gzip |
| Stream Load | csv、json、parquet、orc |
| Routine Load | csv、json |
| MySQL Load | csv |

### 最小写入副本数

默认的数据导入任务，需数据写入副本数过半时返回写入成功，若想提高写入性能，可改为单副本写入成功。类似于kafka producer的acks 0 1 -1。

可以在创建表时设置表的min\_load\_replica\_num ，值需大于0且不超过副本数。

也可在已存在的表修改alter table tablea set ('min\_load\_replica\_num' = '1');

也可在fe配置项中设置全局

### 严格模式

严格模式参数会影响某些数值的导入行为和最终导入的数据。各种导入模式、connector 写入时都可指定。

① 源端目标端数据类型不匹配，若开启参数则数据会被过滤，否则为null

② 严格模式下，部分列更新需目标端必须存在key；非严格模式则没有key会插入新行。

## 数据导出

正常不会将doris数据导出，下游直接查询doris即可。

① EXPORT 支持通过 Broker 进程或 S3 协议/HDFS 协议 导出到远端存储上，支持导出 Doris 本地表 / View 视图 / 外表，支持导出到 parquet / orc / csv / csv\_with\_names / csv\_with\_names\_and\_types 文件格式。

② SELECT INTO OUTFILE 是一个同步命令，命令返回即表示操作结束，同时会返回一行结果来展示导出的执行结果。可将数据导出到hdfs、本地、s3。默认单BE单线程导出，并发调优可参考set enable\_parallel\_outfile = true; be\_instacne\_num ； parallel\_fragment\_exec\_instance\_num；参数。

③ flink doris connector也可读取doris写入其他地方。

④ MySQL Dump 是测试用的，生产不建议。

## 数据更新（update）

### unique模型

**update：**

该操作需读取待更新整行数据，然后修改部分更新字段再写入，读写事务耗时长、性能差、不适合大量数据更新。

where条件尽可能命中索引、分区分桶，且用于少量数据的修正，不频繁的更新，部分列更新。

**导入更新：**

该操作无需读取整行数据，仅需判断key是否存在，效率更高，且2.0之后开启Merge-on-Write性能更好、支持部分列更新，2.1后默认开启该参数。若是其他导入方式则需开启partial\_columns，若是部分列更新需关闭严格模式，否则无法插入新增数据。

### 聚合模型

不支持update语句

导入：全列更新时，聚合值可能在导入时更新，也可能在compaction时更新，用户查询时结果一样。另外也可设置REPLACE\_IF\_NOT\_NULL 来实现部分列更新效果。

## 数据删除（delete）

### delete from：

**原理：**

每执行一次 Delete 都会生成一个空的 rowset 来记录删除条件，并产生一个新的数据版本。每次读取都要对删除条件进行过滤，如果频繁删除或者删除条件过多时，都会严重影响查询性能。

**注意：**

-   使用表模型 AGGREGATE、UNIQUE 时，只能指定 Key 列上的条件。
-   当选定的 Key 列不存在于某个 Rollup 中时，无法进行 Delete。
-   条件之间只能是“与”的关系。若希望达成“或”的关系，需要将条件分写在两个 DELETE 语句中；
-   如果为分区表，需要指定分区，如果不指定，Doris 会从条件中推断出分区。两种情况下，Doris 无法从条件中推断出分区：1) 条件中不包含分区列；2) 分区列的 op 为 not in。当分区表未指定分区，或者无法从条件中推断分区的时候，需要设置会话变量 delete\_without\_partition 为 true，此时 Delete 会应用到所有分区。
-   该语句可能会降低执行后一段时间内的查询效率。影响程度取决于语句中指定的删除条件的数量。指定的条件越多，影响越大。

### 批量删除

**原理：**

在 Unique 表上增加一个隐藏列DORIS\_DELETE\_SIGN来实现，先对要删除数据根据key标记DORIS\_DELETE\_SIGN = true，查询时只查询为false的数据，在增量合并时不会处理数据，基础合并时会将标记为true的数据行真正删除。

**前提条件：**

需要启用导入任务的相关参数

### truncate

-   该语句清空数据，但保留表或分区。
-   不同于 DELETE，该语句只能整体清空指定的表或分区，不能添加过滤条件。
-   不同于 DELETE，使用该方式清空数据不会对查询性能造成影响。
-   该操作删除的数据不可恢复。
-   使用该命令时，表状态需为 NORMAL，即不允许正在进行 SCHEMA CHANGE 等操作。
-   该命令可能会导致正在进行的导入失败。

### 表原子替换

将两表数据快速原子互换，用于重写表数据时，减少先删后导数的数据不可用时长。可先create 新表 like原表，将正常数据导入新表，导入完成后执行以下语句。

```sql
ALTER TABLE [db.]tbl1 REPLACE WITH TABLE tbl2
[PROPERTIES('swap' = 'true')];
```

此操作不会检测两表表结构是否一致，因为本质就是rename操作。

假设要将表 A 替换为表 B，且 swap 为 true，默认true，则操作如下：

1.  将表 B 重名为表 A。
2.  将表 A 重名为表 B。

如果 swap 为 false，则操作如下：

1.  删除表 A。
2.  将表 B 重名为表 A。

### 临时分区

**场景：**

将临时分区和已有分区原子替换，治理分桶、分区不合理等情况，如增减历史分区桶数量、增减历史分区粒度。

**添加：**

临时分区不可读，不可与正式分区同名，可与正式分区范围相同。

```sql
ALTER TABLE tbl1 ADD TEMPORARY PARTITION tp1 VALUES LESS THAN("2020-02-01");

ALTER TABLE tbl2 ADD TEMPORARY PARTITION tp1 VALUES [("2020-01-01"), ("2020-02-01"));

ALTER TABLE tbl1 ADD TEMPORARY PARTITION tp1 VALUES LESS THAN("2020-02-01")
("replication_num" = "1")
DISTRIBUTED BY HASH(k1) BUCKETS 5;

ALTER TABLE tbl3 ADD TEMPORARY PARTITION tp1 VALUES IN ("Beijing", "Shanghai");

ALTER TABLE tbl4 ADD TEMPORARY PARTITION tp1 VALUES IN ((1, "Beijing"), (1, "Shanghai"));

ALTER TABLE tbl3 ADD TEMPORARY PARTITION tp1 VALUES IN ("Beijing", "Shanghai")
("replication_num" = "1")
DISTRIBUTED BY HASH(k1) BUCKETS 5;
```

**删除：**

```sql
ALTER TABLE tbl1 DROP TEMPORARY PARTITION tp1;
```

**替换：**

```sql
ALTER TABLE tbl1 REPLACE PARTITION (p1) WITH TEMPORARY PARTITION (tp1);

ALTER TABLE tbl1 REPLACE PARTITION (p1, p2) WITH TEMPORARY PARTITION (tp1, tp2, tp3);

ALTER TABLE tbl1 REPLACE PARTITION (p1, p2) WITH TEMPORARY PARTITION (tp1, tp2)
PROPERTIES (
    "strict_range" = "false",
    "use_temp_partition_name" = "true"
);
```

**注意：**

**strict\_range为true时会检测替换时分区范围是否一致，为false则只会检测分区范围不重复，不会检测是否缺失范围。use\_temp\_partition\_name为true则会删除正式分区，将临时分区转正，但若分区个数不一致且为false还会保留临时分区名。**

**临时分区存在会影响alter操作，临时分区删除无法恢复，正式分区、表删除后可在一定时间内recover。**

  

# 数据查询

## 支持功能

子查询、cte临时表、炸裂、开窗、加解密、复杂数据类型等。

```sql
SELECT
[hint_statement,...]
[ALL|DISTINCT|DISTINCTROW|ALLEXCEPT( col_name1 [, col_name2, col_name3,...])]
 select_expr [, select_expr ...]
[FROM table_references
[PARTITION partition_list]
[TABLET tabletid_list]
[TABLESAMPLE sample_value [ROWS|PERCENT]
[REPEATABLE pos_seek]]
[WHERE where_condition]
[GROUPBY[GROUPING SETS | ROLLUP | CUBE] {col_name | expr | position}]
[HAVING where_condition]
[ORDERBY {col_name | expr | position}
[ASC|DESC],...]
[LIMIT {[offset,] row_count | row_count OFFSEToffset}]
[INTOOUTFILE'file_name']
```

## 查询变量控制

查看当前变量配置：

```sql
SHOW VARIABLES;
SHOW VARIABLES LIKE '%time_zone%';
```

常用变量

```sql
SET exec_mem_limit = 10 * 1024 * 1024 * 1024;		-- 用于限制单个sql的instance 内存，防止打爆
SELECT /*+ SET_VAR(exec_mem_limit = 8589934592) */ name FROM people ORDER BY name;
SELECT /*+ SET_VAR(query_timeout = 1, enable_partition_cache=true) */ sleep(3);
lower_case_table_names	-- 表名小写，首次安装时可指定，之后无效
query_timeout						-- 查询超时时间
insert_timeout					-- 插入超时时间
wait_timeout						-- 等待超时
enable_profile					-- 开启后可查看更详细的执行计划
```

## 优化器+统计信息

结合CBO与RBO的优点，优化性能更好。

*SET* enable\_nereids\_planner=true;

开启统计信息，能对内表或者外表的查询有很大帮助，能过滤很多数据

| **信息** | **描述** |
| --- | --- |
| row_count | 总行数 |
| data_size | 总数据量 |
| avg_size_byte | 值的平均⻓度 |
| ndv | 不同值数量 |
| min | 最小值 |
| max | 最⼤值 |
| null_count | 空值数量 |

```sql
ANALYZE < TABLE | DATABASE table_name | db_name > 
    [ (column_name [, ...]) ]
    [ [ WITH SYNC ] [ WITH SAMPLE PERCENT | ROWS ] ];
```

-   table\_name: 指定的目标表。可以是 db\_name.table\_name 形式。
-   column\_name: 指定的目标列。必须是 table\_name 中存在的列，多个列名称用逗号分隔。
-   sync：同步收集统计信息。收集完后返回。若不指定则异步执行并返回 JOB ID。
-   sample percent | rows：抽样收集统计信息。可以指定抽样比例或者抽样行数。

2.03之后内表自动开启，外表可设置开启。可设置开启的时间策略。

```sql
ALTER CATALOG external_catalog SET PROPERTIES ('enable.auto.analyze'='true'); // 打开自动收集
ALTER CATALOG external_catalog SET PROPERTIES ('enable.auto.analyze'='false'); // 关闭自动收集
```

## 执行引擎

### pipeline 执行引擎

替换当前 Doris 的火山模型的执行引擎，充分释放多核 CPU 的计算能力，并对 Doris 的查询线程的数目进行限制，解决 Doris 的执行线程膨胀的问题。

```sql
set enable_pipeline_engine = true;
set parallel_pipeline_task_num = 0;
```

### pipelineX执行引擎

PipelineX 执行引擎的目标是为了解决 Doris pipeline 引擎的四大问题：

1.  执行并发上，当前 Doris 执行并发收到两个因素的制约，一个是 fe 设置的参数，另一个是受存储层 bucket 数量的限制，这样的静态并发使得执行引擎无法充分利用机器资源。
2.  执行逻辑上，当前 Doris 有一些固定的额外开销，例如表达式部分各个 instance 彼此独立，而 instance 的初始化参数有很多公共部分，所以需要额外进行很多重复的初始化步骤。
3.  调度逻辑上，当前 pipeline 的调度器会把阻塞 task 全部放入一个阻塞队列中，由一个线程负责轮询并从阻塞队列中取出可执行 task 放入 runnable 队列，所以在有查询执行的过程中，会固定有一个核的资源作为调度的开销。
4.  profile 方面，目前 pipeline 无法为用户提供简单易懂的指标。

```sql
set enable_pipeline_x_engine = true;
set enable_local_shuffle = true;
set ignore_storage_data_distribution = true;
```

## 查询缓存

缓存适用于一次写入多次查询的场景，如t-1生成的报表多方查询，可将频繁查询的结果缓存起来（一次计算多次复用）。但是不适用于实时场景，因为数据更新频繁，缓存也需更新计算反而更无用。

sqlcache：

*set*[*global*] enable\_sql\_cache=true;

第一次查询后，如果满足下面三个条件，查询结果就会被缓存。

1.  (当前时间 - 查询的分区最后更新时间) 大于 fe.conf 中的 cache\_last\_version\_interval\_second。
2.  查询结果行数 小于 fe.conf 中的 cache\_result\_max\_row\_count。
3.  查询结果 bytes 小于 fe.conf 中的 cache\_result\_max\_data\_size。

## 视图与物化视图

### 逻辑视图

逻辑视图即对sql的逻辑封装，把常用固定模式封装为一个视图、把底层表通过视图封装后对上层隐蔽。

逻辑视图不存储数据，只是逻辑的封装，仅为封装底层逻辑而生。

### 物化视图

物化视图是对底层数据的复用+封装，与数仓建模意义相似，物化视图会存储数据。根据数据的刷新时机分为同步物化视图和异步物化视图，同步即数据的导入删除等都会同步更新物化视图，异步即指定策略去不定期或手动刷新视图数据。

**使用场景**

-   分析需求覆盖明细数据查询以及固定维度查询两方面。
-   查询仅涉及表中的很小一部分列或行。
-   查询包含一些耗时处理操作，比如：时间很久的聚合操作等。
-   查询需要匹配不同前缀索引。

**优势特点**

-   对于那些经常重复的使用相同的子查询结果的查询性能大幅提升。
-   Doris 自动维护物化视图的数据，无论是新的导入，还是删除操作都能保证 Base 表和物化视图表的数据一致性，无需任何额外的人工维护成本。
-   查询时，会自动匹配到最优物化视图，并直接从物化视图中读取数据。

**局限性**

1.  如果删除语句的条件列，在物化视图中不存在，则不能进行删除操作。如果一定要删除数据，则需要先将物化视图删除，然后方可删除数据。
2.  单表上过多的物化视图会影响导入的效率：导入数据时，物化视图和 Base 表数据是同步更新的，如果一张表的物化视图表超过 10 张，则有可能导致导入速度很慢。这就像单次导入需要同时导入 10 张表数据是一样的。
3.  物化视图针对 Unique Key 数据模型，只能改变列顺序，不能起到聚合的作用，所以在 Unique Key 模型上不能通过创建物化视图的方式对数据进行粗粒度聚合操作
4.  目前一些优化器对 sql 的改写行为可能会导致物化视图无法被命中，例如 k1+1-1 被改写成 k1，between 被改写成<=和>=，day 被改写成 dayofmonth，遇到这种情况需要手动调整下查询和物化视图的语句。

## join优化

| **Shuffle 方式** | **网络开销** | **物理算子** | **适用场景** |
| --- | --- | --- | --- |
| BroadCast | N * T(R) | Hash Join / Nest Loop Join | 通用，右表广播到左表的所有扫描节点 |
| Shuffle | T(S) + T(R) | Hash Join | 通用，左右表根据join键hash后拉取到计算节点 |
| Bucket Shuffle | T(R) | Hash Join | 左表的分桶键用于关联，将右表数据按桶键分发到左表数据的存储节点 |
| Colocate | 0 | Hash Join | Join 条件中存在左表的分布式列，且左右表同属于一个 Colocate Group，即本地join |

优化方向：

谓词下推、提前裁剪：如列裁剪、分区裁剪、条件过滤等。

join顺序：小表严格放右表（broadcast 、runtime filter）

join方式手动选择：broadcast shuffle的指定

## 高效去重

### bitmap：精确去重

Bitmap是一个位数组，每一位（bit）表示一个数据是否出现过。

在Doris中，Bitmap通常用于表示一个数据集合中的唯一元素。使用一位（bit）表示一个数据是否出现过，因此能够节省大量的存储空间。通过将数据按照范围进行分桶，并将不同范围的Bitmap值存储在不同的分桶中，可以进一步降低单个Bitmap的大小和IO传输的开销。这有助于减少存储成本和提高查询性能。

```sql
--建表时字段类型如下定义为bitmap、bitmap_union为聚合类型，因此只能使用聚合模型。
--分桶间的数据是正交的，可优化老版本大数据量的bitmap全在一个be节点计算的压力。
--有了分桶，相当于提前桶内预聚合
CREATE TABLE `user_tag_bitmap` (
  `tag` bigint(20) NULL COMMENT "用户标签",
  `hid` smallint(6) NULL COMMENT "分桶id",
  `user_id` bitmap BITMAP_UNION NULL COMMENT ""
) ENGINE=OLAP
AGGREGATE KEY(`tag`, `hid`)
COMMENT "OLAP"
DISTRIBUTED BY HASH(`hid`) BUCKETS 3;

select BITMAP_COUNT(orthogonal_bitmap_intersect(user_id, tag, 13080800, 11110200)) 
from user_tag_bitmap  
where tag in (13080800, 11110200);

-- 人群圈选：
 select orthogonal_bitmap_intersect_count(user_id, tag, 13080800, 11110200) 
 from user_tag_bitmap where tag in (13080800, 11110200);
 -- 注：13080800、11110200代表用户标签

-- 计算 user_id 的去重值：
select orthogonal_bitmap_union_count(user_id) 
from user_tag_bitmap where tag in (13080800, 11110200);

-- bitmap 交并差集合混合计算：
select orthogonal_bitmap_expr_calculate_count(user_id, tag, '(833736|999777)&(1308083|231207)&(1000|20000-30000)') 
from user_tag_bitmap where tag in (833736,999777,130808,231207,1000,20000,30000);
-- 注：1000、20000、30000等整形tag，代表用户不同标签

select orthogonal_bitmap_expr_calculate_count(user_id, tag, '(A:a/b|B:2\\-4)&(C:1-D:12)&E:23') 
from user_str_tag_bitmap where tag in ('A:a/b', 'B:2-4', 'C:1', 'D:12', 'E:23');
 -- 注：'A:a/b', 'B:2-4'等是字符串类型tag，代表用户不同标签, 其中'B:2-4'需要转义成'B:2\\-4'

```

### HyperLogLog（HLL）：近似去重

HLL（HyperLogLog）算法是一种用于估算数据集基数的概率算法。它通过计算数据集中不同元素的哈希值的最高有效位（MSB）来估算基数，而不是直接存储数据本身。

相比传统的 COUNT(DISTINCT) 操作，HLL 算法能够使用较少的内存空间来估算基数，并且随着数据量的增长，其内存使用增长缓慢。

由于 HLL 算法是基于概率的估算，因此其结果会有一定的误差。通常，HLL 的估算误差在 1% 左右。

```sql
create table test_hll(
    dt date,
    id int,
    name char(10),
    province char(10),
    os char(10),
    pv hll hll_union
)
Aggregate KEY (dt,id,name,province,os)
distributed by hash(id) buckets 10
PROPERTIES(
    "replication_num" = "1",
    "in_memory"="false"
);
--等同于distinct
select HLL_UNION_AGG(pv) from test_hll;

select HLL_UNION_AGG(pv) from test_hll group by dt;
```

## 高并发点查

Doris 基于列存格式引擎构建，不适合点查场景， Doris 中引入了行存、短查询路径、PreparedStatement 来解决这种不适。

只支持单表 key 列等值查询不支持 join、嵌套子查询， where 条件里需要有且仅有 key 列的等值，可以认为是一种 key value 查询

### 行存

Olap 表中可开启行存模式，只能在建表时开启，且需要额外的空间来存储行存。

"store\_row\_column" = "true"

unique模型应当开启以下三个参数来优化

"enable\_unique\_key\_merge\_on\_write"="true",  
"light\_schema\_change"="true",  
"store\_row\_column"="true"

### 使用 PreparedStatement

设置 JDBC url 并在 Server 端开启 prepared statement

```plain
url = jdbc:mysql://127.0.0.1:9030/ycsb?useServerPrepStmts=true
```

使用 PreparedStatement

```java
// use `?` for placement holders, readStatement should be reused
PreparedStatement readStatement = conn.prepareStatement("select * from tbl_point_query where key = ?");
...
readStatement.setInt(1,1234);
ResultSet resultSet = readStatement.executeQuery();
...
readStatement.setInt(1,1235);
resultSet = readStatement.executeQuery();
...
```

### 开启行缓存

doris的缓存是针对列式存储Page 级别的 Cache，行缓存是单独引入的，需开启：

-   disable\_storage\_row\_cache是否开启行缓存，默认不开启
-   row\_cache\_mem\_limit指定 Row cache 占用内存的百分比，默认 20% 内存

## 查询分析

### 查看profile

#### 正常查询的profile

**set enable\_profile=true; -- 可全局设置，但是不建议，SQL需调优时开启辅助查看详细信息。**

**开启后可 show query profile "/c257c52f93e149ee-ace8ac14e8c9fef9"**

**开启后可在8030端口的web界面查看对应sql的执行情况**

#### **导入任务的profile**

**SET is\_report\_success=true;**

**show load profile "/980014623046410a-af5d36f23381017f";**

### 查看plan-常用

**explain graph select xxxxx -- 以图的形式展示执行计划**

**explain select xxxxxx -- 比前者更详细**

**explain verbose select xxxx -- 比前两个都详细**

## 自定义函数

支持JAVA自定义udf、udaf、udtf，和hive的类似。hive的udf函数可直接注册用于doris，udaf、udtf不支持。函数可能性能不如在hive中性能（生产迁移过hive的加密函数，执行效率很差，应该是JAVA和c++不同语言的兼容性）

也支持远程函数；

  

# 湖仓一体

## 概念理解与区分

### 数据库 (Database)

数据库是计算机系统中用于存储和管理数据的一种软件系统。它可以是关系型数据库（如MySQL、Oracle、Microsoft SQL Server），也可以是非关系型数据库（如MongoDB、Cassandra）。数据库设计有特定的模式，以确保数据的准确性和一致性。其主要功能包括：

-   **数据存储**：存储结构化数据。
-   **数据操作**：提供SQL（结构化查询语言）或其他接口进行数据的插入、更新、删除和查询。
-   **事务处理**：保证数据操作的原子性、一致性、隔离性和持久性（ACID属性）。
-   **数据安全**：提供访问控制和权限管理。
-   **并发控制**：管理多用户同时访问数据时的冲突。

### 数据仓库 (Data Warehouse)

数据仓库是一种特殊类型的数据库，设计用于数据分析和报告。它通常包含来自不同源系统的集成数据，这些数据经过清洗、转换和汇总。数据仓库的主要特征包括：

-   **数据整合**：从多个源系统抽取数据，进行ETL（抽取、转换、加载）过程。
-   **历史数据存储**：保留长期的历史数据，用于趋势分析。
-   **优化查询**：数据结构和索引优化，以支持复杂的分析查询。
-   **维度建模**：常用星型或雪花模型来组织数据，便于分析。

### 数据湖 (Data Lake)

数据湖是一种存储大量原始数据的环境，数据以自然形式存储，无需预定义的结构。它通常使用低成本的分布式文件系统（如Hadoop的HDFS或云存储如AWS S3）。数据湖的关键特性有：

-   **原始数据存储**：存储结构化、半结构化和非结构化数据，无需预定义模式。
-   **灵活性**：数据可以在需要时进行解析和转换。
-   **大数据分析**：支持MapReduce、Spark等框架进行大数据处理和分析。
-   **机器学习和AI**：为机器学习和人工智能应用提供原始数据集。

### 湖仓一体 (Lakehouse)

湖仓一体架构是近年来出现的一个概念，它结合了数据湖的灵活性和数据仓库的结构化特性。湖仓一体使用数据湖作为基础存储，但在其上增加了一层数据治理和优化的查询能力，以实现高性能的分析。湖仓一体的关键点包括：

-   **统一存储**：所有数据（原始和结构化）存储在同一位置。
-   **数据治理**：提供元数据管理、数据质量检查、安全性和审计功能。
-   **ACID事务**：支持ACID事务，确保数据一致性。
-   **优化查询**：利用现代数据处理框架（如Apache Spark、Delta Lake）提供高性能查询。

  

**总结来说，数据库是日常操作数据的存储和管理，数据仓库侧重于分析和报告，数据湖强调原始数据的灵活性和大规模处理，而湖仓一体则是尝试融合这些优点，提供一个既能存储和处理大规模原始数据，又能支持结构化数据的高性能查询和分析的综合平台。**

## 数据库分析能力

通过创建catalog来拓展doris的联邦查询能力，提升数据分析能力。

支持hive catalog的读写；hudi、iceberg、paimon、阿里云DLF、maxcompute、jdbc（支持 MySQL、PostgreSQL、Oracle、SQLServer、Clickhouse、Doris、SAP HANA、Trino/Presto、OceanBase）、elasticsearch 的读取。

生产集成过程中的难点：权限的处理、如kerberos认证等。

## 文件分析能力

### Table Value Function 功能（读取文件）

将hdfs文件、s3对象存储上的文件解析为一个‘表’，按照使用表的习惯来管理和查询，可将查询结果插入doris表。

如读取s3上的一个文件：

```sql
SELECT * FROM s3 (
  "URI"="http://127.0.0.1:9312/test2/test.snappy.parquet",
  "s3.access_key"="ak",
  "s3.secret_key"="sk",
  "format"="parquet",
  "use_path_style"="true"
)
LIMIT 5;
```

### 文件缓存

可设置开启文件缓存，将常用热点远程文件数据缓存到本地be节点，减少网络开销。

SET [gloable] enable\_file\_cache = true;

## 外表统计信息

### 统计信息

统计表中列的min、max、avg、count等信息，帮助查询时了解数据的分布情况，生成更优查询计划。

### 注意

1.  目前 (2.0.3) 只有 Hive 外表支持自动和采样收集。HMS 类型的 Iceberg 和 Hudi 外表，以及 JDBC 外表只支持手动全量收集。其他类型的外表暂不支持统计信息收集。
2.  外表默认关闭自动统计信息收集功能，需要在创建 Catalog 的时候添加属性来打开，或者通过设置 Catalog 属性来开启或关闭。

### 创建 Catalog 时打开自动收集的属性 (默认是 false）：

```plain
'enable.auto.analyze' = 'true'
```

### 通过修改 Catalog 属性控制是否开启自动收集：

```sql
ALTER CATALOG external_catalog SET PROPERTIES ('enable.auto.analyze'='true'); // 打开自动收集
ALTER CATALOG external_catalog SET PROPERTIES ('enable.auto.analyze'='false'); // 关闭自动收集
```

## 云服务认证+sql方言

### 云服务认证

可在catalog中根据endpoint、ak、sk等信息来认证云上服务，也可通过系统属性认证。

### sql方言

可安装sql方言工具

从 2.1 版本开始，Doris 可以支持多种 SQL 方言，如 Presto、Trino、Hive、PostgreSQL、Spark、Clickhouse 等等。通过这个功能，用户可以直接使用对应的 SQL 方言查询 Doris 中的数据，方便用户将原先的业务平滑的迁移到 Doris 中。即能兼容对应的sql方言的数据类型、函数。

# 管理指南

## 集群管理

### 集群升级

**升级思想：**

1.  元数据备份
2.  关闭集群副本修复和均衡功能
3.  兼容性测试
4.  升级 BE
5.  升级 FE
6.  打开集群副本修复和均衡功能

**操作步骤：**

[https://www.yuque.com/g/yuncengshangdelantian/ghbp0u/pkd0wqeeozbvw67p/collaborator/join?token=hn60SdTEGB4AmM8W&source=doc\_collaborator#](https://www.yuque.com/g/yuncengshangdelantian/ghbp0u/pkd0wqeeozbvw67p/collaborator/join?token=hn60SdTEGB4AmM8W&source=doc_collaborator#) 《Doris升级操作(3fe+12be)》

### 集群扩缩容

**fe扩缩容：**

./bin/start\_fe.sh --helper leader\_fe\_host:edit\_log\_port --daemon

ALTER SYSTEM ADD FOLLOWER "follower\_host:edit\_log\_port";

ALTER SYSTEM DROP FOLLOWER[OBSERVER] "fe\_host:edit\_log\_port";

**be的扩缩容：**

ALTER SYSTEM ADD BACKEND "be\_host:be\_heartbeat\_service\_port";

ALTER SYSTEM DECOMMISSION BACKEND "be\_host:be\_heartbeat\_service\_port";

ALTER SYSTEM DROP BACKEND "be\_host:be\_heartbeat\_service\_port";

### 负载均衡

**jdbc：**

jdbc:mysql:loadbalance://[host:port],[host:port].../[database][?propertyName1][=propertyValue1][&propertyName2]\[=propertyValue

**proxy sql：**

**​**  

**NGINX tcp 反向代理：**

**​**  

**haproxy：**

### FQND

FQDN（Fully Qualified Domain Name，完全限定域名）

## 数据管理

### 数据备份

备份操作是将指定表或分区的数据，直接以 Doris 存储的文件的形式，通过broker上传到远端仓库中进行存储（hdfs、s3）。当用户提交 Backup 请求后，系统内部会做如下操作：

1.  快照及快照上传

快照阶段会对指定的表或分区数据文件进行快照。之后，备份都是对快照进行操作。在快照之后，对表进行的更改、导入等操作都不再影响备份的结果。快照只是对当前数据文件产生一个硬链，耗时很少。快照完成后，会开始对这些快照文件进行逐一上传。快照上传由各个 Backend 并发完成。

2.  元数据准备及上传

数据文件快照上传完成后，Frontend 会首先将对应元数据写成本地文件，然后通过 broker 将本地元数据文件上传到远端仓库。完成最终备份作业

3.  动态分区表说明

如果该表是动态分区表，备份之后会自动禁用动态分区属性，在做恢复的时候需要手动将该表的动态分区属性启用，命令如下：

```sql
ALTER TABLE tbl1 SET ("dynamic_partition.enable"="true")
```

4.  备份和恢复操作都不会保留表的 colocate\_with 属性。

```plain
CREATE REPOSITORY `example_repo`
WITH HDFS
ON LOCATION "hdfs://hadoop-name-node:54310/path/to/repo/"
PROPERTIES
(
"fs.defaultFS"="hdfs://hdfs_host:port",
"hadoop.username" = "hadoop"
);

-- 全量备份
BACKUP SNAPSHOT example_db.snapshot_label1
TO example_repo
ON (example_tbl)
PROPERTIES ("type" = "full");

-- 按分区备份
BACKUP SNAPSHOT example_db.snapshot_label2
TO example_repo
ON
(
   example_tbl PARTITION (p1,p2),
   example_tbl2
);

-- 查看备份情况
show BACKUP\G;

-- 查看远端备份情况
SHOW SNAPSHOT ON example_repo WHERE SNAPSHOT = "snapshot_label1";

-- 恢复版本1数据
RESTORE SNAPSHOT example_db1.`snapshot_1`
FROM `example_repo`
ON ( `backup_tbl` )
PROPERTIES
(
    "backup_timestamp"="2022-04-08-15-52-29",
    "replication_num" = "1"
);
-- 查看备份恢复情况
SHOW RESTORE\G;

```

### 主键表数据修复

unique 模型可能存在主键重复的bug，可执行full compaction来合并数据

```plain
curl -X POST "http://127.0.0.1:8040/api/compaction/run?tablet_id=10015&compact_type=full"
curl -X POST "http://127.0.0.1:8040/api/compaction/run?table_id=10104&compact_type=full"
```

### 数据删除恢复

**drop操作恢复：**默认是删除一天内的数据，fe还会保留元数据，故可恢复

```plain
-- 查看可修复数据
SHOW CATALOG RECYCLE BIN [ WHERE NAME [ = "name" | LIKE "name_matcher"] ]
RECOVER DATABASE example_db;
RECOVER TABLE example_db.example_tbl;
RECOVER PARTITION p1 FROM example_tbl;
```

**BE tablet数据恢复：**数据、元数据被删除后会保留在回收站3天

数据存放路径：/root\_path/trash/time\_label/tablet\_id/schema\_hash/

```plain
-- 恢复单个tablet：
curl -X POST "http://be_host:be_webserver_port/api/restore_tablet?tablet_id=11111\&schema_hash=12345"
-- 批量恢复：需将tabletId放入一个文件中，且借助restore_tablet_tool.sh
sh tools/restore_tablet_tool.sh -b "http://127.0.0.1:8040" -t 12345 -s 11111
sh tools/restore_tablet_tool.sh --backend "http://127.0.0.1:8040" --tablet_id 12345 --schema_hash 11111

```

**数据无法恢复时：**

可重新导数/算数（重要）

可将副本置空（不重要）

```plain
-- 数据无法恢复
backend [10001] invalid situation. tablet[20000] has few replica[1], replica num setting is [3]
-- 开启空副本填充
ADMIN SET FRONTEND CONFIG ("recover_with_empty_tablet" = "true");
--填充成功
tablet 20000 has only one replica 20001 on backend 10001 and it is lost. create an empty replica to recover it.
-- 关闭空副本填充功能
ADMIN SET FRONTEND CONFIG ("recover_with_empty_tablet" = "false");
```

### 数据跨集群同步

首先源集群和目标集群都需要打开 binlog，在源集群和目标集群的 fe.conf 和 be.conf 中配置如下信息：

```sql
enable_feature_binlog=true
```

部署 syncers并启动：

打开源集群的binlog

```plain
-- 如果是整库同步，可以执行如下脚本，使得该库下面所有的表都要打开 binlog.enable
vim shell/enable_db_binlog.sh
修改源集群的 host、port、user、password、db
或者 ./enable_db_binlog.sh --host $host --port $port --user $user --password $password --db $db

-- 如果是单表同步，则只需要打开 table 的 binlog.enable，在源集群上执行：
ALTER TABLE enable_binlog SET ("binlog.enable" = "true");
```

发起同步：

```plain
curl -X POST -H "Content-Type: application/json" -d '{
    "name": "ccr_test",
    "src": {
      "host": "localhost",
      "port": "9030",
      "thrift_port": "9020",
      "user": "root",
      "password": "",
      "database": "your_db_name",
      "table": "your_table_name"
    },
    "dest": {
      "host": "localhost",
      "port": "9030",
      "thrift_port": "9020",
      "user": "root",
      "password": "",
      "database": "your_db_name",
      "table": "your_table_name"
    }
}' http://127.0.0.1:9190/create_ccr

-- 参数说明
name: CCR同步任务的名称，唯一即可
host、port：对应集群 Master FE的host和mysql(jdbc) 的端口
user、password：syncer以何种身份去开启事务、拉取数据等
database、table：
如果是db级别的同步，则填入your_db_name，your_table_name为空
如果是表级别同步，则需要填入your_db_name，your_table_name
向syncer发起同步任务中的name只能使用一次
```

## 资源管理

### workload group

可限制组内任务在单个 be 节点上的计算资源和内存资源的使用。当前支持 query 绑定到 workload group。

cpu\_share

memory\_limit

enable\_memory\_overcommit

cpu\_hard\_limit

max\_concurrency

max\_queue\_size

queue\_timeout

scan\_thread\_num

使用：

```plain
-- 创建组
create workload group if not exists g1
properties (
    "cpu_share"="1024",
    "memory_limit"="30%",
    "enable_memory_overcommit"="true"
);
-- 将用户与资源组绑定
set property 'default_workload_group' = 'g1';
-- 会话级资源组配置
set workload_group = 'g1';
```

### Workload Policy

workload group解决了资源隔离的问题，但是同组内仍无法解决大查询熔断问题。workload policy 支持查询负载管理的自动化，比如实现自动取消运行时间超过5s的查询这样的功能。

```sql
create workload policy test_cancel_policy
conditions(query_time > 1000)
actions(cancel_query) 
properties('enabled'='true'); 

-- 查看已经创建的，要修改需要重建
select * from workload_policy;
drop workload policy test_cancel_big_query;
```

policy有适用于fe的，也有适用be的，一个policy的conditions和actions要么都是fe的，要么都是be的，可仅作用于一个workload group

### Workload系统表

Workload系统表作用：

1.  查看集群中Workload Group的资源用量，包括CPU和内存。
2.  查看目前集群中目前资源用量最大的N个sql。
3.  查看集群中Workload Group的排队情况

可通过查询information\_schema库里active\_queries和backend\_active\_tasks找出目前系统中资源占用比较高的Workload Group或者sql，并进行相应的处理。

### Resource Group

将be节点打上tag，通过tag与用户以及副本绑定，控制数据存储到不同的be组，控制不同的用户查询不同副本数据，从而达到资源隔离、互不干扰。

### 弹性计算节点

doris支持将be设置为存储一体的节点，也可把be设置为只负责计算的节点。另fe也可配置observe节点来拓展集群的查询能力（备份元数据、同时提供查询元数据的能力）

## 查询管理

### 高危 SQL 限制

该功能用于限制执行 sql 语句（DDL / DML 都可限制）。 支持按用户配置 SQL 黑名单：

1.  通过正则匹配的方式拒绝指定 SQL
2.  通过设置 partition\_num, tablet\_num, cardinality, 检查一个查询是否达到其中一个限制

-   partition\_num, tablet\_num, cardinality 可以一起设置，一旦一个查询达到其中一个限制，查询将会被拦截

### 非法查询kill

```sql
-- 查询当前运行线程
SHOW PROCESSLIST;
-- 查询当前链接
select connection_id();
-- kill
KILL [CONNECTION] processlist_id
KILL QUERY processlist_id | query_id
```

## 安全管理

Doris 支持内置认证方案和以及 LDAP 的认证方案。支持通过 [Apache Ranger](https://doris.apache.org/zh-CN/docs/admin-manual/auth/ranger) 来设置脱敏策略。

LDAP

RANGER

## 内存管理

## 运维监控

## 配置管理

## 审计日志

## open ai

## 文件管理器

## compaction调整

## 系统表

# SQL手册

  

# 性能测试

# 常见问题