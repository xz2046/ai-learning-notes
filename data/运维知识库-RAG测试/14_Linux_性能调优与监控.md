# Linux 性能调优与监控工具

## 1. 性能观测三板斧

- CPU：`top`/`htop`/`mpstat -P ALL 1`，关注 `%usr`、`%sys`、`%iowait`。
- 内存：`free -h`、`vmstat 1`，关注 `cache`、`swap`、`available`。
- I/O：`iostat -xm 1`，关注 `%util`、`await`、`r/s w/s`。

## 2. CPU 调优

```bash
# 查看频率与调速器
cpupower frequency-info
# 设为性能模式
sudo cpupower frequency-set -g performance

# 进程 CPU 亲和
taskset -cp 0-3 <pid>
```

- 中断均衡：`irqbalance` 服务自动分发。
- NUMA：`numactl --cpubind=0 --membind=0 <cmd>`。

## 3. 内存调优

- `swappiness`：降低 swap 倾向（如 `vm.swappiness=10`）。
- 大页内存：`echo 512 > /proc/sys/vm/nr_hugepages`。
- 清理缓存（测试场景）：`echo 3 > /proc/sys/vm/drop_caches`（非生产）。

## 4. 磁盘 I/O 调优

- 调度器：`cat /sys/block/sda/queue/scheduler`，NVMe 用 `none`（内核多队列）。
- 预读：`blockdev --setra 4096 /dev/sda`。
- 写屏障与挂载选项：`noatime,nodiratime,data=ordered`。

## 5. 网络调优速查

```bash
sysctl -w net.core.somaxconn=4096
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_max_syn_backlog=8192
sysctl -w net.core.netdev_max_backlog=5000
```

持久化到 `/etc/sysctl.d/99-network.conf`。

## 6. 监控工具对比

| 工具 | 用途 | 特点 |
|------|------|------|
| `top`/`htop` | 实时进程 | 轻量 |
| `vmstat` | 内存/CPU/IO 概览 | 无历史 |
| `iostat` | 磁盘 I/O | sysstat 包 |
| `sar` | 历史采集 | 定时记录 |
| `netdata` | 全栈监控 | 开箱即用 |
| `Prometheus + Grafana` | 生产级监控 | 可扩展 |
| `atop` | 进程级资源 | 历史回溯 |

## 7. flamegraph 与 perf

```bash
# 采样 30 秒
perf record -F 99 -p <pid> -g -- sleep 30
perf script > out.perf
# 使用 FlameGraph 生成 SVG（需安装脚本）
./stackcollapse-perf.pl out.perf > out.folded
./flamegraph.pl out.folded > flame.svg
```

## 8. 排查思路

- CPU 高 → `top` 找进程 → `perf top` 找函数 → 优化热点。
- 内存涨 → `pmap -x <pid>` / `smem` → `valgrind`/`heaptrack` 查泄漏。
- I/O 高 → `iotop` / `pidstat -d 1` → `strace` / `lsof` 看文件操作。
- 网络延迟 → `mtr` → `tcpdump` + `wireshark` 分析。

## 9. 基线采集

- 日常采集 `sar` 或 Prometheus node_exporter 数据。
- 对比变更前后关键指标；设立阈值告警。

## 10. 注意事项

- 调优先在测试环境验证，有回滚方案。
- 禁用 transparent hugepages 可能改善数据库性能（如 Redis/MySQL）。
- 文件描述符上限：`ulimit -n` 与 `fs.file-max` 保持一致。