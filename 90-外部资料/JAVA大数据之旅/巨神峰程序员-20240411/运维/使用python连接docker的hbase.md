# 使用python连接hbase

## 1\. 安装`docker`镜像

  

首先启动`docker`，我们这里仍然是用的`wsl2`启动`docker`

  

```shell
root@LAPTOP-D9UA419L:~# service docker start
```

查找镜像

```shell
root@LAPTOP-D9UA419L:~# docker search hbase
NAME                                 DESCRIPTION                                     STARS     OFFICIAL   AUTOMATED
gchq/stroom-stats-hbase              An instance of hbase pre-loaded with the str…   1
aaionap/hbase                        AAI Hbase                                       4
dajobe/hbase                         HBase 2.1.2 in Docker                           94
imagenarium/hbase                                                                    3
harisekhon/hbase                     Apache HBase, opens shell - pseudo-distribut…   118                  [OK]
banno/hbase-standalone               HBase master running in standalone mode on U…   17                   [OK]
gradiant/hbase-base                  Hbase small footprint Image (Alpine based)      4                    [OK]
zenoss/hbase                         HBase image for Zenoss 5.0                      10
boostport/hbase-phoenix-all-in-one   HBase with phoenix and the phoenix query ser…   14                   [OK]
imagenarium/hbase-regionserver                                                       1
bde2020/hbase-regionserver           Regionserver Docker image for Apache HBase.     4                    [OK]
dwpdigital/hbase-table-provisioner   Docker image containing Hbase-Table-Provisio…   0
imagenarium/hbase-master                                                             1
harisekhon/hbase-dev                 Apache HBase + dev tools, github repos, pseu…   9                    [OK]
bde2020/hbase-master                 Master docker image for Apache HBase.           2                    [OK]
newnius/hbase                        Setup a HBase cluster in a totally distribut…   1                    [OK]
pierrezemb/hbase-docker              hbase in docker                                 1                    [OK]
blueskyareahm/hbase-zookeeper                                                        0
pilchard/hbase                       Hbase 1.2.0 (CDH 5.11) with openjdk-1.8         1                    [OK]
cellos/hbase                         HBase on top of Alpine Linux                    0
openiamdocker/hbase                  Wrapper around hbase                            0
nerdammer/hbase                      HBase pseudo-distributed (configured for loc…   25                   [OK]
bde2020/hbase-standalone             Standalone Apache HBase docker image. Suitab…   6                    [OK]
blueskyareahm/hbase-base                                                             1
stellargraph/hbase-master                                                            1
```

  

我们这里选择`star`最多的，直接安装

```shell
root@LAPTOP-D9UA419L:~# docker pull harisekhon/hbase:1.3
1.3: Pulling from harisekhon/hbase
cd784148e348: Already exists
9375f15adfac: Already exists
bd1652f47081: Already exists
14b70f0f559e: Pull complete
e76e1b28b55c: Pull complete
917179dcefda: Pull complete
4adad1f1ef2b: Pull complete
209dd8366d03: Pull complete
5e9899213c00: Pull complete
Digest: sha256:c4e4aba496437bb5edcb6d94c9dc0283871c3710757642bc5b6790bbf6ac45ed
Status: Downloaded newer image for harisekhon/hbase:1.3
docker.io/harisekhon/hbase:1.3
```

  

## 2\. 运行hbase

```shell
oot@LAPTOP-D9UA419L:~# docker run -d --name hbase001 -P harisekhon/hbase:1.3
4efd2f758b53e6ff663b957e76df32904fa207e78491619bde66abd86bcbb399
```

  

注意：因为只是一个`demo`，所以并没有指定端口进行映射，而是**随机端口映射，端口映射情况可以通过容器进行查看**

```shell
root@LAPTOP-D9UA419L:~# docker ps -a
CONTAINER ID   IMAGE                                 COMMAND                  CREATED         STATUS
   PORTS

                                                         NAMES
4efd2f758b53   harisekhon/hbase:1.3                  "/entrypoint.sh"         5 seconds ago   Up 3 seconds
   0.0.0.0:32776->2181/tcp, :::32776->2181/tcp, 0.0.0.0:32775->8080/tcp, :::32775->8080/tcp, 0.0.0.0:32774->8085/tcp, :::32774->8085/tcp, 0.0.0.0:32773->9090/tcp, :::32773->9090/tcp, 0.0.0.0:32772->9095/tcp, :::32772->9095/tcp, 0.0.0.0:32771->16000/tcp, :::32771->16000/tcp, 0.0.0.0:32770->16010/tcp, :::32770->16010/tcp, 0.0.0.0:32769->16201/tcp, :::32769->16201/tcp, 0.0.0.0:32768->16301/tcp, :::32768->16301/tcp   hbase001
```

  

这里我们可以看到，`9090`端口被映射成`32773`，这也是我们之后连接`hbase` 需要用到的端口，当然我们也可以在启动`hbase`时就直接指定端口

```shell
docker run -d \
    -p 41189:41189 \
    -p 2181:2181 \
    -p 60000:60000 \
    -p 60010:60010 \
    -p 60020:60020 \
    -p 60030:60030 \
    -p 9091:9090 \
    --name hbase001 \
    harisekhon/hbase:1.3
```

  

这样我们就会将容器的端口映射到本机指定的端口了。

## 3\. 运行hbase

接下来我们就可以进入到容器中

```shell
root@LAPTOP-D9UA419L:~# docker exec -it hbase001 /bin/bash
```

  

然后输入`hbase shell`连接到`hbase client`

```shell
bash-4.4# hbase shell
2024-04-09 13:53:58,097 WARN  [main] util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
HBase Shell; enter 'help<RETURN>' for list of supported commands.
Type "exit<RETURN>" to leave the HBase Shell
Version 1.3.2, r1bedb5bfbb5a99067e7bc54718c3124f632b6e17, Mon Mar 19 18:47:19 UTC 2018

hbase(main):001:0>
```

### 3.1. 查看hbase所有表

```shell
hbase(main):001:0> list
TABLE
0 row(s) in 0.2040 seconds

=> []
```

### 3.2. 查看所有namespace

```shell
hbase(main):002:0> list_namespace
NAMESPACE
default
hbase
2 row(s) in 0.0400 seconds
```

### 3.3. 新建namespace

```shell
hbase(main):003:0> create_namespace 'test'
0 row(s) in 0.8660 seconds

hbase(main):004:0> list_namespace
NAMESPACE
default
hbase
test
3 row(s) in 0.0090 seconds
```

### 3.4. 查看指定namespace下所有表

```shell
hbase(main):005:0> list_namespace_tables 'test'
TABLE
0 row(s) in 0.0140 seconds
```

### 3.5. 在指定namespace下创建新表，指定列族

```shell
hbase(main):006:0> create 'test:student', 'cf1'
0 row(s) in 1.2630 seconds

=> Hbase::Table - test:student
hbase(main):007:0> list
TABLE
test:student
1 row(s) in 0.0050 seconds

=> ["test:student"]
```

## 4\. 使用python连接hbase

我们可以通过`[happybase](https://happybase.readthedocs.io/en/latest/)`来连接hbase\`，并对其进行增删改查操作。

### 4.1. 安装`happybase`

```powershell
(python38) PS E:\Projects\Python\hbase_demo> pip install happybase -i https://pypi.tuna.tsinghua.edu.cn/simple/
Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple/
Collecting happybase
  Using cached happybase-1.2.0-py2.py3-none-any.whl
Requirement already satisfied: six in d:\softwares\conda\envs\python38\lib\site-packages (from happybase) (1.16.0)
Collecting thriftpy2>=0.4
  Using cached thriftpy2-0.4.20-py2.py3-none-any.whl
Collecting ply<4.0,>=3.4
  Using cached https://pypi.tuna.tsinghua.edu.cn/packages/a3/58/35da89ee790598a0700ea49b2a66594140f44dec458c07e8e3d4979137fc/ply-3.11-py2.py3-none-any.whl (49 kB)
Installing collected packages: ply, thriftpy2, happybase
Successfully installed happybase-1.2.0 ply-3.11 thriftpy2-0.4.20
```

### 4.2. 编写python代码

我们尝试连接`hbase`，并且向新建的`test:student`表中插入数据，代码如下

```python
import happybase

class HbaseUtils:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        self.conn = happybase.Connection(self.host, self.port)
        self.conn.open()
        print("Connected to HBase Server")

    def put(self, table_name, data):
        if table_name not in self.conn.tables():
            print("Table not found")
            return
        row_key = data.get('rowKey')
        row_value = data.get('rowValue')
        table = self.conn.table(table_name)
        table.put(row_key, row_value)
        print("Put data success")

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    hbase = HbaseUtils("localhost", 32773)
    hbase.connect()
    data = {'rowKey': b'a', 'rowValue': {b'cf1:name': b'thomas', b'cf1:age': b'21'}}
    hbase.put(b'test:student', data)
    hbase.close()
```

运行代码

```plain
D:\softwares\conda\envs\python38\python.exe E:\Projects\Python\hbase_demo\save.py 
Connected to HBase Server
Put data success
```

我们回到`hbase`，看看数据是否成功插入

```shell
hbase(main):002:0> scan 'test:student'
ROW                             COLUMN+CELL
 a                              column=cf1:age, timestamp=1712673737989, value=21
 a                              column=cf1:name, timestamp=1712673737989, value=thomas
1 row(s) in 0.0820 seconds

hbase(main):003:0> get 'test:student', 'a'
COLUMN                          CELL
 cf1:age                        timestamp=1712673737989, value=21
 cf1:name                       timestamp=1712673737989, value=thomas
1 row(s) in 0.0200 seconds
```

数据已经成功插入，代码跑通~