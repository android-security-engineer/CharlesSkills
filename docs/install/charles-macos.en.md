# Install Charles Proxy on macOS

This guide covers installing Charles Proxy from scratch on macOS and wiring it
up for `charles-mcp`. For other OSes see [Windows](./charles-windows.en.md) /
[Linux](./charles-linux.en.md).

## Download

Charles is commercial software. Official download page:
<https://www.charlesproxy.com/download/>. The macOS build ships as a `.dmg`.
Grab the latest stable release (version like `4.x.x`).

## Install

Open the downloaded `.dmg` and drag `Charles.app` into `Applications`.
The executable lives at:

```bash
/Applications/Charles.app/Contents/MacOS/Charles
```

This is exactly the path `charles-mcp` probes in `config.py`.

The macOS `.app` bundle **bundles its own JRE** — you do not need to install
Java first. Only if you start from a tar.gz and get `No Java`, run
`brew install --cask temurin`.

If Gatekeeper blocks first launch, right-click `Charles.app` → "Open".
If still blocked, recursively strip the quarantine attribute:

```bash
xattr -dr com.apple.quarantine /Applications/Charles.app
```

## Launch & First-time Setup

Launch Charles from Launchpad or `Applications`. On first launch it asks
whether to set itself as the system proxy — choose "Yes" to route system
traffic through Charles automatically.

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

GUI path: menu `Help → SSL Proxying → Install Charles Root Certificate`, then
in Keychain Access locate the imported `Charles Proxy CA` cert, double-click
→ expand "Trust" → set to "Always Trust".

Command line (after exporting the cert as
`charles-ssl-proxying-certificate.pem` via the menu or Charles data dir):

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain charles-ssl-proxying-certificate.pem
```

Also in Charles menu `Proxy → SSL Proxying Settings`, check
`Enable SSL Proxying` and add the `host:port` entries to decrypt (e.g. `*:443`).

## Open Firewall Port 8888

Charles listens on `127.0.0.1:8888` by default (local only) — usually no
firewall rule is needed. If you let other LAN devices proxy through this
machine (Charles bound to `0.0.0.0`), allow inbound 8888:

```bash
/usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Charles.app/Contents/MacOS/Charles
```

## System Proxy & Restore

Charles sets itself as the system HTTP/HTTPS proxy on launch. Quitting Charles
normally restores it. If an abnormal exit leaves the proxy set and breaks
networking, restore manually: `System Settings → Network → select adapter →
Details → Proxies`, turn off HTTP/HTTPS/SOCKS proxies.

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
