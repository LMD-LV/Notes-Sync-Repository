---
tags: [Java与大数据, MOC]
created: 2026-09-06
updated: 2026-09-06
status: 成熟
domain: Java与大数据
source: 个人总结
---

# Flink

> [!note] 拆分说明
> 原笔记共 61136 字节 / 1454 行，于 2026-09-06 按主题拆分为以下 5 篇子笔记（本文件转为 MOC 索引页）。
> 所有正文内容逐字搬运、未改写、未增删；仅将行首语雀导出遗留的转义列表符 `\*` 还原为 Markdown 列表（共 2 处）。
> 正文遗留疑问已登记至开放问题清单。

- [[Flink-概述与运行架构]] — 2025 补充要点、Flink 概述(流/批与事件驱动)、部署模式(local/standalone/Yarn 三种模式与高可用)、运行架构(JobManager/TaskManager/Slot、并行度、任务链与共享组、执行图四层)及提交流程

- [[Flink-流处理核心API]] — Environment/Source/Transform/sink 核心编程接口、Rich 函数生命周期、重分区算子、执行模式选择(STREAMING/BATCH)与第六章实战注意事项

- [[Flink-窗口与时间语义]] — window 机制(时间/计数窗口、Window Function)、Keyed vs Non-Keyed、时间语义与 WaterMark、侧输出流、ProcessFunction API 与定时器

- [[Flink-状态与容错]] — 状态编程(键控状态/算子状态、Managed State 分类)与状态后端;容错机制(一致性级别、端到端一致性、Checkpoint 原理与 Barrier 对齐/不对齐、Savepoint、Flink+Kafka 端到端严格一次)

- [[Flink-CEP复杂事件处理]] — Flink CEP 复杂事件处理:概念与开发步骤、模式 API(单个/组合模式、条件、贪婪、模式组)与匹配后跳过策略
