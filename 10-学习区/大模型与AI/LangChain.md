---
tags: [大模型与AI, 概念]
created: 2026-05-16
domain: 大模型与AI
source: 个人总结
---


LangChain(核心作用是什么)
模型包装器,数据增强,记忆,Agent,链,回调处理器
LangGraph


统一Agent创建接口
中间件系统 起 拦截,修改,增强请求(监视,调整,控制) 的作用  

标准化输出
统一各家模型的返回结果

链
自动实现 prompt,LLM,outparser 串行


结构化输出 解析控制

中间件系统
常见的有: 总结摘要的中间件,自动汇总对话历史记录
人机交互中间件, 对于具体的操作实现人工审核的功能


LangChain实现RAG


md格式的文档,天然适合上下文和切割


向量数据库,实际存储的时候 按照集合来, 类似于数据库的库名
 存储的时候,可以同步增加上元数据


LangGraph
多智能体协作
构建智能体, 接入mcp服务, Graph流程结构, 多轮交互,可溯回源

Graph进一步简化了chain的实现链
实行复杂工作流
State(共享数据结构),Node(处理问题的节点),Edge(Node的依赖关系)
条件Edge,EntryPoint



中间状态输出
方便了对于工具的调用流程的开发
可以声明tools返回的结果,是否要大模型修饰

多轮对话的历史记录保存
短期记忆, 长期记忆
对历史消息的删除策略


hunman-in-loop
人类监督, 增加了中断任务的能力
具体实现的时候, 需要指定checkpoint短期记忆, 需要指定带有thread_id的配置项,需要通过interrupt方法中断任务,需要提交command任务,恢复任务

Time Travel时间回溯
其实就是指定某个node重演



MCP工作机制
SSE, 基于http实现的长连接协议
STDIO 在客户端执行本地的应用程序
接入mcp服务, 目前只要接入一个配置文件


