# 一起读源码

  

*在学习java过程中，学会看源码是一门必修课。作为一个有一些Python基础但没有学习过相关源码的Python应用者，我将会在这个系列逐步更新java源码的学习。本系列基于JAVA8，IDE使用IDEA。*

  

第一期，将会对在算法中常用的`ArrayList`的扩容机制源码进行学习。ArrayList 类是一个可以动态修改的数组，与普通数组的区别就是它是没有固定大小的限制，我们可以添加或删除元素。ArrayList可以通过**无参构造器**和**有参构造器**进行初始化。接下来，我们将分别讨论两种情况下的源码。

  

## 1\. 通过无参构造器初始化

  

### 1.1. 示例代码

  

```java
package com.geekthomas.list_;

import java.util.ArrayList;

/**
 * @className: ArrayListSource
 * @Description: TODO
 * @version:
 * @author: GeekThomas
 * @date: 2022/3/18 10:54
 */
public class ArrayListSource {
    public static void main(String[] args) {
        ArrayList arrayList = new ArrayList();
        for (int i = 1; i < 11; i++) {
            arrayList.add(i);
        }

        for (int i = 11; i < 16; i++) {
            arrayList.add(i);
        }

        System.out.println(arrayList);

    }
}
```

  

在示例代码中，先使用**无参构造器**初始化空数组。然后先添加十个整数，再添加五个整数。

  

### 1.2. 源码剖析

  

开始下断点，进行debug

  

![](./images/image-20220318121928574.png)

  

#### 1.2.1. 初始化数组

  

将elementData初始化为一个空数组（即为`DEFAULTCAPACITY_EMPTY_ELEMENTDATA`）

  

![](./images/image-20220318114513020.png)

  

#### 1.2.2. 添加操作

  

在向数组中添加整数时，先完成自动装箱，转换成`Integer`类

  

![](./images/image-20220318113133777.png)

  

在添加元素前，先会调用`ensureCapacityInternal()`方法，确定是否需要扩容，然后再执行添加操作

  

![](./images/image-20220318113216354.png)

  

##### 1\. 确认容量

  

再次step into，可以发现确认容量需要进行两个操作：一是要确认需要的容量；二是要确认当前数组的容量。可以看到，在计算容量的过程中，如果传进去的elementData为空数组（即为`DEFAULTCAPACITY_EMPTY_ELEMENTDATA`），那么就需要取最小需要容量（此时为1）与默认容量（`DEFAULT_CAPACITY=10`）中较大值作为最小容量。由于最小容量（10）要大于数组长度（0），因此需要执行`grow()`来进行扩容。**第一次扩容为10**

  

![](./images/image-20220318115129305.png)

  

##### 2\. 扩容

  

扩容逻辑如下：

  

① 确认新容量（新容量是数组长度的1.5倍）：在第一次操作时，因为数组长度是0，其实并没有用到数组1.5倍扩容，直接使用最小容量（10）

  

② 扩容：调用`Arrays.copyOf()`方法

  

![](./images/image-20220318115705132.png)

  

可以看到，此时elementData已经有十个元素（都为空）

  

![](./images/image-20220318121056412.png)

  

在完成扩容之后，可以进行添加元素操作（size更新为1）

  

![](./images/image-20220318122048678.png)

  

因此，在使用无参构造器初始化数组的情况下，第一次添加元素时，需要先确认最小容量（默认为10），如果数组当前长度小于最小容量，就会调用`Arrays.copyOf()`方法，对数组进行扩容。

  

接下来，我们再看看当数组已经填满十个元素，再次添加元素，会发生什么。

  

![](./images/image-20220318122132073.png)

  

仍然需要确定是否需要扩容。当前数组长度10，所需最小长度为11

  

![](./images/image-20220318122203210.png)

  

此时最小容量为11，要大于数组长度，因此需要扩容。

  

![](./images/image-20220318122636717.png)

  

在第二次扩容中，newCapacity变为数组长度的1.5倍（10+5），此时在原数组的基础上，再添加五个位置。

  

![](./images/image-20220318122757601.png)

  

此时的elementData如下所示：

  

![](./images/image-20220318122947336.png)

  

## 2\. 通过有参构造器初始化

  

### 2.1. 示例代码

  

```java
package com.geekthomas.list_;

import java.util.ArrayList;

/**
 * @className: ArrayListSource
 * @Description: TODO
 * @version:
 * @author: GeekThomas
 * @date: 2022/3/18 10:54
 */
public class ArrayListSource {
    public static void main(String[] args) {
//        ArrayList arrayList = new ArrayList();
        ArrayList arrayList = new ArrayList(8);
        for (int i = 1; i < 11; i++) {
            arrayList.add(i);
        }

        for (int i = 11; i < 16; i++) {
            arrayList.add(i);
        }

        System.out.println(arrayList);

    }
}
```

  

### 2.2. 源码剖析

  

#### 2.2.1. 初始化数组

  

在传入有参构造器后，此时elementData被初始化为长度为8的数组。

  

![](./images/image-20220318123516969.png)

  

#### 2.2.2. 添加数据

  

##### 1\. 确认容量

  

因为elementData不为空，所以`minCapacity`就是最小需要的容量（此时为1），并且由于最小容量小于数组长度，也不会调用`grow()`方法，因此不需要扩容。

  

![](./images/image-20220318124110283.png)

  

当添加到9时，此时需要的容量已经超过数组长度了，再次添加就需要先进行扩容操作。

  

![](./images/image-20220318124613975.png)

  

##### 2\. 扩容

  

此时，**newCapacity为12（扩容为原数组长度的1.5倍）**

  

![](./images/image-20220318124721723.png)

  

## 总结

  

从上面的源码中可以看到，在java中对于数组扩容的机制如下：

  

-   使用无参构造器初始化数组，在添加元素前需要验证是否通过比较最小容量与当前数组进行扩容。在第一次扩容中，默认扩充为10；而在后续的扩容中，则是将数组在之前的基础上，长度扩容为1.5倍

-   使用有参构造器初始化数组，仍然需要验证是否需要扩容。如不需要扩容，则添加元素，当需要扩容时，再将数组在之前的基础上，长度扩容为1.5倍

  

通过编译器debug来学习源码是一种很好的学习方式，只是可惜在Pycharm中并不能看到源码，所以此前也没有好好学习过源码。更多详细内容可以参考[B站韩顺平JAVA系列课程](https://www.bilibili.com/video/BV1fh411y7R8?p=512)