### 基本

-   实际基于linux环境，仅有runtime环境，轻量化，不会虚拟化硬件，CS架构，docker后台守护进程
-   使用docker安装的服务，实际是运行在docker环境中，在服务器的系统中找不到，得进入docker的环境下查看
-   docker 生态由 镜像，容器，仓库 组成，从镜像创建容器，将服务打包成为镜像，从镜像创建容器执行实际服务，镜像层都是只读的，创建容器后 最上面再添加一层，也叫做容器层。
-   镜像使用 unionfilesystem实现，每次都是层层加载，镜像的最底层是bootfs，好处是可以共享文件
-   容器通过commit，提交成为新的镜像，也可以通过docker file的方式，后者需要执行编译
-   虚悬镜像，指的是仓库名，标签名都是none，docker file中的编辑没有指定会导致该情况
-   使用-d后台执行，但是有些服务需要 有个前台交互，不然会自我判断为未被使用，kill掉
-   部分容器执行的时候需要COMMADN参数，比如，centos，这些镜像的 Dockerfile 通常没有设置默认的 `CMD` 或 `ENTRYPOINT`。若直接运行 `docker run centos`，容器会立即退出（因为没有需要执行的命令）。因此需要手动指定 `/bin/bash`，让容器启动后进入交互模式。
-   docker部署数据库的历史争议，容器虚拟化层可能引入I/O性能损耗（尤其是写密集型场景），可以通过-V，容器默认共享宿主机资源（CPU、内存、磁盘I/O），可能因资源竞争导致性能不稳定，支持通过 `--cpus`、`--memory` 等参数限制资源，但需手动配置，容器网络虚拟化可能引入额外延迟，且跨节点通信复杂度高，Docker的Overlay网络和Kubernetes的Service网络已成熟，容器逃逸、未授权访问等风险。 已支持用户命名空间（User Namespace）、Seccomp、AppArmor等安全特性。

##### 常见命令

-   完整的镜像由 镜像名称+Tag 组成,pull的时候不指定默认是latest
-   使用run将镜像创建容器并执行，同时可以使用相应的参数，指定运行的方式

-   \-it 指定 以交互模式，执行，-d 以 后台守护的方式执行
-   \-p 指定映射的端口号，-P 随机分配端口映射
-   \-name 指定容器的名称
-   COMMAND 指令，设置了进入容器后的执行命令，会覆盖dockerfile中的 CMD指令，一般在进入系统等基本容器的时候使用

-   退出容器的方式 有 退出停止(exit)，不停止退出(ctrl+P+Q)
-   启动容器start，停止 stop，重启 restart, 强制停止kill，删除 rm，查看inspect
-   进入正在运行的容器，attach，直接进入，exec 启动新的终端后进入，且退出不会终止容器

##### 内外交互

-   使用cp，复制文件
-   可以使用 import，export 命令，export 将容器转成tar文件，反之同理
-   \-v 设置挂载，相当于备份数据，容器和外部系统 共享数据，加载外部配置文件也是通过-V

### 使用场景

##### docker file

-   本质是一个脚本，通过编译build，构建成为镜像，两种语法格式，exec和shell
-   每次RUN指令都会创建一个新的镜像，然后提交，一层层累积
-   RUN，CMD，ENTRYPOINT指令，RUN指令是在构建镜像时执行命令，比如安装软件包、创建目录等，这些操作会被记录到镜像的层中。而CMD则是设置容器启动时默认执行的命令，用户可以在运行容器时覆盖它，ENTRYPOINT则是配置容器启动时的执行命令，通常和CMD一起使用，这时CMD可以实现传参的效果
-   使用volume的时候，指定添加数据卷，会在默认路径下创建
-   将服务打包成相关的镜像，就是上传包，编辑file文件，build后得到

##### 网络

-   docker启动后，在网络层模拟网桥，启动docker0网络服务
-   每次启动docker容器，都会被分配一个IP地址，所以服务的IP地址会出现改变
-   docker默认的网络策略为 host，bridge，none,container，也可以自己创建网络组，在该网路组中可以实现根据服务名称联通不同的服务，默认的bridge策略不可以，none模式下只有回环地址能使用，所有的网络策略都需要自己配置，container是指定一个运行的容器作为父网络，共用同样的IP地址和端口
-   通常使用的是bridge，每个docker服务都和docker层面的网桥通讯，当使用host的时候，直接使用主机的网络，此时端口映射无意义
-   Docker 的集群部署能力主要通过 Docker Swarm 或 Kubernetes 实现，而 `overlay` 网络是 Docker 原生支持的跨节点网络方案，不需要单独下载镜像，它是 Docker 引擎内置的功能。
-   普通的Docker Compose用于单机部署，而要在集群中使用overlay网络，必须通过Docker Swarm模式，并且需要在Compose文件中指定网络类型为overlay，同时使用\`docker stack deploy\`命令部署。

##### Compose

-   管理多个docker服务，确定服务间的调用关系，本质是一个yaml文件，将服务串通变成工程，可以做到一键起停
-   不负责构建镜像，只启动容器，但是通过 `build` 字段指向 `Dockerfile` 路径，也能触发镜像构建
-   对于一个compose中指定的服务，默认生成一个网路组，每个服务的DNS名称就是服务的名称
-   用于单机部署的情况

##### 监控工具

-   web端Portainer
-   监控链：Cadvisor(采集)+InfluxDB(存储)+Granfana(展示)