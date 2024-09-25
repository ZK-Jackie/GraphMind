FROM redis/redis-stack-server
LABEL authors="ZK-Jackie"

# TODO 以 redis 为基石，下载 neo4j 入容器，配置好数据库 + 外挂数据库 + 配置文件

EXPOSE 6379 7474 7473 7687
ENTRYPOINT ["top", "-b"]