是什么:

一个在main方法执行之前，执行点什么东西，可以通过各种手段，主要用作让执行的类合java代码对应不上

如何用：

写一个特殊的jar包，jar包里的MAINFEST.MF文件有个Premain-Class配置一个类名，比如A

A类里要有个方法premain格式为如下：

```java
public static void premain(String agentArgs, Instrumentation inst) throws Exception{
    xxxxxx
}
```

agentArgs为参数，inst用于拦截和改变要加载类的工具`​`

可以配置多个agent jar，执行顺序与参数写的顺序一致 启动方式为

```shell
java -javaagent:agent1.jar=参数xxxxx -javaagent:agent2.jar=参数yyyy -jar MyProgram.jar
```

inst使用，需要添加ClassFileTransformer的实现，实现ClassFileTransformer关键是实现以下方法

```java
inst.addTransformer(new ClassFileTransformerImpl(prop, inst), true);
```

loader为要加载类的classloader，className为类的内部名，第3，4的参数一般用不到且多数情况为null，最后一个参数为class文件的字节数组，返回值为通过改变之后的class文件字节数组

可以干啥

可通过特定框架，读取classfileBuffer，解析其结构，添加比如删库的逻辑，然后生成新的class字节返回，这样源代码找不到删库逻辑，实际上执行了删库，查还不好查，因为加上的逻辑压根没源码

​  

完整代码示例如下：

```java
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
public class AgentMain {

    public static void premain(String agentArgs, Instrumentation inst) throws Exception {
        System.out.println(agentArgs);
        inst.addTransformer(new HookClassFileTransformer(agentArgs), true);

    }

    private static class HookClassFileTransformer implements ClassFileTransformer {

        private String agentArgs
        public HookClassFileTransformer(String agentArgs) {
            this.agentArgs = agentArgs;
        }

        @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
            //这块要自己实现xxxxx的逻辑
            byte[] newClassFileBuffer = xxxxx(className,classfileBuffer,loader);
            return newClassFileBuffer;
        }
    }

}
```