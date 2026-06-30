# Nginx 入门与安装

> 目标：快速理解 Nginx 的定位与核心概念，完成常见平台的安装与基础验证。

## 1. Nginx 是什么

- 一个高性能的 HTTP 服务器与反向代理服务器。
- 事件驱动模型，适合高并发、低内存占用场景。
- 常见用途：静态资源服务、反向代理、负载均衡、API 网关、SSL/TLS 终止。

## 2. 核心概念

- master/worker 进程：master 接收信号、管理 worker；worker 处理请求。
- 模块化：核心 + 各类模块（HTTP、Stream、Mail 等）。
- 配置层级：`main` → `http` → `server` → `location`，从外到内逐层生效。
- 上游（upstream）：Nginx 作为代理时的后端服务池。

## 3. 安装方式概览

- 包管理器安装：方便、稳定，版本可能滞后。
- 官方仓库：稳定及时，推荐生产使用。
- 源码编译：可选模块更丰富，维护成本高。

## 4. 在常见系统上安装

### 4.1 Debian/Ubuntu（使用官方仓库）

```bash
sudo apt-get update
sudo apt-get install -y curl gnupg2 ca-certificates lsb-release ubuntu-keyring
curl -fsSL https://nginx.org/keys/nginx_signing.key | gpg --dearmor | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/$(. /etc/os-release && echo $ID) $(lsb_release -cs) nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
sudo apt-get update
sudo apt-get install -y nginx
```

验证：

```bash
nginx -v
sudo systemctl enable --now nginx
curl -I http://127.0.0.1
```

### 4.2 CentOS/RHEL

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo http://nginx.org/packages/centos/$releasever/$basearch/
sudo yum install -y nginx
sudo systemctl enable --now nginx
nginx -V
```

### 4.3 macOS（开发环境）

```bash
brew install nginx
brew services start nginx
open http://localhost:8080
```

> macOS 的默认端口通常为 8080，配置文件在 `/usr/local/etc/nginx/nginx.conf`。

## 5. 目录与常见配置文件

- 可执行文件：`/usr/sbin/nginx`
- 主配置：`/etc/nginx/nginx.conf`
- 站点配置：`/etc/nginx/conf.d/*.conf`（或 `/etc/nginx/sites-available` + `sites-enabled`）
- 日志目录：`/var/log/nginx/`
- 静态根目录：`/usr/share/nginx/html`

## 6. 一个最小可用配置示例

`/etc/nginx/conf.d/demo.conf`

```nginx
server {
    listen 80;
    server_name _;

    location /healthz {
        return 200 'ok';
        add_header Content-Type text/plain;
    }

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
}
```

重载与检查：

```bash
sudo nginx -t
sudo nginx -s reload
```

## 7. 常用管理命令

```bash
# 语法检查
ginx -t
# 平滑重载
nginx -s reload
# 停止（快速/优雅）
nginx -s stop
nginx -s quit
# systemd
systemctl status nginx
journalctl -u nginx -f
```

## 8. 基础性能与连接参数

在 `http` 段加入：

```nginx
worker_processes auto;
events {
    worker_connections  10240;  # 单 worker 最大并发连接数
}
http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 4096;
}
```

## 9. 排障清单（Checklist）

- 端口占用：`ss -lntp | grep :80`
- SELinux/防火墙：开放 80/443；或暂时 `setenforce 0`（生产请按策略放行）。
- 配置语法：`nginx -t` 必过。
- 日志：`/var/log/nginx/error.log`、`access.log`。
- 权限：静态目录与用户（`user nginx;`）读权限是否正确。

## 10. 最佳实践

- 使用官方仓库保持稳定版本。
- 配置拆分：每个站点单独文件，便于管理。
- 变更先 `-t` 检查，再 `-s reload`。
- 打开访问与错误日志，结合 logrotate 管理体积。
- 最小权限运行，避免给配置与目录多余写权限。
