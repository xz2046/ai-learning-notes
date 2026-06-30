# Linux Shell 脚本编写规范

## 1. 基本要求

- 使用 `#!/bin/bash`，不用 `/bin/sh`（避免不同系统 bash 行为差异）。
- 启用严格模式：`set -euo pipefail`。
  - `-e`：命令失败立即退出。
  - `-u`：使用未定义变量时报错。
  - `-o pipefail`：管道中任一命令失败则整体失败。
- 脚本头部加注释说明用途、参数、作者、日期。

```bash
#!/bin/bash
set -euo pipefail
# 用途：数据库备份脚本
# 参数：$1 - 备份目标目录
# 日期：2024-06-01
```

## 2. 变量与引用

- 变量赋值不加空格：`name="hello"`。
- 使用变量时加双引号，防止分词与通配展开：`echo "$path"`。
- 默认值：`${VAR:-default}`、`${VAR:=default}`。
- 只读常量：`readonly CONF="/etc/app.conf"` 或 `declare -r CONF="/etc/app.conf"`。

## 3. 条件判断

```bash
# 文件测试
if [[ -f "$file" ]]; then ... fi
if [[ ! -d "$dir" ]]; then ... fi

# 字符串
if [[ "$a" == "$b" ]]; then ... fi
if [[ -z "$str" ]]; then ... fi

# 数值
if (( count > 10 )); then ... fi
```

> 推荐 `[[ ]]` 而非 `[ ]`：更安全，支持 `&&`/`||` 和正则。

## 4. 循环与函数

```bash
# for 循环
for host in node{1..5}; do
    echo "Pinging $host"
    ping -c 1 "$host" &>/dev/null || echo "FAIL: $host"
done

# while 读取文件
while IFS= read -r line; do
    echo "$line"
done < /etc/hosts

# 函数
log() {
    local level="$1"
    local msg="$2"
    echo "[$(date +'%F %T')] [$level] $msg" >&2
}
log INFO "服务启动"
```

## 5. 输入输出与重定向

```bash
# 读取用户输入
read -rp "确认操作 (y/N): " confirm
[[ "$confirm" != "y" ]] && exit 0

# 重定向
command > stdout.log 2> stderr.log
command &> all.log         # 合并输出
command > /dev/null 2>&1   # 静默

# 临时文件（安全）
tmpfile=$(mktemp /tmp/myscript.XXXXXX)
trap 'rm -f "$tmpfile"' EXIT
```

## 6. 错误处理与退出

```bash
cleanup() {
    echo "清理资源..."
}
trap cleanup EXIT

fatal() {
    echo "ERROR: $*" >&2
    exit 1
}
[[ -f "$config" ]] || fatal "配置文件不存在: $config"
```

## 7. 日志规范

```bash
log_info()  { echo "[$(date +%F_%T)] [INFO] $*"; }
log_warn()  { echo "[$(date +%F_%T)] [WARN] $*" >&2; }
log_error() { echo "[$(date +%F_%T)] [ERROR] $*" >&2; }
```

生产脚本应同时写日志文件：`exec &> >(tee -a "$LOGFILE")`

## 8. 调试技巧

```bash
# 逐行执行并打印
bash -x script.sh

# 脚本内局部调试
set -x
# 待调试代码
set +x

# 打印调用栈（适合 trap 中使用）
trap 'echo "行 $LINENO 出错，退出码: $?"' ERR
```

## 9. 生产环境 checklist

- [ ] 脚本可重复执行（幂等性）。
- [ ] 敏感信息不硬编码，走环境变量或密钥管理。
- [ ] 超时保护（`timeout` 命令或 `read -t`）。
- [ ] 并发锁：`flock` 防止重入。
- [ ] 对路径加引号，防止空格与特殊字符。