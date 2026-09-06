​  

背景：工作2年

  

面试问题：

  

1.  为什么找机会
2.  公司使用的技术栈是啥
3.  项目的最高QPS有多高
4.  遇到的开发问题有哪些？
5.  觉得自己从校招到现在有哪些提升
6.  项目-搭建的xx平台
7.  如何处理下游超时，一致性怎么保证

[链接](https://www.yuque.com/hollis666/dkfgay/xm675quxo1bc5qm8)

8.  RocketMq的特性

[✅RocketMQ的架构是怎么样的？](https://yuque.com/hollis666/dkfgay/fkx1hga7xlpbfbuv)

9.  如何用Redis统计亿级网站的uv

[链接](https://www.yuque.com/hollis666/dkfgay/gxqm60)

10.  遇到过什么线上问题，如何处理

[链接](https://www.yuque.com/hollis666/dkfgay/za04hyyegpeg4h2i)

11.  分布式锁如何设计

[链接](https://www.yuque.com/hollis666/dkfgay/feovxr7gr8ois5yt)

12.  分布式框架的服务发现怎么做

[链接](https://www.yuque.com/hollis666/dkfgay/io1pkwin43mkwaup)

13.  TheadLocal的使用场景，如何防止内存泄露

[链接](https://www.yuque.com/hollis666/dkfgay/ihoye3)

14.  JVM的堆栈各存储什么内容

[链接](https://www.yuque.com/hollis666/dkfgay/oyxrdhamqrmn291o)

15.  写过什么公共组件么？
16.  反问：用增营销和交易营销的区别、技术栈，生活 作息等
17.  写题：

```java
import java.util.Arrays;

public class Main {

    public static int[] findClosestElements(int[] arr, int k, int x) {
        //书写算法逻辑
        int left = 0, right = arr.length - 1;
        int mid = (left + right)/2;
        while(left < right) {
            if(arr[mid] > x) {
                right = mid;
            } else if(arr[mid] < x) {
                left = mid + 1;
            } else {
                break;
            }
            mid = (left + right)/2;
        }
        int lp = mid, rp = mid, count = 1;
        while(count < k) {
            if(rp > arr.length - 1) {
                lp --;
            }
            if(lp < 0) {
                rp ++;
            }
            if(x - arr[lp] > arr[rp] - x) { 
                rp ++;
                
            } else {
                lp --;
            }
            count ++;
        }
        int[] ans = new int[rp - lp + 1];
        for(int i = lp; i <= rp; i ++) { 
            ans[i - lp] = arr[i]; 
        }
        return ans;
    }

    // 获取到离x最近的k个数
    public static void main(String[] args) {
        int[] arr = {0, 0, 1, 2, 3, 3, 4, 7, 7, 8};
        int k = 3;
        int x = 5;
        int[] res = findClosestElements(arr, k, x);
        System.out.println(Arrays.toString(res));
    }
}

```