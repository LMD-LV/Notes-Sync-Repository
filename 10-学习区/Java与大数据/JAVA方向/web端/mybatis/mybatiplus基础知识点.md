---
tags: [Java与大数据, 概念]
created: 2026-08-02
domain: Java与大数据
source: 个人总结
---

#### 概述

mybatis的增强工具，实现了基本的CRUD，支持lamdba表达式的查询条件，主键生成策略等

  

#### 整合配置文件

当引入了mybatis-plus的依赖的时候，已经间接的引入了 mybatis，spring整合mybatis 的依赖，所以不能再引入后两者

当mapper映射文件在resouce下的路径和 mapper接口的路径一致的时候，applicationContext配置文件中不需要在引入

mapper接口的地址需要在applicaitonContext配置文件中配置，用于创建动态代理，交付ioc管理

类型别名对应的 pojo 也需配置

添加扫描组件的配置，扫描不同层的组件

​  

#### 默认的功能

BaseMapper 范型为要操作的实体类型，包含了各种CRUD方法，可以继承提供了

驼峰转下划线已经被设置为默认配置了

​  

#### 常见注释

@TableName 指定表，当出现了表都有统一的前缀的时候，在GlobalConfig中开启前缀的配置，也可以开启主键的相关配置

@TableId 指定主键，value参数指定列的名称，

@TabldField 支持修改字段的名称

@TableLogic 指定逻辑字段

​  

#### wrapper的使用

Wrapper条件构造器，常见的有 queryWrapper ，UpdateWrapper，LambdaQueryWrapper，LambdaUpdateWrapper

BaseMapper中的多数方法都支持Wrapper类型的形参

​  

​  

#### 常见插件

分页插件，也可以自定义分页插件

通过version和乐观锁插件实现避免并发冲突

支持将某个属性设置为枚举类型，@EnumValue，配置文件中配置 通用枚举

#### 高级功能

通过读取表，快速生成mapper接口，或者反过来

​  

​  

​  

​