top命令

[https://cloud.tencent.com/developer/article/2020839](https://cloud.tencent.com/developer/article/2020839)

-   us(user)：表示 CPU 在用户运行的时间百分比，通常用户 CPU 高表示有应用程序比较繁忙。典型的用户程序有：[数据库](https://cloud.tencent.com/solution/database?from_column=20065&from=20065)、Web 服务器等。
-   sy(sys)：表示 CPU 在内核态运行的时间百分比（不包括中断），通常内核态 CPU 越低越好，否则表示系统存在某些瓶颈。
-   ni(nice)：表示用 nice 修正进程优先级的用户进程执行的 CPU 时间。nice 是一个进程优先级的修正值，如果进程通过它修改了优先级，则会单独统计 CPU 开销。
-   id(idle)：表示 CPU 处于空闲态的时间占比，此时，CPU 会执行一个特定的虚拟进程，名为 System Idle Process。
-   wa(iowait)：表示 CPU 在等待 I/O 操作完成所花费的时间，通常该指标越低越好，否则表示 I/O 存在瓶颈，可以用 iostat 等命令做进一步分析。
-   hi(hardirq)：表示 CPU 处理硬中断所花费的时间。硬中断是由外设硬件（如键盘控制器、硬件传感器等）发出的，需要有中断控制器参与，特点是快速执行。
-   si(softirq)：表示 CPU 处理软中断所花费的时间。软中断是由软件程序（如网络收发、定时调度等）发出的中断信号，特点是延迟执行。
-   st(steal)：表示 CPU 被其他虚拟机占用的时间，仅出现在多虚拟机场景。如果该指标过高，可以检查下[宿主机](https://cloud.tencent.com/product/cdh?from_column=20065&from=20065)或其他虚拟机是否异常。
-   通过上面的显示我们发现Cpu(s)表示的是 所有用户进程占用整个cpu的平均值，由于每个核心占用的百分比不同，所以按平均值来算比较有参考意义。而%CPU显示的是进程占用一个核的百分比，而不是整个cpu（12核）的百分比，有时候可能大于100，那是因为该进程启用了多线程占用了多个核心，所以有时候我们看该值得时候会超过100%，但不会超过总核数\*100。