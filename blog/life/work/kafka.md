# 启动流程

- Kafka KRaft 模式下，必须配置 controller.quorum.voters 参数，指定哪些节点是 controller。
- 并且修改自定义log.dirs目录

1. 在 server.properties 文件中添加如下配置（假设你本机 node.id=1，监听端口 9093）：

```properties
controller.quorum.voters=1@localhost:9093
```

2. 保存 server.properties 后，重新执行格式化命令：

```powershell
bin\windows\kafka-storage.bat format -t ahcHZfIvRkWYPgORqGsIxg -c config\server.properties
```

3. 然后再启动 Kafka：

```powershell
bin\windows\kafka-server-start.bat config\server.properties
```

说明：
- controller.quorum.voters 的格式为：node.id@host:port，单节点就写一个，多节点用逗号分隔。
- 你只需在 server.properties 里加这一行即可解决问题。
# 众多的端口问题


# 可视化问题

下载使用 [kafka-ui](https://github.com/provectus/kafka-ui)

并启动ssl加密通信和指定web监听端口

```

```cmd
java --add-opens java.rmi/javax.rmi.ssl=ALL-UNNAMED -jar kafka-ui-api-v0.7.2.jar --server.port=8090 --kafka.clusters[0].name=local --kafka.clusters[0].bootstrapServers=localhost:9092
```


## 并发性

即使不能类似http请求点对点的传输更有实时性，但是允许多个消费者并发处理，因此其实速度不一定会在高峰期大幅度下降。

但硬要说，队列之中依旧要排队，即时性不如直接使用网络，但是能胜任高并发和异步，并且解耦，我是非常讨厌使用python进行业务服务框架的搭建。WebSocket 适合前端实时推送但不适合服务间高并发通信。