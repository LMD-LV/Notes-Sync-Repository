---
tags: [Java与大数据, 概念]
created: 2026-09-06
status: 整理中
domain: Java与大数据
source: 个人总结
---
#### IO流(暂时快过)

*字节流 处理流  
* 优点：提高了读写的速度  
* 注意  
* 1.如何关闭流：相反顺序关闭 先开后关  
* 2.其实只要关闭高层流即可，高层流会关闭底层流*

*​*  

*BufferdReader BufferedWriter  
* 字符流 处理流  
*  
* 好处  
* 1.提高访问速度  
* 2.简化了操作  
* String str = br.readLine();  
* bw.newLine();  
*  
* 之前读文件：  
* 方法1：一个一个字符的读 read()  
* 方法2：使用字符数组读 read(cbuf)  
* 方法3:BufferedReader额外提供了按行读取的功能（InputStream绝对不会提供该方法）  
  
*

/\*\*  
* InputStreamReader 转换流  
* 处理流 输入流 字节流还是字符流 ？？ 字符流  
* Reader fr = new InputStreamReader(System.in);  
* public class InputStreamReader extends Reader  
\*/  
2\. 只可以将字节流转换为字符流  
* OutputStream---->OutputStreamWriter---------->Writer  
* InputStream ----->InputStreamReader----->Reader  
*  
* 没有WriterOutputStream ReaderInputStream类，没有这种应用场景  
\*/

​  

* File用来指向一个文件（文件夹/目录也是文件）  
* 可以获取该文件的各种属性：文件名、路径、大小、可读可写.....  
* 创建新文件，删除文件，查看当前文件夹下的内容  
*  
* 切记：File不能读写文件的内容 需要借助IO流来实现  
* package java.io  
*  
* 功能1：可以获取该文件的各种属性：文件名、路径、大小、可读可写.....

​  

  
*/\*\*  
* 功能2：如何创建File对象  
*  
* 1.路径的分隔符  
* 正斜杠 e:/java0212/readme.txt 推荐使用  
* 反斜杠 e:\\\\java0212\\\\readme.txt  
* 2.路径的类型  
* 绝对路径： e:/java0212/readme.txt 从盘符开始  
* 相对路径： readme.txt 相对于C:\\Users\\Administrator\\IdeaProjects\\javase0212  
* ../../readme.txt  
* 3. File指向一个目录  
* File file = new File("e:/java0212");  
*  
* 4.File类不同的构造方法  
* File file = new File("e:/java0212/readme.txt"); //路径文件名  
* File file = new File("e:/java0212","readme.txt");  
* File file = new File(new File("e:/java0212"),"readme.txt");  
* /*

*​*  

  
* 功能3：创建文件  
* file.createNewFile();  
* 创建目录  
* dir.mkdirs(); //创建一级或者多级文件夹 推荐使用  
* dir.mkdir();//创建一级文件夹 mkdir make directory  
* 删除文件 删除目录  
* file.delete();  
  
  
/\*\*  
* FileInputStream  
* 字节流 输入流（读） 节点流  
* 数据源是文件  
*  
* int n = fis.read(); 对一个字节 赋值给n 如果文件读完毕继续读，返回-1  
* len = fis.read(bytes); //将文件中的数据放入字节数组，字节数组length=3，真正读取的字节数可能不同，作为返回值返回  
*  
* String---byte[]  
* "尚硅谷".getBytes()  
* byte[] ---->String  
* new String(bytes)  
* new String(bytes,0,len)  
  
  
/\*\*  
* FileOutputStream  
* 字节流 输出流（写） 节点流  
* 目的地是File  
* public abstract void write(int b) throws IOException; 写一个字节 根据编号值写入对应的字符  
* public void write(byte b[]) throws IOException 写多个字节（字节数组的全部）  
* public void write(byte b[], int off, int len) throws IOException 字节数组的一部分  
\*/  
  
  
/\*\*  
* 使用字节流可以读写任意类型的文件  
* 使用字符流只可以读写文本文件（.txt .java .properties ） 使用记事本可以正确打开的文件  
*  
* 问题：doc docx word文档是文本文件  
* 不是。不可以使用记事本打开，只可以使用专门的软件，比如word、wps来打开，是二进制文件  
*  
* 字符流没有提供指定编码的功能  
* 解决：  
* idea中字符集是utf-8，window平台上是gbk （ansi）  
* 1.使用FileReader的父类InputStreamReader，FileWriter的父类 OutputStreamWriter来指定编码解决  
* 2.修改字符集一致 window平台上改为utf-8  
* 3.使用相对路径，相对于idea的路径，此时创建的文件默认是idea指定的编码  
*  
* 字符的方法：  
* int n = fr.read();  
* int len = fr.read(cbuf);  
*  
* fw.write(n);  
* fw.write(cbuf,0,len);  
*  
* 相对路径到底是哪里  
* 当前模块 @Test Junit  
* C:\\Users\\Administrator\\IdeaProjects\\javase0212\\ch14\_io  
* 当前项目 main  
* C:\\Users\\Administrator\\IdeaProjects\\javase0212  
*  
*  
*  
\*/

​  

#### 网络编程(以后再深入)

相关知识点代码中少

\----------TheTwentueth

​  

#### 反射(重点,难点,目前先跳过)

* \*  
* 问题1：Java的哪些类型可以有Class对象  
*  
* 所有类型都有Class对象  
* 基本数据类型  
* 类  
* 接口  
* 注解  
* 枚举  
*  
* 引入泛型后，出现了更多的类型，这些类型不能用Class表示，用扩展类型表示。  
* Class是Type接口的实现类  
* 其他都是Type的子接口  
*  
*  
\*/  
/\*\*  
* 问题2：如何获取一个类型的Class对象  
*  
* 方式1：类名.class  
* 可以获取各种类型的Class对象  
* 编译的时候已经知道了类型 TestClass2.class  
*  
* 方式2：对象名.getClass()  
* 必须新创建对象，才可以拿到类对象  
* 编译的时候已经知道了类型  
* TestClass2 tc2 = new TestClass2();  
* Class clazz2 = tc2.getClass();  
*  
* 方式3：Class.forName()  
* 编译的时候知道了类型，可以用该方式，但是没有必要  
* 编译的时候不知道类型（反射），只能用该方式  
* 从配置文件中获取类的完整路径 字符串  
* String className="com.atguigu.entity.Dog";  
* Class clazz = Class.forName(className);  
\*/  
  
/\*  
（1）运行主方法所在的类，要先完成类初始化，再执行main方法  
（2）子类初始化时，发现它的父类还没有初始化的话，那么先初始化父类  
（3）第一次使用某个类型就是在new它的对象，此时这个类没有初始化的话，先完成类初始化再做实例初始化  
（4）调用某个类的静态成员（类变量和类方法），此时这个类没有初始化的话，先完成类初始化  
（5）通过反射操作某个类时，如果这个类没有初始化，也会导致该类先初始化  
\*/