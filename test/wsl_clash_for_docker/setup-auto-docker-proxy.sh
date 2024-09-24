#!/bin/bash

# Author: Jackie Yang
# Date: 2021-07-06
# Description:
# 1. 脚本功能说明：
#   - 本脚本用于在 WSL 中设置 Docker 的代理，以便在 WSL 中使用 Clash 代理 Docker 的网络请求。
#   - WSL 系统每次启动时，都会运行更新脚本，找寻本次启动被分配的网卡 IP 地址，设置 Docker 的代理服务器地址。
# 2. 使用方法：
#   - 请将本脚本放置在 WSL 中的任意目录下，并执行 `sudo bash setup-auto-docker-proxy.sh`。
# 3. 卸载方法：
#   - 请执行 `sudo bash setup-auto-docker-proxy.sh uninstall`。

### 1 初始化变量
# 定义更新脚本和配置文件路径
SCRIPT_PATH="/usr/local/bin/update-docker-proxy.sh" # 脚本路径
SERVICE_PATH="/etc/systemd/system/update-docker-proxy.service"  # 服务文件路径
PROXY_CONF="/etc/systemd/system/docker.service.d/http-proxy.conf" # 代理配置文件路径

# 定义代理服务器的端口号
PROXY_PORT="7890"

### 2 判断用户意图
# 判断用户是否传入了 uninstall 参数
if [ "$1" == "uninstall" ]; then
    # 停止并禁用服务
    systemctl stop update-docker-proxy.service
    systemctl disable update-docker-proxy.service

    # 删除服务文件
    rm -f "$SERVICE_PATH"

    # 删除脚本文件
    rm -f "$SCRIPT_PATH"

    # 删除代理配置文件
    rm -f "$PROXY_CONF"

    # 重新加载 systemd 管理器配置
    systemctl daemon-reload

    echo "auto-docker-proxy. Uninstall completed."
    exit 0
elif [ "$1" != "" ]; then
    # 输出帮助信息
    echo "Usage: $0 [uninstall]"
    echo "  uninstall: Uninstall auto-docker-proxy."
    echo "  no argument: Install auto-docker-proxy."
    exit 1
fi

### 3 创建更新代理的脚本
# 创建更新代理的脚本
cat <<'EOF' > "$SCRIPT_PATH"
#!/bin/bash

PROXY_CONF="/etc/systemd/system/docker.service.d/http-proxy.conf"
PROXY_PORT="7890"
PROXY_IP=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print$2}')

if [ -z "$PROXY_IP" ]; then
    echo "Failed to extract nameserver IP from /etc/resolv.conf"
    exit 1
fi

mkdir -p "$(dirname "$PROXY_CONF")"

cat <<EOF2 > "$PROXY_CONF"
[Service]
Environment="HTTP_PROXY=http://${PROXY_IP}:${PROXY_PORT}"
Environment="HTTPS_PROXY=http://${PROXY_IP}:${PROXY_PORT}"
EOF2

systemctl daemon-reload
systemctl restart docker
EOF

# 赋予执行权限
chmod +x "$SCRIPT_PATH"

### 4 创建 systemd 服务
# 创建 systemd 服务文件
cat <<'EOF' > "$SERVICE_PATH"
[Unit]
Description=Update Docker Proxy Configuration on Boot
After=network.target

[Service]
Type=oneshot
ExecStart=$SCRIPT_PATH

[Install]
WantedBy=multi-user.target
EOF

### 5 重启 Docker 服务
# 重新加载 systemd 管理器配置并启用服务
systemctl daemon-reload
systemctl enable update-docker-proxy.service

# 输出提示信息
echo "auto-docker-proxy Setup completed."
