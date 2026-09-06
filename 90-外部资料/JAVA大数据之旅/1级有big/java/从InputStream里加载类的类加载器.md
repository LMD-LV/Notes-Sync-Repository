```java
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;

import java.io.ByteArrayInputStream;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLStreamHandler;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.jar.JarEntry;
import java.util.jar.JarInputStream;
import java.util.stream.Collectors;

@Slf4j
public class JarByteArrayClassLoader extends ClassLoader implements Closeable {

    private Map<String, List<byte[]>> cacheEntityBytes = new ConcurrentHashMap<>();

    private Map<String, Class> cacheClass = new HashMap<>();

    private Map<String, List<URL>> cacheResource = new HashMap<>();

    public JarByteArrayClassLoader(List<InputStream> inputStreams, ClassLoader parent) {
        super(Objects.isNull(parent) ? Thread.currentThread().getContextClassLoader() : parent);
        inputStreams.forEach(inputStream -> {
            try {
                this.parseJar(inputStream);
            } catch (Exception ex) {
                log.error("parse jar error", ex);
            }
        });
    }

    public static JarByteArrayClassLoader of(ClassLoader parent, InputStream... inputStreams) {
        return new JarByteArrayClassLoader(Arrays.asList(inputStreams), parent);
    }

    public static JarByteArrayClassLoader of(ClassLoader parent, List<byte[]> bytes) {
        List<InputStream> list = bytes.stream().map(ByteArrayInputStream::new).collect(Collectors.toList());
        return new JarByteArrayClassLoader(list, parent);
    }

    private void parseJar(InputStream input) throws Exception {
        JarInputStream jis = new JarInputStream(input);
        while (true) {
            JarEntry nextJarEntry = jis.getNextJarEntry();
            if (Objects.isNull(nextJarEntry)) {
                break;
            } else if (nextJarEntry.isDirectory()) {
                continue;
            }
            String name = nextJarEntry.getName();
            byte[] byteArray = IOUtils.toByteArray(jis);
            this.cacheEntityBytes.computeIfAbsent(name, k -> new ArrayList<>()).add(byteArray);
            jis.closeEntry();
        }
        IOUtils.closeQuietly(jis);
        IOUtils.closeQuietly(input);
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        if (this.cacheClass.containsKey(name)) {
            return this.cacheClass.get(name);
        }
        String classFileName = String.format("%s.class", StringUtils.replace(name, ".", "/"));
        if (!this.cacheEntityBytes.containsKey(classFileName)) {
            throw new ClassNotFoundException("class " + name + " not found");
        }
        List<byte[]> entries = this.cacheEntityBytes.get(classFileName);
        byte[] classBytes = this.decode(entries.get(entries.size() - 1));
        Class<?> clazz = this.defineClass(name, classBytes, 0, classBytes.length);
        synchronized (this) {
            this.cacheClass.put(name, clazz);
            this.cacheEntityBytes.remove(classFileName);
        }

        return clazz;
    }

    @Override
    protected Enumeration<URL> findResources(String name) throws IOException {
        if (this.cacheResource.containsKey(name)) {
            return Collections.enumeration(this.cacheResource.get(name));
        }
        if (!this.cacheEntityBytes.containsKey(name)) {
            return Collections.emptyEnumeration();
        }
        synchronized (this) {
            List<byte[]> resources = this.cacheEntityBytes.get(name);
            List<URL> urls = this.cacheResource.computeIfAbsent(name, k -> new ArrayList<>());
            for (byte[] resource : resources) {
                urls.add(new URL(null, "bytes://bytes", new ByteArrayURLStreamHandler(this.decode(resource))));
            }
            this.cacheEntityBytes.remove(name);
            return Collections.enumeration(urls);
        }
    }

    protected byte[] decode(byte[] data) {
        return data;
    }

    @Override
    protected URL findResource(String name) {
        try {
            Enumeration<URL> resources = this.findResources(name);
            if (resources.hasMoreElements()) {
                return resources.nextElement();
            }
        } catch (IOException e) {
        }
        return null;

    }

    @Override
    public void close() throws IOException {
        this.cacheEntityBytes.clear();
    }

    private class ByteArrayURLStreamHandler extends URLStreamHandler {

        private byte[] bytes;

        public ByteArrayURLStreamHandler(byte[] bytes) {
            this.bytes = bytes;
        }

        @Override
        protected URLConnection openConnection(URL u) throws IOException {
            return new ByteArrayURLConnection(u, this.bytes);
        }

    }

    private class ByteArrayURLConnection extends URLConnection {
        private byte[] bytes;

        protected ByteArrayURLConnection(URL url, byte[] bytes) {
            super(url);
            this.bytes = bytes;
        }

        @Override
        public void connect() throws IOException {

        }

        @Override
        public InputStream getInputStream() throws IOException {
            return new ByteArrayInputStream(this.bytes);
        }
    }

}
```