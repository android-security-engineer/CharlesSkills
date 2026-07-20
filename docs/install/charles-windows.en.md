# Install Charles Proxy on Windows

This guide covers installing Charles Proxy from scratch on Windows and wiring
it up for `charles-mcp`. For other OSes see [macOS](./charles-macos.en.md) /
[Linux](./charles-linux.en.md).

## Download

Charles is commercial software. Official download page:
<https://www.charlesproxy.com/download/>. The Windows build is a 64-bit
installer. Grab the latest stable release (version like `4.x.x`).

## Install

Run the downloaded installer with default options. The 64-bit executable lives
at:

```text
C:\Program Files\Charles\Charles.exe
```

`charles-mcp` probes `C:/Program Files/Charles/Charles.exe` in `config.py`
(with a 32-bit fallback `C:/Program Files (x86)/Charles/Charles.exe`).

The Windows installer **bundles its own JRE** — no need to install Java first.

Charles config file paths probed by `charles-mcp`:

- Desktop build: `%APPDATA%\Charles\charles.config`
- Microsoft Store / UWP build: `%LOCALAPPDATA%\Packages\XK72.Charles_*\RoamingState\charles.config`

## Launch & First-time Setup

Launch Charles from the Start menu. On first launch it asks whether to set
itself as the system proxy — choose "Yes". If UAC or Windows Defender Firewall
prompts for inbound access, choose "Allow".

## Enable the Web Interface

`charles-mcp` drives Charles via the Web Interface control plane, which must
be enabled manually: menu `Proxy → Web Interface Settings`, confirm:

- Check `Enable web interface`
- Username: `admin`
- Password: `123456`

> `admin`/`123456` is the `charles-mcp` convention default (see the project's
> `config.py` and `.env.example`), **not** a Charles default. Charles does not
> enable the Web Interface or preset a password by default. To change them,
> update both the Charles side and the `charles-mcp` env vars
> `CHARLES_USER`/`CHARLES_PASS`.

## Install the SSL Root Certificate

To decrypt HTTPS, the system must trust the Charles root CA.

GUI path (recommended): menu `Help → SSL Proxying → Install Charles Root
Certificate` — this opens the Windows certificate manager and prompts you to
import into "Trusted Root Certification Authorities".

Command line (admin PowerShell, after exporting the cert as
`charles-ssl-proxying-certificate.crt` via the menu):

```bash
certutil -addstore -f "Root" charles-ssl-proxying-certificate.crt
```

Also in Charles menu `Proxy → SSL Proxying Settings`, check
`Enable SSL Proxying` and add the `host:port` entries to decrypt (e.g. `*:443`).

> Restart Chrome / Edge for trust to take effect; Firefox has its own
> certificate store — use `Help → SSL Proxying → Install Charles Root
> Certificate (Firefox)`.

## Open Firewall Port 8888

Charles listens on `127.0.0.1:8888` by default (local only) — usually no
firewall rule is needed. If you let other LAN devices proxy through this
machine (Charles bound to `0.0.0.0`), allow inbound 8888 in an admin shell:

```bash
New-NetFirewallRule -DisplayName "Charles Proxy 8888" -Direction Inbound -Protocol TCP -LocalPort 8888 -Action Allow -Profile Any
```

## System Proxy & Restore

Charles sets itself as the system proxy on launch. Quitting Charles normally
restores it. If an abnormal exit leaves the proxy set and breaks networking,
restore manually: `Settings → Network & Internet → Proxy`, turn off "Use a
proxy server".

## Trial-version Notes

The unregistered Charles trial auto-disconnects the session / pauses the proxy
roughly 30 minutes after launch, and shows a trial prompt on each start.
Registering (entering a license) removes both. The trial stays usable long
term; it just interrupts every 30 minutes. For long captures, register or
re-enable recording manually after an interruption.

## Wire up charles-mcp

With the above done, the Charles side meets the `charles-mcp` connection
contract:

- Charles is running
- Web Interface enabled, credentials `admin` / `123456`
- proxy listening on `127.0.0.1:8888`
- control-plane base URL `http://control.charles` (Charles-registered virtual
  host, reached via the `127.0.0.1:8888` proxy)

Then follow [README Quick Start](../README.en.md#quick-start) to add
`charles-mcp` to your MCP client.
