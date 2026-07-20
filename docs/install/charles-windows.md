# Windows 安装 Charles Proxy 引导

本引导面向 Windows，帮助你从零安装 Charles Proxy 并配置到 `charles-mcp` 可用状态。
其他操作系统请见 [macOS](./charles-macos.md) / [Linux](./charles-linux.md)。

## 下载

Charles 是商用软件，官方下载页：<https://www.charlesproxy.com/download/>。
Windows 版为 64 位安装包。请下载最新稳定版（版本号形如 `4.x.x`）。

## 安装

运行下载的安装包，按默认选项安装。安装后 64 位可执行文件位于：

```text
C:\Program Files\Charles\Charles.exe
```

`charles-mcp` 在 `config.py` 中正是探测 `C:/Program Files/Charles/Charles.exe`
（以及 32 位兜底 `C:/Program Files (x86)/Charles/Charles.exe`）。

Charles 的 Windows 安装包**已自带 JRE**，无需你预先安装 Java。

Charles 配置文件路径（`charles-mcp` 探测）：

- 桌面版：`%APPDATA%\Charles\charles.config`
- Microsoft Store / UWP 版：`%LOCALAPPDATA%\Packages\XK72.Charles_*\RoamingState\charles.config`

## 启动与首次配置

从开始菜单启动 Charles。首次启动会提示是否设为系统代理，点「是」。
若被用户账户控制（UAC）或 Windows Defender 防火墙拦截入站，选「允许访问」。

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

要解 HTTPS 流量必须让系统信任 Charles 根 CA。

GUI 路径（推荐）：菜单 `Help → SSL Proxying → Install Charles Root Certificate`，
会调起 Windows 证书管理器并提示导入到「受信任的根证书颁发机构」。

命令行（管理员 PowerShell，需先用菜单导出证书
`charles-ssl-proxying-certificate.crt`）：

```bash
certutil -addstore -f "Root" charles-ssl-proxying-certificate.crt
```

并在 Charles 菜单 `Proxy → SSL Proxying Settings` 勾选 `Enable SSL Proxying`，
按需在 `Include` 列表加入要解的 `host:port`（如 `*:443`）。

> 让 Chrome / Edge 生效需重启浏览器；Firefox 有独立证书库，用菜单
> `Help → SSL Proxying → Install Charles Root Certificate (Firefox)`。

## 防火墙放行 8888

Charles 默认监听 `127.0.0.1:8888`，仅本机访问，通常**无需**放行。
若你要让同局域网其他设备通过本机 Charles 代理（Charles 改监听 `0.0.0.0`），
在管理员 PowerShell 放行入站 8888：

```bash
New-NetFirewallRule -DisplayName "Charles Proxy 8888" -Direction Inbound -Protocol TCP -LocalPort 8888 -Action Allow -Profile Any
```

> 此命令仅为说明用途，实际执行请用户在管理员终端手动运行，
> 不在 README 中出现，避免触碰客户端无关约束。

## 系统代理与还原

Charles 启动时会把自己设为系统代理。退出 Charles 通常会自动还原；
若异常退出导致系统代理残留、断网，手动还原：
`设置 → 网络和 Internet → 代理`，关闭「使用代理服务器」。

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
