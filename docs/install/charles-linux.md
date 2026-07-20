# Linux 安装 Charles Proxy 引导

本引导面向 Linux，帮助你从零安装 Charles Proxy 并配置到 `charles-mcp` 可用状态。
其他操作系统请见 [macOS](./charles-macos.md) / [Windows](./charles-windows.md)。

## 下载

Charles 是商用软件，官方下载页：<https://www.charlesproxy.com/download/>。
Linux 版提供 `.deb`（amd64）与 `.tar.gz` 两种包。请下载最新稳定版
（版本号形如 `4.x.x`）。

## 安装

### 方式 A：deb 包（Debian / Ubuntu，推荐）

```bash
# 下载后放在当前目录，文件名按实际版本替换
sudo apt install ./charles_<version>_amd64.deb
```

`apt install ./...` 会自动解析依赖；旧系统可用 `sudo dpkg -i ... && sudo apt -f install -y`。

### 方式 B：tar.gz（任意发行版）

```bash
tar xzf charles.tar.gz
cd charles
./bin/charles
```

若想全局可用：

```bash
sudo mv charles /opt/charles
sudo ln -s /opt/charles/bin/charles /usr/local/bin/charles
```

> Charles 的官方 `.deb` 与 `.tar.gz` **均自带 JRE**，无需你预装 Java。
> 仅在使用社区打包版或解压启动报 `No Java` 时，补装
> `sudo apt install -y openjdk-17-jre`（Debian/Ubuntu）或
> `sudo dnf install -y java-17-openjdk`（Fedora/RHEL）。

Charles 配置文件路径（`charles-mcp` 探测）：

- `$XDG_CONFIG_HOME/Charles/charles.config`（默认 `~/.config/Charles/charles.config`）
- `~/.charles.config`、`~/.charles/charles.config`（兜底）

## 启动与首次配置

从桌面菜单或 `charles` 命令启动。首次启动会提示是否设为系统代理，按需选择。
若发行版桌面环境没有系统代理设置，可手动设 `http_proxy`/`https_proxy` 环境变量。

## 启用 Web Interface

`charles-mcp` 通过 Charles 的 Web Interface 控制面遥控 Charles，必须手动启用：

菜单 `Proxy → Web Interface Settings`，确认：

- 勾选 `Enable web interface`
- 用户名填 `admin`
- 密码填 `123456`

> 这组 `admin`/`123456` 是 `charles-mcp` 的约定默认值（见项目 `config.py` 与
> `.env.example`），**不是 Charles 的默认密码**。Charles 默认不启用 Web
> Interface、也不预置密码。如需更换，请同时改 Charles 端与 `charles-mcp`
> 环境变量 `CHARLES_USER`/`CHARLES_PASS`。

## 安装 SSL 根证书

要解 HTTPS 流量必须让系统信任 Charles 根 CA。先在菜单
`Help → SSL Proxying → Save Charles Root Certificate` 导出证书为
`charles-ssl-proxying-certificate.pem`。

### Ubuntu / Debian

```bash
sudo cp charles-ssl-proxying-certificate.pem /usr/local/share/ca-certificates/charles.crt
sudo chmod 644 /usr/local/share/ca-certificates/charles.crt
sudo update-ca-certificates
```

### Fedora / RHEL / CentOS

```bash
sudo cp charles-ssl-proxying-certificate.pem /etc/pki/ca-trust/source/anchors/charles.crt
sudo chmod 644 /etc/pki/ca-trust/source/anchors/charles.crt
sudo update-ca-trust
```

并在 Charles 菜单 `Proxy → SSL Proxying Settings` 勾选 `Enable SSL Proxying`，
按需在 `Include` 列表加入要解的 `host:port`（如 `*:443`）。

> 以上只让系统级 CA 存储（curl / openssl / git）信任。Linux 上
> Chrome / Firefox 有独立证书库：Firefox 用菜单 `Help → SSL Proxying →
> Install Charles Root Certificate (Firefox)`；Chrome（NSS）执行：
> `certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n "Charles" -i charles.crt`

## 防火墙放行 8888

Charles 默认监听 `127.0.0.1:8888`，仅本机访问，通常**无需**放行。
若你要让同局域网其他设备通过本机 Charles 代理（Charles 改监听 `0.0.0.0`）：

```bash
# Debian / Ubuntu (ufw)
sudo ufw allow 8888/tcp

# Fedora / RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --reload
```

## 系统代理与还原

Charles 启动时会把自己设为系统代理（若桌面环境支持）。
退出 Charles 通常会自动还原；若异常退出导致代理残留、断网，
手动清空 `http_proxy`/`https_proxy`/`all_proxy` 环境变量，
或在桌面环境的「网络代理」设置里关闭。

## 试用版注意

未注册的 Charles 试用版会在启动后约 30 分钟自动断开当前会话/暂停代理，
且每次启动弹一次试用提示窗。注册（输入许可证）后断开与弹窗消失。
试用本身长期可用，只是每 30 分钟一次中断。
分析长流量时建议注册，或在中断后手动重新启用录制。

## 一键安装脚本（Debian / Ubuntu）

以下脚本自动检测 Java、下载最新 `.deb`、安装 Charles。
**请先阅读脚本再执行**；需要 `sudo` 权限与网络访问 `charlesproxy.com`。

```bash
#!/usr/bin/env bash
set -euo pipefail

# 从下载页解析最新版本号（官网无稳定 latest 直链）
DOWNLOAD_PAGE="https://www.charlesproxy.com/download/"
echo "请访问 ${DOWNLOAD_PAGE} 确认最新版本号，再以 VERSION 变量传入。"
VERSION="${VERSION:-}"
if [ -z "$VERSION" ]; then
  echo "用法: VERSION=4.6.7 $0" >&2
  exit 1
fi

DEB_URL="https://www.charlesproxy.com/assets/release/${VERSION}/charles_${VERSION}_amd64.deb"
TMP_DEB="$(mktemp --suffix=.deb)"
echo "下载 ${DEB_URL}"
curl -fL "$DEB_URL" -o "$TMP_DEB"

echo "安装 ${TMP_DEB}"
sudo apt install -y "$TMP_DEB"
rm -f "$TMP_DEB"

# 仅在 charles 启动报 Java 缺失时才装系统 JRE（官方包通常自带）
if ! command -v charles >/dev/null 2>&1 && [ -x /opt/charles/bin/charles ]; then
  echo "提示：可执行 charles 已装在 /opt/charles/bin/charles"
fi

cat <<'REPORT'
安装完成。请手动完成以下步骤以对接 charles-mcp：
1. 启动 Charles（菜单或命令 charles）
2. Proxy → Web Interface Settings，勾选 Enable web interface，
   用户名 admin、密码 123456
3. 安装 SSL 根证书（见本文「安装 SSL 根证书」小节）
4. 按 README 把 charles-mcp 配置到 MCP 客户端
REPORT
```

## 与 charles-mcp 对接

确认以上步骤完成后，Charles 侧应满足 `charles-mcp` 的连接约定：

- Charles 已启动
- Web Interface 已启用，凭据 `admin` / `123456`
- 代理监听 `127.0.0.1:8888`
- 控制面 base URL 为 `http://control.charles`（Charles 注册的虚拟主机，经 `127.0.0.1:8888` 代理访问）

随后按 [README 快速开始](../README.md#快速开始) 把 `charles-mcp` 配置到你的 MCP 客户端。
