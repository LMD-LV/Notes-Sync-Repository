# docker搭建大数据集群

  

最近在玩大数据，平时家里的电脑配置比较好（32G+2T固态），可以直接起虚拟机，但是有时候在公司需要搭个临时环境测试，所以就考虑使用docker搭建一个大数据集群。目前先准备搭好`hadoop`。

  

## 1\. 网络规划

  

我们需要确保各个节点之间网络互通，我们使用`192.168.10.0/24`作为子网，`192.168.10.2`作为网关。关于`Docker`的网络设置，可以参考这篇文章[Docker网络](https://www.cnblogs.com/ZhuChangwu/p/13689736.html)

  

```shell
# 大数据子网
docker network create --subnet 192.168.10.0/24 --gateway 192.168.10.2 big-data
```

  

对于不同节点规划如下：

| 节点 | IP | 说明 |
| --- | --- | --- |
| hadoop100 | 192.168.10.100 | 大数据基础镜像 |
| hadoop102 | 192.168.10.102 | 节点1 |
| hadoop103 | 192.168.10.103 | 节点1 |
| hadoop104 | 192.168.10.104 | 节点1 |

  

下面开始构建基础镜像。

  

## 2\. 构建基础镜像

  

使用下面的命令创建基础镜像`hadoop100`：

  

```shell
# 最基础镜像
docker run -itd --name hadoop100 --net big-data --ip 192.168.10.100  --hostname hadoop100 --privileged  centos:centos7.9.2009 /usr/sbin/init

docker exec -it hadoop100 /bin/bash
```

  

**注：**`**--privileged**`**和**`**/usr/sbin/init**`**是必须的，否则会存在容器权限不足的问题！**

  

进入镜像后执行：

  

```shell
# 更新软件源
yum install -y epel-release
yum update -y

# 安装和配置SSH
yum install -y openssh-server
systemctl start sshd
systemctl enable sshd

## 增加配置内容
vi /etc/ssh/sshd_config
UseDNS no
PermitRootLogin yes #允许root登录
PermitEmptyPasswords no #不允许空密码登录
PasswordAuthentication yes # 设置是否使用口令验证

systemctl restart sshd

# 安装SSH客户端
yum -y install openssh-clients

# 安装Vim
yum install -y vim

# 安装网络工具
yum install -y net-tools

# 修改hosts，增加节点内容
vi /etc/hosts
192.168.10.102     hadoop102
192.168.10.103     hadoop103
192.168.10.104     hadoop104
```

  

上述命令执行完毕后，退出容器，执行`docker commit`将容器保存为镜像

  

```shell
docker commit --message "基本镜像：添加ssh、net-tools等工具" hadoop100 geekthomas/hadoop100:v0.1
# 像DockerHub推送镜像（可选）
docker push geekthomas/hadoop100:v0.1
```

  

测试基础镜像：

  

```shell
docker run -itd --name hadoop102 --net big-data --ip 192.168.10.102  --hostname hadoop102 --privileged  geekthomas/hadoop100:v0.1 /usr/sbin/init
docker run -itd --name hadoop103 --net big-data --ip 192.168.10.103  --hostname hadoop103 --privileged  geekthomas/hadoop100:v0.1 /usr/sbin/init
docker run -itd --name hadoop104 --net big-data --ip 192.168.10.104  --hostname hadoop104 --privileged  geekthomas/hadoop100:v0.1 /usr/sbin/init
```

  

这样就使用基础镜像创建了三个大数据容器：

  

-   `hadoop102`

-   `hadoop103`

-   `hadoop104`

  

进入容器1：

  

```shell
docker exec -it hadoop102 /bin/bash
```

  

尝试`ping`其他容器：

  

```shell
[root@hadoop102 /]# ping hadoop103
PING hadoop103 (192.168.10.103) 56(84) bytes of data.
64 bytes from hadoop103.big-data (192.168.10.103): icmp_seq=1 ttl=64 time=3.41 ms
64 bytes from hadoop103.big-data (192.168.10.103): icmp_seq=2 ttl=64 time=0.096 ms
64 bytes from hadoop103.big-data (192.168.10.103): icmp_seq=3 ttl=64 time=0.256 ms
^C
--- hadoop103 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2032ms
rtt min/avg/max/mdev = 0.096/1.254/3.411/1.526 ms
[root@hadoop102 /]# ping hadoop104
PING hadoop104 (192.168.10.104) 56(84) bytes of data.
64 bytes from hadoop104.big-data (192.168.10.104): icmp_seq=1 ttl=64 time=0.572 ms
64 bytes from hadoop104.big-data (192.168.10.104): icmp_seq=2 ttl=64 time=0.068 ms
64 bytes from hadoop104.big-data (192.168.10.104): icmp_seq=3 ttl=64 time=0.076 ms
^C
--- hadoop104 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2058ms
rtt min/avg/max/mdev = 0.068/0.238/0.572/0.236 ms
```

  

可以看到，网络是通的！

  

我们给`root`用户设置密码：三台机器均设置为`123456`

  

```shell
[root@hadoop102 /]# passwd
Changing password for user root.
New password:
BAD PASSWORD: The password is shorter than 8 characters
Retype new password:
passwd: all authentication tokens updated successfully.
```

  

## 3\. 安装和配置软件及脚本

  

### 3.1. 配置SSH

  

在每个容器中执行，生成`SSH Key`：

  

```shell
ssh-keygen -t rsa
```

  

然后将生成的`id_rsa.pub`（公钥）写入到每个容器中，注意也要把自己的写进去

  

```shell
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

  

这里也可以用`ssh-copy-id`快速写入

  

```shell
ssh-copy-id -i ~/.ssh/id_rsa.pub root@hadoop102
```

  

测试`SSH`免密登录

  

```shell
[root@hadoop102 ~]# ssh hadoop102
Last login: Wed Mar 20 15:10:04 2024 from 192.168.10.103
[root@hadoop102 ~]# ssh hadoop103
Last login: Wed Mar 20 15:09:59 2024 from 192.168.10.102
[root@hadoop103 ~]# ssh hadoop103
Last login: Wed Mar 20 15:15:37 2024 from 192.168.10.102
[root@hadoop103 ~]# ssh hadoop104
Last login: Wed Mar 20 15:08:24 2024 from 192.168.10.102
[root@hadoop104 ~]# ssh hadoop104
Last login: Wed Mar 20 15:15:47 2024 from 192.168.10.103
[root@hadoop104 ~]# ssh hadoop102
Last login: Wed Mar 20 15:15:33 2024 from 192.168.10.102
[root@hadoop102 ~]#
```

  

### 3.2. 编写容器集群同步文件脚本xsync

  

首先在三个容器内分别安装`rsync`

  

```shell
yum install -y rsync
```

  

编辑创建`xsync`文件

  

```shell
mkdir ~/bin
cd ~/bin
vim xsync

#!/bin/bash

#1. 判断参数个数
if [ $# -lt 1 ]
then
   echo Not Enough Argument!
   exit;
fi

#2. 遍历所有机器
for host in hadoop102 hadoop103 hadoop104
do
    echo ======================= $host =======================
    #3. 遍历所有目录，挨个发送
    for file in $@
    do
        #4. 判断文件是否存在
        if [ -e $file ]
        then
           #5. 获取父目录
           pdir=$(cd -P $(dirname $file); pwd)

           #6. 获取当前文件名称
           fname=$(basename $file)
           ssh $host "mkdir -p $pdir"
           rsync -av $pdir/$fname $host:$pdir
        else
           echo $file does not exists!
        fi
    done
done
```

  

这里发现一个问题：`centos`下`vim`编辑器乱码

  

![](https://geekthomasabc.oss-cn-beijing.aliyuncs.com/img/image-20240320232336372.png)

  

打开`/etc/vimrc`文件，在文件头上添加以下配置：

  

```shell
set fileencodings=utf-8,gb2312,gbk,gb18030
set termencoding=utf-8
set fileformats=unix
set encoding=prc
```

  

保存设置，重新打开`xsync`文件，中文显示正常

  

![](https://geekthomasabc.oss-cn-beijing.aliyuncs.com/img/image-20240320232713837.png)

  

给`xsync`文件增加可执行权限：

  

```shell
chmod +x xsync
```

  

测试，将`xsync`文件和`/etc/vimrc`文件分发到其他机器

  

```shell
[root@hadoop102 bin]# xsync xsync /etc/vimrc
======================= hadoop102 =======================
sending incremental file list

sent 44 bytes  received 12 bytes  112.00 bytes/sec
total size is 687  speedup is 12.27
sending incremental file list

sent 44 bytes  received 12 bytes  112.00 bytes/sec
total size is 2,086  speedup is 37.25
======================= hadoop103 =======================
sending incremental file list

sent 44 bytes  received 12 bytes  112.00 bytes/sec
total size is 687  speedup is 12.27
sending incremental file list
vimrc

sent 207 bytes  received 53 bytes  520.00 bytes/sec
total size is 2,086  speedup is 8.02
======================= hadoop104 =======================
sending incremental file list
xsync

sent 778 bytes  received 35 bytes  1,626.00 bytes/sec
total size is 687  speedup is 0.85
sending incremental file list
vimrc

sent 207 bytes  received 53 bytes  520.00 bytes/sec
total size is 2,086  speedup is 8.02
```

  

成功执行~

  

### 3.3. 安装jdk

  

因为我这里是在`windows`的`wsl`中安装的`docker`，所以这里需要将下载的`jdk-8u202-linux-x64.tar.gz`从`windows`先拷贝到`wsl`，然后再拷贝到容器

  

```shell
thomas@DESKTOP-BSA5AD6:/opt$ sudo cp /mnt/e/install/jdk-8u202-linux-x64.tar.gz /opt
```

  

再每个容器中都新建以下目录：

  

```shell
mdkir -p /opt/module
mkdir -p /opt/software
```

  

-   压缩包/安装包都放在`/opt/module`

-   软件安装在`/opt/module`

  

将文件从宿主机（也就是`wsl`）拷贝到三个容器内：

  

```shell
thomas@DESKTOP-BSA5AD6:/opt$ docker cp jdk-8u202-linux-x64.tar.gz hadoop102:/opt/software
Successfully copied 194MB to hadoop102:/opt/software
thomas@DESKTOP-BSA5AD6:/opt$ docker cp jdk-8u202-linux-x64.tar.gz hadoop103:/opt/software
Successfully copied 194MB to hadoop103:/opt/software
thomas@DESKTOP-BSA5AD6:/opt$ docker cp jdk-8u202-linux-x64.tar.gz hadoop104:/opt/software
Successfully copied 194MB to hadoop104:/opt/software
```

  

在三个容器内解压压缩包，并设置环境变量

  

```shell
# 解压
cd /opt/software
tar -zxvf jdk-8u202-linux-x64.tar.gz -C /opt/module

# 配置环境变量
vim /etc/profile.d/my_env.sh

export JAVA_HOME=/opt/module/jdk1.8.0_202
export PATH=$PATH:$JAVA_HOME/bin

# 分发文件
xsync /etc/profile.d/my_env.sh

# 使环境变量生效
source /etc/profile.d/my_env.sh

# 验证java是否安装成功
[root@hadoop102 software]# java -version
java version "1.8.0_202"
Java(TM) SE Runtime Environment (build 1.8.0_202-b08)
Java HotSpot(TM) 64-Bit Server VM (build 25.202-b08, mixed mode)
```

  

### 3.5. 安装hadoop

  

与安装`jdk`一样，先从`windows`拷贝到`wsl`

  

```shell
thomas@DESKTOP-BSA5AD6:/opt$ sudo cp /mnt/e/install/hadoop-3.1.3.tar.gz /opt
```

  

然后从`wsl`分别拷贝到三个容器

  

```shell
docker cp /opt/hadoop-3.1.3.tar.gz hadoop102:/opt/software
docker cp /opt/hadoop-3.1.3.tar.gz hadoop103:/opt/software
docker cp /opt/hadoop-3.1.3.tar.gz hadoop104:/opt/software
```

  

解压并配置环境变量

  

```shell
# 解压hadoop
cd /opt/software
tar -zxvf hadoop-3.1.3.tar.gz -C /opt/module/

# 添加HADOOP相关环境变量
vim /etc/profile.d/my_env.sh
# HADOOP_HOME
export HADOOP_HOME=/opt/module/hadoop-3.1.3
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin

export HDFS_NAMENODE_USER="root"
export HDFS_DATANODE_USER="root"
export HDFS_SECONDARYNAMENODE_USER="root"
export YARN_RESOURCEMANAGER_USER="root"
export YARN_NODEMANAGER_USER="root"

# 分发文件
xsync /etc/profile.d/my_env.sh

# 使环境变量生效
source /etc/profile.d/my_env.sh

# 验证环境变量已配置
[root@hadoop102 software]# hadoop version
Hadoop 3.1.3
Source code repository https://gitbox.apache.org/repos/asf/hadoop.git -r ba631c436b806728f8ec2f54ab1e289526c90579
Compiled by ztang on 2019-09-12T02:47Z
Compiled with protoc 2.5.0
From source with checksum ec785077c385118ac91aadde5ec9799
This command was run using /opt/module/hadoop-3.1.3/share/hadoop/common/hadoop-common-3.1.3.jar
```

  

### 3.6. 配置hadoop

  

#### 1\. 集群规划

|  | `hadoop102` | `hadoop103` | `hadoop104` |
| --- | --- | --- | --- |
| `HDFS` | `NameNode、DataNode` | `DataNode` | `SecondaryNameNode、DataNode` |
| `YARN` | `NodeManager` | `ResourceManager、NodeManager` | `NodeManager` |

  

注意：

  

-   `NameNode`和`SecondaryNameNode`不要安装在同一台服务器

-   `ResourceManager`也很消耗内存，不要和`NameNode、SecondaryNameNode`配置在同一台机器上。

  

我们在`hadoop102`上进行配置，之后再将配置分发到其他容器上。

  

进入`hadoop`目录

  

```shell
cd ${HADOOP_HOME}/etc/hadoop
```

  

#### 2\. 修改配置文件

  

修改核心配置文件`core-site.xml`

  

```xml
<configuration>
<!-- 指定NameNode的地址 -->
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://hadoop102:8020</value>
    </property>
    <!-- 指定hadoop数据的存储目录 -->
        <property>
            <name>hadoop.tmp.dir</name>
            <value>/opt/module/hadoop-3.1.3/data</value>
    </property>
    <!-- 配置HDFS网页登录使用的静态用户为root -->
        <property>
            <name>hadoop.http.staticuser.user</name>
            <value>root</value>
    </property>
    <!-- 配置该root(superUser)允许通过代理访问的主机节点 -->
        <property>
            <name>hadoop.proxyuser.root.hosts</name>
            <value>*</value>
    </property>
    <!-- 配置该root(superUser)允许通过代理用户所属组 -->
        <property>
            <name>hadoop.proxyuser.root.groups</name>
            <value>*</value>
    </property>
    <!-- 配置该root(superUser)允许通过代理的用户-->
        <property>
            <name>hadoop.proxyuser.root.users</name>
            <value>*</value>
    </property>
</configuration>
```

  

配置`HDFS`配置文件`hdfs-site.xml`

  

```xml
<configuration>
<!-- nn web端访问地址-->
    <property>
        <name>dfs.namenode.http-address</name>
        <value>hadoop102:9870</value>
    </property>

<!-- 2nn web端访问地址-->
    <property>
        <name>dfs.namenode.secondary.http-address</name>
        <value>hadoop104:9868</value>
    </property>
<!-- 测试环境指定HDFS副本的数量1 -->
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>
```

  

配置`YARN`配置文件`yarn-site.xml`

  

```xml
<configuration>
<!-- 指定MR走shuffle -->
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>

    <!-- 指定ResourceManager的地址-->
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>hadoop103</value>
    </property>

    <!-- 环境变量的继承 -->
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
<value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME</value>
    </property>

    <!-- yarn容器允许分配的最大最小内存 -->
    <property>
        <name>yarn.scheduler.minimum-allocation-mb</name>
        <value>512</value>
    </property>
    <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>4096</value>
    </property>

    <!-- yarn容器允许管理的物理内存大小 -->
    <property>
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>4096</value>
    </property>

    <!-- 关闭yarn对虚拟内存的限制检查 -->
    <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
    </property>
</configuration>
```

  

配置`MapReduce`配置文件`mapred-site.xml`

  

```xml
<configuration>
<!-- 指定MapReduce程序运行在Yarn上 -->
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
</configuration>
```

  

配置`workers`：

  

```shell
vim /opt/module/hadoop-3.1.3/etc/hadoop/workers

hadoop102
hadoop103
hadoop104
```

  

配置历史服务器地址`mapred-site.xml`

  

```xml
<!-- 历史服务器端地址 -->
<property>
    <name>mapreduce.jobhistory.address</name>
    <value>hadoop102:10020</value>
</property>

<!-- 历史服务器web端地址 -->
<property>
    <name>mapreduce.jobhistory.webapp.address</name>
    <value>hadoop102:19888</value>
</property>
```

  

配置日志聚集`yarn-site.xml`

  

```xml
<!-- 开启日志聚集功能 -->
<property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
</property>

<!-- 设置日志聚集服务器地址 -->
<property>  
    <name>yarn.log.server.url</name>  
    <value>http://hadoop102:19888/jobhistory/logs</value>
</property>

<!-- 设置日志保留时间为7天 -->
<property>
    <name>yarn.log-aggregation.retain-seconds</name>
    <value>604800</value>
</property>
```

  

分发`hadoop`配置文件

  

```shell
xsync /opt/module/hadoop-3.1.3/
```

  

### 3.7. 启动集群

  

**如果集群是第一次启动，需要在hadoop102节点格式化NameNode（注意格式化之前，一定要先停止上次启动所有namenode和datanode进程，然后再删除data和log数据）！**

  

#### 1\. 格式化节点

  

```shell
# 在hadoop102上执行
cd $HADOOP_HOME
./bin/hdfs namenode -format
```

  

#### 2\. 启动HDFS

  

```shell
sbin/start-dfs.sh
```

  

#### 3\. 启动YARN

  

在配置了`ResourceManager`的节点（`hadoop103`）启动YARN：

  

```shell
cd $HADOOP_HOME
sbin/start-yarn.sh
```

  

#### 4\. 查看是否启动成功

  

```shell
[root@hadoop103 hadoop-3.1.3]# curl hadoop102:9870
<!--
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="REFRESH" content="0;url=dfshealth.html" />
<title>Hadoop Administration</title>
</head>
</html>
```

  

如果我们需要在外网访问页面，就像我们之前在虚拟机中设置的那样，需要做以下操作：

  

首先在`wsl2`中开启ip转发

  

```shell
iptables -A FORWARD -i eth0 -j ACCEPT
```

  

获取我们`wsl2`的ip

  

```shell
root@DESKTOP-BSA5AD6:/bin# ifconfig eth0

root@DESKTOP-BSA5AD6:/bin# ifconfig eth0
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.28.176.2  netmask 255.255.255.0  broadcast 172.28.176.255
        inet6 fe80::215:5dff:fe0c:a403  prefixlen 64  scopeid 0x20<link>
        ether 00:15:5d:0c:a4:03  txqueuelen 1000  (Ethernet)
        RX packets 162909  bytes 232795487 (232.7 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 39716  bytes 3562627 (3.5 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

  

这里`wsl2`的ip就是`inet`，也就是`172.28.176.2`。

  

然后用管理员权限打开cmd，添加一条路由

  

```plain
route add 192.168.10.0/24 mask 255.255.0.0 172.28.176.2
```

  

这样，我们就可以在`windows`访问我们的`hdfs`页面了（当然我们需要将`hadoop102`加入到`windows`的`hosts`文件中）！

  

![](https://geekthomasabc.oss-cn-beijing.aliyuncs.com/img/bf255a1f55aa65d44432ef176248ae1.png)

  

因为实际上`wsl2`的`ip`是动态`ip`，也就是每次重启之后都会发生变化，我们可以在`wsl2`启动的时候动态获取`ip`，并配置路由

  

```shell
# 开启IP转发
iptables -A FORWARD -i eth0 -j ACCEPT

# 每次WSL重启都获取WSL ip
ip=$(ifconfig eth0 | grep "inet " | awk '{print $2}')
echo "route add 192.168.10.0/24 mask 255.255.0.0 $ip" > /mnt/f/projects/scripts/route.bat
echo "route add 192.168.10.0/24 mask 255.255.0.0 $ip" >> /mnt/f/projects/scripts/route.bat
echo "route add $ip"
```

  

我们只需要在`windows`下使用管理员启动`bat`即可（感谢我的组长！！！！）

  

### 3.8. 编写集群启动和进程监控脚本

  

#### 1\. Hadoop 集群启停脚本

  

包括`hdfs`、`yarn`、`historyserver`。我们再来回顾下关闭和重启的步骤：

  

-   关闭集群模块

-   在`hadoop102`上关闭`historyserver`

-   在`hadoop103`上关闭`yarn`

-   在`hadoop102`上关闭`hdfs`

-   启动集群模块

-   在`hadoop102`上启动`hdfs`

-   在`hadoop103`上启动`yarn`

-   在`hadoop102`上启动`historyserver`

  

根据我们前面的经验，编写出对应的`shell`脚本

  

在`/usr/bin`目录下，新建`hdp.sh`

  

```shell
#!/bin/bash

if [ $# -lt 1 ]
then
   echo "No Args Input..."
   exit;
fi

case $1 in
"start")
    echo "=================== 启动 hadoop集群 ==================="

    echo " --------------- 启动 hdfs ---------------"
    ssh hadoop102 "/opt/module/hadoop-3.1.3/sbin/start-dfs.sh"
    echo " --------------- 启动 yarn ---------------"
    ssh hadoop103 "/opt/module/hadoop-3.1.3/sbin/start-yarn.sh"
    echo " --------------- 启动 historyserver ---------------"
    ssh hadoop102 "/opt/module/hadoop-3.1.3/bin/mapred --daemon start historyserver"
;;
"stop")
    echo "=================== 关闭 hadoop集群 ==================="

    echo " --------------- 关闭 historyserver ---------------"
    ssh hadoop102 "/opt/module/hadoop-3.1.3/bin/mapred --daemon stop historyserver"
    echo " --------------- 关闭 yarn ---------------"
    ssh hadoop103 "/opt/module/hadoop-3.1.3/sbin/stop-yarn.sh"
    echo " --------------- 关闭 hdfs ---------------"
    ssh hadoop102 "/opt/module/hadoop-3.1.3/sbin/stop-dfs.sh"
;;
*)
    echo "Input Args Error..."
;;
esac
```

  

将脚本保存后退出

  

（这里中文显示可能有问题，参考这篇文章https://www.cnblogs.com/fan-gx/p/11137943.html）

  

> 主要就是以下几步：

```shell
yum -y install kde-l10n-Chinese
yum -y reinstall glibc-common 
#基本就能搞定 ，还有修改一下/etc/locale.conf  
LC_ALL="zh_CN.UTF-8" 
source /etc/locale.conf
# 在docker容器中执行
localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
```

  

给`hdp.sh`添加可执行权限

  

```shell
chmod +x hdp.sh
```

  

#### 2\. jps进程查看脚本

  

在`/usr/bin`目录下，新建`xcall.sh`

  

```shell
#! /bin/bash

for host in hadoop102 hadoop103 hadoop104
do
        echo "--------- $host ----------"
        ssh $host "$*"
done
```

  

给`xcall.sh`添加可执行权限

  

```shell
chmod +x xcall.sh
```

  

分发脚本并启动集群，查看`jps`

  

```shell
[root@hadoop102 ~]# xsync /usr/bin/hdp.sh /usr/bin/xcall.sh
[root@hadoop102 ~]# hdp.sh start
=================== 启动 hadoop集群 ===================
 --------------- 启动 hdfs ---------------
Starting namenodes on [hadoop102]
Last login: 四 3月 21 15:21:29 UTC 2024 from 192.168.10.104 on pts/10
Starting datanodes
Last login: 四 3月 21 15:29:41 UTC 2024
Starting secondary namenodes [hadoop104]
Last login: 四 3月 21 15:29:43 UTC 2024
 --------------- 启动 yarn ---------------
Starting resourcemanager
Last login: 四 3月 21 15:20:51 UTC 2024 from 192.168.10.102 on pts/11
Starting nodemanagers
Last login: 四 3月 21 15:29:53 UTC 2024
 --------------- 启动 historyserver ---------------
[root@hadoop102 ~]# xcall.sh jps
--------- hadoop102 ----------
12049 Jps
11895 JobHistoryServer
11431 DataNode
11786 NodeManager
11292 NameNode
--------- hadoop103 ----------
9863 DataNode
10601 Jps
10074 ResourceManager
10220 NodeManager
--------- hadoop104 ----------
9824 Jps
9473 DataNode
9546 SecondaryNameNode
9677 NodeManager
```

  

### 3.9. 集群功能测试

  

-   写入`HDFS`文件

  

```shell
# 创建目录

[root@hadoop102 ~]# hadoop fs -ls /
Found 1 items
drwxrwx---   - root supergroup          0 2024-03-21 14:36 /tmp
```

  

-   上传文件

  

```shell
[root@hadoop102 ~]# cat test.txt
hello hadoop
hello World
Hello Java
Hey man
i am a programmer
测试
[root@hadoop102 ~]# hadoop fs -put test.txt /input
```

  

-   运行`wordcount`

  

```shell
[root@hadoop102 hadoop-3.1.3]# hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.1.3.jar wordcount /input/test.txt /output
```

  

![](https://geekthomasabc.oss-cn-beijing.aliyuncs.com/img/image-20240408181244056.png)

  

## 4\. 创建Big-Data镜像

  

经过上面的安装和配置，我们已经创建了一个三节点的Hadoop集群；

  

接下来我们将这几个容器提交为镜像：

  

```shell
root@DESKTOP-BSA5AD6:/usr/bin# docker commit --message "大数据集群基本镜像：完成Hadoop和Yarn 部分" hadoop102 geekthomas/hadoop102:v1.0
sha256:afeac5ab1ff36e8e346dd4a344ba94a4287db6326240066a2cab3525dcedd229
root@DESKTOP-BSA5AD6:/usr/bin# docker commit --message "大数据集群基本镜像：完成Hadoop和Yarn 部分" hadoop103 geekthomas/hado
op103:v1.0
sha256:e501801135824ceefa9985445ba18e6a9e9189f05751efd8195660d8f596f5af
root@DESKTOP-BSA5AD6:/usr/bin# docker commit --message "大数据集群基本镜像：完成Hadoop和Yarn 部分" hadoop104 geekthomas/hado
op104:v1.0
sha256:a63b2deb75ff944348866e06052e7d28c9f7f91140a296b69191a3cf814dbc70
root@DESKTOP-BSA5AD6:/usr/bin#
```

  

编写`docker-compose.yml`

  

```yaml
version: '2.3'

services:
  hadoop102:
    image: geekthomas/hadoop102:v1.0
    hostname: hadoop102
    container_name: hadoop102
    privileged: true
    links:
      - hadoop103
      - hadoop104
    depends_on:
      - hadoop103
      - hadoop104
    ports:
      - 9870:9870
      - 22
    entrypoint: ["/usr/sbin/init"]
    networks:
      big-data:
        ipv4_address: 192.168.10.102

  hadoop103:
    image: geekthomas/hadoop103:v1.0
    hostname: hadoop103
    container_name: hadoop103
    privileged: true
    entrypoint: ["/usr/sbin/init"]
    ports:
      - 22
    networks:
      big-data:
        ipv4_address: 192.168.10.103

  hadoop104:
    image: geekthomas/hadoop104:v1.0
    hostname: hadoop104
    container_name: hadoop104
    privileged: true
    entrypoint: ["/usr/sbin/init"]
    ports:
      - 22
    networks:
      big-data:
        ipv4_address: 192.168.10.104

networks:
  big-data:
    external:
      name: big-data
```