# 测试环境3fe+3be升级脚本如下附件。

[Doris集群滚动升级.txt](https://www.yuque.com/attachments/yuque/0/2024/txt/35670500/1713030163679-be7b35de-c840-4331-8ab5-e700dbe68bf4.txt)

# 生产脚本参考如下：

show frontends; -- 查看fe节点

show backends; -- 查看be节点

所有操作均使用hadoop用户执行

**（1）**fe节点元数据备份

登录fe 30.147.81.21，切换到hadoop用户

```shell
cd /opt/doris/apache-doris-2.0.2-bin-x64/fe 
sudo cp -r /opt/doris/apache-doris-2.0.2-bin-x64/fe/doris-meta /opt/doris/apache-doris-2.0.2-bin-x64/fe/doris-meta-20240218
ssh 30.147.81.23 "sudo cp -r /opt/doris/apache-doris-2.0.2-bin-x64/fe/doris-meta /opt/doris/apache-doris-2.0.2-bin-x64/fe/doris-meta-20240218" 
ssh 30.147.81.83 "sudo cp -r /opt/doris/apache-doris-2.0.2-bin-x64/fe/doris-meta /opt/doris/apache-doris-2.0.2-bin-x64/fe/doris-meta-20240218"
```

**（2）**关闭集群副本修复和均衡功能 ###升级过程中会有节点重启，所以可能会触发不必要的集群均衡和副本修复逻辑，先通过以下命令关闭：

```sql
admin set frontend config("disable_balance" = "true"); 
admin set frontend config("disable_colocate_balance" = "true"); 
admin set frontend config("disable_tablet_scheduler" = "true");
```

**（3）**开始升级 先升级 BE，后升级FE，一般而言，Doris 只需要升级 FE 目录下的 /bin 和 /lib 以及 BE 目录下的 /bin 和 /lib 。在 2.0.2 及之后的版本，FE 和 BE 部署路径下新增了 custom\_lib/ 目录（如没有可以手动创建）。custom\_lib/ 目录用于存放一些用户自定义的第三方 jar 包，如 hadoop-lzo-\*.jar，orai18n.jar 等。 这个目录在升级时不需要替换。但是在大版本升级时，可能会有新的特性增加或者老功能的重构， 这些修改可能会需要升级时替换/新增更多的目录来保证所有新功能的可用性， #请大版本升级时仔细关注该版本的 Release-Note，以免出现升级故障

升级BE

**（3.1）**在多副本的前提下，选择一台 BE 节点停止运行，进行灰度升级

```shell
ssh 30.147.81.121 "sudo ls -l /opt/doris/apache-doris-2.0.2-bin-x64/fe/conf/" 
ssh 30.147.81.121 "sudo klist -kt /opt/doris/apache-doris-2.0.2-bin-x64/fe/conf/hive.keytab" 
ssh 30.147.81.121 "sudo kinit -kt /opt/doris/apache-doris-2.0.2-bin-x64/fe/conf/hive.keytab hive/szf-bpl1060921.app.paic.com.cn"
ssh 30.147.81.121 "sudo hdfs dfs -get /tmp/apache-doris-2.0.4-bin-x64.tar.gz /opt/doris/" 
ssh 30.147.81.121 "sudo ls -l /opt/doris/" 
ssh 30.147.81.121 "sudo tar zxvf /opt/doris/apache-doris-2.0.4-bin-x64.tar.gz" 
ssh 30.147.81.121 "sudo mv apache-doris-2.0.4-bin-x64 /opt/doris/" 
```

**（3.2）** 停止服务

```shell
ssh 30.147.81.121 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/be/bin/stop_be.sh" 
```

**(3.3)** 升级应用

```shell
ssh 30.147.81.121 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/bin /opt/doris/apache-doris-2.0.2-bin-x64/be/bin_bak_20240220" 
ssh 30.147.81.121 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/be/bin /opt/doris/apache-doris-2.0.2-bin-x64/be/"
ssh 30.147.81.121 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/lib /opt/doris/apache-doris-2.0.2-bin-x64/be/lib_bak_20240220" 
ssh 30.147.81.121 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/be/lib /opt/doris/apache-doris-2.0.2-bin-x64/be/"
```

**(3.4)** 修改日志目录 （不需要做）

```shell
ssh 30.147.81.121 "sudo mkdir -p /data1/doris/be/" 
ssh 30.147.81.121 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/log /data1/doris/be/" 
ssh 30.147.81.121 "sudo ln -s /data1/doris/be/log /opt/doris/apache-doris-2.0.2-bin-x64/be/log"
```

**(3.5)** 启动be

```shell
ssh 30.147.81.121 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/be/bin/start_be.sh --daemon"
```

**(3.6)** 链接集群，查看该节点信息

show backends\\G

若该 BE 节点 alive 状态为 true，且 Version 值为新版本，则该节点升级成功

**（3.7）** 依次完成其他 BE 节点升级

```shell
admin set frontend config("disable_balance" = "false"); 
admin set frontend config("disable_colocate_balance" = "false"); 
admin set frontend config("disable_tablet_scheduler" = "false");
```
```shell
ssh 30.147.80.154 "sudo ls -l /opt/doris/apache-doris-2.0.2-bin-x64/fe/conf/" 
ssh 30.147.80.154 "sudo klist -kt /opt/doris/apache-doris-2.0.2-bin-x64/fe/conf/hive.keytab" 
ssh 30.147.80.154 "sudo kinit -kt /opt/doris/apache-doris-2.0.2-bin-x64/fe/conf/hive.keytab hive/szf-bpl1060921.app.paic.com.cn" 
ssh 30.147.80.154 "sudo hdfs dfs -get /tmp/apache-doris-2.0.4-bin-x64 /opt/doris/" 
ssh 30.147.80.154 "sudo ls -l /opt/doris/" 
ssh 30.147.80.154 "sudo tar zxvf /opt/doris/apache-doris-2.0.4-bin-x64.tar.gz" 
ssh 30.147.80.154 "sudo mv apache-doris-2.0.4-bin-x64 /opt/doris/" 
ssh 30.147.80.154 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/be/bin/stop_be.sh" 
ssh 30.147.80.154 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/bin /opt/doris/apache-doris-2.0.2-bin-x64/be/bin_bak_20240220" 
ssh 30.147.80.154 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/be/bin /opt/doris/apache-doris-2.0.2-bin-x64/be/" 
ssh 30.147.80.154 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/lib /opt/doris/apache-doris-2.0.2-bin-x64/be/lib_bak_20240220" 
ssh 30.147.80.154 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/be/lib /opt/doris/apache-doris-2.0.2-bin-x64/be/" 
ssh 30.147.80.154 "sudo mkdir -p /data1/doris/be/" ssh 30.147.80.154 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/log /data1/doris/be/" 
ssh 30.147.80.154 "sudo df -h" 
ssh 30.147.80.154 "sudo rm -rf /opt/doris/apache-doris-2.0.4-bin-x64" 
ssh 30.147.80.154 "sudo ln -s /data1/doris/be/log /opt/doris/apache-doris-2.0.2-bin-x64/be/log" ssh 30.147.80.154 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/be/bin/start_be.sh --daemon"
```

​  

```shell
ssh 30.147.81.90 "sudo kinit -kt /opt/doris/apache-doris-2.0.2-bin-x64/fe/conf/hive.keytab hive/szf-bpl1060921.app.paic.com.cn" 
ssh 30.147.81.90 "sudo hdfs dfs -get /tmp/apache-doris-2.0.4-bin-x64 /opt/doris/" 
ssh 30.147.81.90 "sudo ls -l /opt/doris/" ssh 30.147.81.90 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/be/bin/stop_be.sh" 
ssh 30.147.81.90 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/bin /opt/doris/apache-doris-2.0.2-bin-x64/be/bin_bak_20240220" 
ssh 30.147.81.90 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/be/bin /opt/doris/apache-doris-2.0.2-bin-x64/be/" 
ssh 30.147.81.90 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/lib /opt/doris/apache-doris-2.0.2-bin-x64/be/lib_bak_20240220" 
ssh 30.147.81.90 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/be/lib /opt/doris/apache-doris-2.0.2-bin-x64/be/" 
ssh 30.147.81.90 "sudo mkdir -p /data1/doris/be/" ssh 30.147.81.90 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/be/log /data1/doris/be/" 
ssh 30.147.81.90 "sudo df -h" 
ssh 30.147.81.90 "sudo ln -s /data1/doris/be/log /opt/doris/apache-doris-2.0.2-bin-x64/be/log" 
ssh 30.147.81.90 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/be/bin/start_be.sh --daemon" 
ssh 30.147.81.90 "sudo rm -rf /opt/doris/apache-doris-2.0.4-bin-x64"
```

###############其他十个be节点也如此 ##################

​  

**（4）**升级 FE 。提示：先升级非 Master 节点，后升级 Master 节点。

多个 FE 节点情况下，选择一个非 Master 节点进行升级，先停止运行

**（4.1）** 停止服务

```shell
sh ${DORIS_OLD_HOME}/fe/bin/stop_fe.sh 
ssh 30.147.81.83 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin/stop_fe.sh"
```

**（4.2）** 备份文件，重命名 FE 目录下的 /bin，/lib，/mysql\_ssl\_default\_certificate 目录

```shell
ssh 30.147.81.83 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin_bak_20240220" 
ssh 30.147.81.83 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/lib /opt/doris/apache-doris-2.0.2-bin-x64/fe/lib_bak_20240220" 
ssh 30.147.81.83 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/mysql_ssl_default_certificate /opt/doris/apache-doris-2.0.2-bin-x64/fe/mysql_ssl_default_certificate_bak_20240220" 
ssh 30.147.81.83 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/bin /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
ssh 30.147.81.83 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/lib /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
ssh 30.147.81.83 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/mysql_ssl_default_certificate /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
ssh 30.147.81.83 "sudo ls -l /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
```

**（4.3）** 启动fe ssh 30.147.81.83 "

```shell
sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin/start_fe.sh --daemon"
```

**（4.4）** 链接集群，查看该节点信息 show frontends\\G

若该 FE 节点 alive 状态为 true，且 Version 值为新版本，则该节点升级成功 ###依次完成其他 FE 节点升级，最后完成 Master 节点的升级

升级 30.147.81.21

```shell
sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin/stop_fe.sh 
sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin_bak_20240220 
sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/lib /opt/doris/apache-doris-2.0.2-bin-x64/fe/lib_bak_20240220 
sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/mysql_ssl_default_certificate /opt/doris/apache-doris-2.0.2-bin-x64/fe/mysql_ssl_default_certificate_bak_20240220 
sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/bin /opt/doris/apache-doris-2.0.2-bin-x64/fe/ 
sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/lib /opt/doris/apache-doris-2.0.2-bin-x64/fe/ 
sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/mysql_ssl_default_certificate /opt/doris/apache-doris-2.0.2-bin-x64/fe/ 
sudo ls -l /opt/doris/apache-doris-2.0.2-bin-x64/fe/ 
sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin/start_fe.sh --daemon
```

​  

```shell
ssh 30.147.81.23 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin/stop_fe.sh" 
ssh 30.147.81.23 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin_bak_20240220" 
ssh 30.147.81.23 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/lib /opt/doris/apache-doris-2.0.2-bin-x64/fe/lib_bak_20240220" 
ssh 30.147.81.23 "sudo mv /opt/doris/apache-doris-2.0.2-bin-x64/fe/mysql_ssl_default_certificate /opt/doris/apache-doris-2.0.2-bin-x64/fe/mysql_ssl_default_certificate_bak_20240220" 
ssh 30.147.81.23 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/bin /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
ssh 30.147.81.23 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/lib /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
ssh 30.147.81.23 "sudo cp -r /opt/doris/apache-doris-2.0.4-bin-x64/fe/mysql_ssl_default_certificate /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
ssh 30.147.81.23 "sudo ls -l /opt/doris/apache-doris-2.0.2-bin-x64/fe/" 
ssh 30.147.81.23 "sudo sh /opt/doris/apache-doris-2.0.2-bin-x64/fe/bin/start_fe.sh --daemon"
```

​  

打开集群副本修复和均衡功能 ，升级完成，并且所有 BE 节点状态变为 Alive 后，打开集群副本修复和均衡功能：

```sql
admin set frontend config("disable_balance" = "false"); 
admin set frontend config("disable_colocate_balance" = "false"); 
admin set frontend config("disable_tablet_scheduler" = "false");
show proc '/cluster_health/tablet_health';
```

  

  

# doris升级注意事项

升级前要把以下参数（副本均衡）置为true，升级后记得设置回false。

```sql
admin set frontend config("disable_balance" = "true");
admin set frontend config("disable_colocate_balance" = "true");
admin set frontend config("disable_tablet_scheduler" = "true");
```

升级后不置为true，很可能造成副本丢失，版本不一致问题，进而没法读取数据，作业挂掉。

```sql
-- 查看集群tablet均衡状态，主要看pending状态的数量是否过多或者是否长时间不变
show proc '/cluster_balance/'; 
-- 查看被挂起的tablet，查询超时、insert超时的事务引起的，调低超时时间，或者手动kill事务可解决。
show proc '/cluster_balance/pending_tablets'; 
-- 查看tablet状态是否正常，由pending的来查。 
show proc '/diagnose/cluster_balance';有warning、error要注意。第三个感觉没啥影响。
```

![306cb893d9e7e9745fc3ebcd4da1625.jpg](assets/Doris升级操作(3fe+12be)-1.jpeg)

手动kill掉大事务，或者等待大事务超时被kill掉之后：

发现有个error，但是没啥影响。（问题待排查）

![8afb4abb98a24b9ab96aae820641960.jpg](assets/Doris升级操作(3fe+12be)-2.jpeg)