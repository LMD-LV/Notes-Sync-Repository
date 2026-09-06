# 一、背景：

工作中常被内网限制，想要安装某个组件，尝尝需要拷贝进内网后，逐一上传或分发，将其中一台服务器配置为仓库源并启用http服务，其他机器通过配置yum repo仓库来访问下载组件，这样就可以更好的管理组件安装包，用到时就可以yum 操作。

# 二、操作

## httpd服务

[Linux——搭建Apache(httpd)服务器 - 王智刚 - 博客园 (cnblogs.com)](https://www.cnblogs.com/wzgwzg/p/15587199.html)

-   http：超文本传输协议，通过线路以明文形式发送，默认使用80端口/TCP
-   https：经TLS/SSL安全加密的超文本传输协议，默认使用443端口/TCP

配置文件

| 配置文件 | 存放位置 |
| --- | --- |
| 服务目录 | /etc/httpd |
| 主配置文件 | /etc/httpd/conf/httpd.conf |
| 虚拟主机的配置文件目录 | /etc/httpd/conf.d |
| 基于用户的配置文件 | /etc/httpd/conf.d/userdir.conf |
| 日志文件目录 | /etc/httpd/logs |
| 默认的网站数据目录 | /var/www/html |

主配置文件：/etc/httpd/conf/httpd.conf

| 参数 | 作用 | 参数 | 作用 |
| --- | --- | --- | --- |
| ServerRoot | 服务目录 | ServerName | 网站服务器的域名 |
| Listen | 监听的IP地址与端口号 | DocumentRoot | 默认网站数据目录 |
| User | 运行服务的用户 | Directory | 文件目录的权限 |
| Group | 运行服务的用户组 | DirectoryIndex | 默认的索引页页面 |
| ServerAdmin | 管理员邮箱 | ErrorLog | 错误日志文件 |

### 搭建简单的httpd服务

**Server端**配置：

```bash
# 1、安装httpd服务
[root@server ~]# yum -y install httpd

# 2、配置防火墙（关闭防火墙的无需操作）
[root@server ~]# firewall-cmd --permanent --add-service=http
[root@server ~]# firewall-cmd --reload

# 3、开启服务
[root@server ~]# systemctl restart httpd
[root@server ~]# systemctl enable httpd
```

**Client端**访问：访问的是/var/www/html下的文件

```bash
# 有图形化
[root@client ~]# firefox http://192.168.100.10
# 没有图形化
[root@client ~]# curl http://192.168.100.10
```

## yum源配置hhtpd搭建的仓库

[yum的repo文件详解、以及epel简介、yum源的更换 - nineep - 博客园 (cnblogs.com)](https://www.cnblogs.com/nineep/p/6795692.html)

进入到 /etc/yum.repos.d目录下

新增 xxxxx.repo文件,如下是一个cdp仓库的例子

```bash
[cloudera_manager]
name=Cloudera_Manager_cm7.11.3.16
baseurl=http://30.236.160.81/cm7.11.3
gpgcheck=0
enabled=1
```

配置完成后运行 yum repolist 查看是否多出来了cloudera-manager这个仓库

把需要的文件放入 httpd目录

mv ./cm7.11.3 /var/www/html/

cd /var/www/html//cm7.11.3

createrepo . 使用这个命令生成rpm元数据

会在当前目录下生成一个repodata目录

## 访问使用仓库

配置了cloudera-manager仓库的机器执行例子

```bash
yum -y install cloudera-manager-server 
```