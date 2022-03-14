# Oozie install in docker  
```bash
cd oozie 
docker build -t shwsun/oozie .

docker run -itd --privileged --name oozie --hostname oozie --rm -p 10000-10001:11000-11001 shwsun/oozie

docker exec -it oozie jps

```


```bash
apt-get install -y maven
mvn -version 



docker exec -it oozie /bin/bash
# oozie 
wget https://dlcdn.apache.org/oozie/5.2.1/oozie-5.2.1.tar.gz
tar xfv oozie-5.2.1.tar.gz && rm oozie-5.2.1.tar.gz
cd /install-files/oozie-5.2.1
mvn clean package assembly:single -DskipTests -P hadoop-3,uber -Dhadoop.version=3.2.2 
# ==> compile error 발생 : 아래와 같이 hdoop 3 패치 적용. 
# /install-files/oozie-5.2.1/distro/target/oozie-5.2.1-distro.tar.gz 생성 됨. 


# patch 파일 다운로드
# /install-files/oozie-5.2.1/tools/src/test/java/org/apache/oozie/tools/TestECPolicyDisabler.java
#wget https://issues.apache.org/jira/secure/attachment/13025322/OOZIE-3621.v0.patch
cat << EOF |tee /install-files/oozie-5.2.1/tools/src/main/java/org/apache/oozie/tools/ECPolicyDisabler.v0.patch 
diff --git a/tools/src/main/java/org/apache/oozie/tools/ECPolicyDisabler.java b/tools/src/main/java/org/apache/oozie/tools/ECPolicyDisabler.java
index e24ac7a07..58df898bf 100644
--- a/tools/src/main/java/org/apache/oozie/tools/ECPolicyDisabler.java
+++ b/tools/src/main/java/org/apache/oozie/tools/ECPolicyDisabler.java
@@ -48,7 +48,7 @@ public final class ECPolicyDisabler {
     }
 
     public static void tryDisableECPolicyForPath(FileSystem fs, Path path) {
-        switch (check(fs, path)) {
+        switch (check(fs, path, GETERASURECODINGPOLICY_METHOD)) {
             case DONE:
                 System.out.println("Done");
                 break;
@@ -64,12 +64,12 @@ public final class ECPolicyDisabler {
         }
     }
 
-    static Result check(FileSystem fs, Path path) {
+    static Result check(FileSystem fs, Path path, String getErasureCodingPolicyMethodName) {
         if (fs instanceof DistributedFileSystem && supportsErasureCoding()) {
             System.out.println("Found Hadoop that supports Erasure Coding. Trying to disable Erasure Coding for path: "+ path);
             DistributedFileSystem dfs = (DistributedFileSystem) fs;
             final Object replicationPolicy = getReplicationPolicy();
-            Method getErasureCodingPolicyMethod = getMethod(dfs, GETERASURECODINGPOLICY_METHOD);
+            Method getErasureCodingPolicyMethod = getMethod(dfs, getErasureCodingPolicyMethodName);
             final Pair<Object,Result> currentECPolicy = safeInvokeMethod(getErasureCodingPolicyMethod, dfs, path);
             if (currentECPolicy.getRight() != null) {
                 return currentECPolicy.getRight();
EOF

cat << EOF |tee /install-files/oozie-5.2.1/tools/src/test/java/org/apache/oozie/tools/TestECPolicyDisabler.v0.patch 
diff --git a/tools/src/test/java/org/apache/oozie/tools/TestECPolicyDisabler.java b/tools/src/test/java/org/apache/oozie/tools/TestECPolicyDisabler.java
index c2ba314c8..e24c63aec 100644
--- a/tools/src/test/java/org/apache/oozie/tools/TestECPolicyDisabler.java
+++ b/tools/src/test/java/org/apache/oozie/tools/TestECPolicyDisabler.java
@@ -43,11 +43,17 @@ import org.mockito.Mockito;
 
 /**
  * Test for the Erasure Coding disabler code.
+ *
+ * Noted that getErasureCodingPolicy was introduced to hadoop 3 and the returned class (ErasureCodingPolicy) does
+ * NOT exist in hadoop 2. That is to say, the implementation of getErasureCodingPolicy can't work with both hadoop 2
+ * and hadoop 3. Hence, this test makes ECPolicyDisabler#check to test another method `getFakeErasureCodingPolicy`
  */
 public class TestECPolicyDisabler  {
 
+    private static final String FAKE_METHOD_NAME = "getFakeErasureCodingPolicy";
+
     static abstract class MockDistributedFileSystem extends DistributedFileSystem {
-        public abstract SystemErasureCodingPolicies.ReplicationPolicy getErasureCodingPolicy(Path path);
+        public abstract SystemErasureCodingPolicies.ReplicationPolicy getFakeErasureCodingPolicy(Path path);
         public abstract void setErasureCodingPolicy(Path path, String policy);
     }
 
@@ -59,27 +65,27 @@ public class TestECPolicyDisabler  {
     @Test
     public void testNotSupported() {
         FileSystem fs = mock(FileSystem.class);
-        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null);
+        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null, FAKE_METHOD_NAME);
         Assert.assertEquals("result is expected", Result.NOT_SUPPORTED, result);
     }
 
     @Test
     public void testOkNotChanged() {
         MockDistributedFileSystem fs = mock(MockDistributedFileSystem.class);
-        when(fs.getErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.DEFAULT);
-        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null);
+        when(fs.getFakeErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.DEFAULT);
+        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null, FAKE_METHOD_NAME);
         assertEquals("result is expected", Result.ALREADY_SET, result);
-        verify(fs).getErasureCodingPolicy(any());
+        verify(fs).getFakeErasureCodingPolicy(any());
         verifyNoMoreInteractions(fs);
     }
 
     @Test
     public void testOkChanged() {
         MockDistributedFileSystem fs = mock(MockDistributedFileSystem.class);
-        when(fs.getErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
-        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null);
+        when(fs.getFakeErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
+        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null, FAKE_METHOD_NAME);
         assertEquals("result is expected", Result.DONE, result);
-        verify(fs).getErasureCodingPolicy(any());
+        verify(fs).getFakeErasureCodingPolicy(any());
         verify(fs).setErasureCodingPolicy(any(), eq("DEFAULT"));
         verifyNoMoreInteractions(fs);
     }
@@ -87,11 +93,11 @@ public class TestECPolicyDisabler  {
     @Test
     public void testServerNotSupports() {
         MockDistributedFileSystem fs = mock(MockDistributedFileSystem.class);
-        when(fs.getErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
+        when(fs.getFakeErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
         Mockito.doThrow(createNoSuchMethodException()).when(fs).setErasureCodingPolicy(any(), any());
-        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null);
+        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null, FAKE_METHOD_NAME);
         assertEquals("result is expected", Result.NO_SUCH_METHOD, result);
-        verify(fs).getErasureCodingPolicy(any());
+        verify(fs).getFakeErasureCodingPolicy(any());
         verify(fs).setErasureCodingPolicy(any(), eq("DEFAULT"));
         verifyNoMoreInteractions(fs);
     }
@@ -99,35 +105,35 @@ public class TestECPolicyDisabler  {
     @Test
     public void testServerNotSupportsGetErasureCodingPolicyMethod() {
         MockDistributedFileSystem fs = mock(MockDistributedFileSystem.class);
-        when(fs.getErasureCodingPolicy(any(Path.class))).thenThrow(createNoSuchMethodException());
-        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, mock(Path.class));
+        when(fs.getFakeErasureCodingPolicy(any(Path.class))).thenThrow(createNoSuchMethodException());
+        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, mock(Path.class), FAKE_METHOD_NAME);
         assertEquals("result is expected", Result.NO_SUCH_METHOD, result);
-        verify(fs).getErasureCodingPolicy(any(Path.class));
+        verify(fs).getFakeErasureCodingPolicy(any(Path.class));
         verifyNoMoreInteractions(fs);
     }
 
     @Test
     public void testServerNotSupportsGetName() {
         MockDistributedFileSystem fs = mock(MockDistributedFileSystem.class);
-        when(fs.getErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
+        when(fs.getFakeErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
 
         ReplicationPolicy mockPolicy = mock(ReplicationPolicy.class);
         SystemErasureCodingPolicies.setSystemPolicy(mockPolicy);
         when(mockPolicy.getName()).thenThrow(createNoSuchMethodException());
-        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null);
+        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null, FAKE_METHOD_NAME);
         assertEquals("result is expected", Result.NO_SUCH_METHOD, result);
-        verify(fs).getErasureCodingPolicy(any());
+        verify(fs).getFakeErasureCodingPolicy(any());
         verifyNoMoreInteractions(fs);
     }
 
     @Test
     public void testServerNotSupportsSetErasureCodingPolicyMethod() {
         MockDistributedFileSystem fs = mock(MockDistributedFileSystem.class);
-        when(fs.getErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
+        when(fs.getFakeErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
         Mockito.doThrow(createNoSuchMethodException()).when(fs).setErasureCodingPolicy(any(), any());
-        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null);
+        ECPolicyDisabler.Result result = ECPolicyDisabler.check(fs, null, FAKE_METHOD_NAME);
         assertEquals("result is expected", Result.NO_SUCH_METHOD, result);
-        verify(fs).getErasureCodingPolicy(any());
+        verify(fs).getFakeErasureCodingPolicy(any());
         verify(fs).setErasureCodingPolicy(any(), eq("DEFAULT"));
         verifyNoMoreInteractions(fs);
     }
@@ -135,15 +141,15 @@ public class TestECPolicyDisabler  {
     @Test
     public void testOtherRuntimeExceptionThrown() {
         MockDistributedFileSystem fs = mock(MockDistributedFileSystem.class);
-        when(fs.getErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
+        when(fs.getFakeErasureCodingPolicy(any())).thenReturn(ReplicationPolicy.OTHER);
         Mockito.doThrow(new RuntimeException("mock io exception")).when(fs).setErasureCodingPolicy(any(), any());
         try {
-            ECPolicyDisabler.check(fs, null);
+            ECPolicyDisabler.check(fs, null, FAKE_METHOD_NAME);
             Assert.fail("exception expected");
         } catch (RuntimeException e) {
             assertNotNull("runtime exception got", e);
         }
-        verify(fs).getErasureCodingPolicy(any());
+        verify(fs).getFakeErasureCodingPolicy(any());
         verify(fs).setErasureCodingPolicy(any(), eq("DEFAULT"));
         verifyNoMoreInteractions(fs);
     }
EOF



apt-get install -y patch
# 1) TestECPolicyDisabler.java
# patch 파일 현재 디렉토리로 가져오기

# patch 명령 적용
# patch [-p숫자] [패치를 적용할 파일] < 패치파일.patch
cd /install-files/oozie-5.2.1/tools/src/test/java/org/apache/oozie/tools
patch -p9 TestECPolicyDisabler.java < TestECPolicyDisabler.v0.patch
cd /install-files/oozie-5.2.1/tools/src/main/java/org/apache/oozie/tools
patch -p9 ECPolicyDisabler.java < ECPolicyDisabler.v0.patch
# /install-files/oozie-5.2.1/distro/target/oozie-5.2.1-distro.tar.gz  
mv /install-files/oozie-5.2.1/distro/target/oozie-5.2.1-distro.tar.gz /opt/ && cd /opt && tar xfv oozie-5.2.1-distro.tar.gz && rm oozie-5.2.1-distro.tar.gz

# extJS 2.2  
cd /install-files
wget http://archive.cloudera.com/gplextras/misc/ext-2.2.zip  

# mkdir -p /var/log/oozie && chown -R hdfs /var/log/oozie
# mkdir -p /var/lib/oozie/data && chown -R hdfs /var/lib/oozie
mkdir -p /var/log/oozie 
mkdir -p /var/lib/oozie/data
ln -s /var/log/oozie /opt/oozie-5.2.1/log
ln -s /var/lib/oozie/data /opt/oozie-5.2.1/data

mkdir /opt/oozie-5.2.1/libext
cp /install-files/ext-2.2.zip /opt/oozie-5.2.1/libext/
/opt/oozie-5.2.1/bin/oozie-setup.sh prepare-war

# ADD https://github.com/jcassee/parameterized-entrypoint/releases/download/0.9.0/entrypoint_linux_amd64 /usr/local/bin/entrypoint
# RUN chmod +rx /usr/local/bin/entrypoint
# COPY core-site.xml.tmpl /templates/opt/oozie-4.2.0/conf/hadoop-conf/core-site.xml
cat << EOF |tee /opt/oozie-5.2.1/conf/hadoop-conf/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>{{ FS_DEFAULTFS }}</value>
    </property>
    <property>
        <name>mapreduce.jobtracker.kerberos.principal</name>
        <value>mapred/_HOST@LOCALREALM</value>
    </property>
    <property>
      <name>yarn.resourcemanager.principal</name>
      <value>yarn/_HOST@LOCALREALM</value>
    </property>
    <property>
        <name>dfs.namenode.kerberos.principal</name>
        <value>hdfs/_HOST@LOCALREALM</value>
    </property>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
</configuration>
EOF

# # Oozie web ports ( API; admin ui )
# EXPOSE 11000 11001
# RUN chown -R hdfs /opt/oozie-4.2.0
# USER hdfs
# ENV PATH $PATH:/opt/oozie-4.2.0/bin



oozie-setup.sh sharelib create -fs hdfs://namenode:port

docker run -d --name oozie -p 10000:11000 -p 10001:11001 shwsun/oozie oozied.sh run
```