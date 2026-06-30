# Linux 基础命令速查

## 1. 文件与目录

```bash
ls -alh        # 列目录（含隐藏）
cd /path       # 切换目录
pwd            # 当前目录
mkdir -p a/b   # 递归创建
rm -rf file    # 删除（谨慎）
cp -a src dst  # 保留属性拷贝
mv a b         # 移动/改名
find . -name "*.log" -mtime +7 -delete  # 删除 7 天前日志
```

## 2. 查看与编辑

```bash
cat file
less -S file
tail -f app.log
head -n 20 file
wc -l file     # 行数
nl file        # 行号
sed -n '1,50p' file
awk -F, '{print $1,$3}' data.csv
```

## 3. 权限与账号

```bash
chmod 640 file
chown user:group file
useradd -m app
passwd app
usermod -aG docker app
groups app
```

## 4. 进程与服务

```bash
ps aux | grep nginx
pgrep -fa node
htop              # 交互式（可能需安装）
kill -9 <pid>
systemctl status nginx
systemctl enable --now nginx
journalctl -u nginx -f
```

## 5. 网络

```bash
ip addr
ip route
ss -lntp
curl -I http://localhost
nc -zv 10.0.0.5 3306
scp file user@host:/path
rsync -avz src/ user@host:/dst/
```

## 6. 磁盘与文件系统

```bash
df -h
lsblk -f
du -sh * | sort -h
mount | column -t
truncate -s 0 app.log
lsof +L1        # 找到已删除但被占用的文件
```

## 7. 压缩与打包

```bash
tar -czf backup_$(date +%F).tar.gz /data
zip -r logs.zip logs/
7z a data.7z /data   # 需安装 p7zip-full
```

## 8. 定时任务

```bash
crontab -e
# 每晚 2 点备份
0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

## 9. 包管理

```bash
# Debian/Ubuntu
apt-get update && apt-get install -y pkg
# CentOS/RHEL
yum install -y pkg
```

## 10. 常见技巧

```bash
# 替换文件中字符串（原地备份）
sed -i.bak 's@http://@https://@g' config.conf
# 并行处理
echo -e "a\nb\nc" | xargs -I{} -P 4 bash -c 'echo {} && sleep 1'
# 端口占用
lsof -i :8080
```
