# ZhengXuQiao Website Tunnel Manager Service

## 概述

本服务用于管理zhengxuqiao.github.io网站的隧道配置，自动从cpolar日志中提取隧道信息并更新tunnel.json文件，然后执行上传脚本。

## 安装说明

### 1. 复制服务文件

将`zhengxuqiao.service`文件复制到`/etc/systemd/system/`目录下：

```bash
sudo cp zhengxuqiao.service /etc/systemd/system/
```

### 2. 重新加载systemd配置

```bash
sudo systemctl daemon-reload
```

### 3. 启用服务

设置服务开机自启：

```bash
sudo systemctl enable zhengxuqiao.service
```

### 4. 启动服务

```bash
sudo systemctl start zhengxuqiao.service
```

## 服务管理

### 查看服务状态

```bash
sudo systemctl status zhengxuqiao.service
```

### 停止服务

```bash
sudo systemctl stop zhengxuqiao.service
```

### 重启服务

```bash
sudo systemctl restart zhengxuqiao.service
```

### 查看服务日志

```bash
sudo journalctl -u zhengxuqiao.service
# 实时查看日志
sudo journalctl -u zhengxuqiao.service -f
```

## 配置说明

服务文件中的主要配置项：

- `User=pi`: 以pi用户身份运行服务
- `WorkingDirectory=/home/pi/Desktop/zhengxuqiao.github.io`: 工作目录
- `ExecStart=/usr/bin/python3 /home/pi/Desktop/zhengxuqiao.github.io/cmd/cmd.py`: 执行的命令
- `Restart=on-failure`: 失败时自动重启
- `RestartSec=5`: 重启间隔为5秒

## 注意事项

1. 确保cpolar服务已经安装并正在运行
2. 确保脚本有执行权限：
   ```bash
   chmod +x /home/pi/Desktop/zhengxuqiao.github.io/cmd/cmd.py
   chmod +x /home/pi/Desktop/zhengxuqiao.github.io/upload-cmd.sh
   ```
3. 确保日志目录存在：
   ```bash
   mkdir -p /home/pi/Desktop/zhengxuqiao.github.io/cmd/log
   ```
4. 确保tunnel.json文件有正确的权限：
   ```bash
   touch /home/pi/Desktop/zhengxuqiao.github.io/tunnel.json
   chown pi:pi /home/pi/Desktop/zhengxuqiao.github.io/tunnel.json
   ```

## 卸载说明

1. 停止服务：
   ```bash
   sudo systemctl stop zhengxuqiao.service
   ```

2. 禁用服务：
   ```bash
   sudo systemctl disable zhengxuqiao.service
   ```

3. 删除服务文件：
   ```bash
   sudo rm /etc/systemd/system/zhengxuqiao.service
   ```

4. 重新加载systemd配置：
   ```bash
   sudo systemctl daemon-reload
   ```

## 与旧版本的区别

1. 用Linux systemd服务管理
2. 自动重启功能，提高可靠性
3. 更好的日志管理
4. 开机自启功能

## 故障排查

如果服务无法启动或运行不正常，可以通过以下方式排查：

1. 查看服务状态和日志
2. 检查脚本路径和权限
3. 检查工作目录是否正确
4. 检查依赖服务是否正常运行
5. 手动运行脚本，查看是否有错误输出：
   ```bash
   cd /home/pi/Desktop/zhengxuqiao.github.io
   python3 /home/pi/Desktop/zhengxuqiao.github.io/cmd/cmd.py
   ```