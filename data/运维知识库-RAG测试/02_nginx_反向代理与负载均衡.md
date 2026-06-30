# Nginx 反向代理与负载均衡

## 1. 反向代理基础

- 反向代理将客户端请求转发到后端服务，隐藏后端真实地址。
- 常与缓存、压缩、限流、WAF 配合使用。

最小示例：

```nginx
server {
    listen 80;
    server_name example.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 2. 上游（upstream）与负载均衡

```nginx
upstream api_backend {
    least_conn;             # 最少连接
    server 10.0.0.10:8080 max_fails=3 fail_timeout=10s;
    server 10.0.0.11:8080 max_fails=3 fail_timeout=10s;
    server 10.0.0.12:8080 backup;  # 备机
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://api_backend;
    }
}
```

支持策略：`round_robin`（默认）、`ip_hash`、`least_conn`、`hash`（商业版有更多）。

## 3. 健康检查与熔断

开源版可借助 `max_fails`/`fail_timeout` 实现基础熔断，或使用第三方模块/商业版主动健康检查。

```nginx
upstream api_backend {
    server 10.0.0.10:8080 max_fails=2 fail_timeout=5s;
    server 10.0.0.11:8080 max_fails=2 fail_timeout=5s;
}

map $upstream_http_x_health $backend_ok {
    default 1;
    "down" 0;
}
```

## 4. 超时时间与缓冲

```nginx
proxy_connect_timeout 3s;
proxy_send_timeout 30s;
proxy_read_timeout 30s;
proxy_buffering on;
proxy_buffers 32 64k;
proxy_busy_buffers_size 128k;
proxy_max_temp_file_size 0; # 禁用大文件落盘
```

## 5. WebSocket 与长连接

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 80;
    location /ws {
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_pass http://127.0.0.1:7001;
    }
}
```

## 6. HTTPS 反代与证书

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://api_backend;
    }
}
```

HTTP → HTTPS 跳转：

```nginx
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}
```

## 7. 缓存与静态加速

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=mycache:100m max_size=10g inactive=1h use_temp_path=off;

server {
    location /img/ {
        proxy_cache mycache;
        proxy_cache_key "$scheme$proxy_host$request_uri";
        proxy_cache_valid 200 301 302 10m;
        proxy_hide_header Set-Cookie;
        add_header X-Cache-Status $upstream_cache_status;
        proxy_pass http://img_backend;
    }
}
```

## 8. 限流与防护

```nginx
# 基于 IP 的并发/速率限制
limit_conn_zone $binary_remote_addr zone=addr:10m;
limit_req_zone $binary_remote_addr zone=req10r:10m rate=10r/s;

server {
    location /api/ {
        limit_conn addr 50;
        limit_req zone=req10r burst=20 nodelay;
        proxy_pass http://api_backend;
    }
}
```

## 9. 日志与追踪

```nginx
log_format json escape=json '{"time":"$time_iso8601","remote_addr":"$remote_addr","request":"$request","status":$status,"body_bytes_sent":$body_bytes_sent,"request_time":$request_time,"upstream_response_time":"$upstream_response_time","upstream_addr":"$upstream_addr"}';

access_log /var/log/nginx/access.json json;
```

## 10. 常见问题

- 502/504：后端不可达、超时或 header 过大（调大 `proxy_buffer_size`）。
- 413：请求体过大（`client_max_body_size`）。
- 499：客户端提前断开（可能是超时设置不匹配）。
- 缓存未命中：检查 `proxy_cache_key` 与 `Cache-Control`。
