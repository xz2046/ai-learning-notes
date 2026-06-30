# Linux 权限、进程与系统管理

## 1. 权限模型

- 用户/组/其它（ugo）+ 读写执行（rwx）。
- 特殊位：SUID、SGID、sticky。
- umask：新建文件/目录的默认权限屏蔽。

```bash
chmod u+s /usr/bin/somebin   # SUID，执行时以文件属主身份运行
chmod g+s /data/shared       # SGID，目录中文件继承组
chmod +t /tmp                # sticky，只有属主可删
```

## 2. ACL 与 Capabilities

```bash
# ACL：细粒度权限
setfacl -m u:app:rw file
getfacl file

# Linux capabilities：更细的特权控制
setcap cap_net_bind_service=+ep /usr/bin/myapp
getcap /usr/bin/myapp
```

## 3. 进程与调度

- 进程状态：R 运行，S 睡眠，D 不可中断，Z 僵尸。
- nice/priority：CPU 调度优先级。
- cgroups：资源限制与隔离（容器基础）。

```bash
renice -n 10 -p <pid>
ionice -c2 -n7 -p <pid>
```

## 4. systemd 基础

- 单元类型：service、timer、socket、mount 等。
- 依赖：`After=`、`Requires=`、`Wants=`。

示例服务：`/etc/systemd/system/myapp.service`

```ini
[Unit]
Description=My App
After=network.target

[Service]
User=app
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/myapp --port 8080
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now myapp
journalctl -u myapp -f
```

## 5. 日志管理

- systemd-journald：`journalctl` 查询。
- rsyslog：写入文件/远端。
- logrotate：切割与保留策略。

`/etc/logrotate.d/myapp`：

```
/var/log/myapp/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    copytruncate
}
```

## 6. 内核与参数

```bash
uname -a
sysctl -a | grep tcp
cat /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1
```

持久化：`/etc/sysctl.d/99-sysctl.conf`。

## 7. 硬件与性能

```bash
lscpu
free -h
iostat -xm 1   # 需安装 sysstat
vmstat 1
sar -n DEV 1 5
```

## 8. 安全基础

- SSH：禁用密码登录，使用密钥；限制 root 登录。
- 防火墙：基于最小权限；入站默认拒绝。
- 漏洞：定期更新内核/包；使用自动化扫描。
- 审计：`auditd` 记录关键操作。

## 9. 故障应急

- CPU 飙高：定位进程 `top`/`htop` → `perf`/`strace`。
- I/O 瓶颈：`iostat`/`iotop`；检查磁盘与队列。
- 内存泄漏：`pmap`/`smem`；检查大页、cache；必要时重启服务。
- 网络不通：`ip route`、`ss -lntp`、`tcpdump`。

## 10. 最佳实践清单

- 明确文件与目录权限，最小化特权运行。
- 所有服务纳入 systemd 管理，统一日志。
- 关键参数配置化（sysctl、limits）。
- 使用配置管理工具保持一致性（Ansible 等）。
- 变更前快照/备份，变更后回滚预案。
