---
tags: [Java与大数据, MOC]
created: 2026-09-06
updated: 2026-09-06
status: 成熟
domain: Java与大数据
source: 个人总结
---

# Flink优化

> [!note] 拆分说明
> 原笔记《Flink优化》共 **50486 字节 / 1299 行**,于 **2026-09-06** 按一级标题主题拆分为以下 5 篇子笔记。拆分内容**逐字搬运、未改写、未增删正文**(仅将行首语雀导出遗留的转义列表符 `\*` 还原为 Markdown 列表,共处理 0 处);正文遗留疑问已登记至开放问题清单。

## 子笔记索引

- [[Flink优化-资源配置优化]] — 任务提交脚本(Generic CLI)与参数、TaskManager 内存模型与生产资源配置示例、Yarn CPU 调度策略(Default/DominantResourceCalculator)、Source/Transform/Sink 并行度设置(原第 7~307 行)
- [[Flink优化-大状态及CheckPoint调优]] — RocksDB 原理与大状态调优(State 访问性能监控、增量 Checkpoint 与本地恢复、预定义选项、block cache/write buffer/后台线程/分区索引参数及提交案例)、Checkpoint 间隔与 EXACTLY_ONCE 调优(原第 308~561 行)
- [[Flink优化-反压机制]] — 反压概述与危害、定位反压节点(Web UI、瓶颈算子分析、Metrics 指标)、反压原因及处理(数据倾斜、外部组件交互、火焰图分析、GC 分析)(原第 562~825 行)
- [[Flink优化-数据倾斜与Job优化]] — 数据倾斜的判断与解决(keyBy 前 shuffle、keyBy 后聚合 LocalKeyBy 思想、窗口两阶段聚合);Job 优化:DataGen 造数据、算子指定 UUID、链路延迟测量、对象重用、细粒度滑动窗口优化(原第 826~1009 行)
- [[Flink优化-FlinkSQL优化与常见故障排除]] — FlinkSQL 优化:空闲状态保留时间、MiniBatch、LocalGlobal、Split Distinct、多维 DISTINCT 使用 FILTER、调优参数总结;常见故障排除(原笔记仅存标题骨架)(原第 1010~1299 行)
