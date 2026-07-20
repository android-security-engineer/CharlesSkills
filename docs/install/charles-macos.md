# macOS 安装 Charles Proxy 引导

本引导面向 macOS，帮助你从零安装 Charles Proxy 并配置到 `charles-mcp` 可用状态。
其他操作系统请见 [Windows](./charles-windows.md) / [Linux](./charles-linux.md)。

## 下载

Charles 是商用软件，官方下载页：<https://www.charlesproxy.com/download/>。
macOS 版为 `.dmg` 安装镜像。请下载最新稳定版（版本号形如 `4.x.x`）。

## 安装

双击下载的 `.dmg`，在弹出的窗口里把 `Charles.app` 拖入 `Applications` 文件夹。
安装后可执行文件位于：

```bash
/Applications/Charles.app/Contents/MacOS/Charles
```

`charles-mcp` 在 `config.py` 中正是探测这个路径。

Charles 的 macOS `.app` 包**已自带 JRE**，无需你预先安装 Java。
仅当你用 tar.gz 手动启动且报 `No Java` 时，才执行 `brew install --cask temurin` 补 Java。

首次启动若被 Gatekeeper 拦截，右键点击 `Charles.app` →「打开」；
仍被拦则递归移除隔离属性：

```bash
xattr -dr com.apple.quarantine /Applications/Charles.app
```

## 启动与首次配置

从「启动台」或 `Applications` 启动 Charles。
首次启动会提示是否设为系统代理，点「是」可让系统流量自动走 Charles。

## 启用 Web Interface

`charles-mcp` 通过 Charles 的 Web Interface 控制面遥控 Charles，必须手动启用：

菜单 `Proxy → Web Interface Settings`，确认：

- 勾选 `Enable web interface`
- 用户名填 `admin`
- 密码填 `123456`

> 这组 `admin`/`123456` 是 `charles-mcp` 的约定默认值（见项目 `config.py` 与 `.env.example`），**不是 Charles 的默认密码**。Charles 默认不启用 Web Interface、也不预置密码。如需更换，请同时改 Charles 端与 `charles-mcp` 环境变量 `CHARLES_USER`/`CHARLES_PASS`。

## 安装 SSL 根证书

要解 HTTPS 流量必须让系统信任 Charles 根 CA。

GUI 路径：菜单 `Help → SSL Proxying → Install Charles Root Certificate`，
在「钥匙串访问」里找到导入的 `Charles Proxy CA` 证书，双击 → 展开「信任」→ 设为「始终信任」。

命令行（需先用上一步或菜单导出证书为 `charles-ssl-proxying-certificate.pem`）：

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain charles-ssl-proxying-certificate.pem
```

并在 Charles 菜单 `Proxy → SSL Proxying Settings` 勾选 `Enable SSL Proxying`，
按需在 `Include` 列表加入要解的 `host:port`（如 `*:443`）。

## 防火墙放行 8888

Charles 默认监听 `127.0.0.1:8888`，仅本机访问，通常**无需**放行。
若你要让同局域网其他设备通过本机 Charles 代理（Charles 改监听 `0.0.0.0`），
需放行入站 8888：

```bash
/usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Charles.app/Contents/MacOS/Charles
```

## 系统代理与还原

Charles 启动时会把自己设为系统 HTTP/HTTPS 代理。
退出 Charles 通常会自动还原系统代理；若异常退出导致系统代理残留、断网，
手动还原：`系统设置 → 网络 → 选中网卡 → 详细信息 → 代理`，关闭 HTTP/HTTPS/SOCKS 代理。

## 试用版注意

未注册的 Charles 试用版会在启动后约 30 分钟自动断开当前会话/暂停代理，
且每次启动弹一次试用提示窗。注册（输入许可证）后断开与弹窗消失。
试用本身长期可用，只是每 30 分钟一次中断。
分析长流量时建议注册，或在中断后手动重新启用录制。

## 与 charles-mcp 对接

确认以上步骤完成后，Charles 侧应满足 `charles-mcp` 的连接约定：

- Charles 已启动
- Web Interface 已启用，凭据 `admin` / `123456`
- 代理监听 `127.0.0.1:8888`
- 控制面 base URL 为 `http://control.charles`（Charles 注册的虚拟主机，经 `127.0.0.1:8888` 代理访问）

随后按 [README 快速开始](../README.md#快速开始) 把 `charles-mcp` 配置到你的 MCP 客户端。
