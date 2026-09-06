---
tags: [Java与大数据, 概念]
created: 2026-08-02
status: 整理中
domain: Java与大数据
source: 个人总结
---

#### 工具类

BigInteger类

* 类的位置

* 不可变的任意精度的整数

* 类的特点

* java.math

* 类的构造器

* public BigInteger(String val)

* 将 BigInteger 的十进制字符串表示形式转换为 BigInteger。

* 类的方法

BigDecimal类

* 类的位置

* java.math

* 类的特点

* 不可变的、任意精度的有符号十进制数。

* 类的构造器

* public BigDecimal(String val)

* 将 BigDecimal 的字符串表示形式转换为 BigDecimal。

日期时间类:

* 第一代(JDK1.0):Date,DateFormat,SimpleDateFormat

* 第二代(JDK1.1):Calendar

* 第三代(JDK8.0):LocalDate,LocalTime,LocalDateTime,DateTimeFormatter

* 

* Date类:

* 类的位置

* java.util

* 类的特点

* 类 Date 表示特定的瞬间，精确到毫秒。

* 类的构造器

* public Date()

* 分配 Date 对象并初始化此对象，以表示分配它的时间（精确到毫秒）。

* public Date(long date)

* 分配 Date 对象并初始化此对象，以表示自从标准基准时间（称为“历元（epoch）”，即 1970 年 1 月 1 日 00:00:00 GMT）以来的指定毫秒数。

* 类的方法

* public long getTime()

* 返回自 1970 年 1 月 1 日 00:00:00 GMT 以来此 Date 对象表示的毫秒数。

* 

DateFormat类

* 类的位置

* java.text

* 类的特点

* 针对日期时间对象进行格式化和解析操作工具类的父类

* 格式化:Date对象==>文本(String)

* 解析:文本(String)==>Date对象

* 类的构造器

* 因为抽象类,创建其子类对象进行使用

* 类的方法

* public final String format(Date date)

* 将一个 Date 格式化为日期/时间字符串。

* public Date parse(String source)

* 从给定字符串的开始解析文本，以生成一个日期

* 

* SimpleDateFormat类

* 类的位置:

* java.text

* 类的特点:

* 针对日期时间对象进行格式化和解析操作工具类

* 类的构造器:

* public SimpleDateFormat(String pattern)

* 用给定的模式和默认语言环境的日期格式符号构造 SimpleDateFormat。

* 类的方法

* 继承DateFormat类中的format(Date date)和parse(String source)

* /

Calendar类

* 类的位置

* java.util

* 类的特点

* 针对日期时间操作提供的第二代工具类

* 类的构造器

* 该类为抽象类,通过静态方法进行获取

* 类的方法

* public static Calendar getInstance()

* 使用默认时区和语言环境获得一个日历。

* public int get(int field)

* 返回给定日历字段的值

  

LocalDateTime类

* 类的位置

* java.time

* 类的特点

* 针对日期时间操作提供的第三代工具类

* 类的构造器

* 构造器私有化

* 类的方法

* public static LocalDateTime now()

* 从默认时区中的系统时钟中获取当前日期时间。

* public static LocalDateTime parse(CharSequence text,DateTimeFormatter formatter)

* 获得 LocalDateTime实例从使用特定格式的文本字符串。

  

DateTimeFormatter类

* 类的位置

* java.time.format

* 类的特点

* 针对LocalDate,LocalTime,LocalDateTime对象进行格式化和解析操作的工具类

* 类的构造器

* 构造器私有化

* 类的方法

* public static DateTimeFormatter ofPattern(String pattern)

* 创建一个格式化程序使用指定的模式。

* public String format(TemporalAccessor temporal)

* 使用此格式化程序格式的日期时间对象。

* public TemporalAccessor parse(CharSequence text)

* 充分分析文本产生的时空对象。

  

#### 异常:

* 在程序编译或运行的过程中,出现了非正常的情况,从而导致JVM终止

  

  

Throwable类

* 类的位置

* java.lang

* 类的特点

* 在程序中是所有Exception和Error的直接父类

* Exception:在程序编译或运行的过程中,出现了非正常的情况,从而导致JVM非法终止;这类问题是程序员可以通过代码进行修复的

* Error:在程序运行的过程中,出现了非正常的情况,从而导致JVM非法终止;这类问题是程序员无法通过代码进行修复的

* 类的构造器

* public Throwable()

* 构造一个将 null 作为其详细消息的新 throwable。

* public Throwable(String message)

* 构造带指定详细消息的新 throwable。

* 类的方法

* public void printStackTrace()

* 将此 throwable 及其追踪输出至标准错误流。

* public String getMessage()

* 返回此 throwable 的详细消息字符串。

Exception的体系:

* 编译时异常:

* 含义:代码没有任何语法格式错误,导致程序编译报错

* 位置:java.lang包下Exception类及其子类(RuntimeException类及其子类除外)

* 运行时异常:

* 含义:代码没有任何语法格式错误,编译正常,在运行时期程序报错

* 位置:java.lang包下RuntimeException类及其子类

  

#### 异常处理:

* 关键字:throw,throws,try,catch,finally

* 注意事项:

* 无论是编译时异常还是运行时异常,都必须进行处理

* 处理方案:

* 编译时异常:

* 必须由程序员手动通过"异常声明"方式或"异常捕获"方式进行处理

* 运行时异常:

* 程序员可以选择不处理,交给JVM进行处理

* 第一步:调用异常对象的父类方法printStackTrace()

* 第二步:终止JVM

* 程序员手动进行处理

* 1.异常声明

* 2.异常捕获

  

throw关键字:

* 含义:抛出异常,将异常交给JVM进行识别

* 格式:

* throw new 异常类名(实参);

  

异常处理方案1:异常声明

* 含义:

* 当前方法不进行异常的处理,交给调用者方法进行处理

* 格式:

* 修饰符 返回类型 方法名 () throws 异常类名1,异常类名2,......,异常类名n {

* 

* }

  

异常声明的注意事项:异常声明和面向对象中的"继承"有一定的关系

* 在进行异常声明的时候出现了子父类继承关系

* 声明的异常类存在子父类继承关系

* 1.在进行异常声明的时候,异常子类和异常父类throws的顺序没有约束

* 2.声明的多个异常类存在子父类继承关系,可以直接声明一个父类即可

* 异常所在的类存在子父类继承关系

* 异常在父类被重写的方法中

* 当子类重写的时候,可以无需理会该异常信息,直接进行重写即可

* 异常在子类重写后的方法中

* 处理方案只有唯一的一种,就是"异常捕获"

  

  

异常处理方案2:异常捕获

* 含义:

* 找到可能发生异常的代码片段,进行捕获,如果存在异常,进行异常的处理,如果没有异常,执行后续代码

* 格式:

* try {

* 可能发生异常的代码判断

* } catch (异常类名 对象名) {

* 捕获到该异常对象时,进行该异常的处理方案

* }

  

异常捕获的注意事项:异常捕获和面向对象中的"继承"有一定的关系

* 在进行异常捕获的时候出现了子父类继承关系

* 捕获的异常类存在子父类继承关系

* 可以分别捕获,分别处理

* 前提:遇到每个异常的处理方案是不同的,异常间是独立

* 可以一起捕获,分别处理

* 前提:遇到每个异常的处理方案是不同的,异常间是关联

* 注意事项:异常子类需要先进行处理,否则出现编译报错

* 可以一起捕获,一起处理

* 前提:遇到每个异常的处理方案是相同的,直接处理一次

* 异常所在的类存在子父类继承关系

* 异常在父类被重写的方法中

* 当子类重写的时候,可以无需理会该异常信息,直接进行重写即可

* 异常在子类重写后的方法中

* 处理方案只有唯一的一种,就是"异常捕获"

  

finally关键字:

* 含义:

* 必须执行的(代码)

* 格式:

* try {

* 

* } catch () {

* 

* } finally {

* 必须执行的代码

* }

  

finally关键字的注意事项:

* 在try,catch,finally里面避免使用return语句

  

自定义异常类

* 自定义编译时异常类

* 自定义运行时异常类

* 

* 自定义运行时异常类步骤

* 1.创建自定义运行时异常类

* 2.将该类继承RuntimeException类

* 3.根据父类生成合适的构造器,至少有2个

* 无参和String参数

* 

* 自定义编译时异常类步骤:

* 1.创建自定义编译时异常类

* 2.将该类继承Exception类

* 3.据父类生成合适的构造器,至少有2个

* 无参和String参数

  

System类

* 类的位置

* java.lang

* 类的特点

* 常用方法的工具类

* 类的构造器

* 构造器私有化

* 类的变量和方法

* public static final InputStream in

* “标准”输入流

* public static final PrintStream out

* “标准”输出流

* public static void gc()

* 运行垃圾回收器。

* public static void setOut(PrintStream out)

* 重新分配“标准”输出流。

* public static long currentTimeMillis()

* 返回以毫秒为单位的当前时间。

* public static long nanoTime()

* 返回最准确的可用系统计时器的当前值，以毫微秒为单位。

  

#### 包装类:

* 含义:针对8种基本类型数据进行对应的引用类型

* 

* 基本类型(包装类型):

* byte(Byte),short(Short),int(Integer),long(Long)

* float(Float),double(Double)

* char(Character)

* boolean(Boolean)

* 

* 学习包装类目的:

* 1.基本类型和包装类型之间的转换

* 2.基本类型和字符串类型之间的转化

* 3.笔试或面试题

  

* 装箱和拆箱:

* 装箱:将基本类型数据转换为包装类型数据

* 拆箱:将包装类型数据转换为基本类型数据

* 

* 装箱:

* 1.以基本类型数据为参数的包装类型构造器

* 2.包装类型的静态方法valueOf(基本类型数组)

* 3.自动装箱

* 

  

//装箱1:包装类型的构造器

Integer num01 = new Integer(123);

  

//装箱2:包装类型的静态方法valueOf(基本类型数组)

Integer num02 = Integer.valueOf(456);

  

//拆箱1.包装类型的实例方法xxxValue()

int num03 = num01.intValue();

* 拆箱:

* 1.包装类型的实例方法xxxValue()

* 2.自动拆箱

  

自动装箱和自动拆箱(JDK5.0)

* 由JVM自动进行隐式的装箱和拆箱

//自动拆箱

int num01 = new Integer(123);

//自动装箱

Integer num02 = 456;

  

#### 基本类型和字符串类型间的转换

* 将基本类型数据转换为字符串类型数据:

* 1.字符串连接符

* 2.通过包装类型的实例方法toString()

* 3.通过包装类型的静态方法toString()

* 4.通过String的静态方法valueOf()(推荐)

* 将字符串类型数据转换为基本类型数据:

* 1.包装类型的构造器,再进行自动拆箱

* 2.包装类型的静态方法parseXxx() (推荐)

* //基本==>字符串1:字符串连接符

String str1 = 123 + "";//字符串连接符在内存中相当一个new

//基本==>字符串2:通过包装类型的实例方法toString()

String str2 = Integer.valueOf(234).toString();

//基本==>字符串3:通过包装类型的静态方法toString()

String str3 = Integer.toString(345);

//基本==>字符串4:通过String的静态方法valueOf()

String str4 = String.valueOf(456);

  

//字符串==>基本1:包装类型的构造器,再进行自动拆箱

int num01 = new Integer("567");

//字符串==>基本2:包装类型的静态方法parseXxx()

int num02 = Integer.parseInt("678");

}

* 注意事项:

* Character类并没有提供将字符串类型转换为char类型的两种方式

包装类型没有基本类型数据的自动提升,只有向上转型和向下转型

包装类笔试题2:

当通过自动装箱的方式创建Integer对象时,如果初始化值在-128~127之间,直接整数常量池中拿数据,如果不在其范围内,直接在堆中new

* /

  

  

#### String类

* 类的位置

* java.lang

* 类的特点

* 1.String类代表字符串

* 2.所有的字符串字面值常量都是String对象,可以进行String实例方法的调用

* 3.字符串是常量,一旦创建初始化不能改变

* 4.String底层的数据结构是一个被final修饰的数组变量

* 5.String底层数组的数据类型:

* 在JDK8.0(包含)以前,数据类型为:char[]

* 在JDK9.0(包含)以后,数据类型为:byte[]

* 6.为什么在JDK9.0中将char[]修改为byte[]?

* 时间复杂度:

* 如果是char[],里面的元素是char类型,在进行存储的时候,先将char类型转换为字节,再由字节转换成二进制

* 如果是byte[],里面的元素是byte类型,在进行存储的时候,直接byte类型转换为二进制

* 空间复杂度

* 如果是char[],

* 字符串内容为"abc",将abc分为三个字符存储到数组中,字符元素变量由底层创建,遵循"内码"规则,每个字符占2个字节,总共占6个字节 字符串内容为"尚硅谷",将"尚硅谷"分为三个字符存储到数组中,字符元素变量由底层创建,遵循"内码"规则,每个字符占2个字节,总共占6个字节

* 如果是byte[],

* 字符串内容为"abc",根据平台默认的编码表进行存储,将字符串中的内容转换为字节,考虑到平台是"UTF8",每个英文字符占用1个字节,总共占用3个字节 字符串内容为"尚硅谷",根据平台默认的编码表进行存储,将字符串中的内容转换为字节,考虑到平台是"UTF8",每个中文字符占用3个字节,总共占用9个字节

* 7.String对象为什么可以存储中文?

* String类底层是以"UTF-16"编码方式进行封装的,只要是Unicode字符集中的中文都可以支持

* 

* 类的构造器

* public String()

* 初始化一个新创建的 String 对象，使其表示一个空字符序列。

* public String(byte[] bytes)

* 通过使用平台的默认字符集解码指定的 byte 数组，构造一个新的 String

* public String(byte[] bytes,int offset,int length)

* 通过使用平台的默认字符集解码指定的 byte 子数组，构造一个新的 String。

* public String(char[] value)

* 分配一个新的 String，使其表示字符数组参数中当前包含的字符序列。

* public String(char[] value,int offset,int count)

* 分配一个新的 String，它包含取自字符数组参数一个子数组的字符。

* public String(String original)

* 初始化一个新创建的 String 对象，使其表示一个与参数相同的字符序列；换句话说，新创建的字符串是该参数字符串的副本。

* public String(StringBuffer buffer)

* 分配一个新的字符串，它包含字符串缓冲区参数中当前包含的字符序列。

* public String(StringBuilder builder)

* 分配一个新的字符串，它包含字符串生成器参数中当前包含的字符序列。

* 类的方法

* 判断功能方法

* 获取功能方法

* 转换功能方法

* 分割功能方法

* 

* String对象创建的两种方式:

* 1.字符串字面值常量

* 2.通过构造器

//通过无参构造器创建对象  
String str2 = new String();//类似于"",二者有本质的不同  
System.*out*.println("str2 = " \+ str2);

  

String类的常用方法:判断

* public boolean equals (Object anObject)

* 将此字符串与指定对象进行比较

* public boolean equalsIgnoreCase (String anotherString)

* 将此字符串与指定对象进行比较，忽略大小写。

* public boolean contains(CharSequence s)

* 当且仅当此字符串包含指定的 char 值序列时，返回 true。

* public boolean endsWith(String suffix)

* 测试此字符串是否以指定的后缀结束。

* public boolean isEmpty()

* 当且仅当 length() 为 0 时返回 true。

* public boolean startsWith(String prefix)

* 测试此字符串是否以指定的前缀开始。

* public boolean startsWith(String prefix,int toffset)

* 测试此字符串从指定索引开始的子字符串是否以指定前缀开始。

* 

  

String类常用方法:获取

* public int length ()

* 返回此字符串的长度。

* public String concat (String str)

* 将指定的字符串连接到该字符串的末尾。

* public char charAt (int index)

* 返回指定索引处的 char值。

* public int indexOf (String str)

* 返回指定子字符串第一次出现在该字符串内的索引。

* public int lastIndexOf(String str)

* 返回指定子字符串在此字符串中最右边出现处的索引。

* public String substring (int beginIndex)

* 返回一个子字符串，从beginIndex开始截取字符串到字符串结尾。

* public String substring (int beginIndex, int endIndex)

* 返回一个子字符串，从beginIndex到endIndex截取字符串。含beginIndex，不含endIndex。

* /

  

String的常用方法:

* public char[] toCharArray ()

* 将此字符串转换为新的字符数组

* public byte[] getBytes ()

* 使用平台的默认字符集将该 String编码转换为新的字节数组。

* public String replace (CharSequence target, CharSequence replacement)

* 将与target匹配的字符串使用replacement字符串替换。

* public String toLowerCase()

* 使用默认语言环境的规则将此 String 中的所有字符都转换为小写。

* public String toUpperCase()

* 使用默认语言环境的规则将此 String 中的所有字符都转换为大写。

* /

  

String类的常用方法:分割

* public String[] split(String regex)

* 根据给定规则的匹配拆分此字符串。

* 

* 注意事项:

* 1.进行分割时候,分割后的字符串没有"给定规则"

* 2.只要"给定规则"不在字符串的最后,都正常分割

* 3.如果给定的规则在字符串的最后,删除最后的给定规则,不进行分割

  

StringBuilder类和StringBuffer类

* 相同点:

* 1.拥有相同的父类AbstractStringBuilder

* 2.都是可变的字符序列

* 不同点:

* 1.StringBuilder类是线程不安全,适合单线程程序,如果在多线程程序中进行上使用,需要手动添加线程安全

* 2.StringBuffer类是线程安全,适合多线程程序,如果在单线程程序中进行使用,效率过低,不推荐在单线程中进行使用

* /

  

  

StringBuilder类

* 类的位置

* java.lang

* 类的特点

* 1.一个可变的字符序列

* 2.StringBuilder类是线程不安全,适合单线程程序,如果在多线程程序中进行上使用,需要手动添加线程安全

* 类的构造器

* public StringBuilder()

* 构造一个不带任何字符的字符串生成器，其初始容量为 16 个字符。

* 类的方法

* public StringBuilder append(String s)

* 将 String 参数的字符串表示形式追加到序列。

* public StringBuilder insert(int offset,String str)

* 将字符串插入此字符序列。

* public StringBuilder reverse()

* 将此字符序列用其反转形式取代。

  

StringBuilder类的源码分析:

* 1.StringBuilder类底层数组的初始容量

* 初始容量是多少取决于创建对象时选择的"构造器"

* (1)StringBuilder()

* 初始容量:16

* (2)StringBuilder(CharSequence seq)

* 初始容量:参数长度+16

* (3)StringBuilder(int capacity)

* 初始容量:自定义

* (4)StringBuilder(String str)

* 初始容量:参数长度+16

* 2.StringBuilder类底层数组的扩容规则

* JDK8.0(包含)以后扩容规则:

* (原来数组长度 << 1) + 2;

* JDK7.0(包含)扩容规则:

* 原来数组长度 \* 2 + 2;

* JDK6.0(包含)以前扩容规则:

* (原来数组长度 + 1) \* 2

* 3.StringBuilder类底层数组进行扩容的时候,为什么加2?

* 当使用带有int参数的构造器创建对象时,自定义长度为0,进行扩容不加2永远为0,需要通过+2进行扩容,访问底层数组为0的情况

  

*/* String笔试题1:

String str5 = new String("Hello");

String str6 = new String("World");

System.out.println(str1 == (str5 + str6));//false

// str5 + str6 相当于new StringBuilder().append(str5).append(str6).toString();

  

String笔试题2

在程序中,JVM将通过直接声明初始化的自定义常量当成字面值进行使用

public static final String str1 = "HelloWorld";

public static final String str2 = "HelloWorld";

public static final String str3 = "Hello";

public static final String str4 = "World";

public static final String str5;

public static final String str6;

public static final String str7;

public static final String str8;

  

static {

str5 = "HelloWorld";

str6 = "HelloWorld";

str7 = "Hello";

str8 = "World";

}

System.out.println(str1 == (str3 + str4));

System.out.println(str5 == (str7 + str8));

String笔试题3:

* 在堆内存中数String对象的个数

String str1 = "HelloWorld";

//String对象数量:1个(常量池)

  

String str2 = new String("HelloWorld");

//String对象数量:2个,1个new的,1个常量池

  

String str3 = "H" + "e" + "l" + "l" + "o" + "W" + "o" + "r" + "l" + "d";

//String对象数量:1个,在常量池

String str4 = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9 + s10;

//String对象数量:8个,7个常量池,1个堆

  

