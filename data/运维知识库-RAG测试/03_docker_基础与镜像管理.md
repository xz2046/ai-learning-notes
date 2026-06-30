# Docker 基础与镜像管理

## 1. Docker 架构

- Client：`docker` CLI 或 API 客户端。
- Daemon：`dockerd`，负责镜像、容器、网络、存储。
- Registry：镜像仓库（Docker Hub、Harbor、阿里云等）。

## 2. 安装与配置

### 2.1 安装（Ubuntu）

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

### 2.2 国内加速与基础配置

`/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://hub-mirror.c.163.com"
  ],
  "data-root": "/var/lib/docker",
  "log-driver": "json-file",
  "log-opts": {"max-size": "100m", "max-file": "3"},
  "exec-opts": ["native.cgroupdriver=systemd"]
}
```

```bash
sudo systemctl enable --now docker
sudo systemctl restart docker
```

## 3. 镜像管理

- 查找：`docker search nginx`
- 拉取：`docker pull nginx:1.25`
- 列表：`docker images`
- 删除：`docker rmi <IMAGE_ID>`
- 清理悬挂层：`docker image prune -f`

### 3.1 构建镜像

`Dockerfile` 示例：

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]
```

构建与推送：

```bash
docker build -t registry.example.com/demo/web:1.0 .
docker login registry.example.com
docker push registry.example.com/demo/web:1.0
```

### 3.2 多阶段构建

```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist/ /usr/share/nginx/html/
```

## 4. 容器运行与调试

- 运行：`docker run -d --name web -p 8080:80 nginx:alpine`
- 进入：`docker exec -it web /bin/sh`
- 日志：`docker logs -f web`
- 资源限制：`-m 512m --cpus 1.0`
- 自动重启：`--restart=always`

## 5. 存储与挂载

- 匿名卷：由 Docker 管理生命周期。
- 命名卷：`docker volume create data01`；跨容器共享。
- 绑定挂载：`-v /host/path:/container/path:ro`；方便开发、需注意权限。

示例：

```bash
docker run -d --name mysql \
  -v mysql_data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=secret \
  -p 3306:3306 mysql:8
```

## 6. 网络与端口

- bridge（默认）：NAT 转发，容器互联通过名称解析。
- host：共享宿主网络，性能高但隔离弱。
- none：无网络。
- 自定义网络：

```bash
docker network create --driver bridge app_net
docker run --network app_net --name api -d api:1.0
docker run --network app_net --name web -d -p 80:80 web:1.0
```

## 7. Docker Compose 快速上手

`compose.yaml`：

```yaml
version: "3.9"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
  api:
    build: ./api
    depends_on: [db]
    environment:
      DATABASE_URL: postgres://postgres:secret@db:5432/postgres
  web:
    build: ./web
    ports:
      - "8080:80"
    depends_on: [api]
volumes:
  pgdata:
```

启动：`docker compose up -d`

## 8. 安全与最佳实践

- 最小化镜像（alpine/distroless），降低 CVE 面积。
- 固定版本与摘要（`image@sha256:...`）。
- 非 root 用户运行：`USER appuser`。
- 定期扫描镜像漏洞（Trivy、Grype）。
- 只开放必要端口与 capabilities。

## 9. 常见问题排查

- 构建失败：检查缓存、网络代理、私有仓库权限。
- 容器起不来：`docker logs`、`docker inspect` 查看退出码与健康检查。
- 端口冲突：`ss -lntp | grep :<port>`。
- 磁盘爆满：`docker system df`、`docker system prune`。
