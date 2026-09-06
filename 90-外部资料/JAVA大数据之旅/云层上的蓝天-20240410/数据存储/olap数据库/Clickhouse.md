# 概念

### 概念

**列存与行存：**行存是将数据以一整行存储到一起；列存是将同一列的数据存一起。因此行存方便查询一条记录的所有信息，列式存储则对不同维度的聚合计算（数据分析）时优势较大（可高达百倍）；列存因为相同数据往往会存到一起，比如一个字段的所有值很可能存储到一个页，此时压缩同一类型的数据压缩效率就会很高，同时读写io较低。

**向量化执行引擎：**简单理解即向量化可利用cpu的并行能力，将sql拆分为多步并行，因此提高查询效率。非向量化引擎大多是串行执行。

### 特点

列存、向量化执行引擎、sql语言容易上手、单表查询性能强劲、多表关联能力较差，分片可横向扩展集群、多副本数据高可用、多种表引擎适配不同场景使用、字段级与列级ttl、性能好是因为由底向上优化，更贴近硬件。

# 安装

略

# 数据类型

略

# 表引擎

**TinyLog：**以列文件的形式保存在磁盘上，不支持索引，没有并发控制。一般保存少量数据的小表。

**Memory：**内存引擎，数据以未压缩的原始形式直接保存在内存当中，服务器重启数据就会消失。读写操作不会相互阻塞，不支持索引。简单查询下有非常非常高的性能表现（超过10G/s）

**MergeTree：**

支持索引和分区、支持字段级与列级ttl设置；数据写入时先写入临时分区，之后后台写入到指定分区。

```sql
create table t_order_mt(
id UInt32,
sku_id String,
total_amount Decimal(16,2) TTL create_time+interval 10 SECOND, -- 列级ttl配置
create_time Datetime,
INDEX a total_amount TYPE minmax GRANULARITY 5		-- 二级索引，在一级索引上建立的二级索引
) engine =MergeTree												-- 指定引擎：此时为明细模型
  partition by toYYYYMMDD(create_time)		-- 按天分区
primary key (id)													-- 主键，并不唯一，用于排序二分查找，一级索引
order by (id,sku_id);											-- 排序列，pk需前置

-- 表级ttl，最好使用分区字段来控制ttl
alter table t_order_mt3 MODIFY TTL create_time + INTERVAL 10 SECOND; 
```

**ReplacingMergeTree：**

增加去重功能：数据的去重只会在合并的过程中出现；如果表经过了分区，去重只会在分区内部进行去重，不能执行跨分区的去重。因此并非完全去重，依然可能数据重复。

```sql
create table t_order_rmt(
id UInt32,
sku_id String,
total_amount Decimal(16,2) ,
create_time  Datetime 
) engine =ReplacingMergeTree(create_time)		-- 可指定去重逻辑，此处按create_time比大小，不加按先来后到处理重复
  partition by toYYYYMMDD(create_time)
primary key (id)
order by (id, sku_id);

-- 手动合并表
OPTIMIZE TABLE t_order_rmt FINAL;   
```

​  

**SummingMergeTree：**

聚合模型，按维度聚合：依然存在没法及时合并所有数据的问题，查询时最好加上sum（汇总列）

```sql
create table t_order_smt(
id UInt32,
sku_id String,
total_amount Decimal(16,2) ,
create_time Datetime 
) engine =SummingMergeTree(total_amount)		-- 聚合的字段，没指定的都是维度字段。
  partition by toYYYYMMDD(create_time)
primary key (id)
order by (id,sku_id );

-- 可手动触发聚合
OPTIMIZE TABLE t_order_smt FINAL;
```

​  

# sql操作

略

# 副本和分片

副本：为了数据高可用，可将同一份数据存于不同节点

```sql
create table t_order_rep2 (
id UInt32,
sku_id String,
total_amount Decimal(16,2),
create_time  Datetime
) engine =ReplicatedMergeTree('/clickhouse/table/01/t_order_rep','rep_102')
  partition by toYYYYMMDD(create_time)
primary key (id)
order by (id,sku_id);
```

分片：分片是将表数据分散到多个节点，以使用多个节点的资源来查询数据，因此集群资源瓶颈时可增加节点来横向扩展集群能力。

Ø 会自动同步到hadoop103和hadoop104上

Ø 集群名字要和配置文件中的一致

Ø 分片和副本名称从配置文件的宏定义中获取

```sql
create table st_order_mt on cluster gmall_cluster (
id UInt32,
sku_id String,
total_amount Decimal(16,2),
create_time  Datetime
) engine =ReplicatedMergeTree('/clickhouse/tables/{shard}/st_order_mt','{replica}')
  partition by toYYYYMMDD(create_time)
primary key (id)
order by (id,sku_id);
```
```sql
create table st_order_mt_all2 on cluster gmall_cluster
(
id UInt32,
sku_id String,
total_amount Decimal(16,2),
create_time  Datetime
)engine = Distributed(gmall_cluster,default, st_order_mt,hiveHash(sku_id));

参数含义：
	Distributed（集群名称，库名，本地表名，分片键）
分片键必须是整型数字，所以用hiveHash函数转换，也可以rand()
```

没有建立Distributed的表只能查询本身节点拥有的分片数据，反之能查表所有分片数据

  

​