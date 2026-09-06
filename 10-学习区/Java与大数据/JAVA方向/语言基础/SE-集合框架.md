---
tags: [Java与大数据, 概念]
created: 2026-08-02
status: 整理中
domain: Java与大数据
source: 个人总结
---

> [!note] 边界声明
> 本文讲集合体系 API 用法与红黑树等结构;HashMap/TreeMap 底层实现细节见 [[JAVA复习2022-Map与Set体系]]。

#### 集合,

集合: 存储同一数据类型多个元素对象的容器

* 数组和集合的区别: 1.容器长度可变性:数组:一旦创建,长度不可改变

集合:可以改变的

2.容器元素的数据类型 数组:元素既可以是基本类型,还可以是引用类型

集合:元素只能是引用类型

3.容器方法 数组:没有特有方法,调用Object类中的方法

集合:含有特有方法,也可以调用Object类中的方法

集合框架体系结构:单列集合(Collection接口):存储元素的单位是"个"

双列集合(Map接口):存储元素的单位是"对"

Collection接口:

* List接口:

* ArrayList类

* Vector类

* LinkedList类

* Set接口:

* HashSet类

* LinkedHashSet类

* TreeSet类

* Map接口

* HashMap类

* LinkedHashMap类

* TreeMap类

* Hashtable类

* Properties类

  

Collection接口

* 接口的位置

* java.util

* 接口的特点

* 是单列集合的顶级接口

* 接口的方法

* boolean add(E e)

* 确保此 collection 包含指定的元素（可选操作）。

* void clear()

* 移除此 collection 中的所有元素（可选操作）。

* boolean contains(Object o)

* 如果此 collection 包含指定的元素，则返回 true。

* boolean isEmpty()

* 如果此 collection 不包含元素，则返回 true。

* Iterator\<E> iterator()

* 返回在此 collection 的元素上进行迭代的迭代器。

* boolean remove(Object o)

* 从此 collection 中移除指定元素的单个实例，如果存在的话（可选操作）。

* int size()

* 返回此 collection 中的元素数。

  

Collection集合的面试题:

通过Collection接口的多态形式对象调用toString(),先判断Collection父接口中是否存在toString(),如果存在, 调用ArrayList类中重写后的toString();如果没有,编译报错;通过查询源码,发生Collection接口及它的父接口中都没有toString(),根据多态的特点应该编译报错,但是实际上并没有编译报错,代码可以正常调用ArrayList类重写后的toString(),为什么?

程序中所有的接口都隐式包含Object类中方法的抽象形式

  

Collection集合第一种遍历方式:Iterator迭代器

* 

* Iterator接口

* 接口的位置

* java.util

* 接口的特点

* 针对Collection接口进行迭代的迭代器工具接口

* 接口的方法

* boolean hasNext()

* 如果仍有元素可以迭代，则返回 true

* E next()

* 返回迭代的下一个元素。

* void remove()

* 从迭代器指向的 collection 中移除迭代器返回的最后一个元素（可选操作）。

* 

Iterator迭代器的注意事项:

1.获取的迭代器对象只能针对集合遍历一次,如果想再次遍历,需要重新调用iterator()获取新的迭代器对象

2.在使用迭代器针对集合迭代的过程中,不能针对集合做任何元素的修改,否则会发ConcurrentModificationException(并发修改异常)

  

Iterator接口是针对Collection接口进行迭代的迭代器工具接口

boolean hasNext() E next() void remove()

  

#### 增强for

Collection集合第二种遍历方式:增强for(JDK5.0新特性)

底层:增强for的底层就是迭代器对象

格式:

* for (容器中元素的数据类型 元素名 : 容器名 ) {

* 

* }

  

1.在使用增强for针对集合迭代的过程中,不能针对集合做任何元素的修改,否则会发生ConcurrentModificationException(并发修改异常)

2.增强for除了可以遍历集合外,还可以遍历数组,将数组转换为集合再进行迭代,不推荐使用增强for遍历数组

  

Collection集合第三种遍历方式:forEach()

Collection集合第四种遍历方式:Stream流

  

#### 泛型

泛型: 未知的数据类型

前提条件: 如果需要使用泛型,需要进行声明

格式 \<未知类型>

注意事项:如果使用含有泛型的类,接口,方法,必须给其确认泛型,如果不进行确认,JVM自动帮助我们进行确认为Object类型

  

泛型的使用 基础应用 高级应用 含有泛型的类,接口,方法

  

含有泛型的接口:

格式: public interface 接口名\<泛型> {}

确认时机: 创建该接口的实现类对象

确认格式: 接口名\<泛型类型> 对象名 = new 实现类类名();

含有泛型的类:

格式: public class 类名\<泛型> {}

确认时机: 创建该类对象时

确认格式:优化前:类名\<泛型类型> 对象名 = new 类名\<泛型类型>();

父类名\<泛型类型> 对象名 = new 类名\<泛型类型>();

优化后(JDK7.0):

类名\<泛型类型> 对象名 = new 类名<>();

父类名\<泛型类型> 对象名 = new 类名<>();

含有泛型的方法:

格式: 修饰符 \<泛型> 返回类型 方法名 () {}

确认时机: 调用方法并进行传参时

确认格式: 方法名(泛型类型);

  

泛型的高级应用:通配符

格式: 优化前: 修饰符 \<泛型>返回类型 方法名 (类名或接口\<泛型> 对象名) {}

优化后: 修饰符 返回类型 方法名 (类名或接口<?> 对象名) {}

通配符的上限和下限

泛型的上限:格式:<? extends 数据类型>

特点:泛型的类型是该类型本身,也可以是该类型的子类类型

泛型的下限:格式:<? super 数据类型>

特点: 泛型的类型是该类型本身,也可以是该类型的父类类型

  

#### List接口

* 接口的位置

* java.util

* 接口的特点

* 1.List集合是有序的集合

* 集合的有序性:存储元素的顺序和获取元素的顺序一致

* 集合的无序性:存储元素的顺序和获取元素的数据不一致

* 2.List集合是有整数索引的集合

* 3.List集合是可以存储重复元素

* 4.List集合中的索引实现方式共有4种

* 数组结构

* 链表结构

* 栈结构

* 队列结构

* 5.List集合含有特有的迭代器ListIterator

* 接口的方法

* void add(int index,E element)

* 在列表的指定位置插入指定元素（可选操作）。

* E get(int index)

* 返回列表中指定位置的元素。

* int indexOf(Object o)

* 返回此列表中第一次出现的指定元素的索引；如果此列表不包含该元素，则返回 -1。

* int lastIndexOf(Object o)

* 返回此列表中最后出现的指定元素的索引；如果列表不包含此元素，则返回 -1。

* ListIterator\<E> listIterator()

* 返回此列表元素的列表迭代器（按适当顺序）。

* E remove(int index)

* 移除列表中指定位置的元素（可选操作）。将所有的后续元素向左移动（将其索引减 1）。

* E set(int index,E element)

* 用指定元素替换列表中指定位置的元素（可选操作）。

* List\<E> subList(int fromIndex,int toIndex)

* 返回列表中指定的 fromIndex（包括 ）和 toIndex（不包括）之间的部分视图。

* /

  

List集合的6种遍历方式:1.迭代器 2.增强for 3.forEach() 4.Stream流 5.特有迭代器 6.普通for

  

集合删除时的小问题:每次成功删除,集合的长度都会改变

解决方案:1.每次成功删除,将索引往前移动一位 2.倒序遍历进行删除 3 . 迭代器中remove()

  

#### ArryList与Vetor

ArrayList类

* 类的位置

* java.util

* 类的特点

* 1.ArrayList集合底层的数据结构是"数组结构"

* 数组结构的特点(相比链表结构):

* 查询效率高,增删效率低

* 2.ArrayList集合可以存储null元素,在获取元素的时候需要进行元素的非空校验,防止空指针异常

* 3.ArrayList集合是线程不安全的集合,适用于单线程程序,如果在多线程中进行使用,需要手动添加线程安全

* 类的构造器

* public ArrayList()

* 构造一个初始容量为 10 的空列表。

* 类的方法

* 详见Collection集合和List集合的常用方法

  

ArrayList集合的源码分析:

* 1.ArrayList集合底层数组的初始长度

* 初始长度是多少所选择的构造器

* (1)public ArrayList()

* 初始容量:

* JDK6.0(包含)以前:10

* JDK7.0(包含)以后:0

* (2)public ArrayList(Collection<? extends E> c)

* 初始容量:

* 参数集合长度

* (3)public ArrayList(int initialCapacity)

* 初始容量:

* 自定义

* 2.ArrayList集合底层数组的扩容原理

* JDK6.0(包含)以前:

* (原来数组长度 \* 3) / 2 + 1

* JDK7.0(包含)以后:

* 第一次扩容:

* 10

* 后续扩容:

* 原来数组长度 + (原来数组长度 >> 1);

* 

  

Vector类

* 类的位置

* java.util

* 类的特点

* 1.Vector集合底层的数据结构是"数组结构"

* 2.Vector集合可以存储null元素,在获取元素的时候需要进行元素的非空校验,防止空指针异常

* 3.Vector集合是线程安全的,适用于多线程程序,不推荐在单线程中进行使用,因为效果过低

* 类的构造器

* public Vector()

* 类的方法

* 详见Collection集合和List集合的常用方法

  

ArrayList集合和Vector集合的区别:

* 1.线程安全性:

* ArrayList集合是线程不安全的集合,适用于单线程程序,如果在多线程中进行使用,需要手动添加线程安全

* Vector集合是线程安全的,适用于多线程程序,不推荐在单线程中进行使用,因为效果过低

* 2.无参构造器的初始长度不同:

* ArrayList初始容量:

* JDK6.0(包含)以前:10

* JDK7.0(包含)以后:0

* Vector初始容量:

* 10

* 3.扩容机制不同:

* ArrayList:

* 根据计算公式进行扩容:

* JDK6.0(包含)以前:

* (原来数组长度 \* 3) / 2 + 1

* JDK7.0(包含)以后:

* 第一次扩容:

* 10

* 后续扩容:

* 原来数组长度 + (原来数组长度 >> 1);

* Vector:

* 根据增量变量进行扩容

* 当增量为0时(无参构造器,int参数构造器,Collection参数构造器)

* 原来数组长度 + 原来数组长度

* 当增量大于0时(两个int参数构造器)

* 原来数组长度 + 增量变量

  

#### Collections类

* 类的位置

* java.util

* 类的特点

* 针对Collection集合进行操作的工具类

* 类的构造器

* 构造器私有化

* 类的方法

* public static \<T> boolean addAll(Collection<? super T> c,T... elements)

* 将所有指定元素添加到指定 collection 中

* public static void reverse(List<?> list)

* 反转指定列表中元素的顺序。

* public static void shuffle(List<?> list)

* 使用默认随机源对指定列表进行置换。

* public static \<T extends Comparable<? super T>> void sort(List\<T> list)

* 根据元素的自然顺序 对指定列表按升序进行排序

* public static \<T> void sort(List\<T> list,Comparator<? super T> c)

* 根据指定比较器产生的顺序对指定列表进行排序。

* /

  

#### 链接列表(链表):

* 类似于女生带的"手链",本质上其实就是一个类

* 

* 链表的分类:

* 单向链表:

* 当前元素(泛型类型)

* 下一个链表对象(链表类型)

* 双向链表

* 当前元素(泛型类型)

* 下一个链表对象(链表类型)

* 上一个链表对象(链表类型)

* 

* 链表结构的特点:

* 查询效率低,增删效率高

* 针对链表结构中首尾两个元素快速操作

* 

* 链表结构的弊端:

* 链表越长且数据越靠后,链表结构的查询和增删效率会更低

* 

* LinkedList类

* 类的位置

* java.util

* 类的特点

* 1.LinkedList集合底层的数据结构是"链表结构",而且是双向链表

* 2.LinkedList集合可以存储null元素,在获取元素时候需要进行非空校验,防止空指针异常

* 3.LinkedList集合是线程不安全的,适用于单线程程序,如果在多线程中进行使用,需要手动添加线程安全处理

* 类的构造器

* public LinkedList()

* 构造一个空列表。

* 类的方法

* public void addFirst(E e)

* 将指定元素插入此列表的开头。

* public void addLast(E e)

* 将指定元素添加到此列表的结尾。

* public E getFirst()

* 返回此列表的第一个元素。

* public E getLast()

* 返回此列表的最后一个元素。

* public E removeFirst()

* 移除并返回此列表的第一个元素。

* public E removeLast()

* 移除并返回此列表的最后一个元素。

  

#### Map接口

* 接口的位置

* java.util

* 接口的特点

* 1.Map集合存储元素不是以"个"为单位,而是以"对"为单位,一个key(键),一个value(值)

* 2.Map集合中的泛型类型可以相同,也可以不同

* 3.Map集合中key和value之间的关系为"映射关系"

* 4.在映射关系中,key的值不能重复

* 5.在映射关系中,value的值可以重复

* 6.Map集合中提供了三个Collection属性,分别是键集,值集,键值对集

* 接口的方法

* V put(K key,V value)

* 将指定的值与此映射中的指定键关联（可选操作）。

* V remove(Object key)

* 如果存在一个键的映射关系，则将其从此映射中移除（可选操作）。

* boolean containsKey(Object key)

* 如果此映射包含指定键的映射关系，则返回 true

* boolean containsValue(Object value)

* 如果此映射将一个或多个键映射到指定值，则返回 true。

* V get(Object key)

* 返回指定键所映射的值；如果此映射不包含该键的映射关系，则返回 null。

* boolean isEmpty()

* 如果此映射未包含键-值映射关系，则返回 true。

* void clear()

* 从此映射中移除所有映射关系（可选操作）。此调用返回后，该映射将为空。

* int size()

* 返回此映射中的键-值映射关系数

* Set\<K> keySet()

* 返回此映射中包含的键的 Set 视图。

* Collection\<V> values()

* 返回此映射中包含的值的 Collection 视图。

* Set\<Map.Entry\<K,V>> entrySet()

* 返回此映射中包含的映射关系的 Set 视图。

* /

Map集合通用的遍历方式

2:键值对对象的方式

  

* Map.Entry接口

* 接口的位置

* java.util下,Map接口中

* 接口的特点

* 针对put()每对元素进行对象创建的工具接口

* 接口的方法

* K getKey()

* 返回与此项对应的键。

* V getValue()

* 返回与此项对应的值

  

#### Set接口:

* 接口的位置

* java.util

* 接口的特点

* 1.Set集合是不可以存储重复元素的集合

* 2.Set集合中既有有序的集合,也有无序的集合

* 3.Set集合是没有索引的集合

* 4.Set集合没有特有的迭代器

* 5.Set集合的遍历方式只有4种

* (1)迭代器

* (2)增强for

* (3)forEach()

* (4)Stream流

* 接口的方法

* 详见Collection集合常用方法

  

#### HashSet类

* 类的位置

* java.util

* 类的特点

* 1.HashSet集合底层其实就是一个HashMap实例

* 2.HashSet集合是无序的集合

* 3.HashSet集合无法保证元素的顺序在集合中永远不会改变

* 元素的顺序和HashMap底层的数组长度有关,一旦长度发生改变,就有可能改变元素的顺序

* 4.HashSet集合可以存储null元素,当获取元素时需要进行非空校验,防止空指针异常

* 5.HashSet集合是线程不安全的,适用于单线程程序,如果在多线程中进行使用,需要手动添加线程安全处理

* 类的构造器

* public HashSet()

* 构造一个新的空 set，其底层 HashMap 实例的默认初始容量是 16，加载因子是 0.75。

* 类的方法

* 详见Collection集合常用方法

  

  

HashSet集合过滤重复元素原理

* 1.hashCode值不同当成不同的元素进行存储;如果hashCode值相同,元素内容有可能相同,也有可能不同

* 2.进行内容的比较equals(),内容如果相同,直接过滤,如果不同直接进行存储

* 

* 如果想保证元素的唯一性:

* 1.重写Object类的hashCode()

* 2.重写Object类的equals()

* 

* 在重写hashCode()中为什么乘 31 → 详见 [[为什么hashCode乘31]]


* 

  

LinkedHashSet类

* 类的位置

* java.util

* 类的特点

* 1.LinkedHashSet类是HashSet类的子类

* 2.LinkedHashSet集合是有序的集合

* 3.LinkedHashSet集合的底层其实是一个LinkedHashMap实例

* 4.LinkedHashSet集合在底层比HashSet集合多封装了一个链表,用来保证元素的有序性

* 5.LinkedHashSet集合可以存储null元素,当获取元素时需要进行非空校验,防止空指针异常

* 6.LinkedHashSet集合是线程不安全的,适用于单线程程序,如果在多线程中进行使用,需要手动添加线程安全处理

* 类的构造器

* public LinkedHashSet()

* 构造一个带默认初始容量 (16) 和加载因子 (0.75) 的新空链接哈希 set。

* 类的方法

* 详见Collection集合常用方法

  

#### 红黑树数据结构:

* 红黑树结构是树形结构和二叉树结构中的一种,本质上也是一个类

* 

* 树形结构结点对象:

* 当前元素(泛型类型)

* 父结点对象(树形结点类型)

* 子左结点对象(树形结点类型)

* 子右结点对象(树形结点类型)

* 

* 树形结构特点(相比链表结构):

* 1.整体上查询效率快,增删效率快

* 注意:在一定的数据个数范围内,链表结构效率要比红黑树结构要快一点点

* 2.树形结构在添加元素的时候针对结点中的元素数据进行数值排序

* 如果比较的数值相同,JVM会默认为同一元素,只存储一个

* 

#### TreeSet类

* 类的位置

* java.util

* 类的特点

* 1.TreeSet集合底层其实就是一个TreeMap实例

* 2.TreeSet集合是无序的集合

* 3.TreeSet集合在添加元素的时候,可以根据所选择的构造器针对待添加元素进行数据值大小排序

* 4.TreeSet集合不可以存储null,在进行添加元素的时候需要进行非空校验,防止空指针异常

* 5.TreeSet集合是线程不安全的,适用于单线程程序,如果在多线程中进行使用,需要手动添加线程安全处理

* 类的构造器

* public TreeSet()

* 构造一个新的空 set，该 set 根据其元素的自然顺序进行排序。

* public TreeSet(Comparator<? super E> comparator)

* 构造一个新的空 TreeSet，它根据指定比较器进行排序

* 类的方法

* 详见Collection集合常用方法

  

TreeSet集合的排序特点:

* 包装类型(Boolean类型除外):

* 按照数据值的大小的升序排序

* String类型:

* 每一位字符对应的Unicode码表值进行升序排序

* 自定义类型Student:

* 通过无参构造器实现的自然顺序

* 通过有参构造器实现的定制顺序

* 

* 注意事项:

* 针对TreeSet集合存储自定义类型对象时,必须给其实现自然顺序或定制顺序,否则在添加对象时运行报错

* 

  

自然顺序比较器:

* 1.将集合中元素的类型实现Comparable接口

* 2.在集合元素的类型中重写Comparable接口的抽象方法compareTo(T o)

* 3.在重写方法时,需要确认比较的规则,使用规则进行减法计算

  

定制顺序的比较器

* 1.使用匿名内部类创建Comparator\<T>接口的实现类对象

* 2.确认比较规则,在匿名内部类中重写compare(Student o1, Student o2)

* 3.将Comparator\<T>接口的实现类对象作为实参,创建TreeSet集合对象

* 4.添加元素即可完成排序

## 附:2022 复习版独有内容·集合框架Collection与List(2026-09-06 合并)

> 来自已删除的 JAVA复习2022-集合框架Collection与List.md,为该版独有,逐字搬运;行首 `*` 为原笔记的列表转义残留。

#### Collection
*集合:  
**\* 存储**同一数据类型**多个元素对象的容器  
**\* 数组和集合的区别:  
**\* 1.容器长度可变性:  
**\* 数组:一旦创建,长度不可改变  
**\* 2.容器元素的数据类型  
**\* 数组:元素既可以是基本类型,还可以是引用类型  
**\* 3.容器方法  
**\* 数组:没有特有方法,调用Object类中的方法  
*集合框架体系结构:  
**\* 单列集合(Collection接口):存储元素的单位是"个"  
**\* 返回在此 collection 的元素上进行迭代的迭代器。**\* boolean remove(Object o)  
**\* 通过Collection接口的多态形式对象调用toString(),先判断Collection父接口中是否存在toString(),如果存在,  
**\* 调用ArrayList类中重写后的toString();如果没有,编译报错;通过查询源码,发生Collection接口及它的父接口中  
**\* 都没有toString(),根据多态的特点应该编译报错,但是实际上并没有编译报错,代码可以正常调用ArrayList类重写  
**\* 后的toString(),为什么?  
**\* 2.在使用迭代器针对集合迭代的过程中,不能针对集合做任何元素的修改,否则会发生ConcurrentModificationException(并发修改异常)  
*增强for的注意事项  
#### 泛型:
*\* 含义:  
**\* 未知的数据类型(类似于小学数学中"设某个量为x")  
**\* 前提条件:  
**\* 如果需要使用泛型,需要进行声明  
**\** *\<未知类型>  
**\* 如果使用含有泛型的类,接口,方法,必须给其确认泛型,如果不进行确认,JVM自动帮助我们进行确认为Object类型  
*泛型的使用  
**\* 基础应用  
**\* 高级应用  
**\* 含有泛型的类,接口,方法  
**\* public interface 接口名**\<泛型>* *{}  
**\* 确认时机:  
**\* 创建该接口的实现类对象  
**\* 确认格式:  
**\* 接口名**\<泛型类型>* *对象名 = new 实现类类名();  
**\* public class 类名**\<泛型>* *{}  
**\* 确认时机:  
**\* 创建该类对象时  
**\* 确认格式:  
**\* 优化前:  
**\* 类名**\<泛型类型>* *对象名 = new 类名**\<泛型类型>**();  
**\* 修饰符* *\<泛型>* *返回类型 方法名 () {}  
**\* 确认时机:  
**\* 调用方法并进行传参时  
**\* 确认格式:  
**\* 方法名(泛型类型);*
**\* 优化前:  
**\* 修饰符* *\<泛型>**返回类型 方法名 (类名或接口**\<泛型>* *对象名) {}  
**\* 优化后:  
**\* 修饰符 返回类型 方法名 (类名或接口*<?> *对象名) {}\\*
*Collections类  
