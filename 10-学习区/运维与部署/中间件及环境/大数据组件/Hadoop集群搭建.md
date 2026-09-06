---
tags: [运维与部署, 教程]
created: 2026-09-06
status: 整理中
domain: 运维与部署
source: 个人总结
---

# Hadoop 集群搭建

> [!note] 迁移说明
> 2026-09-06 自 [[大数据]] 迁入(概览篇去操作细节),逐字搬运。含 scp/rsync/xsync/SSH 免密/首次格式化注意事项。

**scp（secure copy）安全** **拷贝**定义 scp可以实现服务器与服务器之间的数据拷贝

scp -r $pdir/$fname $user@$host:$pdir/$fname

命令 递归 要拷贝的文件路径/名称 目的地用户@主机:目的地路径/名称

#### rsync远程同步工具

rsync主要用于备份和镜像。具有速度快、避免复制相同内容和支持符号链接的优点。

rsync和scp区别：用rsync做文件的复制要比scp的速度快，rsync只对差异文件做更新。scp是把所有文件都复制过去

（1）基本语法

rsync -a(归档拷贝)v(显示复制过程) $pdir/$fname $user@$host:$pdir/$fname

命令 选项参数 要拷贝的文件路径/名称 目的地用户@主机:目的地路径/名称

#### xsync集群分发脚本

（1）需求：循环复制文件到所有节点的相同目录下

期望脚本在任何路径都能使用（脚本放在声明了全局环境变量的路径）

SSH无密登录配置

![image.png](assets/大数据-3.png)

然后敲（三个回车），就会生成两个文件id_rsa（私钥）、id_rsa.pub（公钥）

  

**ssh** **文件夹下（** **~/.ssh** **）的文件功能解释**

| known_hosts | 记录ssh访问过计算机的公钥（public key） |
| --- | --- |
| id_rsa | 生成的私钥 |
| id_rsa.pub | 生成的公钥 |
| authorized_keys | 存放授权过的无密登录服务器公钥 |

  

  

**如果集群是第一次启动**，需要在hadoop102节点格式化NameNode（注意：格式化NameNode，会产生新的集群id，导致NameNode和DataNode的集群id不一致，集群找不到已往数据。如果集群在运行过程中报错，需要重新格式化NameNode的话，一定要先停止namenode和datanode进程，并且要删除所有机器的data和logs目录，然后再进行格式化。）

  

###
