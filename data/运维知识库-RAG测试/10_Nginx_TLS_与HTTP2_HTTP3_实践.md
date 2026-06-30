# Nginx 的 TLS、HTTP/2 与 HTTP/3 实践

## 1. 证书准备

- 使用 ACME（Let's Encrypt）或商用证书。
- 密钥权限：`chmod 600`，仅 Nginx 用户可读。

## 2. 基础 TLS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name www.example.com;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384';
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
}
```

## 3. HTTP/2 注意事项

- 多路复用改善高延迟网络下的吞吐，TLS 基本必需（浏览器端）。
- 调整 `http2_max_concurrent_streams`、`http2_chunk_size` 根据负载优化。
- 避免域名分片，HTTP/2 下单连接已足够；多域名共享一个连接。

## 4. HTTP/3（QUIC）

- 需要 Nginx QUIC 分支或支持 QUIC 的发行版（如 nginx-quic）。
- 监听 UDP 443，配置 `quic`：

```nginx
server {
    listen 443 quic reuseport;
    listen 443 ssl http2;
    add_header Alt-Svc 'h3=":443"; ma=86400';
    add_header QUIC-Status $quic;
}
```

- 防火墙必须放通 UDP/443，客户端先试 HTTP/3，降级到 HTTP/2。

## 5. OCSP Stapling 与会话优化

```nginx
ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 8.8.8.8 valid=300s;
resolver_timeout 5s;
```

## 6. 性能调优清单

- ECDSA 证书优先（更快握手），同时提供 RSA 兼容。
- 启用会话缓存与 0-RTT 恢复（注意重放风险，GET 幂等请求可开启）。
- TLS 记录大小调优：`ssl_buffer_size 4k;`（实验性）。
- 减少握手延迟：使用 DNS-over-HTTPS 与 ECH（Encrypted Client Hello，实验性）。

## 7. 常见问题

- 浏览器不认自签名证书：使用可信 CA 或企业内网私有 CA 并推送到客户端。
- HSTS 误配后不可逆：先短周期测试，确认无误再延长。
- HTTP/3 不生效：检查 UDP/443 端口、`Alt-Svc` 头与客户端支持。
- 证书到期：自动化续签（certbot + cron/systemd timer）。

## 8. 安全加固

- 禁用不安全的协议版本：不启用 TLSv1.0/1.1 和 SSLv3。
- 使用强密码套件，移除 CBC 模式与弱哈希。
- 配置 `ssl_early_data on;` 时评估重放攻击风险。
- 定期用 SSL Labs 或 testssl.sh 扫描评分。