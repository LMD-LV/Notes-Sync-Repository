注意：没个64GB内存别玩了，我已卡死了

# 需下载信息：（cm7.4.4+cdh7.1.7是使用版，无账号也可下，我下载的是最新的）

cdh7.1.7包括： CDH-7.1.7-1.cdh7.1.7.p0.15945976-el7.parcel CDH-7.1.7-1.cdh7.1.7.p0.15945976-el7.parcel.sha1 CDH-7.1.7-1.cdh7.1.7.p0.15945976-el7.parcel.sha256 manifest.json cm7.4.7包括： cloudera-manager-agent-7.4.4-15850731.el7.x86\_64.rpm cloudera-manager-daemons-7.4.4-15850731.el7.x86\_64.rpm cloudera-manager-server-7.4.4-15850731.el7.x86\_64.rpm cloudera-manager-server-db-2-7.4.4-15850731.el7.x86\_64.rpm openjdk8-8.0+232\_9-cloudera.x86\_64.rpm cloudera-manager.repo RPM-GPG-KEY-cloudera allkeys.asc , 相关下载链接：[https://download.csdn.net/download/qq\_24817093/85301394?utm\_source=bbsseo](https://download.csdn.net/download/qq_24817093/85301394?utm_source=bbsseo)

​  

# 安装软硬件环境

## 3台服务器安装 centos7.9

网络: 静态分配

yum源配置:

## cdp版本说明

安装的CM版本为7.11.3.16

CDP版本为7.1.9-1.cdh7.1.9.p1000

## 配置/etc/hosts，必须完全限定域名FQDN

> 192.168.10.121 cdp001.com.cn cdp001
> 
> 192.168.10.122 cdp002.com.cn cdp002
> 
> 192.168.10.123 chp003.com.cn chp003

​  

## 修改hostname（和hosts的第二列一致）

> cdp001.com.cn
> 
> cdp002.com.cn
> 
> chp003.com.cn

  

## 前置准备（每个机器）

### 创建挂载点（若需要）

```xml
mkdir /data
mkfs.xfs /dev/sdb
修改/etc/fstab，添加
/dev/sdb /data xfs defaults,noatime 0 0
挂盘
mount -a
```

​  

### 安装一些基础包

```xml
yum install vim tmux lrzsz rsync unzip wget -y net-tools
yum install -y epel-release

```

### 设置操作系统

```xml
# 停止firewall
systemctl stop firewalld.service
# 禁止firewall开机启动
systemctl disable firewalld.service
# 确认关闭
firewall-cmd --state
```

### 关闭 SELinux

SELinux 是Linux访问控制机制。它使用策略来控制系统中各个进程和文件之间的交互，以增强系统的安全性。

\# 临时关闭

setenforce 0

\# 永久关闭

\# /etc/sysconfig/selinux是/etc/selinux/config的一个软链接

```xml
sed -i s@enforcing@disabled@g /etc/selinux/config
systemctl stop tuned
systemctl disable tuned
```

### 关闭透明大页（ Transparent Huge Pages, THP ）

透明大页是一种内存管理机制，它通过合并多个小页（通常是4KB）为一个大页（通常是2MB）来提高性能。禁用它有时可以减少延迟或提高性能，特别是在某些数据库或高性能计算场景中。

\# 临时关闭

```xml
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
# 永久关闭
echo "echo never > /sys/kernel/mm/transparent_hugepage/enabled" >> /etc/rc.d/rc.local
echo "echo never > /sys/kernel/mm/transparent_hugepage/defrag" >>/etc/rc.d/rc.local
chmod +x /etc/rc.d/rc.local
```

\# 确认是否关闭

grep -i HugePages\_Total /proc/meminfo

cat /proc/sys/vm/nr\_hugepages

sysctl vm.nr\_hugepages

### 降低交换空间使用权重（Swappiness）

**调整 Swappiness**: 降低 swappiness 值使得系统尽可能多地使用物理内存而不是交换空间，从而提高性能，特别是在内存充足的情况下。

注：值可设置为0

```xml
# for runtime effect
sudo sysctl -w vm.swappiness=1
# for permanent effect
echo vm.swappiness=1 >> /etc/sysctl.conf
# check
cat /proc/sys/vm/swappiness
```

​  

### 修改/etc/security/limits.conf，添加

> \* soft nofile 128000
> 
> \* hard nofile 128000
> 
> \* soft nproc 128000
> 
> \* hard nproc 128000

  

### 克隆机器

略

### 配置免密（可选）

每个节点执行一次

```xml
ssh-keygen  ## 三次回车
ssh-copy-id root@localhost
for i in {121..123}; do
  rsync -azvP /root/.ssh 192.168.10.$i:/root/;
done
```

​  

​  

### 时钟同步

```xml
sudo yum remove chrony -y
sudo yum install -y ntp
```

在cdp001机器配置

```xml
vim /etc/ntp.conf
```
> #server 0.centos.pool.ntp.org iburst
> 
> #server 1.centos.pool.ntp.org iburst
> 
> #server 2.centos.pool.ntp.org iburst
> 
> #server 3.centos.pool.ntp.org iburst
> 
> #网络丢失使用本地时间作为服务器时间
> 
> server 127.127.1.0
> 
> fudge 127.127.1.0 stratum 10

  

其他两台机器做如下配置

> #server 0.centos.pool.ntp.org iburst
> 
> #server 1.centos.pool.ntp.org iburst
> 
> #server 2.centos.pool.ntp.org iburst
> 
> #server 3.centos.pool.ntp.org iburst
> 
> ​  
> 
> server cdp001.com.cn
```xml
sudo systemctl start ntpd  #启动NTP服务
sudo systemctl enable ntpd #设置NTP开机自启

```

  

## 安装httpd服务（cdp003）

### 添加parcel包类型识别

```xml
yum install -y httpd
yum install -y createrepo

vim /etc/httpd/conf/httpd.conf 
```
> AddType application/x-gzip .gz .tgz .parcel

​  

```xml
systemctl restart httpd
systemctl status httpd
```

​  

### 配置安装源（所有机器）

vim /etc/yum.repos.d/cloudera-manager.repo

> [cloudera-manager]
> 
> name = Cloudera Manager, Version cm7.11.3.16
> 
> baseurl = [http://192.168.10.123/cm7.11.3.16/](http://10.32.2.18/cloudera/cm-redhat8/cm7.11.3.9/)
> 
> gpgcheck = 0
> 
> enabled=1

配置自己下载的文件的源

需下载cm包、cdp包 放入/var/www/html目录下

cd cm7.11.3.16

生成rpm元数据

```bash
createrepo .
```

  

> http://192.169.10.123/cm7.11.3.16
> 
> http://192.169.10.123/cdp7.1.9

​  

访问文件是否能访问到

  

## 安装数据库

### 安装MySQL

方法一：

官网下载安装包

> mysql-community-client-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-community-client-plugins-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-community-common-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-community-devel-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-community-icu-data-files-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-community-libs-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-community-libs-compat-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-community-server-8.0.33-1.el7.x86\_64.rpm
> 
> mysql-connector-j-8.0.33.jar

​  

```shell
yum install ./*.rpm

```

方法二：

```shell
yum install mysql  mysql-server -y

```

​  

启动MySQL

```shell
systemctl start mysqld
cat /var/log/mysqld.log  查看临时密码
sudo cat /var/log/mysqld.log | grep "temporary password" | awk '{print $NF}'
```
```sql
alter user 'root'@'localhost' identified by 'zzzZZZ@123456';
```

修改配置文件（参考）

vim /etc/my.cnf

```xml
[mysqld]

default_authentication_plugin=mysql_native_password

datadir=/var/lib/mysql
socket=/var/lib/mysql/mysql.sock
transaction-isolation = READ-COMMITTED
symbolic-links = 0

validate_password.length=4
validate_password.policy=0

key_buffer_size = 32M
max_allowed_packet = 32M
thread_stack = 256K
thread_cache_size = 64

max_connections = 550

log_bin=/var/lib/mysql/mysql_binary_log

server_id=1
binlog_format = mixed
read_buffer_size = 2M
read_rnd_buffer_size = 16M
sort_buffer_size = 8M
join_buffer_size = 8M

innodb_file_per_table = 1
innodb_flush_log_at_trx_commit  = 2
innodb_log_buffer_size = 64M
innodb_buffer_pool_size = 4G
innodb_thread_concurrency = 8
innodb_flush_method = O_DIRECT
innodb_log_file_size = 512M

log_bin_trust_function_creators=true

[mysqld_safe]
log-error=/var/log/mysqld.log
pid-file=/var/run/mysqld/mysqld.pid

sql_mode=STRICT_ALL_TABLES
```
```sql
systemctl restart mysqld
```

登录mysql

```shell
mysql -h localhost -P 3306 -u root -p
```

修改root密码（先修改一个高强度的）

```sql

alter user 'root'@'localhost' identified by 'szk123';
update mysql.user set host='%' where user = 'root';

flush privileges;

```

创建数据库

```sql
create database scm DEFAULT CHARACTER SET utf8;
create database rman DEFAULT CHARACTER SET utf8;
create database hive DEFAULT CHARACTER SET utf8;
create database oozie DEFAULT CHARACTER SET utf8;
create database hue DEFAULT CHARACTER SET utf8;
create database ranger DEFAULT CHARACTER SET utf8;
create database queryprocessor DEFAULT CHARACTER SET utf8;
create database yqm DEFAULT CHARACTER SET utf8;
create database sr DEFAULT CHARACTER SET utf8;
create database sm DEFAULT CHARACTER SET utf8;

CREATE USER 'scm'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'rman'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'hive'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'oozie'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'hue'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'ranger'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'queryprocessor'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'yqm'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'sr'@'%' IDENTIFIED BY 'szk123';
CREATE USER 'sm'@'%' IDENTIFIED BY 'szk123';

ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'scm'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'rman'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'hive'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'hue'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'oozie'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'ranger'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'queryprocessor'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'yqm'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'sr'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
ALTER USER 'sm'@'%' IDENTIFIED WITH mysql_native_password BY 'szk123';
FLUSH PRIVILEGES;

GRANT ALL PRIVILEGES ON scm.* TO 'scm'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON rman.* TO 'rman'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON hive.* TO 'hive'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON oozie.* TO 'oozie'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON hue.* TO 'hue'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON ranger.* TO 'ranger'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON queryprocessor.* TO 'queryprocessor'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON yqm.* TO 'yqm'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON sr.* TO 'sr'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON sm.* TO 'sm'@'%' WITH GRANT OPTION;

flush privileges;

```

  

连接hue的依赖安装

```shell
yum install mysql-devel gcc python38-devel -y
pip3 install mysqlclient 
```

### 卸载mysql

```xml
停服务：
sudo systemctl stop mysqld
查看data存放目录
sudo cat /etc/my.cnf
进入目录删除所有数据
cd /var/lib/mysql
rm -rf *
卸载包
rpm -qa | grep -i -E mysql\|mariadb | xargs -n1 sudo rpm -e --nodeps
```

### 配置MySQL驱动（所有节点）

maven自行下载一个版本

```shell
mkdir -p /usr/share/java
mv mysql-connector-j-8.0.33.jar /usr/share/java/
ln -s /usr/share/java/mysql-connector-j-8.0.33.jar /usr/share/java/mysql-connector-java.jar
```

  

## 安装jdk（所有节点）

```bash
卸载
rpm -qa | grep -i java | xargs -n1 rpm -e --nodeps 

安装（需要先有安装包，或者配了yum源）
yum install openjdk8-8.0+372_1-cloudera.x86_64.rpm

先找到安装路径
cd /usr/java/
配置环境变量
vim /etc/profile
export JAVA_HOME=/usr/java/jdk1.8u372-b07-cloudera/
export PATH=$JAVA_HOME/bin:$PATH

测试
java -version
```

​  

## 安装Python3.8(所有节点，cm7.11.3需要最低3.8.12)

上传包（Python-3.8.0.tgz）并解压进入解压目录

```plain
yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel -y

方法一：从 CentOS 软件集合（SCL）安装 Python 3.8
yum install centos-release-scl 
yum install rh-python38 rh-python38-python-pip rh-python38-python-pip-wheel
python3 --version

方法二：源码构建
cd /opt/soft
curl -O https://www.python.org/ftp/python/3.8.17/Python-3.8.17.tgz
tar -zxvf Python-3.8.17.tgz
cd /opt/soft/Python-3.8.17
./configure --prefix=/usr/local/python3.8
make && make install
cp  --no-clobber  ./libpython3.8.so* /lib64/

ln -s /usr/local/python3.8/bin/python3.8.17 /usr/bin/python3.8

chmod 755 /lib64/libpython3.8.so*

若报错执行以下语句
报错信息：error while loading shared libraries: libpython3.8.so.1.0: cannot open shared object file: No such file or directory

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

chmod -R 755 /usr/local/python3.8

```

​  

> To add an environment variable to the Cloudera Manager Agent in the systemd service definition files perform the following steps:
> 
> 1.  SSH into the host system on which you installed Python 3.8 as a root user.
> 2.  Open the /usr/lib/systemd/system/cloudera-scm-supervisord.service file for editing.
> 3.  Add the following line in the cloudera-scm-supervisord.service file under the [Service] section:
> 
> Environment=”PYTHONBIN=/usr/local/python38/bin/python3.8”
> 
> 4.  Open the /usr/lib/systemd/system/cloudera-scm-agent.service file for editing.
> 5.  Add the following line in the cloudera-scm-agent.service file under the [Service] section:
> 
> Environment=”PYTHONBIN=/usr/local/python38/bin/python3.8”
> 
> **important**If your custom version of Python 3.8 installation requires setting up the `PYTHONHOME` or `PYTHONPATH` variables, then add them with additional Environment lines.
> 
> Enable Hue to use Python 3.8 installed in a custom location
> 
> If you have installed Python 3.8 in a custom location and you did not configure alternatives, then you must prepend the custom path to the custom bin directory in Cloudera Manager \> Clusters \> Hue \> Configuration \> Hue Service Environment Advanced Configuration Snippet (Safety Valve) separated by colon (:) as follows:
> 
> Key: PATH
> 
> Value: [\*\*\*CUSTOM-INSTALL-PATH\*\*\*]:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
> 
> Install the psycopg2-binary package
> 
> Install the psycopg2-binary package after installing Python 3.8 for using PostgreSQL as a backend database for Hue.

根据上述提示配置环境：

方法一：自定义位置安装了 Python 3.8，则必须使用alternatives 命令创建符号链接

方法二：添加systemd环境变量，如下

```sql
vim /usr/lib/systemd/system/cloudera-scm-supervisord.service
Environment=”PYTHONBIN=/usr/local/python38/bin/python3.8”

vim /usr/lib/systemd/system/cloudera-scm-agent.service
Environment=”PYTHONBIN=/usr/local/python38/bin/python3.8”
```

  

安装hue依赖（使用pg作为后端库时需要）

```shell
/usr/local/python38/bin/pip3.8 install psycopg2-binary
```

## 配置IPA作为Kerberos和LDAP（cdp002）

### 安装随机数发生器

freeipa安装需要大量的随机数运算加密操作，需要安装rngd服务防止操作系统的熵值过低。

```xml
yum install -y rng-tools
cp /usr/lib/systemd/system/rngd.service /etc/systemd/system/
systemctl daemon-reload
systemctl start rngd
systemctl enable rngd
```

​  

查看熵(三位数以下不太够用，安装后应该都上千的)

```xml
cat /proc/sys/kernel/random/entropy_avail
```

  

### ipv6堆栈开启（freeipa依赖需要）

vim /etc/sysctl.conf

```plain
net.ipv6.conf.lo.disable_ipv6 = 0
net.ipv6.conf.all.disable_ipv6 = 0 ###注释/删除此行或将其值从1更改为0
net.ipv6.conf.default.disable_ipv6 = 0 ###注释/删除此行或将其值从1更改为0
```

sudo sysctl -p /etc/sysctl.conf

### 安装IPA服务端（cdp002）

```shell
yum install -y ipa-server ipa-server-dns bind bind-dyndb-ldap
```

> 1.  **ipa-server**:
> 
> -   这是 FreeIPA 服务器的核心软件包。它包含了安装和配置 FreeIPA 服务器的所有必要文件，包括安装脚本、配置文件模板、服务单元文件等。安装此软件包将配置和启动 FreeIPA 服务器，该服务器提供用户管理、身份验证、策略管理等功能。
> 
> 2.  **ipa-server-dns**:
> 
> -   这是一个附加软件包，用于将 FreeIPA 服务器配置为 DNS 服务器。它扩展了 ipa-server 的功能，允许 FreeIPA 管理 DNS 记录，如主机名、别名、服务记录等。这对于实现集成的身份验证和 DNS 解决方案非常有用，因为 DNS 和身份验证是紧密相关的。
> 
> 3.  **bind**:
> 
> -   BIND（Berkeley Internet Name Domain）是一款广泛使用的 DNS 服务器软件。尽管 ipa-server-dns 可能已经包含了 BIND 的必要部分或与之集成的版本，但直接安装 bind 包可能是为了确保系统上有 BIND 的完整实现，或者用于某些特定的配置需求。然而，在 FreeIPA 环境中，通常会使用 ipa-server-dns 提供的 BIND 集成。
> 
> 4.  **bind-dyndb-ldap**:
> 
> -   这个软件包提供了 BIND 的动态 LDAP 后端支持。这意味着 BIND 可以从 LDAP 数据库中动态读取和写入 DNS 记录。在 FreeIPA 环境中，这允许 BIND 实时地从 LDAP（由 FreeIPA 管理）中读取和更新 DNS 记录，实现了 DNS 和身份验证系统的无缝集成。

​  

配置IPA服务端

```shell
ipa-server-install
```

​  

命令执行以后会有以下设置

> ![image.png](assets/CDP私有云安装(centos7)-1.png)

以下报错信息暂时忽略

![image.png](assets/CDP私有云安装(centos7)-2.png)

### 安装IPA客户端（其他所有机器）

注意这里如果你把本地的DNS改成IPA后，ipa-client-install命令行自动发现IPA Server地址，不需要手动配置，但是这样生成的krb5.conf文件也会使用DNS发现，不符合CM的规范，还是要改成下文的样子。

​  

```shell
yum install -y ipa-client

ipa-client-install 
```

命令执行过程

![image.png](assets/CDP私有云安装(centos7)-3.png)

### 其他配置

① 修改所有/etc/sssd/sssd.conf，在nss下添加

注：为了在新加机器、或者加了机器后装ipa的时候，能保证原先有的用户（sssd即Linux用户）不会被cm从ipa同步到本地，从而引起权限不一致或其他问题，如果新加机器没有这些用户才会被同步到新机器sssd

```xml
filter_groups = root,mysql,hadoop,yarn,hdfs,mapred,kms,httpfs,hbase,hive,sentry,spark,solr,sqoop,oozie,hue,flume,impala,llama,postgres,sqoop2,kudu,kafka,accumulo,zookeeper,cloudera-scm,keytrustee
filter_users = root,mysql,cloudera-scm,zookeeper,yarn,hdfs,mapred,kms,httpfs,hbase,hive,sentry,spark,solr,sqoop,oozie,hue,flume,impala,llama,sqoop2,postgres,kudu,kafka,accumulo,keytrustee
```

清理缓存后重启所有(例如查看 id hdfs，可能之前缓存有，并没有创建)

```shell
sss_cache -E 
service sssd restart 
```

​  

② krb5文件修改（刚安装完ipa时，或者配置/etc/resolv.conf ip自动发现后需要改，这里我不太理解dns就还没改，先这样办）

修改/etc/krb5.conf,注释keyring，添加renew\_lifetime，参考配置如下

```xml
#File modified by ipa-client-install

includedir /etc/krb5.conf.d/
[libdefaults]
default_realm = CLOUDERA.LOCAL
dns_lookup_realm = false
rdns = false
dns_canonicalize_hostname = false
dns_lookup_kdc = true
ticket_lifetime = 24h
renew_lifetime = 7d
forwardable = true
udp_preference_limit = 0
default_ccache_name = /tmp/krb5cc_%{uid}
#  default_ccache_name = KEYRING:persistent:%{uid}

[realms]
CLOUDERA.LOCAL = {
kdc = cdplhcm.com.cn:88
master_kdc = cdplhcm.com.cn:88
admin_server = cdplhcm.com.cn:749
kpasswd_server = cdplhcm.com.cn:464
default_domain = cloudera.local
pkinit_anchors = FILE:/var/lib/ipa-client/pki/kdc-ca-bundle.pem
pkinit_pool = FILE:/var/lib/ipa-client/pki/ca-bundle.pem

}

[domain_realm]
.cloudera.local = CLOUDERA.LOCAL
cloudera.local = CLOUDERA.LOCAL
cdplh03.com.cn = CLOUDERA.LOCAL
如果/etc/krb5.conf.d/下面存在kcm_default_ccache文件，需要删除或者注释
```

​  

③ 当ssh ipa用户，默认自动kinit认证，但是cache是kcm开头的证书，此证书访问不到资源，cm不认。需做如下两步设置

```shell
rm /etc/krb5.conf.d/kcm_default_ccache
```

在/etc/profile中添加如下变量，或者在/etc/profile.d/下增加一个ipa.sh文件，内容如下，否则使用ipa用户ssh后kinit还是会使用keyring

```shell
vim /etc/profile.d/ipa.sh
unset KRB5CCNAME
```

​  

④ IPA密码默认90天过期，需要重新生成keytab等文件，可以修改为永不过期，这里也可以修改最大失败次数，重置间隔等配置 ，偷懒就可以适当设大

​  

![image.png](assets/CDP私有云安装(centos7)-4.png)

![image.png](assets/CDP私有云安装(centos7)-5.png)

创建用户后，密码会立即过期，需要使用kinit或者登录webui修改

​  

给用户生成keytab

```shell
ipa-getkeytab -s 主机对应的fqnd -p 用户 -k 用户.keytab -P
```

​  

  

  

​  

## 安装Cloudera Manager

### 安装CM

```bash
yum install -y cloudera-manager-daemons cloudera-manager-server
```

  

### 确认JDBC驱动配置：安装mysql时已配置

### 为CM配置外部数据库初始化

> sudo /opt/cloudera/cm/schema/scm\_prepare\_database.sh <可选参数> <数据库类型> <数据库名称> <数据库用户> <密码>
```xml
# mysql

/opt/cloudera/cm/schema/scm_prepare_database.sh mysql scm scm szk123
```

​  

### 卸载CM

```shell
yum remove cloudera-manager-agent cloudera-manager-daemons cloudera-manager-server cloudera-manager-server-db
rm -rf /opt/cloudrea
rm -rf /var/lib/cloudera-scm-agent/cm_guid
```

### 启动CM

```bash
systemctl start cloudera-scm-server

tail -f /var/log/cloudera-scm-server/cloudera-scm-server.log
# 可以看启动日志，有报错可以先忽略，等等看
```

​  

使用7180端口访问CM

> admin/admin

试用60天

![image.png](assets/CDP私有云安装(centos7)-6.png)

​  

CM启用kerberos（如果不想玩直接忽略下一步）autotls忽略

![image.png](assets/CDP私有云安装(centos7)-7.png)

![image.png](assets/CDP私有云安装(centos7)-8.png)

yum install openldap-clients krb5-workstation krb5-libs

yum install freeipa-client

​  

如下配置项cloudera.internal 是大写的（否则报错）

![image.png](assets/CDP私有云安装(centos7)-9.png)

不建议动以下配置

![image.png](assets/CDP私有云安装(centos7)-10.png)

接下来输入freeipa的那个admin用户密码

![image.png](assets/CDP私有云安装(centos7)-11.png)

![image.png](assets/CDP私有云安装(centos7)-12.png)

freeipa中生成了一个cmadmin用户

![image.png](assets/CDP私有云安装(centos7)-13.png)

  

![image.png](assets/CDP私有云安装(centos7)-14.png)

继续，取名，扫描机器（适用hosts）

![image.png](assets/CDP私有云安装(centos7)-15.png)

![image.png](assets/CDP私有云安装(centos7)-16.png)

添加本地parcels的repo

![image.png](assets/CDP私有云安装(centos7)-17.png)

![image.png](assets/CDP私有云安装(centos7)-18.png)

使用自己已经装好的jdk

![image.png](assets/CDP私有云安装(centos7)-19.png)

  

输入root密码

![image.png](assets/CDP私有云安装(centos7)-20.png)

开始安装agent（注意看报错信息，正常Python3.8.17布置好应该就没问题了，其他情况失败重试一下可能能解决）

![image.png](assets/CDP私有云安装(centos7)-21.png)

![image.png](assets/CDP私有云安装(centos7)-22.png)

接下来开始安装CDP组件

![image.png](assets/CDP私有云安装(centos7)-23.png)

自定义安装

  

  

  

  

  

由于cm需要调用ipa命令，因此需要在cm所在服务器安装ipa相关组件

yum install -y ipa-admintools

如果IPA Server和集群服务共用，需要额外允许获取ipa所在服务器的HTTP凭据，$(hostname)为ipa服务器的主机名，注意为FQDN

如果ipa为单独的服务器，不需要配置此步

​  

注意要把CM在IPA中自动生成的用户加到admins组里，这个用户一般以cmadmin开头

​  

kinit admin

ipa service-allow-retrieve-keytab HTTP/$(hostname) --users=cmadmin-357ad997

​  

​  

通过Cloudera Manager引导安装CDP

访问CM的UI，按照向导安装CDP

​  

使用admin/admin登录到CM，选择60天试用，点击继续

这里如果需要开启Kerberos，则先点击Click here to setup KDC，如果不需要安装，直接点击下一步。

​  

选择相应的Kerberos类型

![image.png](assets/CDP私有云安装(centos7)-24.png)

![image.png](assets/CDP私有云安装(centos7)-25.png)

![image.png](assets/CDP私有云安装(centos7)-26.png)

![image.png](assets/CDP私有云安装(centos7)-27.png)

![image.png](assets/CDP私有云安装(centos7)-28.png)

![image.png](assets/CDP私有云安装(centos7)-29.png)

![image.png](assets/CDP私有云安装(centos7)-30.png)

选择自定义存储库，输入cm的http地址

![image.png](assets/CDP私有云安装(centos7)-31.png)

“CDH and other software”中选择“Parcel Repositories & Network Settings”，点击“ 更多选项”，点击“-”删除其它所有地址，输入CDP Parcel的HTTP地址，点击“保存更改”

![image.png](assets/CDP私有云安装(centos7)-32.png)

![image.png](assets/CDP私有云安装(centos7)-33.png)

进入下一步配置ssh账号密码，确保所有机器的root密码都一致，然后输入root的密码即可。

![image.png](assets/CDP私有云安装(centos7)-34.png)

![image.png](assets/CDP私有云安装(centos7)-35.png)

点击Inspect Network Performance和Inspect Hosts，检查主机

![image.png](assets/CDP私有云安装(centos7)-36.png)

## cdp集群设置安装向导

选择需要安装的服务，根据需要选择，这里选择自定义服务

![image.png](assets/CDP私有云安装(centos7)-37.png)

调整角色分配，建议安装主节点，工作节点的角色划分

参考官方文档

[https://docs.cloudera.com/cdp-private-cloud-base/7.1.9/installation/topics/cdpdc-runtime-cluster-hosts-role-assignments.html](https://docs.cloudera.com/cdp-private-cloud-base/7.1.9/installation/topics/cdpdc-runtime-cluster-hosts-role-assignments.html)

​  

这里选择多个节点可以直接完成Atlas，Hbase，Hive，Hive on Tez，HUE，Knox，Kudu，Oozie，Ozone，Ranger服务的高可用

​  

![image.png](assets/CDP私有云安装(centos7)-38.png)

点击“继续”，进入下一步，配置数据库连接

![image.png](assets/CDP私有云安装(centos7)-39.png)

Ranger相关的初始密码

![image.png](assets/CDP私有云安装(centos7)-40.png)

![image.png](assets/CDP私有云安装(centos7)-41.png)

![image.png](assets/CDP私有云安装(centos7)-42.png)

![image.png](assets/CDP私有云安装(centos7)-43.png)

![image.png](assets/CDP私有云安装(centos7)-44.png)

## 高可用和负载均衡

CDP服务开启高可用

​  

通过界面开启HDFS和YARN的高可用

​  

使用Haproxy给CDP服务配置负载均衡

​  

集群中的某些服务，例如HiveServer2，Impalad，Solr等，需要额外配置一个负载均衡器实现负载均衡，这里以开源haproxy为例，当然也可以使用其他负载均衡器，例如nginx等

​  

操作系统自带haproxy

​  

yum -y install haproxy

chkconfig haproxy on

修改haproxy的配置文件/etc/haproxy/haproxy.cfg，参考配置如下

​  

global

log 127.0.0.1 local2

chroot /var/lib/haproxy

pidfile /var/run/haproxy.pid

maxconn 4000

user haproxy

group haproxy

daemon

stats socket /var/lib/haproxy/stats

​  

defaults

mode http

log global

option httplog

option dontlognull

#option http-server-close

#option forwardfor except 127.0.0.0/8

option redispatch

retries 3

timeout http-request 10s

timeout queue 1m

timeout connect 10s

timeout client 1m

timeout server 1m

timeout http-keep-alive 10s

timeout check 10s

maxconn 3000

​  

\# HAProxy的http状态管理界面

listen stats

bind 0.0.0.0:1080

mode http

option httplog

maxconn 5000

stats refresh 30s

stats uri /stats

​  

listen hiveserver2

bind 0.0.0.0:10010

mode tcp

balance roundrobin

option tcplog

timeout connect 30000

timeout client 30000

timeout server 30000

server real\_server1 cdplh01.com.cn:10000 inter 100 rise 2 fall 5 check

server real\_server2 cdplh02.com.cn:10000 inter 100 rise 2 fall 5 check

server real\_server3 cdplh03.com.cn:10000 inter 100 rise 2 fall 5 check

retries 3

​  

listen impala

bind 0.0.0.0:21000

mode tcp

balance roundrobin

option tcplog

timeout connect 30000

timeout client 30000

timeout server 30000

server real\_server1 cdplh01.com.cn:21000 inter 100 rise 2 fall 5 check

server real\_server2 cdplh02.com.cn:21000 inter 100 rise 2 fall 5 check

server real\_server3 cdplh03.com.cn:21000 inter 100 rise 2 fall 5 check

retries 3

​  

listen impalajdbc

bind 0.0.0.0:21050

mode tcp

option tcplog

balance roundrobin

timeout connect 30000

timeout client 30000

timeout server 30000

server real\_server1 cdplh01.com.cn:21050 inter 100 rise 2 fall 5 check

server real\_server2 cdplh02.com.cn:21050 inter 100 rise 2 fall 5 check

server real\_server3 cdplh03.com.cn:21050 inter 100 rise 2 fall 5 check

retries 3

重启haproxy

​  

systemctl restart haproxy

在HiveServer2，Impala的配置中搜索Load Balancer，填入负载均衡器的地址。

​  

在Kerberos环境保存后CM会自动生成负载均衡器的kerberos票据。如果不配置该步会导致负载均衡器无法使用。

​  

集群服务集成IPA的LDAP

Knox集成IPA

​  

默认使用PAM方式集成

​  

配置HUE集成IPA

​  

搜索Authentication Backend，选择desktop.auth.backend.LdapBackend，desktop.auth.backend.AllowFirstUserDjangoBackend，

​  

LDAP URL请填写IPA服务器的域名 ldap://cdplhcm.com.cn

​  

LDAP 用户名模式ldap\_username\_pattern填写uid=<username>,cn=users,cn=accounts,dc=cloudera,dc=local，其中dc按照实际情况修改。

​  

勾选使用搜索绑定身份验证search\_bind\_authentication

​  

按照实际情况决定是否勾选登录时创建 LDAP 用户

​  

LDAP 搜索基础base\_dn填写dc=cloudera,dc=local，其中dc按照实际情况修改。

​  

LDAP 绑定用户可分辨名称bind\_dn填写uid=ldapbind,cn=users,cn=accounts,dc=cloudera,dc=local,其中dc按照实际情况修改，此用户只需对ldap目录有只读权限，建议新建用户专门用于绑定。

​  

LDAP 绑定密码bind\_password填写上一步绑定用户的密码

​  

LDAP 用户筛选user\_filter填写

​  

全部用户(objectClass=person)

​  

筛选用户(&(objectclass=person)(memberOf=cn=ipausers,cn=groups,cn=accounts,dc=cloudera,dc=local))

​  

LDAP 用户名属性user\_name\_attr填写uid

​  

LDAP 组筛选填写(objectClass=\*)

​  

LDAP 组名称属性填写cn

​  

LDAP 组成员身份属性填写member

​  

配置Hive集成IPA

​  

LDAP URL请填写freeipa服务器的域名 ldap://cdplhcm.com.cn

​  

LDAP BaseDN填写cn=users,cn=accounts,dc=cloudera,dc=local，其中dc按照实际情况修改

​  

在HUE中搜索hive-site.xml,添加配置hive.server2.authentication，值为kerberos

​  

​  

​  

配置Impala集成IPA

​  

在Impala配置中搜索ldap

​  

勾选启用LDAP身份验证

​  

LDAP URL请填写freeipa服务器的域名 ldap://cdplhcm.com.cn

​  

勾选启动LDAP TLS，不然impala daemon无法正常启动

​  

LDAP BaseDN填写cn=users,cn=accounts,dc=cloudera,dc=local

​  

配置Ranger user sync集成IPA

​  

ranger.usersync.source.impl.class配置为org.apache.ranger.ldapusersync.process.LdapUserGroupBuilder

ranger.usersync.ldap.url配置为ldap://cdplhcm.com.cn

ranger.usersync.ldap.binddn 填写绑定用户名

ranger.usersync.ldap.ldapbindpassword    填写绑定密码

ranger.usersync.ldap.user.searchbase配置为cn=users,cn=accounts,dc=cloudera,dc=local

ranger.usersync.ldap.user.objectclass配置为person

ranger.usersync.ldap.user.nameattribute配置为uid  

ranger.usersync.group.searchbase配置为cn=groups,cn=accounts,dc=cloudera,dc=local

ranger.usersync.group.objectclass配置为ipausergroup

ranger.usersync.group.nameattribute配置为cn

​  

ranger.usersync.group.memberattributename配置为member

​  

​  

​  

安装后建议配置修改

关闭Hive ACID

​  

修改Ranger Plugin URL Auth Filesystem Schemes

​  

修改 HMS Token Store

​  

修改HUE的时区

​  

​  

​  

集群可用性测试

HDFS可用性测试

​  

hdfs dfs -ls /

echo aaa > /tmp/test.txt

hdfs dfs -put /tmp/test.txt /tmp

hdfs dfs -get /tmp/test.txt

HIVE可用性测试

​  

LDAP连接

​  

beeline -u "jdbc:hive2://cdplhcm.com.cn:10000/default;" -n admin -p Cloudera@123

Kerberos连接

​  

beeline -u "jdbc:hive2://cdplhcm.com.cn:10000/default;principal=hive/cdplhcm.com.cn@CLOUDERA.LOCAL"

Impala可用性测试

​  

LDAP连接

​  

impala-shell -l -i cdplhcm.com.cn -u admin

Kerberos连接

​  

impala-shell -k -i cdplhcm.com.cn

MapReduce任务

​  

​  

​  

hadoop jar /opt/cloudera/parcels/CDH/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar pi 10 10000

​  

​  

Spark任务

​  

​  

​  

spark-submit --class org.apache.spark.examples.SparkPi --master yarn-client /opt/cloudera/parcels/CDH/jars/spark-examples\_2.11-2.4.8.7.1.9.14-2.jar