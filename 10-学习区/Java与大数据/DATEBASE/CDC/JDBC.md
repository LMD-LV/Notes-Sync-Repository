---
tags: [Java与大数据, 概念]
created: 2026-08-02
domain: Java与大数据
source: 个人总结
---

JDBC：Java Database Connectivity，它是代表一组独立于任何数据库管理系统（DBMS）的API，声明在java.sql与javax.sql包中，是SUN(现在Oracle)提供的一组接口规范。由各个数据库厂商来提供实现类，这些实现类的集合构成了数据库驱动jar。

使用步骤:

#### 1.2.1注册驱动

三部曲：

（1）将DBMS数据库管理软件的驱动jar拷贝到项目的libs目录中

例如：mysql-connector-java-5.1.36-bin.jar

（2）把驱动jar添加到项目的build path中

（3）将驱动类加载到内存中

Class.forName("com.mysql.jdbc.Driver");

#### 1.2.2获取Connection连接对象

Connection conn = DriverManager.getConnection(url,username,password);

mysql的url：jdbc:mysql://localhost:3306/数据库名?参数名\=参数值

#### 1.2.3执行sql并处理结果

（1）编写sql

（2）创建Statement或PreparedStatement对象

（3）执行sql

增删改：调用executeUpate方法

查询：调用executeQuery方法

（4）处理结果

增删改：返回的是整数值

查询：返回ResultSet结果，需要使用next()和getXxx()结合进行遍历

​  

相关的API：

1、DriverManager：驱动管理类

2、Connection：代表数据库连接

3、Statement和PreparedStatement：用来执行sql

执行增、删、改：int executeUpate()

执行查询：ResultSet executeQuery()

## **什么是数据库连池**

连接对象的缓冲区。负责申请，分配管理，释放连接的操作。

不使用数据库连接池，每次都通过DriverManager获取新连接，用完直接抛弃断开，连接的利用率太低，太浪费。 对于数据库服务器来说，压力太大了。我们数据库服务器和Java程序对连接数也无法控制，很容易导致数据库服务器崩溃。

我们就希望能管理连接。我们可以建立一个连接池，这个池中可以容纳一定数量的连接对象，一开始，我们可以先替用户先创建好一些连接对象，等用户要拿连接对象时，就直接从池中拿，不用新建了，这样也可以节省时间。然后用户用完后，放回去，别人可以接着用。可以提高连接的使用率。当池中的现有的连接都用完了，那么连接池可以向服务器申请新的连接放到池中。直到池中的连接达到“最大连接数”，就不能在申请新的连接了，如果没有拿到连接的用户只能等待。

JDBC,DBCP,C3P0,Proxool,BoneCP,Druid

​  

​  

## JDBC概述

​  

JDBC：Java Database Connectivity，它是代表一组独立于任何数据库管理系统（DBMS）的API，声明在java.sql与javax.sql包中，是SUN(现在Oracle)提供的一组接口规范。由各个数据库厂商来提供实现类，这些实现类的集合构成了数据库驱动jar。

​  

#### JDBC使用步骤

使用步骤：

#### 1.2.1注册驱动

三部曲：

（1）将DBMS数据库管理软件的驱动jar拷贝到项目的libs目录中

例如：mysql-connector-java-5.1.36-bin.jar

（2）把驱动jar添加到项目的build path中

（3）将驱动类加载到内存中

Class.forName("com.mysql.jdbc.Driver");

#### 1.2.2获取Connection连接对象

Connection conn = DriverManager.getConnection(url,username,password);

mysql的url：jdbc:mysql://localhost:3306/数据库名?参数名\=参数值

#### 1.2.3执行sql并处理结果

（1）编写sql

（2）创建Statement或PreparedStatement对象

（3）执行sql

增删改：调用executeUpate方法

查询：调用executeQuery方法

（4）处理结果

增删改：返回的是整数值

查询：返回ResultSet结果，需要使用next()和getXxx()结合进行遍历

#### 1.2.4释放连接等

相关的API：

1、DriverManager：驱动管理类

2、Connection：代表数据库连接

3、Statement和PreparedStatement：用来执行sql

执行增、删、改：int executeUpate()

执行查询：ResultSet executeQuery()

4、如何遍历ResultSet ？

（1）boolean next()：判断是否还有下一行

（2）getString(字段名或序号),getInt(字段名或序号),getObject(字段名或序号)

​  

​  

### **1.2.5** **增，删，改 代码演示**

public class TestJDBC {

public static void main(String[] args) throws ClassNotFoundException, SQLException {

//1、注册驱动

//(1)方式一：Class.forName("驱动类的全名称")

Class.forName("com.mysql.jdbc.Driver");

// (2)创建驱动类的对象

// new com.mysql.jdbc.Driver();//硬编码

//(3)通过DriverManager注册驱动

// DriverManager.registerDriver(new com.mysql.jdbc.Driver());//硬编码

//2、获取连接，连接数据库

//TCP/IP协议编程，需要服务器的IP地址和端口号

//mysql的url格式：jdbc协议:子协议://主机名:端口号/要连接的数据库名

String url = "jdbc:mysql://localhost:3306/test";//其中test是数据库名

String user = "root";

String password = "123456";

Connection conn = DriverManager.getConnection(url, user, password);

//3、执行sql

//添加一个部门到数据库的t\_department表中

//(1)编写sql

String sql = "insert into t\_department values(null,'计算部2','计算钞票2')";

/\*

\* 回忆： TCP/IP程序时

\* Socket代表连接

\* socket.getOutputStream()来发送数据，

\* socket.getInputStream()来接收数据

\*

\* 可以把Connection比喻成Socket

\* 把Statement比喻成OutputStream

\*/

//(2)获取Statement对象

Statement st = conn.createStatement();

//(3)执行sql

int len = st.executeUpdate(sql);

//(4)处理结果

System.out.println(len>0?"成功":"失败");

//4、关闭

st.close();

conn.close();

}

}

### **1.2.6** **查询代码演示**

public class TestSelect {

public static void main(String[] args) throws Exception{

// 1、注册驱动

Class.forName("com.mysql.jdbc.Driver");

​  

// 2、连接数据库

Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/test", "root", "123456");

​  

// 3、执行sql

String sql = "SELECT \* FROM t\_department";

Statement st = conn.createStatement();

ResultSet rs = st.executeQuery(sql);//ResultSet看成InputStream

while(rs.next()){//next()表示是否还有下一行

Object did = rs.getObject(1);//获取第n列的值

Object dname = rs.getObject(2);

Object desc = rs.getObject(3);

/\*

int did = rs.getInt("did");//也可以根据列名称，并且可以按照数据类型获取

String dname = rs.getString("dname");

String desc = rs.getString("description");

\*/

System.out.println(did +"\\t" + dname + "\\t"+ desc);

}

​  

// 4、关闭

rs.close();

st.close();

conn.close();

}

​  

​  

​  

​  

# **使用****PreparedStatement****处理****CRUD**

## **2****.1** **通过****PreparedStatement****来解决****Statement****的问题**

Statement的问题：通过PreparedStatement来代替

#### 2.2.1 sql拼接问题

String sql = "insert into t\_employee(ename,tel,gender,salary) values('" + ename + "','" + tel + "','" + gender + "'," + salary +")";

Statement st = conn.createStatement();

int len = st.executeUpdate(sql);

会发现以上sql语句在拼接时，非常的不好用

#### 2.2.2 sql注入问题

String sql = "SELECT \* FROM t\_employee where ename='" + ename + "'";

//如果我此时从键盘输入ename值的时候，输入：张三' or '1'= '1

//结果会把所有数据都查询出来

Statement st = conn.createStatement();

ResultSet rs = st.executeQuery(sql);

PreparedStatement解决问题：

#### 2.2.3避免sql拼接

String sql = "insert into t\_employee(ename,tel,gender,salary) values(?,?,?,?)";

PreparedStatement pst = conn.prepareStatement(sql);//这里要传带？的sql，然后mysql端就会对这个sql进行预编译

//设置？的具体值

/\*pst.setString(1, ename);

pst.setString(2, tel);

pst.setString(3, gender);

pst.setDouble(4, salary);\*/

pst.setObject(1, ename);

pst.setObject(2, tel);

pst.setObject(3, gender);

pst.setObject(4, salary);

int len = pst.executeUpdate();//此处不能传sql

System.out.println(len);

#### 2.2.4不会有sql注入

String sql = "SELECT \* FROM t\_employee where ename=?";

//即使输入'张三' or '1'= '1'也没问题

PreparedStatement pst = conn.prepareStatement(sql);

//中间加入设置？的值

pst.setObject(1, ename);

ResultSet rs = pst.executeQuery();

​  

​  

#### 2.2 批处理

/\*

\* 批处理：

\* 批量处理sql

\*

\* 例如：

\* （1）订单明细表的多条记录的添加

\* （2）批量添加模拟数据

\* ...

\*

\* 不用批处理，和用批处理有什么不同？

\* 批处理的效率很多

\*

\* 如何进行批处理操作？

\* （1）在url中要加一个参数

\* rewriteBatchedStatements=true

\* 那么我们的url就变成了 jdbc:mysql://localhost:3306/test?rewriteBatchedStatements=true

\* 这里的?，表示?后面是客户端给服务器端传的参数，多个参数直接使用&分割

\* （2）调用方法不同

\* pst.addBatch();

\* int[] all = pst.executeBatch();

\*

\* 注意：如果批量添加时，insert使用values,不要使用value

\*/

public class TestBatch {

public static void main(String[] args) throws Exception{

long start = System.currentTimeMillis();

//例如：在部门表t\_department中添加1000条模拟数据

//1、注册驱动

Class.forName("com.mysql.jdbc.Driver");

//2、获取连接

Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/test?rewriteBatchedStatements=true", "root", "123456");

//3、执行sql

String sql = "insert into t\_department values(null,?,?)";

PreparedStatement pst = conn.prepareStatement(sql);

//设置？的值

for (int i = 1; i <=1000; i++) {

pst.setObject(1, "模拟部门"+i);

pst.setObject(2, "模拟部门的简介"+i);

pst.addBatch();//添加到批处理一组操作中，攒一块处理

/\* if(i % 500 == 0){//有时候也攒一部分，执行一部分

//2.执行

pst.executeBatch();

//3.清空

pst.clearBatch();

}\*/

}

pst.executeBatch();

//4、关闭

pst.close();

conn.close();

long end = System.currentTimeMillis();

System.out.println("耗时：" + (end - start));//耗时：821

}

}

​  

​  

## **​****事务**

/\*

\* mysql默认每一个连接是自动提交事务的。

\* 那么当我们在JDBC这段，如果有多条语句想要组成一个事务一起执行的话，那么在JDBC这边怎么设置手动提交事务呢？

\* (1)在执行之前，设置手动提交事务

\* Connection的对象.setAutoCommit(false)

\* (2)成功：

\* Connection的对象.commit();

\* 失败：

\* Connection的对象.rollback();

\*

\* 补充说明：

\* 为了大家养成要的习惯，在关闭Connection的对象之前，把连接对象设置回自动提交

\* (3)Connection的对象.setAutoCommit(true)

\*

\* 因为我们现在的连接是建立新的连接，那么如果没有还原为自动提交，没有影响。

\* 但是我们后面实际开发中，每次获取的连接，不一定是新的连接，而是从连接池中获取的旧的连接，而且你关闭也不是真关闭，

\* 而是还给连接池，供别人接着用。以防别人拿到后，以为是自动提交的，而没有commit，最终数据没有成功。

\*/

public class TestTransaction {

public static void main(String[] args) throws Exception{

/\*

\* 一般涉及到事务处理的话，那么业务逻辑都会比较复杂。

\* 例如：购物车结算时：

\* （1）在订单表中添加一条记录

\* （2）在订单明细表中添加多条订单明细的记录（表示该订单买了什么东西）

\* （3）修改商品表的销量和库存量

\* ...

\* 那么我们今天为了大家关注事务的操作，而不会因为复杂的业务逻辑的影响导致我们的理解，那么我们这里故意

\* 用两条修改语句来模拟组成一个简单的事务。

\* update t\_department set description = 'xx' where did = 2;

\* update t\_department set description = 'yy' where did = 3;

\*

\* 我希望这两天语句要么一起成功，要么一起回滚

\* 为了制造失败，我在

pst = conn.prepareStatement(sql2);

这行代码的上一行加上

System.out.println(1/0);

\*/

//1、注册驱动

Class.forName("com.mysql.jdbc.Driver");

//2、获取连接

Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/test", "root", "123456");

//设置手动提交事务

conn.setAutoCommit(false);

//3、执行sql

String sql1 = "update t\_department set description = 'xx' where did = 2";

String sql2 = "update t\_department set description = 'yy' did = 3";//这是错的

//使用prepareStatement的sql也可以不带?

PreparedStatement pst = null;

try {

pst = conn.prepareStatement(sql1);

int len = pst.executeUpdate();

System.out.println("第一条：" + (len>0?"成功":"失败"));

pst = conn.prepareStatement(sql2);

len = pst.executeUpdate();

System.out.println("第二条：" + (len>0?"成功":"失败"));

//都成功了，就提交事务

System.out.println("提交");

conn.commit();

} catch (Exception e) {

System.out.println("回滚");

//失败要回滚

conn.rollback();

}

//4、关闭

pst.close();

conn.setAutoCommit(true);//还原为自动提交

conn.close();

}

}

​  

​  

# 数据库连接池

  

## **4.****1****什么是数据库连池**

连接对象的缓冲区。负责申请，分配管理，释放连接的操作。

## **4.2****为什么要使用数据库连接池**

不使用数据库连接池，每次都通过DriverManager获取新连接，用完直接抛弃断开，连接的利用率太低，太浪费。 对于数据库服务器来说，压力太大了。我们数据库服务器和Java程序对连接数也无法控制，很容易导致数据库服务器崩溃。

我们就希望能管理连接。我们可以建立一个连接池，这个池中可以容纳一定数量的连接对象，一开始，我们可以先替用户先创建好一些连接对象，等用户要拿连接对象时，就直接从池中拿，不用新建了，这样也可以节省时间。然后用户用完后，放回去，别人可以接着用。可以提高连接的使用率。当池中的现有的连接都用完了，那么连接池可以向服务器申请新的连接放到池中。直到池中的连接达到“最大连接数”，就不能在申请新的连接了，如果没有拿到连接的用户只能等待。

## **4.****3****市面上有很多现成的数据库连接池技术**

JDBC 的数据库连接池使用 javax.sql.DataSource 来表示，DataSource 只是一个接口（通常被称为数据源），该接口通常由服务器(Weblogic, WebSphere, Tomcat)提供实现，也有一些开源组织提供实现：

DBCP 是Apache提供的数据库连接池，速度相对c3p0较快，但因自身存在BUG，Hibernate3已不再提供支持

C3P0 是一个开源组织提供的一个数据库连接池，速度相对较慢，稳定性还可以

Proxool 是sourceforge下的一个开源项目数据库连接池，有监控连接池状态的功能，稳定性较c3p0差一点

BoneCP 是一个开源组织提供的数据库连接池，速度快

Druid 是阿里提供的数据库连接池，据说是集DBCP 、C3P0 、Proxool 优点于一身的数据库连接池

## **4.****4****阿里的德鲁伊连接池技术**

（1）加入jar包

例如：druid-1.1.10.jar

（2）代码步骤

第一步：建立一个数据库连接池

第二步：设置连接池的参数

第三步：获取连接

public class TestPool {

public static void main(String[] args) throws SQLException {

//1、创建数据源（数据库连接池）对象

DruidDataSource ds =new DruidDataSource();

//2、设置参数

//(1)设置基本参数

ds.setDriverClassName("com.mysql.jdbc.Driver");

ds.setUrl("jdbc:mysql://localhost:3306/test");

ds.setUsername("root");

ds.setPassword("123456");

//(2)设置连接数等参数

ds.setMaxActive(10);//最多不超过10个，如果10都用完了，还没还回来，就会出现等待

ds.setMaxWait(1000);//用户最多等1000毫秒，如果1000毫秒还没有人还回来，就异常了

//3、获取连接

for (int i = 1; i <=15; i++) {

Connection conn = ds.getConnection();

System.out.println("第"+i+"个：" + conn);

//如果这里没有关闭，就相当于没有还

// conn.close();#这里关闭，是还回池中

}

}

}

​  

​  

封装JDBCTools和封装BasicDAOImpl的案例代码演示