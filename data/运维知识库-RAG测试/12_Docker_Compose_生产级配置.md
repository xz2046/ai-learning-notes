# Docker Compose 生产级配置实战

## 1. 项目结构

```
project/
├── compose.yaml
├── .env
├── nginx/
│   ├── Dockerfile
│   └── conf.d/
│       └── default.conf
├── api/
│   ├── Dockerfile
│   └── app/
└── scripts/
    └── backup.sh
```

## 2. compose.yaml 完整示例

```yaml
version: "3.9"
services:
  nginx:
    build: ./nginx
    image: registry.example.com/prod/nginx:${TAG:-latest}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - certs:/etc/nginx/certs:ro
    depends_on:
      - api
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "20m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3

  api:
    build: ./api
    image: registry.example.com/prod/api:${TAG:-latest}
    expose:
      - "8080"
    environment:
      DB_HOST: db
      DB_PORT: "5432"
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 15s
      timeout: 3s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
  certs:
```

## 3. .env 文件

```
TAG=v1.2.3
DB_NAME=myapp
DB_USER=myappuser
DB_PASSWORD=<换真实密码>
```

> `.env` 不要提交到 git；使用 vault/sops 管理生产密码。

## 4. 启动与运维

```bash
# 构建并启动
docker compose build
docker compose up -d

# 查看状态
docker compose ps
docker compose logs -f api

# 滚动更新单服务（不中断）
docker compose up -d --no-deps --build api

# 优雅停止
docker compose down --remove-orphans
```

## 5. 资源限制

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 128M
```

## 6. 网络隔离

```yaml
services:
  api:
    networks:
      - backend
  nginx:
    networks:
      - frontend
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true   # 不暴露到宿主机
```

## 7. 备份与恢复

```bash
# 备份 PostgreSQL
docker compose exec db pg_dump -U myappuser myapp > backup_$(date +%F).sql
# 备份卷
docker run --rm -v pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata.tar.gz -C /data .
```

## 8. 安全建议

- 构建时用固定版本 digest（`image@sha256:...`）。
- 非 root 运行：`user: "1000:1000"`。
- 敏感信息使用 Docker secrets（Swarm）或外部密钥服务。
- 定期扫描镜像漏洞并更新。