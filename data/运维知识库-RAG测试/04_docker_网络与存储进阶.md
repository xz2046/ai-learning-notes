# Docker 网络与存储进阶

## 1. 网络驱动详解

- bridge：默认，基于 `iptables` 的 NAT。
- host：共享宿主机网络栈，延迟低。
- macvlan：为容器分配二层 MAC，与物理网络直连。
- overlay：跨主机网络（Swarm/K8s）。

### 1.1 macvlan 示例

```bash
# 创建子接口网段 192.168.10.0/24
sudo ip link add link eth0 macvlan0 type macvlan mode bridge
sudo ip addr add 192.168.10.2/24 dev macvlan0
sudo ip link set macvlan0 up

# Docker 网络
docker network create -d macvlan \
  --subnet=192.168.10.0/24 \
  --gateway=192.168.10.1 \
  -o parent=eth0 pub_net

docker run --network pub_net --ip 192.168.10.50 -d nginx:alpine
```

## 2. 端口映射与安全

- 避免直接暴露管理端口（如 2375、数据库端口）。
- 使用防火墙限制来源（`ufw`/`iptables`）。
- 生产环境建议通过反向代理/网关统一出口。

## 3. 服务发现与 DNS

- 同一自定义网络内：容器名即 DNS 名称。
- `docker inspect <container>` 可查看 `IPAddress`。
- 外部服务可在启动时通过 `--add-host` 注入：

```bash
docker run --add-host kafka:10.0.0.5 app:1.0
```

## 4. 存储驱动与性能

- `overlay2`：主流通用，写放大较小。
- `devicemapper`/`btrfs`：旧方案或特定场景。
- 宿主磁盘 I/O 对容器性能影响显著，建议单独数据盘。

## 5. 数据卷策略

- 业务数据使用命名卷，避免容器删除导致数据丢失。
- 配置文件使用绑定挂载，便于版本控制。
- 大文件分区/分盘，避免根分区爆满。

## 6. 备份与恢复

```bash
# 停机快照
docker run --rm --volumes-from db -v $(pwd):/backup alpine \
  tar czf /backup/pgdata_$(date +%F).tar.gz /var/lib/postgresql/data

# 恢复
docker run --rm --volumes-from db -v $(pwd):/backup alpine \
  sh -c "rm -rf /var/lib/postgresql/data/* && tar xzf /backup/pgdata_2024-01-01.tar.gz -C /"
```

## 7. 日志方案

- `json-file`：默认，结合 logrotate 控制大小。
- `syslog`/`fluentd`：集中式收集。
- `gelf`/`awslogs`：对接 ELK/Splunk/CloudWatch。

示例：

```bash
docker run -d --log-driver=gelf --log-opt gelf-address=udp://10.0.0.5:12201 app:1.0
```

## 8. 安全加固

- `--read-only` 只读根文件系统；必要目录使用 tmpfs：

```bash
docker run --read-only --tmpfs /tmp --tmpfs /run app:1.0
```

- 限制内核能力：`--cap-drop ALL` + 最小必要的 `--cap-add`。
- seccomp/apparmor：使用官方默认或自定义 profile。
- 根目录挂载保护：避免 `-v /:/host` 这类危险挂载。

## 9. 性能调优

- CPU 亲和与配额：`--cpuset-cpus 0-3 --cpus 2.0`
- 内存与 swap：`-m 1g --memory-swap 1g`
- 网络：选择合适驱动，减少跨主机转发。
- 存储：分离数据盘、合适的 I/O 调度器、启用直写缓存策略。

## 10. 常见故障与诊断

- DNS 解析慢：私网 DNS 加缓存（dnsmasq）或指定 `--dns`。
- 容器时间漂移：同步宿主机 NTP；或挂载 `/etc/localtime`。
- 日志暴涨：检查日志级别与 `log-opts`，或接入集中式。
- 文件权限问题：确认 UID/GID；尽量避免以 root 运行。
