# run spark (scala)
in scala metal prj folder
```bash
# ./.build.sbt
sbt package 
# after packaging completed you can find resulting .jar in ./target/scala-x.x/*.jar  
```
  
copy .jar to run folder.  
  
in run folder 
```bash
spark-submit --class "Main" --master local[4] hello-world_2.13-1.0.jar  
  
spark-submit --class SimpleApp simple-project_2.12-1.0.jar
spark-submit --class SimpleApp --master local[2] simple-project_2.12-1.0.jar
```