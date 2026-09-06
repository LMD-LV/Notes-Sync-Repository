##   
一.flink安装

（1）进入/app/clmpdata/flink

（2）tar -zxvf flink-1.16.1-scala\_2.12.tar

### flink作业问题1: 同问题3

问题java.util.concurrent.TimeoutException: Heartbeat of TaskManager with id job-af2f94d0-59d7-4e51-aa55-dc91d1a264a8-taskmanager-1-1 timed out.

问题分析：TaskManager心跳超时。有可能是TaskManager已经失败，如果没有失败，那么有可能是因为网络不好导致JobManager没能收到心跳信号，或者TaskManager忙于GC，无法发送心跳信号。JobManager会重启心跳超时的TaskManager，如果频繁出现此异常，应该通过日志进一步定位问题所在。

在Flink中，资源的隔离是通过Slot进行的，也就是说多个Slot会运行在同一个JVM中，这种隔离很弱，尤其对于生产环境。Flink App上线之前要在一个单独的Flink集群上进行测试，否则一个不稳定、存在问题的Flink App上线，很可能影响整个Flink集群上的App。

[flink任务的taskmanager失败Heartbeat of TaskManager with id taskmanager-1-1 timed out.\_毛毛是条好狗的博客-CSDN博客](https://blog.csdn.net/kaisadaditebaba/article/details/127993840)

### flink作业经验：

flinksql，regularjoin（join 、left、right、full）都是默认缓存所有数据，需要搭配ttl来使用，否则数据量大时使用有问题。维表join时，事实表需要定义一个系统处理时间字段。

### flink作业问题3：

#### **The heartbeat of TaskManager with id container ....... timed out**

此错误是container心跳超时，出现此种错误一般有两种可能：

1、分布式物理机网络失联，这种原因一般情况下failover后作业能正常恢复，如果出现的不频繁可以不用关注；2、failover的节点对应TM的内存设置太小，GC严重导致心跳超时，建议调大对应节点的内存值。

#### **Caused by: java.util.concurrent.CompletionException: akka.pattern.AskTimeoutException: Ask timed out on [Actor\[akka.tcp://flink@flink88:15265/user/taskmanager\_0#6643546564]\] after [10000 ms]. Sender[null] sent message of type "org.apache.flink.runtime.rpc.messages.RemoteRpcInvocation".**

在flink-conf.yaml中添加或修改：akka.ask.timeout: 100s web.timeout: 100000

### flink作业问题4：

#### **Checkpoint：Checkpoint expired before completing**

checkpointConf.setCheckpointTimeout(5000L)这个值设置过小，默认是10min，需要进行调大测试。

### flink作业问题5：

flinkcdc全量同步完表格后，对数据计算，数据进入计算逻辑时没有按预想watermark的升序进行计算，是乱序的。flinkcdc2.2.1，我全量从头同步一张表a（product\_Id，number，create\_time，update\_time），按照表里的update\_time作为watermark（ts），数据在flinkui界面是能看到完全同步过来了，然后按照product\_id维度，对数据开小时滚动窗口聚合sum（number）。然后问题出现了，我输出的时候应该是一个小时一个产品一条数据，最后输出就几条数据（应该输出几千条），我想着应该是watermark乱了然后更新很快就结束了。我尝试在计算逻辑部分先给a表的watermark字段排个序或者update\_time排个序，但是还是不行？

##### MySQL CDC源表如何工作，会对数据库造成什么影响？

在启动模式为initial（默认值）时，MySQL CDC源表会先通过JDBC连接MySQL，使用SELECT语句读取全量的数据，并记录Binlog的位点。全量阶段结束后，再从记录的位点开始读取Binlog中的增量数据。

全量阶段时，由于通过SELECT语句查询数据，MySQL服务的查询压力可能会增加。增量阶段时，需要通过Binlog Client连接MySQL读取Binlog，当使用的数据表增加时，可能出现连接数过多的问题。

结论：由于MySQL CDC源表会先通过JDBC连接MySQL全量读取表，全量阶段会多线程并行（分多块并行读取），导致数据读取的顺序是乱序的，计算时会出现watermark大的先到，导致数据迟到问题，因此部分场景不建议使用（如开窗窗口大小比较小，乱序会导致窗口数据很少或者窗口数量比实际少很多），解决如下：

1.此时历史数据可由源库直接读取按对应维度聚合得到结果后插入结果表，在插入前启动增量的计算，让重复的数据相互覆盖，比如天窗口，则可以在前一天计算实时增量窗口数据，前一天可以不准，但是后一天是准的且不断更新，当天可计算历史数据插入更新数据，之后当天的实时数据会覆盖当天保证当天数据是准的，同时历史数据也是有了。

2.设置很大的ttl，那就是把数据全存内存了，小表可以，但是表数据量太大，就会oom

3.窗口开很大，或者全局窗口，这样也会oom。

## 二.maven安装（生产忽略）

（1）进入 /app/clmpdata/maven

（2）tar -zxvf apache-maven-3.8.4-bin.tar.gz

（3）更改 apache-maven-3.8.4/conf/settings.xml文件

参照 打包里的settings.xml文件，但是生产上用不了，我们需要的依赖必须手动放入镜像里。

## 三.docker

#### 1.安装

```plain
cd /app/clmp/docker

tar -zxvf docker-20.10.9.tgz 

cp docker/* /usr/local/bin
```

在/etc/systemd/system或者/usr/lib/systemd/system目录下创建文件 docker.socket和docker.service以及containerd.service

vim docker.socke

```plain
[Unit]
Description=Docker Socket for the API
PartOf=docker.service

[Socket]
ListenStream=/var/run/docker.sock
SocketMode=0660
SocketUser=root
SocketGroup=docker

[Install]
WantedBy=sockets.target
```

vim docker.service

```plain
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network.target

[Service]
Type=notify

# the default is not to use systemd for cgroups because the delegate issues still

# exists and systemd currently does not support the cgroup feature set required

# for containers run by docker

#ExecStart=/usr/bin/dockerd
#ExecStart=/usr/bin/docker daemon --tlsverify --tlscacert=/root/openssl/ca.pem --tlscert=/root/openssl/server-cert.pem --tlskey=/root/openssl/server-key.pem --registry-mirror=http://3cda3ca9.m.daocloud.io -H tcp://0.0.0.0:2376

#ExecStart=/usr/bin/docker daemon --registry-mirror=http://3cda3ca9.m.daocloud.io -H fd:// -H tcp://0.0.0.0:2375
#ExecStart=/usr/bin/dockerd --registry-mirror=http://3cda3ca9.m.daocloud.io
ExecStart=/usr/bin/dockerd --registry-mirror=http://3cda3ca9.m.daocloud.io -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2375

ExecReload=/bin/kill -s HUP $MAINPID

# Having non-zero Limit*s causes performance problems due to accounting overhead

# in the kernel. We recommend using cgroups to do container-local accounting.

LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity

# Uncomment TasksMax if your systemd version supports it.

# Only systemd 226 and above support this version.

#TasksMax=infinity
TimeoutStartSec=0

# set delegate yes so that systemd does not reset the cgroups of docker containers

Delegate=yes

# kill only the docker process, not all processes in the cgroup

KillMode=process

[Install]
WantedBy=multi-user.target
```

vim containerd.service

```plain
# Copyright The containerd Authors.

#

# Licensed under the Apache License, Version 2.0 (the "License");

# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at

#

# http://www.apache.org/licenses/LICENSE-2.0

#

# Unless required by applicable law or agreed to in writing, software

# distributed under the License is distributed on an "AS IS" BASIS,

# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# See the License for the specific language governing permissions and

# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5

# Having non-zero Limit*s causes performance problems due to accounting overhead

# in the kernel. We recommend using cgroups to do container-local accounting.

LimitNPROC=infinity
LimitCORE=infinity
LimitNOFILE=infinity

# Comment TasksMax if your systemd version does not supports it.

# Only systemd 226 and above support this version.

TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
```
```plain
其他操作：
groupadd docker

systemctl daemon-reload 

systemctl start docker

systemctl enable docker.service
```

#### 2.配置私有仓库为默认仓库推拉镜像

vim /etc/docker/daemon.json

添加如下：（有slb则配置为slb 的ip）

```plain
{

"insecure-registries":["10.32.165.240:80"],

"registry-mirrors":["http://10.32.165.240:80"],
"graph":"/app/clmp/docker/lib/docker"
}
```

#### 3.docker使用

images：镜像，一个未启动的“虚拟机”的包

container：容器，一个运行中的“虚拟机”

tag：格式为：*仓库ip：端口/存放路径 ：版本*

docker images #查看所有镜像

docker ps #查看运行的容器

docker tag 现有的镜像名称 目标镜像名称

docker push tag标签 #推送到私库

docker pull tag标签 #拉取私库镜像

#### 4.遇到问题整理

##### 遇到问题1：docker磁盘空间不足

分析：我们创建新镜像或者容器、load镜像、pull镜像、往往是将镜像和容器放入/var/lib/docker中，当空间不足时，就会影响docker的正常操作。

查看 磁盘使用情况 df -h

docker info 命令 查看docker root dir

查看 docker磁盘情况

du -sh ${docker root dir}

解决:

1.停止docker服务

systemctl stop docker

2.

vim /etc/docker/daemon.json

在第一层大括号内添加以下内容（指定docker镜像和容器的存储）：

"grap":"空间足够的目录"

3.迁移/var/lib/docker

rsync -avz /var/lib/docker 大磁盘目录/docker/lib/docker

4.刷新重启

systemctl daemon-reload

systemctl restart docker 或者 service docker restart

##### 遇到问题2.对已有镜像修改更新，重新推送私库步骤：

1.docker images 找到要修改的镜像 名字（随机码）

2.docker run -it --name 容器名字（自己取一个） 镜像名字（随机码） /bin/bash -----运行镜像并命名且进入容器内部

exit 退出容器

3.docker cp 要放入容器内的文件或者jar包 容器名字：容器内路径 （把路径调过来在宿主机运行，可实现由内向外复制）

4.docker start 容器名字 运行刚才退出的容器

6.docker exec -it 容器名字 /bin/bash 进入容器后查看指定路径下是否修改成功

exit

docker ps 查看该容器的 容器id

7.docker commit 容器id 指定容器的tag

8.docker push 镜像tag

##### 遇到问题3:

docker: http: server gave HTTP response to HTTPS client

原因分析 docker registry未采用https服务，而客户端docker使用https请求push所致

解决方法： docker客户端将https请求更改为http请求， 将以下配置添加到 /etc/docker/daemon.json 中

{ "insecure-registries":["192.168.220.125:5000"] }注意： 该配置是配置在docker客户端，让docker客户端以不安全的http请求访问docker registry，ip以及端口填写的是提供服务容器的ip以及端口。

增加配置文件后，重启docker服务

service docker restart

  

---

[[Bug]Error from server (BadRequest): container “xx“ in pod “xx“ is waiting to start:trying and faili\_error from server (badrequest): container "calico-\_不以物喜2020的博客-CSDN博客](https://blog.csdn.net/Keyuchen_01/article/details/123882010)

## 四.pgsql高可用安装

参考文档：

[PostgreSQL HA集群高可用方案介绍 & pgpool-II+PostgreSQL HA方案部署\_postgresql 高可用-CSDN博客](https://blog.csdn.net/sunny05296/article/details/121170496)

[PGPool-II 4.2.1+PostgreSQL 13高可用\_pgpool 免密-CSDN博客](https://blog.csdn.net/along1976/article/details/113719487)

#### 1.安装依赖 （没网不安装也行）

yum install -y perl-ExtUtils-Embed readline-devel zlib-devel pam-devel libxml2-devel libxslt-devel openldap-devel python-devel gcc-c++ openssl-devel cmake gcc\* readline-devel

#### 2.创建用户 （用于操作数据库）

```plain
useradd postgres
passwd  postgres 修改密码为 Admin#0803

数据库初始化目录
mkdir -p /app/clmp/pgsql/data
mkdir -p /app/clmp/pgsql/arch

所属主给到postgres
chown postgres:postgres /app/clmp/pgsql/data
```

#### 3.解压tar包

```plain
cd /app/clmp/pgsql

tar -zxvf postgresql-13.3.tar.gz

cd /app/clmp/pgslq/postgresql-13.3
```

#### 4.开始编译安装

```plain
# 上生产时添加指定路径到 (前面依赖没加的话需要加上这个参数--with-readline-devel)
./configure --prefix=/app/clmp/pgsql 

make && make install
```

#### 5.给安装后的文件赋予权限及环境变量设置

```plain
chmod  -R  777 /app/clmp/pgsql      ## 没有权限当切换为postgres去操作时会出现很多问题

vim /etc/profile
export PGHOME=/app/clmp/pgsql
export PGDATA=/app/clmp/pgsql/data
export PGPORT=5432
export PATH=$PATH:$PGHOME/bin

source /etc/profile

测试安装是否成功
psql --help
```

#### 6.初始化数据库

```plain
切户：
su postgres

初始化命令执行
/app/clmp/pgsql/bin/initdb /app/clmp/pgsql/data

启动数据库
/app/clmp/pgsql/bin/pg_ctl -D /app/clmp/pgsql/data start

进入数据库命令行客户端
psql

create databese test;
create table....

退出
exit
```

#### 7.安装从库

重复上述1-6

#### 7.配置主数据库

```plain
su postgres
cd /app/clmp/pgsql/data

vim postgresql.conf
```
```plain
#编辑 PostgreSQL 的主配置文件 postgresql.conf

listen_addresses = '*'               # 允许连接的 IP 地址，这里设置为通配符 '*'，表示允许所有地址连接。
wal_level = replica                  # 设置 WAL 日志级别为 replica，以支持逻辑复制。
archive_mode = on                    # 启用归档模式，将 WAL 日志保存到归档目录。
archive_command = 'cp %p /var/lib/postgresql/archive/%f'    # 设置归档命令，将 WAL 日志复制到指定归档目录。
max_wal_senders = 10                 # 允许的最大 WAL 发送者数量，用于流复制。
wal_keep_size = 1000                 # 设置保留的 WAL 日志大小，以 MB 为单位。
max_slot_wal_keep_size = 10          # 为逻辑复制保留的最大 WAL 日志大小。
wal_sender_timeout = 120s            # WAL 发送者超时时间，设置为 120 秒。
hot_standby = on                     # 启用热备模式，允许从服务器作为热备份。
wal_log_hints = on
logging_collector = on
log_directory = 'log'
```

psql 命令 进入主库，创建一个用户repuser用于同步数据，修改postgres超级用户的密码

```plain
ALTER USER postgres WITH PASSWORD '123456';
create user repuser REPLICATION LOGIN ENCRYPTED PASSWORD '123456';
```

编辑主服务器的 pg\_hba.conf 文件以配置访问权限。添加以下行来允许从服务器（IP ）连接：

```plain
host all all all md5
host replication all all md5
```

重启主服务器：

```plain
chmod  -R  750 /app/clmp/pgsql/data     ## 需要 750 或者 700权限，否则会报data目录非法权限

pg_ctl restart
```

#### 8.从库配置

```plain
su postgres

cd /app/clmp/pgsql/data
```

开始首次同步主库数据：/usr/local/pgsql/data 为数据库数据存储位置

```plain
清空该目录下从库所有数据

rm -rf /app/clmp/pgsql/data/*

将主库数据同步到从库

pg_basebackup -Xs -v -Fp -P -R -d "hostaddr=192.168.10.5 port=5432 user=repuser password=123456" -D /app/clmp/pgsql/data
```

重启从库： pg\_ctl restart

psql进入从库命令客户端，在主库建表插入数据，查看从库是否能同步。

#### 9.主从切换（需要手动配置--不用操作）

停止主库pg

主库data目录下 新建一个文件 standby.signal即可将主库标记为从库

停止从库，且更改pg\_hba.conf文件内配置使主库能有权限到从库拉取数据

```plain
host all all all md5
host    replication all all md5
```

运行命令 “ pg\_ctl promote ” 将从库提升为新的主库

重启从库（新主库） pg\_ctl restart

重启主库（新备库） pg\_ctl restart

测试：在新主库中插入数据到测试表，查看新备库是否能同步。

#### 9.节点免密登录配置

两台服务器root 、postgres分别交叉配置免密登录

[all servers]#su - root

cd ~/.ssh

#ssh-keygen -t rsa -f id\_rsa\_pgpool 直接回车

#ssh-copy-id -i id\_rsa\_pgpool.pub postgres@pg13-node1

#ssh-copy-id -i id\_rsa\_pgpool.pub postgres@pg13-node2

[all servers]#su - postgres

$cd ~/.ssh

$ssh-keygen -t rsa -f id\_rsa\_pgpool 直接回车

$ssh-copy-id -i id\_rsa\_pgpool.pub postgres@pg13-node1

$ssh-copy-id -i id\_rsa\_pgpool.pub postgres@pg13-node2

#### 10.所有节点安装依赖 以及 pgpool ( 依赖包在 /app/clmp/tool 下 )

rpm -ivh libmemcached-1.0.16-5.1.al7.x86\_64.rpm

rpm -ivh postgresql-libs-9.2.24-8.1.al7.x86\_64.rpm

rpm -ivh pgpool-II-pg13-4.2.10-1pgdg.rhe17.x86\_64.rpm

pgpool安装目录在：/etc/pgpool-II/。接下来主要是修改pgpool的配置文件pool\_hba.conf、pcp.conf、pool\_passwd、failover.sh、escalation.sh、pgpool.conf、pgpool\_node\_id、follow\_primary\_command。

#### 11.每个节点pgpool\_node\_id文件中指定机器的编号，要与pgpool.conf中的heartbeat\_hostname数字 要对应。

比如主机 是0 ，从机 1

#### 12.pool\_hba.conf文件中配置和/app/clmp/pgsql/data/pg\_hba.conf一致

```plain
host all all all md5
host    replication all all md5
```

#### 13.pg\_md5 pg中用户的账户密码，如

pg\_md5 123456 123456假如是postgres的密码

将的到的MD5密码复制

在各节点pcp.conf文件中写入

```plain
postgres：MD5密码
repuser:MD5密码
```

同时将各节点各用户的用户名和密码生成到 pool\_passwd文件中

```plain
pg_md5 -p -m -u postgres pool_passwd        
                                ###密码输错了这里不会验证，后续操作不成功可能跟这有关，重新生成一下
```

#### 14.修改各节点failover.sh中，pgsql的安装目录

```plain
cp failover.sh.sample failover.sh

cp follow_primary.sh.sample follow_primary.sh
```
```plain
vim failover.sh

PGHOME=/usr/local/pgsql
```

chown postgres:postgres /etc/pgpool-II/{failover.sh,follow\_primary.sh}

#### 16.修改各节点pgpool.conf文件，参考 pgpool.conf

直接复制已经改好的文件做部分修改。主要修改hostname

```plain
# [CONNECTIONS]

listen_addresses = '*'
port = 9999
socket_dir = '/var/run/postgresql'

## - Backend Connection Settings -

backend_hostname0 = 'server1'
backend_data_directory0 = '/var/lib/pgsql/13/data'
backend_application_name0 = 'server1'
backend_flag0 = 'ALLOW_TO_FAILOVER'
backend_port0 = 5432
backend_weight0 = 1

backend_hostname1 = 'server2'
backend_data_directory1 = '/var/lib/pgsql/13/data'
backend_application_name1 = 'server2'
backend_flag1 = 'ALLOW_TO_FAILOVER'
backend_port1 = 5432
backend_weight1 = 1

backend_hostname2 = 'server3'
backend_data_directory2 = '/var/lib/pgsql/13/data'
backend_application_name2 = 'server3'
backend_flag2 = 'ALLOW_TO_FAILOVER'
backend_port2 = 5432
backend_weight2 = 1

## - Authentication -

enable_pool_hba = on
pool_passwd = 'pool_passwd'

# [LOGS]

logging_collector = on
log_directory = '/var/log/pgpool_log'
log_filename = 'pgpool-%Y-%m-%d_%H%M%S.log'
log_file_mode = 0600
log_truncate_on_rotation = on
log_rotation_age = 1d
log_rotation_size = 10MB

# [FILE LOCATIONS]

pid_file_name = '/var/run/pgpool/pgpool.pid'

## 此目录用来存放 pgpool_status 文件，此文件保存集群状态（刷新有问题时会造成show pool_status不正确）

logdir = '/tmp'

# [NATIVE REPLICATION MODE]

sr_check_user = 'pgpool'

## 为''时查找 pool_passwd

sr_check_password = 'pgpool'
follow_primary_command = '/etc/pgpool-II/follow_primary.sh %d %h %p %D %m %H %M %P %r %R'

# [HEALTH CHECK GLOBAL PARAMETERS]

health_check_period = 5
health_check_timeout = 30
health_check_user = 'pgpool'

## 为''时查找 pool_passwd

health_check_password = 'pgpool'
health_check_max_retries = 3

# [FAILOVER AND FAILBACK]

failover_command = '/etc/pgpool-II/failover.sh %d %h %p %D %m %H %M %P %r %R %N %S'

# [ONLINE RECOVERY]

recovery_user = 'postgres'
recovery_password = 'postgres'
recovery_1st_stage_command = 'recovery_1st_stage'

# [WATCHDOG]

use_watchdog = on
hostname0 = 'server1'
wd_port0 = 9000
pgpool_port0 = 9999

hostname1 = 'server2'
wd_port1 = 9000
pgpool_port1 = 9999

hostname2 = 'server3'
wd_port2 = 9000
pgpool_port2 = 9999

wd_ipc_socket_dir = '/var/run/postgresql'

## - Virtual IP control Setting -

delegate_IP = '172.19.129.100'

## - Behaivor on escalation Setting -

wd_escalation_command = '/etc/pgpool-II/escalation.sh'

## - Lifecheck Setting -

wd_lifecheck_method = 'heartbeat'

### -- heartbeat mode --

heartbeat_hostname0 = 'server1'
heartbeat_port0 = 9694
heartbeat_device0 = ''

heartbeat_hostname1 = 'server2'
heartbeat_port1 = 9694
heartbeat_device1 = ''

heartbeat_hostname2 = 'server3'
heartbeat_port2 = 9694
heartbeat_device2 = ''
```

#### 17.各节点follow\_primary\_command文件修改

follow\_primary\_command脚本中的PCP命令需要用户认证，需要在pcp.conf 中以“ username:encrypted password ”格式指定用户名和md5加密密码 follow\_primary.sh脚本必须在不输入密码的情况下执行PCP命令创建.pcppass

```plain
# pg_md5 密码

[all servers]# echo 'pgpool:'`pg_md5 pgpool` >> /etc/pgpool-II/pcp.conf
[all servers]# su - postgres
[all servers]$ echo 'localhost:9898:pgpool:pgpool' > ~/.pcppass
[all servers]$ chmod 600 ~/.pcppass
```

#### 18.各节点创建目录 复制文件

```plain
mkdir  -p /var/lib/pgsql/13/data/
```

#### 19.选做（我没做）

Online Recovery Configurations：

```plain
[all servers]# cp -p /etc/pgpool-II/recovery_1st_stage.sample /var/lib/pgsql/13/data/recovery_1st_stage
[all server1]# cp -p /etc/pgpool-II/pgpool_remote_start.sample /var/lib/pgsql/13/data/pgpool_remote_start
[all server1]# chown postgres:postgres /var/lib/pgsql/13/data/{recovery_1st_stage,pgpool_remote_start}
```

#### 20.日志目录（正常安装后已经有了）

```plain
#日志：
[all servers]# mkdir /var/log/pgpool_log/
#存储pid:
[all servers]# mkdir /var/run/pgpool/
[all servers]# chown postgres:postgres /var/log/pgpool_log/
[all servers]# chown postgres:postgres /var/run/pgpool/
```

#### 20.看门狗ipc存储

```plain
[all servers]# mkdir /var/run/postgresql/

chmod -R 777  /var/run/postgresql/
```

#### 21.启动pgpool

-   /etc/sysconfig/pgpool Configuration

```plain
# -d表示debug

[all servers]# vi /etc/sysconfig/pgpool
...
OPTS=" -D -n"
```

-   启动pgpool

```plain
# 按顺序启动

[主节点]# 
systemctl start pgpool
tail -f /var/log/pgpool_log/对应日志
[从节点]# 
systemctl start pgpool
tail -f /var/log/pgpool_log/对应日志

主节点连接：
psql -h主节点ip/从节点ip -p9999 -Upostgres
幅节点连接：
psql -h主节点ip/从节点ip -p9999 -Upostgres
```

#### 22.主从模式测试

```plain
# 备节点停pg

[从节点]# pg_ctl stop
查看主节点pgpool日志，是否正常（日志很快就会有反应）。
主节点连接pgsql数据库，插入数据，之后重启从节点pgsql（pg_ctl start），查看从库数据是否能更新主数据库插入的数据

# 主节点操作
[主节点]# pg_ctl stop
查看从节点pgpool日志，是否正常（主节点挂了，从节点变为主节点需要等几分钟的时间才能看到日志的变化，否则从节点连接库之后会是只读的状态，插入不了数据，只能等一会）。
从节点连接pgsql数据库，插入数据，之后重启主节点pgsql（pg_ctl start），查看主库数据是否能更新从数据库插入的数据。

#若是失败则需要根据日志定位分析之前配置的各个文件内容是否正确，保证正确的情况下，删除从库的data目录下文件，然后同步主库数据，重启pgsql、pgpool服务再次测试。
```

虚拟IP问题由于用的服务器是ECS云虚拟主机，所以只在抢到虚拟IP的主机才能连接虚拟IP。相关测试只在相应的主机上进行。

虚拟IP默认掩码为24，我的是20，修改配置（注意/20）：

#### 23.集群管理(参考)

PGPool 集群查看集群配置信息

```plain
pcp_pool_status -h 172.19.129.100 -p 9898 -U pgpool -v
```

查看集群节点详情

```plain
-h 表示集群IP，-p 表示PCP管道端口（默认是9898），-U 表示 PCP管道用户，-v表示查看详细内容
```
```plain
pcp_watchdog_info -h 172.19.129.100 -p 9898 -U pgpool -v
```

查看节点数量

```plain
pcp_node_count -h 172.19.129.100 -p 9898 -U pgpool
```

查看指定节点信息

```plain
pcp_node_info -h 172.19.129.100 -p 9898 -U pgpool -n 0 -v
```

增加一个集群节点

```plain
# -n 表示节点序号（从0开始）

pcp_attach_node -h 172.19.129.100 -p 9898 -U pgpool -n 0 -v
```

脱离一个集群节点

```plain
pcp_detach_node -h 172.19.129.100 -p 9898 -U pgpool -n 0 -v
```

提升一个备用节点为活动节点

```plain
pcp_promote_node -h 172.19.129.100 -p 9898 -U pgpool -n 0 -v
```

恢复一个离线节点为集群节点

```plain
pcp_recovery_node -h 172.19.129.100 -p 9898 -U pgpool -n 0 -v
```

## 五、安装helm

下载helm-v3.8.2-linux-amd64.tar.gz

```plain
tar -zxvf helm-v3.8.2-linux-amd64.tar.gz
```

进入解压后的文件夹

```plain
cp linux-amd64/helm /usr/local/bin/
```

## 六、rke2安装k8s

### 1.服务器准备

1) 关闭防火墙，selinux, swap (以下步骤在开发测试ecs上似乎已经做了)

```plain
#关闭三台节点上的防火墙
systemctl stop firewalld
systemctl disable firewalld

#关闭三台节点上的selinux
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/'  /etc/selinux/config 

#关闭三台节点上的swap分区
swapoff -a
sed -ri 's/.*swap.*/#&/' /etc/fstab
```

2) 查看当前ecs时间，以及是否开启了时钟同步

```plain
systemctl status ntpd
```

### 2.Server 节点安装(高可用)

[高可用 | RKE2](https://docs.rke2.io/zh/install/ha)

#### 1) 启动第一个节点

创建目录 (先在在可以联网的机器执行)

```plain
mkdir -p /var/lib/rancher/rke2/agent/images/   --安装脚本里提到的，没有这目录会报错
mkdir /root/rke2-artifacts && cd /root/rke2-artifacts/
curl -OLs https://github.com/rancher/rke2/releases/download/v1.21.5%2Brke2r2/rke2-images.linux-amd64.tar.zst
curl -OLs https://github.com/rancher/rke2/releases/download/v1.21.5%2Brke2r2/rke2.linux-amd64.tar.gz
curl -OLs https://github.com/rancher/rke2/releases/download/v1.21.5%2Brke2r2/sha256sum-amd64.txt
curl -sfL https://get.rke2.io --output install.sh
```

将安装介质放入/root/rke2-artifacts/,安装介质包括

```plain
install.sh
rke2.linux-amd64.tar.gz
rke2-images.linux-amd64.tar.zst
sha256sum-amd64.txt
```

执行安装脚本

```plain
INSTALL_RKE2_ARTIFACT_PATH=/root/rke2-artifacts sh install.sh
```

配置集群node名字为node1修改文件 rke2-server.service文件

```plain
vim /usr/local/lib/systemd/system/rke2-server.service
在
ExecStart=/usr/local/bin/rke2 server --node-name=node1 --disable rke2-metrics-server --disable rke2-ingress-nginx
```

重新加载rke2-server.service

```plain
systemctl daemon-reload
```

启用 rke2-server 服务

```plain
systemctl enable rke2-server.service
```

启动服务

```plain
systemctl start rke2-server.service
```

设置命令到可用范围以及环境变量

```plain
ln -s /var/lib/rancher/rke2/bin/* /usr/local/bin/
```
```plain
vim /etc/profile
export PATH=/var/lib/rancher/rke2/bin:$PATH
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml

source /etc/profile
```

#### 2) 启动master的其他节点

[rke2 安装 - K8S - 码农殇 (codefarme.com)](https://www.codefarme.com/?id=202)

1.查看第一个master的token

```plain
cat /var/lib/rancher/rke2/server/node-token

K10cc8748a3379c2828abdabd819a919f6adcac08a4bc11ab09718456355f893353::server:8b16b770abd8674c5fb0230ba64eebda
```

2.复制token 编辑config文件，无此文件则创建目录和文件后编辑。

```plain
cd /etc/rancher/rke2/

vim config.yaml
```
```plain
server: https://192.168.123.131:9345 #node1的地址
token: K10cc8748a3379c2828abdabd819a919f6adcac08a4bc11ab09718456355f893353::server:8b16b770abd8674c5fb0230ba64eebda
tls-san:
  - my-kubernetes-domain.com
  - another-kubernetes-domain.com
  - 192.168.123.130  #这个是VIP
  
 node-name: "node1"  
 #node-taint:
 #  - "CriticalAddinsonly=true:NoExecute" 默认是可以调度的，如果添加此段表示不可以调度 
 node-label:
  - "node=Master"
  - "node1=Master"
```

配置完成后安装master参照（1） 步骤

### 3.worker 安装（配置识别到第一个master，安装、刷新启动）

1.查看第一个master的token

```plain
cat /var/lib/rancher/rke2/server/node-token

K10cc8748a3379c2828abdabd819a919f6adcac08a4bc11ab09718456355f893353::server:8b16b770abd8674c5fb0230ba64eebda
```

2.复制token 编辑config文件，无此文件则创建目录和文件后编辑。

cd /etc/rancher/rke2/

vim config.yaml

-     
    

```plain
server: https://192.168.123.131:9345 #node1的地址
token: K10cc8748a3379c2828abdabd819a919f6adcac08a4bc11ab09718456355f893353::server:8b16b770abd8674c5fb0230ba64eebda

 node-name: "node4"  
 node-label:

- "node=Worker"
- "node1=Worker"
```

执行（1）里边的安装步骤。

执行安装脚本

INSTALL\_RKE2\_ARTIFACT\_PATH=/root/rke2-artifacts sh install.sh

重新加载rke2-agent.service

systemctl daemon-reload

启用 rke2-agent 服务

```plain
systemctl enable rke2-agent.service
```

启动服务

systemctl start rke2-agent.service

#### 其他相关操作：

rke2 对image的操作

在.bashrc中添加

!\[点击复制代码\]([https://www.codefarme.com/zb\_system/image/admin/page\_copy.png](https://www.codefarme.com/zb_system/image/admin/page_copy.png)

alias crictl='crictl --config /var/lib/rancher/rke2/agent/etc/crictl.yaml'

source .bashrc

crictl ps #列出镜像

crictl images

crictl images ls

UAT尝试：迁移手动安装k8s的etcd，暂定方案如下

在所有master节点执行：

cd /var/lib/rancher/rke2/server/db/etcd

vim config

先停了k8s集群

更改data-dir到 /app路径下

rsync -avz /var/lib/rancher/rke2/server/db/etcd /app/clmp/db/etcd

重新启动k8s集群

### 3.k8s 证书过期的处理方法

### 4.k8s日志查看方式：

一、K8S查看集群事件

kubectl get events

![](assets/flink_on_k8s_实时系统安装(企业实战的)-1.png)

二、kubelet describe 查看日志，

一定要带上 命名空间，多个命名空间会报错

#kubectl describe node kmaster1 #查看node节点日志

#kubectl describe pod pod名称 #查看pod应用的信息

![](assets/flink_on_k8s_实时系统安装(企业实战的)-2.png)

三、K8S查看pod日志

pod日志的查看具体用法比较多，根据实际场景去用

kubectl logs -f etcd-kmaster1 -n kube-system

kubectl logs --tail 200 -f kube-apiserver -n kube-system #查看最后200行的日志

kubectl logs -l app=frontend # 返回所有标记为 app=frontend 的 pod 的合并日志。

kubectl logs --since=1h nginx#查看名称为nginx这个pod最近一小时的日志

![](assets/flink_on_k8s_实时系统安装(企业实战的)-3.png)

四、journalctl命令

命令一般是服务启动情况的日志

journalctl -u kube-scheduler

journalctl -xefu kubelet #实时刷新

journalctl -u kube-apiserver

journalctl -u kubelet |tail

journalctl -xe

![](assets/flink_on_k8s_实时系统安装(企业实战的)-4.png)

五、操作系统日志

/var/log/messages日志，messages日志中除了操作系统的日志，服务异常的日志也可以去messages中去看看。

![](assets/flink_on_k8s_实时系统安装(企业实战的)-5.png)

### 5.k8s相关的一些问题参考

[kubernetes部署失败的原因 - 初期网工 - 博客园 (cnblogs.com)](https://www.cnblogs.com/laiyuan/p/8607938.html)

### 6.报错1：服务器时间不同步导致显示证书过期

通过/etc/kubernetes/admin.conf去访问某个kubernetes集群时，报错\`Unable to connect to the server: x509: certificate has expired or is not yet valid

### 7.报错2：可能是安装rancher时生成证书信任ip没添加进来。

Unable to connect to the server: x509: certificate is valid for ${kubernetes集群的内网IP列表}, not ${kubernetes集群的master设备的外网IP}

## 七、harbor高可用安装

#### 基于k8s高可用安装harbor

1）pgsql高可用安装以slb方式访问（见四）。在安装好的pgsql内创建数据库registry、notary\_server、notary\_signer。将安装了pgsql的节点ip和9999端口通过slb实现负载均衡。

2）使用已申请的redis客户端。

3）harbor配置镜像存储于oss。

注：helm安装harbor之前需要让k8s先能够识别得到harbor镜像，有两种方案解决：①启动docker本地registry容器（需要registry：2镜像），配置k8s识别该容器。docker load -i harbor镜像，把harbor镜像上传本地仓库 ②安装一个单机的harbor供docker和k8s配置后共用，镜像不用传送到单机harbor，只需要在该机的docker load镜像，k8s去远程harbor拉取镜像拉取不到就会去docker本地拉取。

4）k8s集群准备好（见六），三个master节点，每个节点都要做以下操作：

vim /etc/crictl.yaml #可从已有文件复制过来

```plain
vim /etc/rancher/rke2/registries.yaml
```
```plain
vim /etc/docker/daemon.json
```

5）github下载helm必要镜像和charts。注意版本要对应,如下是安装v2.5.6

```plain
#每台需要安装harbor的机子本地加载harbor镜像

cd /app/harbor/

docker load -i ./harbor.v2.5.6.tar.gz

#harborcharts包解压 只需要单个节点就行

tar -zxvf /app/clmp/harbor/harbor-helm-1.9.6.tar.gz

#在values文件中配置：

cd /app/clmp/harbor/harbor-helm-1.9.6/

vim values.yaml
```

values.yaml 修改如下：

nodeport 和 tls配置：

externalURL配置：

配置s3协议oss存储镜像

配置外部pgsql（生产应为slb负载均衡的地址，TCP）

配置外部redis：

4）安装

```plain
cd /app/clmp/harbor

kubectl create ns harbor

helm install harbor ./harbor-helm-1.9.6/ -n harbor

helm uninstall harbor -n harbor    ##卸载
```

5）修改配置登录harbor

vim /etc/docker/daemon.json

参考配置如下（生产应为slb负载均衡的地址TCP 30002端口），每个harbor所在k8s集群都要设置（需要拉取镜像的都要配置）。

systemctl restart docker

docker login 对应地址

docker tag、docker push推送一个镜像试试，查看oss路径下是否有文件

其他操作：通过修改数据库添加harbor项目（比如我们flink、streampark那些个目录就是一个项目）：

## 八、通过helm安装rancher

参考之前rke2安装k8s步骤完成三个节点的安装。

参照之前步骤设置好harbor为私库，确保能正常pull push。

需修改/etc/docker/daemon.json /etc/rancher/rke2/registraries.yaml文件

[Rancher 高可用安装--自签名证书+4层 LB - 权威教程 - Rancher 中文论坛](https://forums.rancher.cn/t/rancher-4-lb/1681)

参考文章：[使用 Helm CLI 在 Kubernetes 集群上部署 Rancher（离线安装） - Varden - 博客园 (cnblogs.com)](https://www.cnblogs.com/varden/p/15996567.html)

crictl命令 pull 镜像报错，找不到 containerd.sock: find / -name containerd.sock 找到目录后 ，在/etc/crictl.yaml里修改

#### 1.安装helm

下载helm-v3.8.2-linux-amd64.tar.gz

```plain
tar -zxvf helm-v3.8.2-linux-amd64.tar.gz
```

进入解压后的文件夹

```plain
cp helm /usr/local/bin/
```

#### 2.安装rancher

##### 操作步骤

1.  外网准备rancher资源上传到内网
2.  （该步骤用于在可联网的机器下载镜像，将镜像打包，内网不需要操作）执行脚本rancher-save-images.sh并以\--image-list ./rancher-images.txt 作为参数，创建所有需要镜像的压缩包：

```plain
./rancher-save-images.sh --image-list ./rancher-images.txt
```

3.  使用脚本 rancher-load-images.sh提取rancher-images.tar.gz文件中的镜像，根据文件rancher-images.txt中的镜像列表对提取的镜像文件重新打 tag 并推送到您的私有镜像库

```plain
docker load -i rancher-images.tar.gz
./rancher-load-images.sh --image-list ./rancher-images.txt --registry 10.32.165.240:80
```

4.  ssl配置(1)上传脚本create\_self-signed-cert.sh， 并且用脚本在rancher宿主机先生成证书，trused-ip记得添加slb地址以及所有flink对应k8s集群的master ip

```plain
./create_self-signed-cert.sh --ssldomain=rancher.k8s.com --ssl-trusted-ip xxxxxx --ssl-size=2048 --ssl-date=3650
```

得到如下5.安装

```plain
kubectl create namespace cattle-system
```
```plain
helm insall rancher ./rancher-<VERSION>.tgz  \
    --namespace cattle-system \
    --set hostname=<RANCHER.YOURDOMAIN.COM> \
    --set rancherImage=<REGISTRY.YOURDOMAIN.COM:PORT>/rancher/rancher \
    --set ingress.tls.source=secret \
    --set privateCA=true \
    --set systemDefaultRegistry=<REGISTRY.YOURDOMAIN.COM:PORT> \ # 自v2.2.0可用，设置默认的系统镜像仓库
    --set useBundledSystemChart=true # 自v2.3.0可用，使用内嵌的 Rancher system charts
```

命令运行后rancher pod开始启动得到下图，rancher是正常的把证书配置到secret

```plain
kubectl -n cattle-system create secret tls tls-rancher-ingress --cert=tls.crt --key=tls.key
```
```plain
kubectl -n cattle-system create secret generic tls-ca --from-file=cacerts.pem=./cacerts.pem
```

如果要添加新的集群成员，则可以先删除这两证书,然后再重复上边的（4）步中添加新增加的trust\_ip重新生成证书，生成证书后重新把证书配置到secret。

```plain
kubectl -n cattle-system delete secret tls tls-rancher-ingress
```
```plain
kubectl -n cattle-system delete secret generic tls-ca
```

5.  更改rancher的 svc:kubectl edit svc -n cattle-system如下图，先更改type为NodePort，：wq保存退出kubectl edit svc -n cattle-system 再进入一次，更改30003和30004两位置的端口号为30003和30004
6.  至此，https://任意一个rancher地址ip：30004 即可访问rancherUI界面，进入rancherUI界面填入的访问地址填写为[https://rancher](https://rancher) slb后的地址ip：30004 （生产上是30003，30004没挂载网页）
7.  生成随机密码，可根据页面提示命令，复制到k8s集群master服务器上运行，若是不可行则运行下面命令c获取新的随机密码：kubectl -n cattle-system exec $(kubectl -n cattle-system get pods -l app=rancher | grep '1/1' | head -1 | awk '{ print $1 }') --reset-password
8.  利用新密码登录上rancher UI界面后。右上角角色管理更改admin密码为：rancher12345

## 九、rancher注册下游k8s集群

在UI界面选择自定义导入已有集群，创建个集群的名字下一步，然后复制rancher提供的命令，根据提示复制命令到已有集群的master节点运行，运行前注意同样方式映射rancher所有宿主机映射的 rancher.k8s.com域名

注册后：

遇到问题：rancher提供的命令运行后，下游k8s集群的cattle-cluster-agent deployment报错日志

解决：把该deployment重新edit

```plain
kubectl edit deployment cattle-cluster-agent -n cattle-system
```

在 spec.template.spec下添加 节点映射到域名（添加rancher集群所有ip）

## 十、rancher创建下游集群

在UI界面选择创建集群，选择rke 还是 rke2，然后选择节点 是否为 controller-plan etcd worker角色，master全选，worker节点只选择worker，配置节点的名称，然后得到命令，在装有支持版本的docker主机上运行命令，然后下一步即可注册，下一步之后即可注册其他master和worker。

在每个master节点配置rancher所有ip映射到rancher.k8s.com并且执行以下步骤（第一个master执行完之后再执行其他的）：

生成kubeconfig文件，安装kubectl命令。

```plain
docker run --rm --net=host -v $(docker inspect kubelet --format '{{ range .Mounts }}{{ if eq .Destination "/etc/kubernetes" }}{{ .Source }}{{ end }}{{ end }}')/ssl:/etc/kubernetes/ssl:ro --entrypoint bash $(docker inspect $(docker images -q --filter=label=io.cattle.agent=true) --format='{{index .RepoTags 0}}' | tail -1) -c 'kubectl --kubeconfig /etc/kubernetes/ssl/kubecfg-kube-node.yaml get configmap -n kube-system full-cluster-state -o json | jq -r .data.\"full-cluster-state\" | jq -r .currentState.certificatesBundle.\"kube-admin\".config | sed -e "/^[[:space:]]*server:/ s_:.*_: \"https://127.0.0.1:6443\"_"' > kubeconfig_admin.yaml
```

mkdir -p /root/.kube/

将/root/kubeconfig\_admin.yaml文件 复制到 /root/.kube/config

将kubectl命令复制到/usr/local/bin

把deployment cattle-cluster-agent重新edit

```plain
kubectl edit deployment cattle-cluster-agent -n cattle-system
```

在 spec.template.spec下添加 所有节点映射到域名

问题1：注册后都active了，但是集群处于waiting for api to available。此时和注册时问题一样，rancher.k8s.com域名映射到主机，且映射到cattle-cluster-agent deployment容器内。

问题2：之前注册失败的，再一次注册，etcd健康检查会报错，解决如下：

Failed to bring up Etcd Plane: etcd cluster is unhealthy: hosts [192.168.100.666] failed to report healthy. Check etcd container logs on each host for more information

这是上次安装残留没删除完整，运行以下命令，重新复制注册命令即可

## 十一、kafka协议连接datahub

1.datahub创建topic时要开启shard扩展模式

2.datahub里边有project概念，但是datahub没有（直接就是topic），因此datahub 项目.topic = kafka的topic

消费者组为 project.topic.subid。

3.联网下载datahub连接需要证书 /app/clmp/cacertsdir/server.cer，把该证书copy到外网（内网生成证书报内存），根据证书在外生成cacerts（生成flink镜像的时候，将证书生成到指定目录）。

Dockerfile文件如下：lib和plugins为236机器 /app/clmp/flink/flink1.16.1/lib\_bak目录下的。

4.引入依赖及kafka连接datahub参数配置如下：

参考文档：[兼容Kafka (aliyun.com)](https://help.aliyun.com/document_detail/168118.html)

## 十二、安装streampark

[安装部署 | Apache StreamPark (incubating)](https://streampark.apache.org/zh-CN/docs/user-guide/deployment)

（1）进入 /app/clmp/streampark/ 目录下，解压streampark安装包

```plain
tar -zxvf apache-streampark_2.12-2.0.0-incubating-bin.tar.gz
mv apache-streampark_2.12-2.0.0-incubating-bin streampark_2.12-2.0.0
mkdir streampark_workspace
```

（2）初始化mysql -- 在对应的数据库执行命令

创建Streampark数据库到Mysql分别执行/opt/apache-streampark\_2.11-2.0.0-incubating-bin/script/下的schema/mysql-schema.sql和data/mysql-data.sql (dbe连接rds后执行)

（3） 修改mysql相关配置

```plain
vim ./conf/application-mysql.yml
修改为对应rds的信息
```
```plain
vim ./conf/application.yml
主要修改以下配置：
workspace:
  local: /app/clmpdata/streampark/streampark_workspace #看情况修改
```

（4）bin/start.sh

[Flink K8s 集成支持 | Apache StreamPark (incubating)](https://streampark.apache.org/zh-CN/docs/flink-k8s/k8s-dev)

将kubectl命令 复制到 /usr/local/bin目录下

cp ./kubectl /usr/local/bin

将 k8s集群6443 端口和 9345端口通过slb负载均衡出来

将k8smaster的 /root/.kube/config文件复制到 streampark本机 /root/.kube/config，修改server 为slb的ip即可

scp /root/.kube/confg root@streampark地址: /root/.kube/config

创建flink-dev 命名空间

```plain
kubectl create ns flink-test
```

创建flink-dev资源RBAC

```plain
kubectl create clusterrolebinding flink-role-binding-default --clusterrole=edit --serviceaccount=flink-test:default
```

flink checkpoint savepoint的配置：

更改本地安装的flink conf目录下 flink-conf.yaml 将ck sp配置到oss上。

streampark配置：

maven配置-生产上不用，test环境配置settings file paht为：/app/clmp/maven-3.8.4/conf/settiongs.xml maven私服为：[http://10.129.35.4:8081/nexus/content/repositories/shrbank-public](http://10.129.35.4:8081/nexus/content/repositories/shrbank-public)

docker setting :配置为生产上harbor地址，test为：10.32.216.44:30002 admin/Harbor12345

flinkhome配置：配置为flink的安装目录 /app/clmp/flink/flinl-1.16.1

#### 遇到问题：

1.streampark 关闭应用的/bin/shutdown.sh无用，这个在2.1.0版本修复了。可 kill -9 来杀死进程再重启

2.提交了一个application模式后，再提交另一个可能会启动不起来：是否跟资源紧缺有关，或是其他冲突

3.提交了application模式，界面显示失败，但是k8s的pod是正常的，且正常工作（此时kubectl命令删除deployment，页面再重启就OK了）

4.flink taskManager一直重启，多半是数据连接信息有问题（排查配置信息，排查flink问题是否是某些时间配置不对，或者资源不足）

1.  FlinkSQL 中不支持直接使用 NULL 关键字。可以采用 IF 函数的另一种语法形式来实现类似的功能，如下所示：

```plain
IF(condition, col, CAST(NULL AS <data_type>))
```

在上面的代码中，你需要将 <data\_type> 替换为对应列的数据类型。

例如，如果 col 列的数据类型是 INT，你可以这样写：

```plain
IF(condition, col, CAST(NULL AS INT))
```

这样就可以解决你遇到的 Illegal use of ‘NULL’ 错误了。记得替换 <data\_type> 为正确的数据类型。

1.  在 FlinkSQL 中，没有名为 nvl 的内置函数。但你可以使用 COALESCE 函数来实现类似的功能。COALESCE 函数接受多个参数并返回 第一个非空参数。

例如，如果你想要在两个 numeric 类型的列中选择非空值，你可以这样写：

COALESCE(col1, col2)

这样如果 col1 不为空，则返回 col1 的值，否则返回 col2 的值。

如果你想要将空值替换为一个特定的默认值，你可以使用 CAST 函数将默认值显式转换为所需的数据类型。例如，将空值替换为 0：

COALESCE(col1, CAST(0 AS numeric))

注意，你需要根据实际情况将 numeric 替换为对应列的数据类型。

希望这能解决你的问题！如果还有其他疑问，请随时提出。

7.postgres-cdc只能用于source，不能用于sink

8.改了代码，但是没识别到最新的（忘记提交了，这样如果是更改了两次，则修改信息只会保留后一次的，上一次会被覆盖）

启停命令：

./bin/startu.sh

./bin/shutdown.sh

默认密码: **admin / streampark**

## 十三、其他

### 1.安装dinky

#### 1) 编译dinky源码包

目前dinky官方不提供可执行包，需要基于最新源码编译，下面使用tag为v0.7.2的源码编译，编译时选择支持的flink版本为1.16

[DataLinkDC/dinky at v0.7.2 (github.com)](https://github.com/DataLinkDC/dinky/tree/v0.7.2)

编译前需在本机安装npm和maven，npm版本保证在7.19.0之上

#### 2) 初始化环境

在mysql数据库中执行dlink-release-0.7.2.tar.gz中的dinky.sql

修改dlink-release-0.7.2.tar.gz中的application.yml中的数据库jdbc连接为初始化好的数据库

#### 3）上传tar包，解压，启动

```plain
sh auto.sh start
```

参考：

[部署 | Dinky (dlink.top)](http://www.dlink.top/docs/next/deploy_guide/build)

[http://10.32.165.236:8888](http://10.32.165.236:8888) admin/admin

解压后的目录中不包含flink基础运行环境，需要下载flink安装包，并把lib目录下的jar包配置到dinky的classpath下

### 2.安装minio

目前使用linux standalone的方式安装minio

```plain
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
nohup ./minio server /app/minio/data &
```

api 和 console地址在启动后的nohup.out中

API: [http://10.32.165.239:9000](http://10.32.165.239:9000)

Console: [http://10.32.165.239:43455](http://10.32.165.239:43455) minioadmin/minioadmin

[minio/minio: Multi-Cloud Object Storage (github.com)](https://github.com/minio/minio)

配置minio为flink的cp和sp路径

### 3.安装harbor

#### 1.docker安装单机harbor

1）上传harbor离线安装包 harbor-offline-installer-v2.5.6.tgz

2）解压

tar -xvf harbor-offline-installer-v2.5.6.tgz -C /app/harbor/

3）进入解压后目录

```plain
vim harbor.yml 

•   修改 hostname： 10.32.165.240

•   注释掉https相关：

•   以s3协议配置oss作为harbor的存储：

•   ![1690365318638](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1690365318638.png)!1690365323011](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1690365323011.png)

http://10.32.165.240   admin/Harbor12345

k8s集群设置镜像库为harbor：

配置如下文件：

vim /etc/rancher/rke2/registries.yaml
```

mirrors：

docker.io:

endpoint:

\-"http://10.32.165.240:80"

10.32.165.240:80:

endpoint:

\-"http://10.32.165.240:80"

```plain
另外要有一台能向harbor提交镜像的节点

需要先安装docker

添加如下配置文件

vim /etc/docker/daemon.json

{

"insecure-registries":["10.32.165.240:80"],

"registry-mirrors":["http://10.32.165.240:80"]

}

向harbor提交上传镜像（需要先在harbor创建streampark这个项目）

docker tag 你的镜像：版本号  10.32.165.240:80/streampark/你的镜像名：版本号

docker login http://10.32.165.240:80

输入harbor的账户密码

docker push 10.32.165.240:80/streampark/你的镜像名：版本号

启停命令：

docker-compose start

docker-compose stop

#### 2.基于k8s高可用安装harbor

1）pgsql高可用安装以nodeport方式访问（见16）。在安装好的pgsql内创建数据库registry、notary_server、notary_signer。将安装了pgsql的节点ip和nodeport 80端口对应端口通过slb实现负载均衡。

2）使用已申请的redis客户端。

3）harbor配置镜像存储于oss。

4）github下载helm必要镜像和charts。注意版本要对应,如下是安装v2.5.6
```

#本地加载harbor镜像

cd /app/harbor/

tar -zxvf /app/harbor/harbor-offline-installer-v2.5.6.tgz

docker load -i ./harbor/harbor.v2.5.6.tar.gz

#harborcharts包解压

tar -zxvf /app/clmp/harbor/harbor-helm-1.9.6.tar.gz

#在values文件中配置：

cd /app/clmp/harbor/harbor-helm-1.9.6/

vim values.yaml

```plain
values.yaml  修改如下：

nodeport 和 tls配置：

![1692323660840](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1692323660840.png)

•   externalURL配置：

![1692323681913](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1692323681913.png)

配置s3协议oss存储镜像

![1692323748217](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1692323748217.png)

配置外部pgsql（生产应为slb负载均衡的地址）

![1692323766174](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1692323766174.png)

配置外部redis：

![1692323785025](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1692323785025.png)

5）修改配置登录harbor

vim /etc/docker/daemon.json

参考配置如下（生产应为slb负载均衡的地址），每个harbor所在k8s集群都要设置。

![1692323902017](C:\Users\58211\AppData\Roaming\Typora\typora-user-images\1692323902017.png)

systemctl restart docker

docker login 对应地址

docker tag、docker push推送一个镜像试试，查看oss路径下是否有文件

### 4.安装helm

#### 1）离线安装helm可执行文件

官网下载二进制安装文件

[Release Helm v3.11.2 · helm/helm (github.com)](https://github.com/helm/helm/releases/tag/v3.11.2)

* 目前还没安装到master

#### 2）搭建helm私库

* harbor可以作为chart库，下面的可以不装

目前使用docker的方式部署chartmuseum和chartmuseum-ui，其中chartmuseum后续可使用二进制的方式安装，存储可使用minio

#### i 安装chartmuseum
```

docker pull ghcr.io/helm/chartmuseum:v0.15.0

```plain
参考：[helm/chartmuseum: Host your own Helm Chart Repository (github.com)](https://github.com/helm/chartmuseum)

#### ii 安装chartmuseum-ui

github上下载最新源码到本地

[chartmuseum/ui: ChartMuseum frontend UI (github.com)](https://github.com/chartmuseum/ui)

由于使用源码中的docker-compose方式需要访问外网docker仓库，在内网环境下无法做到，所以先再外网环境编译chartmuseum-ui为docker images再传到内网的方式安装

添加如下命令至Dockerfile
```
```plain
修改后的Dockerfile文件如下：
```
```plain
#

# Stage 1

#
FROM library/golang:1 as builder

# set Go env 

RUN go env -w GO111MODULE=auto

# Godep for vendoring

RUN go get github.com/tools/godep

# Recompile the standard library without CGO

RUN CGO_ENABLED=0 go install -a std

ENV APP_DIR $GOPATH/src/github.com/chartmuseum/ui
RUN mkdir -p $APP_DIR
ADD . $APP_DIR

# Compile the binary and statically link

RUN cd $APP_DIR && \
    GO111MODULE=auto CGO_ENABLED=0 godep go build -ldflags '-w -s' -o /chartmuseum-ui && \
    cp -r views/ /views && \
    cp -r static/ /static

#

# Stage 2

#
FROM alpine:3.8
RUN apk add --no-cache curl cifs-utils ca-certificates \
    && adduser -D -u 1000 chartmuseum
COPY --from=builder /chartmuseum-ui /chartmuseum-ui
COPY --from=builder /views /views
COPY --from=builder /static /static
USER 1000
ENTRYPOINT ["/chartmuseum-ui"]
```
```plain
本地编译docker image
```

docker build -t chartmuseum-ui:v1 .

```plain
上传内网

内网启动docker镜像

由于chartmuseum-ui需调用chartmuseum服务，所以需要将他们定义在一个docker网络中
```

docker network create --subnet=192.168.0.0/24 cm

docker run --rm -it --name chartmuseum --network cm --ip 192.168.0.10 -d -p 8080:8080 -e DEBUG=1 -e STORAGE=local -e STORAGE\_LOCAL\_ROOTDIR=/charts -v /app/chartmuseum/charts:/charts ghcr.io/helm/chartmuseum:v0.15.0

docker run --name chartmuseum-ui --network cm --ip 192.168.0.11 -d -p 3000:8080 -e CHART\_MUSEUM\_URL=[http://192.168.0.10:8080](http://192.168.0.10:8080) chartmuseum-ui:v1

```plain
访问chartmuseum-ui服务

http://10.32.165.240:3000
```

## \-----------------------------------------------------------------------

# rancher

## 1.什么是rancher

Rancher 是一个 Kubernetes 管理工具，让你能在任何地方和任何提供商上部署和运行集群。

Rancher 可以创建来自 Kubernetes 托管服务提供商的集群，创建节点并安装 Kubernetes，或者导入在任何地方运行的现有 Kubernetes 集群。

Rancher 基于 Kubernetes 添加了新的功能，包括统一所有集群的身份验证和 RBAC，让系统管理员从一个位置控制全部集群的访问。

此外，Rancher 可以为集群和资源提供更精细的监控和告警，将日志发送到外部提供商，并通过应用商店（Application Catalog）直接集成 Helm。如果你拥有外部 CI/CD 系统，你可以将其与 Rancher 对接。没有的话，你也可以使用 Rancher 提供的 Fleet 自动部署和升级工作负载。

Rancher 是一个 *全栈式* 的 Kubernetes 容器管理平台，为你提供在任何地方都能成功运行 Kubernetes 的工具。

## 2.安装

安装docker

docker pull 镜像

![image.png](assets/flink_on_k8s_实时系统安装(企业实战的)-6.png)

docker run 镜像：先创建挂载卷挂载rancher配置数据

![image.png](assets/flink_on_k8s_实时系统安装(企业实战的)-7.png)

主机名：80 访问UI界面

设置登录密码

​  

未完。。。之后整理

​  

## \-----------------------------------------------------------------------

# harbor

##   

## \-----------------------------------------------------------------------

# helm

## 介绍：

helm：一个命令行客户端工具，主要用于k8s应用chart的创建、打包、发布和管理

chart：应用描述，是一系列用于描述k8s资源相关文件的集合

release：基于chart的部署实体，一个chart被helm运行后将会产生一个对应的release，将在k8s中创建出真实运行的资源对象。

架构：

v2版本是helm通过tiller连接k8s的api server

v3版本是helm通过kubeconfig连接k8s的api server、release可以在不同命名空间重用、支持chart推送至docker镜像仓库中、使用jsonschema验证chart values

## 部署

1.[https://github.com/helm/helm/releases](https://github.com/helm/helm/releases)，git下载二进制包，要和自己的k8s版本搭配（查官网）

2.或者直接下载二进制包解压，并且把helm 移动到usr/bin 或者usr/local/bin下。

![image.png](assets/flink_on_k8s_实时系统安装(企业实战的)-8.png)

3.常用命令

![image.png](assets/flink_on_k8s_实时系统安装(企业实战的)-9.png)

4.配置国内chart仓库或者自己的私库

![image.png](assets/flink_on_k8s_实时系统安装(企业实战的)-10.png)

\# 查看当前配置的仓库地址

$ helm repo list

\# 删除默认仓库，默认在国外pull很慢

$ helm repo remove stable

\# 添加几个常用的仓库,可自定义名字

$ helm repo add stable [https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts](https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts)

$ helm repo add kaiyuanshe [http://mirror.kaiyuanshe.cn/kubernetes/charts](http://mirror.kaiyuanshe.cn/kubernetes/charts)

$ helm repo add azure [http://mirror.azure.cn/kubernetes/charts](http://mirror.azure.cn/kubernetes/charts)

$ helm repo add dandydev [https://dandydeveloper.github.io/charts](https://dandydeveloper.github.io/charts)

$ helm repo add bitnami [https://charts.bitnami.com/bitnami](https://charts.bitnami.com/bitnami)

\# 搜索chart

$ helm search repo redis

\# 拉取chart包到本地

$ helm pull bitnami/redis-cluster --version 8.1.2

\# 安装redis-ha集群，取名redis-ha，需要指定持存储类

$ helm install redis-cluster bitnami/redis-cluster --set global.storageClass=nfs,global.redis.password=xiagao --version 8.1.2

\# 卸载

$ helm uninstall redis-cluster

![image.png](assets/flink_on_k8s_实时系统安装(企业实战的)-11.png)

![image.png](assets/flink_on_k8s_实时系统安装(企业实战的)-12.png)

注意：在install之前，先更改一些chart的配置项，依赖项。如挂载pv。