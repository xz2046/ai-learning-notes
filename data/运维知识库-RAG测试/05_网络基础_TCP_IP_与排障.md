# 网络基础：TCP/IP 与排障

## 1. OSI 与 TCP/IP 模型

- OSI 七层：物理、数据链路、网络、传输、会话、表示、应用。
- TCP/IP 四层：链路、网络、传输、应用。
- 排障时通常关注三层（IP）、四层（TCP/UDP）、七层（HTTP 等）。

## 2. IP、子网与路由

- IPv4：32 位地址，CIDR 表示法（如 `192.168.1.0/24`）。
- 子网掩码：决定网络号与主机号。
- 路由：主机通过默认网关将非本地流量转发。

常用命令：

```bash
ip addr
ip route
ping 8.8.8.8
traceroute 8.8.8.8
```

## 3. ARP 与 DNS

- ARP：将 IP 解析为 MAC，二层通信必需。
- DNS：将域名解析为 IP。

诊断：

```bash
arp -n
nslookup example.com
```

## 4. TCP 三次握手与四次挥手

- 三次握手：SYN → SYN/ACK → ACK；建立连接。
- 四次挥手：FIN/ACK 两对；TIME_WAIT 资源回收。
- 常见问题：半连接、SYN flood、过多 TIME_WAIT。

调优：

- `net.ipv4.tcp_synack_retries`、`tcp_tw_reuse`（注意内核版本与语义变化）。

## 5. 常见协议与端口

- HTTP/HTTPS：80/443
- SSH：22
- MySQL：3306, PostgreSQL：5432
- Redis：6379
- Kafka：9092

## 6. 抓包与分析

```bash
tcpdump -i eth0 port 80 -nn -vv -w http.cap
wireshark http.cap
```

过滤示例：

- 只看 TCP 握手：`tcp[tcpflags] & (tcp-syn|tcp-ack) != 0`
- 只看某 IP：`host 10.0.0.5`

## 7. 防火墙与 NAT

- `iptables`/`nftables`：Linux 包过滤与 NAT。
- DNAT：目的地址转换；SNAT/MASQUERADE：源地址转换。

示例：

```bash
# 放通 80/443
iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT
# SNAT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

## 8. 负载均衡基础

- 四层（L4）：基于 IP/端口转发（LVS、HAProxy TCP）。
- 七层（L7）：理解协议的转发（Nginx、Envoy）。
- 指标：吞吐、时延、并发连接数、后端健康。

## 9. 常见排障思路

- 分层定位：链路 → 网络 → 传输 → 应用。
- 单向可达 vs 双向可达：路由与防火墙是否对称。
- DNS vs IP：先用 IP 验证联通性，排除 DNS 问题。
- 延迟 vs 丢包：`mtr` 观察；抖动大多与队列/带宽有关。

常用工具：`ping`/`mtr`、`traceroute`、`nc`、`curl -v`、`ss -lntp`。

## 10. 性能与调优

- MTU/MSS：不匹配引发分片或丢包，尤其是隧道与云厂商场景。
- BDP（带宽时延积）：大带宽链路需要增大窗口（`tcp_window_scaling`）。
- 队列与拥塞控制算法：`bbr` 对长肥管道效果佳。

```bash
sysctl -w net.ipv4.tcp_congestion_control=bbr
sysctl -w net.core.default_qdisc=fq
```
