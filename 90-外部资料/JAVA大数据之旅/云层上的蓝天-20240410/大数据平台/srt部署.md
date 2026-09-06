## 安装jdk1.8、maven、nvm

jdk1.8、maven：略

[nvm安装详细教程（卸载旧的nodejs，安装nvm、node、npm、cnpm、yarn及环境变量配置）-CSDN博客](https://blog.csdn.net/sjp991012/article/details/134426007)

## 安装版本号为 16.15.0 的 nodejs

```plain
 nvm install 16.15.0  
 nvm list  
 nvm use 16.15.0  
 nvm uninstall 16.15.0  
```

## MySQL8

MySQL8：略

​  

## 大数据相关组件安装

hadoop

hive

海豚调度

flink

kafka

Doris

Redis

tidb

neo4j

## 安装nacos2.1.1

解压、修改conf、mysql创建库初始化

需要在【conf/application.properties】文件末尾，新增如下配置：

> \# 填自己的ip地址，本地填127.0.0.1就行 nacos.inetutils.ip-address=127.0.0.1 spring.datasource.platform=mysql db.num=1 #填自己的数据库连接和密码 db.url.0=jdbc:mysql://127.0.0.1:3306/nacos\_config? characterEncoding=utf8&connectTimeout=1000&socketTimeout=3000&autoReconnect=true &useUnicode=true&useSSL=false&serverTimezone=UTC
> 
> db.user.0=root
> 
> db.password.0=root

mysql建库nacos\_config,执行nacos目录下./conf/nacos-mysql.sql

```plain
 Windows： startup.cmd -m standalone 
Linux: sh startup.sh -m standalone  
```

启动Nacos 访问Nacos管理界面(http://localhost:8848/nacos) ，初始用户名nacos，密码nacos

​  

创建 srt\_cloud 数据库，数据库编码为 utf8mb4 执行 db/srt\_cloud.sql 文件，初始化数据库脚本

create database srt\_cloud CHARACTER SET utf8mb4；

执行 srt\_cloud.sql脚本

​  

web界面导入nacos配置文件 nacos\_config.zip ，配置中修改相关的链接信息