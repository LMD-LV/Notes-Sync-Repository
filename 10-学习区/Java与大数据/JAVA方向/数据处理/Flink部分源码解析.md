---
tags: [Java与大数据, 概念]
created: 2026-08-02
domain: Java与大数据
source: 个人总结
---

在调用方法时，实现一个接口有以下三种方式

1.自定义一个类实现接口 √

2.匿名实现类 √

3.lambda表达式

如果使用lambda表达式，可能会类型擦除报错

解决方式：在方法后面.returns(Types.类型)

  

Flink中流处理方式和批处理方式的区别:

1.执行环境的类不一样

2.分组使用的算子不一样

3.流处理方式最后需要调用execute()启动

  

  

#### keyby源码

--------------------------------------KeyBy源码解析--------------------------------  
1.首先计算出KeyGroupId（计算这个key属于那个分组）  
先通过key.hashCode()这个方法对key做了一次Hash  
然后又调用computeKeyGroupForKeyHash(key.hashCode(), maxParallelism)  
|  
|----->MathUtils.murmurHash(keyHash) % maxParallelism;  
对key又做了一次hash(MathUtils.murmurHash(keyHash))

  

2.通过以上方法获得到KeyGruopId后，再去计算这个key的分组属于哪个分区  
是通过以下方法实现的  
computeOperatorIndexForKeyGroup(maxParallelism, parallelism, assignToKeyGroup(key, maxParallelism));  
|  
|----> keyGroupId \* parallelism / maxParallelism;

  

3.最终再通过一下方法决定这个key的发送  
public int selectChannel(SerializationDelegate\<StreamRecord> record) {  
。  
。  
。  
}

  

  

#### 窗口源码解析

---------------------------------------窗口源码解析---------------------------------

1.窗口怎么实现的左闭右开？

public long maxTimestamp() {

return end - 1;

}

在TimeWindow这个类中有以上这个方法，这个方法的作用：获取仍然属于此窗口的最大时间戳。end指的是窗口结束时间 1指的是1毫秒

  

2.在定义窗口的时候offset的含义？

偏移的是窗口的开始时间，从某种意义上来看窗口的开始时间是固定在某些时间点的，如果不想在这些时间点开窗，可以指定offset来改变窗口的开始时间。

  

3.窗口的开始时间和数据进来的时间有什么关系？

滚动窗口中：

当前数据的处理时间 没有设置默认是0 窗口大小

timestamp - (timestamp - offset + windowSize) % windowSize;

因此从某种意义上来说，窗口的开始时间是固定的，比如窗口大小为5S，那么开启的窗口的开始时间都是5的整数倍不会有类似于\[2,7)这种窗口

  

4在assignWindows方法中，是每来一条数据调用一次，这个方法最后会new TimeWindow，会不会创建大量对象？

Collections.singletonList(new TimeWindow(start, start + size));

因为用到了单例，所以不会创建大量重复的对象

  

5.滑动窗口中，如何判断这个数据是属于哪些窗口的？

第一步：通过long lastStart = TimeWindow.getWindowStartWithOffset(timestamp, offset, slide);

获取到lastStart时间

具体如下：

假如开启一个窗口大小为6S，滑动步长为3S的一个窗口，在第二秒来了一条数据

那么根据以下公式计算 注意！！！！此时传进来windowSize指的是滑动步长

timestamp - (timestamp - offset + windowSize) % windowSize;

计算得到lastStart=2-(2-0+3)%3=0

第二步：将lastStart=0带入for循环计算

for (long start = lastStart; start > timestamp - size; start -= slide) {

windows.add(new TimeWindow(start, start + size));

}

start： 0 -3 -6

0>-4? -3>-4? -6>-4?

window:\[0,6) \[-3,3)

  

6.没有数据过来的时候会不会开窗？

没有数据的时候程序会一直阻塞，不会开窗，因为flink是事件驱动的，有数据才处理，没有的话一直阻塞

  

7.会话窗口中窗口的开始时间和数据进来的时间有什么关系？

new TimeWindow(currentProcessingTime, currentProcessingTime + sessionTimeout)

窗口的开始时间等于数据进来的处理时间，那么就意味着每毫秒来的数据都会创建一个不同的窗口

  

8.会话窗口源码（了解）

在会话窗口中因为每不同毫秒来的数据都会创建一个窗口，

然后这些窗口会放到集合中，并按照窗口开始时间做排序

List\<TimeWindow> sortedWindows = new ArrayList<>(windows);

  

Collections.sort(

sortedWindows,

new Comparator\<TimeWindow>() {

@Override

public int compare(TimeWindow o1, TimeWindow o2) {

return Long.compare(o1.getStart(), o2.getStart());

}

});

接下来，通过以下代码判断排完序的两两窗口是否有重叠

return this.start \<= other.end && this.end >= other.start;

如果有重叠的话，则合并两个窗口

new TimeWindow(Math.min(start, other.start), Math.max(end, other.end))

假如使用的是动态会话间隔现在有这么一组数据

s1,3,1 这个是第0秒来的数据 \[0,3)

s1,10,1 这个是第1秒来的数据 \[1,11)

s1,1,1 这个是第3秒来的数据 \[3,4)

然后排序，两两判断是否有重叠，有重叠则合并

\[0,3)和\[1,11)合并 => \[0,11)

然后再与\[3,4)合并 => \[0,11)最终合并成这么一个窗口

  

9.窗户什么时候触发计算？

当读取有界数据的时候，数据读完时依据数据生成WaterMark还没有达到触发标准，则用上面这个方式触发

if (window.maxTimestamp() <= ctx.getCurrentWatermark()) {

// if the watermark is already past the window fire immediately

return TriggerResult.FIRE;

} else {

ctx.registerEventTimeTimer(window.maxTimestamp());

return TriggerResult.CONTINUE;

}

或者

return time == window.maxTimestamp() ? TriggerResult.FIRE : TriggerResult.CONTINUE;

因此基于事件时间的窗口是否被触发，主要看的还是WaterMark

  

  

10.窗户什么时候关闭（被销毁）？

在WindowOperator这个类中可以找到

registerCleanupTimer(window);

然后在这个注册的清理时间定时器中可以看到清理时间的获取：

if (windowAssigner.isEventTime()) {

long cleanupTime = window.maxTimestamp() + allowedLateness;

return cleanupTime >= window.maxTimestamp() ? cleanupTime : Long.MAX_VALUE;

} else {

return window.maxTimestamp();

}

如果这个窗口是基于事件时间的窗口，则清理时间为window.maxTimestamp()（窗口的最大时间戳） + allowedLateness（设置允许迟到数据的时间）;

如果这个清理时机小于窗口的最大时间戳则清理时间为Long的最大值，不清理

  

如果这个窗口是基于处理时间的窗口，则清理时间为window.maxTimestamp()（窗口的最大时间戳）

然后会依据清理时间注册一个定时器

if (windowAssigner.isEventTime()) {

triggerContext.registerEventTimeTimer(cleanupTime);

} else {

triggerContext.registerProcessingTimeTimer(cleanupTime);

}

在这个定时器被触发时会调用以下方法清理窗口。

clearAllState(triggerContext.window, windowState, mergingWindows);

总结：如果是基于事件时间的窗口，则清理时间看的是window.maxTimestamp()（窗口的最大时间戳） + allowedLateness（设置允许迟到数据的时间）

如果这个窗口是基于处理时间的窗口，则清理时间为window.maxTimestamp()（窗口的最大时间戳）

  

事件时间指的是这个事件发生的时间

处理时间指的是这个事件被程序处理的时间

  

当前时间是2022-07-05 15:43:20 则意味着这个时间之前的事已经发生完了，不应该再出现了

  

  

  

#### WaterMark源码解析

  

------------------------------------WaterMark源码解析--------------------------

1.WaterMark默认生成方式是什么？

public void onEvent(Tevent, long eventTimestamp, WatermarkOutput output) 这个方法是每来一条数据调用一次间歇性

public void onPeriodicEmit(WatermarkOutput output) 这个方法是周期性调用的

因为是在onPeriodicEmit这个方法中生产的WaterMark，所以默认是周期性生成的WaterMark。

  

1.2周期时间是多少？

private long autoWatermarkInterval = 200; 默认为200ms

如何修改这个周期时间？

env.getConfig().setAutoWatermarkInterval(200);

  

1.3为什么有周期性生成和间歇期生成WaterMark的方式？

假如一秒钟来了一万条数据，如果使用周期性生成1000/200个WaterMark，如果使用间歇性生成WaterMark则要生成一万个WaterMark

假如一天来了5条数据，如果使用周期性生成1000\*60\*60\*24/200个WaterMark，如果使用间歇性生成WaterMark则要生成5个WaterMark

周期性生成适用场景：短时间内有大量数据

间歇性生成适用场景：长时间来的数据量很小

1.4周期性生成的WaterMark是怎么实现的？

首先在TimestampsAndWatermarksOperator这个类中可以看到

在open方法中注册了一个基于处理时间的定时器，定时时间为200ms

public void open() throws Exception {

。

。

。

。

//获取生成WaterMark周期时间

watermarkInterval = getExecutionConfig().getAutoWatermarkInterval();

//判断周期时间是否大于0以及是否发射WaterMark

if (watermarkInterval > 0 && emitProgressiveWatermarks) {

//获取当前处理时间

final long now = getProcessingTimeService().getCurrentProcessingTime();

//注册一个基础处理时间的定时器，定时时间默认为200ms

getProcessingTimeService().registerTimer(now + watermarkInterval, this);

}

}

然后当这个open方法中的定时器触发的时候会调用onProcessingTime这个方法，

然后在这个方法中又注册了一个基于处理时间的定时器，

并且在这个方法中调用了onPeriodicEmit，所以这个onPeriodicEmit方法是周期性调用的。

public void onProcessingTime(long timestamp) throws Exception {

watermarkGenerator.onPeriodicEmit(wmOutput);

  

final long now = getProcessingTimeService().getCurrentProcessingTime();

getProcessingTimeService().registerTimer(now + watermarkInterval, this);

}

在以下processElement这个方法中，调用了onEvent这个方法，因为processElement这个方法是来一条数据调用一次，所以onEvent这个方法是间歇性调用的

public void processElement(final StreamRecord\<T> element) throws Exception {

final T event = element.getValue();

final long previousTimestamp =

element.hasTimestamp() ? element.getTimestamp() : Long.MIN_VALUE;

final long newTimestamp = timestampAssigner.extractTimestamp(event, previousTimestamp);

  

element.setTimestamp(newTimestamp);

output.collect(element);

watermarkGenerator.onEvent(event, newTimestamp, wmOutput);

}

2.WaterMark初始值是多少？

Long的最小值

this.maxTimestamp = Long.MIN_VALUE + outOfOrdernessMillis + 1;

output.emitWatermark(new Watermark(maxTimestamp - outOfOrdernessMillis - 1));

  

3.为什么WaterMark是单调增长的？

maxTimestamp = Math.max(maxTimestamp, eventTimestamp);

  

4.关于生成WaterMark周期过长，期间来了很多数据，WaterMark的情况分析

因为WaterMark是在onPeriodicEmit这个方法中生成的，所以，WaterMark会在周期时间到达之后更新。

但是maxTimestamp是在onEvent这个方法中改变的，所以，每来一条数据都会修改maxTimestamp的值。

至于maxTimestamp这个值什么时候用，取决于WaterMark什么时候更新

  

5.为什么读有界数据的时候，所有的窗口都能关闭？当有界数据读完时WaterMark是多少？

在WaterMark这个类中可以看到一下代码

public static final Watermark MAX_WATERMARK = new Watermark(Long.MAX_VALUE);

当有界数据读完时，WaterMark为Long的最大值

/\*\* 事件时间定时器触发时调用. \*/

void onEventTime(InternalTimer\<K, N> timer) throws Exception;

  

/\*\* 处理时间定时器触发时调用. \*/

void onProcessingTime(InternalTimer\<K, N> timer) throws Exception;

  

