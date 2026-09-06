# 一起读源码

  

*在学习java过程中，学会看源码是一门必修课。作为一个有一些Python基础但没有学习过相关源码的Python应用者，我将会在这个系列逐步更新java源码的学习。本系列基于JAVA8，IDE使用IDEA。*

  

第二期，将会对在算法中常用的`HashSet`的添加元素和扩容机制源码进行学习。`HashSet`底层调用`HashMap`实现，在`HashSet`中，不能有重复元素/对象，也不能保证元素有序。

  

## 1\. HashSet添加元素

  

HashSet添加元素的步骤大致如下：

  

-   先获取元素的hash值（hash值与hashCode相关，但不完全等同）

-   对哈希值进行运算，得到一个索引值。

-   找到存储数据表table，看这个索引值对应位置是否有存放的元素。如果没有，则直接加入；如果有，则调用对象的`equals()`方法进行比较，如果相同，就放弃添加，如果不相同，则以链表的方式添加。

  

从添加元素来看，`HashSet`底层实现了一个`HashMap`，并通过在table上挂载链表/红黑树（满足树化的情况下）进行元素的添加。下面我们一起来看看底层的源码。

  

示例代码如下：

  

```java
package com.geekthomas.set_;

import java.util.HashSet;
import java.util.Set;

/**
 * @className: HashSet_
 * @Description: TODO
 * @version:
 * @author: GeekThomas
 * @date: 2022/3/19 11:59
 */
public class HashSet_ {
    public static void main(String[] args) {
        Set hashSet = new HashSet();
        hashSet.add("a");
        hashSet.add("b");
        hashSet.add("a");
        System.out.println(hashSet);
    }
}
```

  

我们仍然按照之前的方法，下断点进行debug

  

![](./images/image-20220319122216838.png)

  

### 1.1. 执行HashMap

  

在对`HashSet`初始化时，调用其构造器，实际上就是new 一个`HashMap`

  

![](./images/image-20220319134012772.png)

  

### 1.2. 添加元素

  

当调用`add()`方法添加元素时，我们来逐步看看底层发生了什么。

  

首先，我们可以看到实现了一个`add()`方法，这个方法调用了map的`put()`方法

  

![](./images/image-20220319134216018.png)

  

再往里step into，可以看到执行了**`HashMap`**的put方法，key对应的就是上一步的e（"a"），而这个value其实是上一步的`PRESENT`（这是`HashSet`中的一个Object对象，用于占位)，该方法会得到key对应的hash值

  

![](./images/image-20220319134457366.png)

  

![](./images/image-20220319134835221.png)

  

接下来我们使用`force step into`进入`hash(key)`方法，看看hash值是如何生成的，可以看到hash值与我们传入的key的hashcode有关，特别地，当key为null的时候，分配给其的hash值为0。

  

![](./images/image-20220319135119602.png)

  

明白了hash值如何生成，我们再回到`put()`方法，看看`putVal()`这一步到底发生了什么。这里代码很长，我们就拿下代码逐行分析。

  

```java
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
               boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;//定义辅助变量
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = newNode(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        else if (p instanceof TreeNode)
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        else {
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    p.next = newNode(hash, key, value, null);
                    if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                        treeifyBin(tab, hash);
                    break;
                }
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;
            }
        }
        if (e != null) { // existing mapping for key
            V oldValue = e.value;
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;
            afterNodeAccess(e);
            return oldValue;
        }
    }
    ++modCount;
    if (++size > threshold)
        resize();
    afterNodeInsertion(evict);
    return null;
}
```

  

#### 1.2.1. 变量说明

  

在`putVal()`方法中，定义了一个`Node`类型的数组`tab`，以及节点，而在之后用到的`table`，则是在`HashMap`中定义的一个`Node`类型的数组，如下所示。

  

![](./images/image-20220319141200634.png)

  

#### 1.2.2. 第一次添加元素

  

在第一次向`HashSet`中添加元素时，由于此时`table`为`null`，因此会调用`resize()`方法，对`table`进行扩容。进入`resize()`方法，在初始化的时候，`oldCap`为0，因此会直接进入到else代码块，这时定义了 `newCap`以及`newThr`（这个接下来讲扩容的时候会用到），可以看到`newCap`被赋值为一个常量`DEFAULT_INITIAL_CAPACITY`，再看看上面的类图，这个其实在`HashMap`底层已经有定义了，就是16。

  

![](./images/image-20220319141959404.png)

  

![](./images/image-20220319142329888.png)

  

然后根据这个`newCap` 创建一个新数组，赋值给`table`

  

![](./images/image-20220319142656269.png)

  

可以看到，这是的`table`已经是长度为16的数组了。

  

![](./images/image-20220319142723604.png)

  

再回到`putVal`方法，此时n=16，通过计算`(n-1)&hash`得到对应索引的值，并把这个位置的对象赋值给p，如果p为空，就说明在表`tab`（其实就是`table`）中，对应索引没有存放元素，那么就创建一个节点加入到表中。

  

![](./images/image-20220319143404196.png)

  

此时可以看到，在`table`中索引为1的位置上已经有元素了，元素就是"a"。

  

![](./images/image-20220319144000233.png)

  

最后，我们可以看到返回`null`，此时在`add()`方法中，返回的就是`true`，表示添加元素成功。

  

![](./images/image-20220319144812570.png)

  

在`HashSet`中确实已经加入了该元素。

  

![](./images/image-20220319145030601.png)

  

继续添加元素"b"，发现对应索引为2（这里重新debug了一下，所以value对象有变化，但实际上都是一个空的Object对象）

  

![](./images/image-20220319145333681.png)

  

#### 1.2.3. 插入重复元素

  

当我们再插入"a"时，会发生什么呢？

  

此时再次进入`putVal`方法，因为此时tab已经不为空了，所以第一个if并不会执行，而且因为"a"对应的哈希值映射后的索引位置上已经有值（"a"），所以第二个if也不会进入。我们关注else这个代码块

  

![](./images/image-20220319145806315.png)

  

在else代码块中，其实进行了一步判断，判断对应索引位置对应的链表的第一个元素与要插入的对象是否为同一对象，需要同时满足以下条件：

  

-   两个对象的hash值相同

-   两个对象的key是同一个对象或者p指向的Node节点的key的equals()方法和准备加入的key比较后相同

  

如果两个条件同时满足，则不能继续加入。

  

如果上面的条件不满足，那么就判断p是不是一棵红黑树，如果是红黑树，那么就调用红黑树的`putTreeVal`进行添加。

  

如果均不满足，则需要以链表的方式进行添加（**这里需要判断链表的长度有没有超过限度（其实就是8），具体在下面的扩容中会详细描述**），对链表进行for循环，逐个比较链表中有无相同元素，如果准备加入的元素在链表中没有相同元素，则加入到链表的最后，否则只要链表中有相同元素，就会跳出循环。

  

最后判断e对象是否为空，当加入相同对象时，e肯定不为空，此时返回对应的value（其实就是上文的`PRESENT`）

  

![](./images/image-20220319150103859.png)

  

在`add()`方法中，此时返回`false`。这样就实现了`HashSet`不能有重复元素/对象的特性了。

  

![](./images/image-20220319152747175.png)

  

## 2\. HashSet扩容和转成红黑树机制

  

### 2.1. table数组扩容

  

我们用一段简单代码来研究

  

```java
package com.geekthomas.set_;

import java.util.HashSet;
import java.util.Set;

/**
 * @className: HashSet_
 * @Description: TODO
 * @version:
 * @author: GeekThomas
 * @date: 2022/3/19 11:59
 */
public class HashSet_ {
    public static void main(String[] args) {
        Set hashSet = new HashSet();
        for (int i = 1; i < 100; i++) {
            hashSet.add(i);
        }

    }
}
```

  

仍然是下断点debug，在初始化时，table为空

  

![](./images/image-20220319154952886.png)

  

当添加元素时，会自动扩容到16

  

![](./images/image-20220319155555619.png)

  

除此之外，我们还可以看到很多属性信息，比如`threshold=12，loadFactor=0.75`，这其实就是我们在添加元素的时候进行的判断，是否超出阈值。

  

![](./images/image-20220319155635759.png)

  

接下来我们直接跳到加入十二个元素

  

![](./images/image-20220319160106153.png)

  

再往后加，因为数组已经达到临界值，这时就会进行扩容，数组长度由12->32，如下所示：

  

![](./images/image-20220319160239688.png)

  

与此同时，我们可以看到数组的临界值由12->24

  

![](./images/image-20220319160330235.png)

  

我们继续添加元素，当加到第25个元素时，数组继续扩容到64

  

![](./images/image-20220319160448761.png)

  

以此类推。

  

在源码中，实际上就是实现了`resize()`方法，在第一次添加时，`oldCap = table = null`，此时`newCap = DEFAULT_INITIAL_CAPACITY = 16`，`newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY) = (int) (0.75 * 16) = 12`。当到达临界值时，`newCap,newThr`均会翻倍。

  

![](./images/image-20220319163225899.png)

  

### 2.2. 红黑树

  

要触发树化机制，我们这里就需要在添加元素的时候，使每个元素的hash值相同，这样才能挂在table数组的同一索引位置。示例代码如下：

  

```java
package com.geekthomas.set_;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

/**
 * @className: HashSet_
 * @Description: TODO
 * @version:
 * @author: GeekThomas
 * @date: 2022/3/19 11:59
 */
public class HashSet_ {
    public static void main(String[] args) {
        Set hashSet = new HashSet();
        for (int i = 1; i < 12; i++) {
            hashSet.add(new A(i));
        }
        System.out.println("hashset=" + hashSet);
    }
}

class A {
   private int n;

    public A(int n) {
        this.n = n;
    }

    @Override
    public int hashCode() {
        return 100;
    }

    @Override
    public String toString() {
        return "A{" +
                "n=" + n +
                '}';
    }
}
```

  

继续断点调试，发现第一个元素插入到表中索引为4的位置处。

  

![](./images/image-20220319161204368.png)

  

我们再来看看下一个元素。没有问题，第二个元素加入到索引为4的链表中了

  

![](./images/image-20220319161313969.png)

  

我们继续往后加，一直到加入8个元素。

  

![](./images/image-20220319161541929.png)

  

继续添加，神奇的事情发生了，此时并没有树化，而是数组扩容到了32。

  

![](./images/image-20220319161647343.png)

  

继续往下走，数组继续扩容到64，还没有树化。

  

![](./images/image-20220319161829675.png)

  

再往下走，数组不会继续扩容，而是树化，从图中可以看出，在表中索引为36的位置处，挂载了一棵树（**此时是TreeNode节点而不再是Node节点**）

  

![](./images/image-20220319162012193.png)

  

在源码中也能够看到，当表的长度小于`MIN_TREEIFY_CAPACITY=64`时，会继续扩容。

  

![](./images/image-20220319162419216.png)

  

接下来还有一个问题，临界值是否包括其他链表上的元素个数呢？

  

我们先通过实际代码验证

  

```java
package com.geekthomas.set_;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

/**
 * @className: HashSet_
 * @Description: TODO
 * @version:
 * @author: GeekThomas
 * @date: 2022/3/19 11:59
 */
public class HashSet_ {
    public static void main(String[] args) {
        Set hashSet = new HashSet();
        for (int i = 1; i < 8; i++) {//在table的某一条链表上添加了7个A对象
            hashSet.add(new A(i));
        }
        
        for (int i = 1; i < 8; i++) {//在table的另一条链表上添加了7个B对象
            hashSet.add(new B(i));
        }
        System.out.println("hashset=" + hashSet);
    }
}

class A {
   private int n;

    public A(int n) {
        this.n = n;
    }

    @Override
    public int hashCode() {
        return 100;
    }

    @Override
    public String toString() {
        return "A{" +
                "n=" + n +
                '}';
    }
}

class B {
    private int n;

    public B(int n) {
        this.n = n;
    }
    

    @Override
    public int hashCode() {
        return 200;
    }

    @Override
    public String toString() {
        return "B{" +
                "n=" + n +
                '}';
    }
}
```

  

我们这里通过重写`hashCode`方法，确保两次添加的元素在不同链表上。接下来就是debug时间。第一次添加后，在`table`数组的索引为4的位置上加入了7个元素。

  

![](./images/image-20220319164700575.png)

  

继续添加B对象，在索引为8的位置处添加对象。

  

![](./images/image-20220319164806019.png)

  

当加入6个B对象，也就是当前共加入13个对象时，数组扩容成32。也就是说，临界值是包括其他链表上的元素个数的。

  

![](./images/image-20220319164915282.png)

  

在源码中也有所体现：在执行`putVal()`方法时，每次执行都会导致size+1，因此每次插入一个新对象，就会导致size的修改。也就是说，临界值是包括`table`数组中所有链表上的元素的。

  

![](./images/image-20220319165055248.png)

  

## 3\. 一个简单应用

  

```java
package com.geekthomas.set_;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

/**
 * @className: HashSet_
 * @Description: TODO
 * @version:
 * @author: GeekThomas
 * @date: 2022/3/19 11:59
 */
public class HashSet_ {
    /*
     * @title main
     * @description 定义一个Employee类，该类包含name, age属性
     *              创建三个Employee，放入到HashSet中，当age和name相同时，则认为是相同员工，不能添加
     * @author GeekThomas
     * @param: args
     * @updateTime 2022/3/19 16:53
     * @throws
     */
    public static void main(String[] args) {
        Set hashSet = new HashSet();
        hashSet.add(new Employee(24, "jack"));
        hashSet.add(new Employee(22, "rose"));
        hashSet.add(new Employee(24, "jack"));

        System.out.println("hashSet=" + hashSet);
    }
}

class Employee {
    private int age;
    private String name;

    public Employee(int age, String name) {
        this.age = age;
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Employee employee = (Employee) o;
        return age == employee.age &&
                Objects.equals(name, employee.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(age, name);
    }

    @Override
    public String toString() {
        return "Employee{" +
                "age=" + age +
                ", name='" + name + '\'' +
                '}';
    }
}
```

  

![](./images/image-20220319170010820.png)

  

## 4\. 总结

  

我们再来梳理一下，

  

①在`HashSet`初始化时，会调用`HashMap()`底层实现，先初始化一个空`table`，在第一次添加元素时，会将`table`扩容到**16**（这与ArrayList调用无参构造器扩容到10需要区分），然后进行添加操作，临界值（threshold）为 16 \* 加载因子（loadFactor）0.75=12。

  

②在`HashMap`中，因为需要传入key-value，因此在`HashSet`中添加元素时，会分配给元素一个value（final static Object）。`HashMap`会统计计算对象的hash值来决定元素在表中的索引，并且进行判断，如果表中对应索引处没有值，那么就将根据传入的元素创建新的Node节点，插入到对应的索引位置。

  

③继续添加元素，仍然会计算该元素对应的hash值，如果在表中对应索引处没有元素存在，则加入；如果对应索引处有元素p存在，则需要分情况：

  

-   插入的对象与p相同（hash值相同，或者说调用equals方法后一致），那么就不再加入

-   插入的对象与p不同，而且p此时是一颗红黑树。这时候就需要将该对象加入到p的树中

-   插入的对象既不与p相同，且p不是红黑树，那么就以链表的方式添加到p所在索引位置的链表中。在添加前，需要判断在链表中有无相同对象，如果链表中无相同对象，则将该对象加入到链表最后，否则只要有一个对象相同，都不执行添加操作。

  

④如果`table`数组长度到达临界值12，那么就会扩容到16 \* 2=32，新的临界值就是24，以此类推

  

⑤在JAVA8中，如果一条链表的元素个数到达`TREEIFY_THRESHOLD`（默认是8），并且table的大小大于等于`MIN_TREEIFY_CAPACITY`（默认是64），就会进行树化（红黑树），否则仍然采用数组扩容机制。

  

更多详细内容可以参考[B站韩顺平JAVA系列课程](https://www.bilibili.com/video/BV1fh411y7R8?p=522)