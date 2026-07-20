# Install Charles Proxy on Linux

This guide covers installing Charles Proxy from scratch on Linux and wiring
it up for `charles-mcp`. For other OSes see [macOS](./charles-macos.en.md) /
[Windows](./charles-windows.en.md).

## Download

Charles is commercial software. Official download page:
<https://www.charlesproxy.com/download/>. The Linux build ships as both a
`.deb` (amd64) and a `.tar.gz`. Grab the latest stable release
(version like `4.x.x`).

## Install

### Option A: deb package (Debian / Ubuntu, recommended)

```bash
# After downloading, place the file in the current directory; replace the version
sudo apt install ./charles_<version>_amd64.deb
```

`apt install ./...` resolves dependencies automatically; on older systems use
`sudo dpkg -i ... && sudo apt -f install -y`.

### Option B: tar.gz (any distro)

```bash
tar xzf charles.tar.gz
cd charles
./bin/charles
```

To make it globally available:

```bash
sudo mv charles /opt/charles
sudo ln -s /opt/charles/bin/charles /usr/local/bin/charles
```

> The official `.deb` and `.tar.gz` **bundle their own JRE** — no need to
> install Java first. Only if you use a community package or the tar.gz reports
> `No Java`, install `sudo apt install -y openjdk-17-jre` (Debian/Ubuntu) or
> `sudo dnf install -y java-17-openjdk` (Fedora/RHEL).

Charles config file paths probed by `charles-mcp`:

- `$XDG_CONFIG_HOME/Charles/charles.config` (default `~/.config/Charles/charles.config`)
- `~/.charles.config`, `~/.charles/charles.config` (fallbacks)

## Launch & First-time Setup

Launch Charles from the desktop menu or the `charles` command. On first launch
it asks whether to set itself as the system proxy — choose as needed. If your
desktop environment has no system-proxy setting, set `http_proxy`/`https_proxy`
env vars manually.

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

To decrypt HTTPS, the system must trust the Charles root CA. First export the
cert via menu `Help → SSL Proxying → Save Charles Root Certificate` as
`charles-ssl-proxying-certificate.pem`.

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

Also in Charles menu `Proxy → SSL Proxying Settings`, check
`Enable SSL Proxying` and add the `host:port` entries to decrypt (e.g. `*:443`).

> The above only makes the system CA store (curl / openssl / git) trust it.
> Linux Chrome / Firefox have separate stores: Firefox via menu `Help → SSL
> Proxying → Install Charles Root Certificate (Firefox)`; Chrome (NSS) via:
> `certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n "Charles" -i charles.crt`

## Open Firewall Port 8888

Charles listens on `127.0.0.1:8888` by default (local only) — usually no
firewall rule is needed. If you let other LAN devices proxy through this
machine (Charles bound to `0.0.0.0`):

```bash
# Debian / Ubuntu (ufw)
sudo ufw allow 8888/tcp

# Fedora / RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --reload
```

## System Proxy & Restore

Charles sets itself as the system proxy on launch (if the desktop environment
supports it). Quitting Charles normally restores it. If an abnormal exit leaves
the proxy set and breaks networking, clear `http_proxy`/`https_proxy`/`all_proxy`
env vars or turn off the proxy in your desktop "Network Proxy" settings.

## Trial-version Notes

The unregistered Charles trial auto-disconnects the session / pauses the proxy
roughly 30 minutes after launch, and shows a trial prompt on each start.
Registering (entering a license) removes both. The trial stays usable long
term; it just interrupts every 30 minutes. For long captures, register or
re-enable recording manually after an interruption.

## One-click install script (Debian / Ubuntu)

The script below auto-detects Java, downloads the latest `.deb`, and installs
Charles. **Read it before running**; it needs `sudo` and network access to
`charlesproxy.com`.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Resolve the latest version number from the download page (no stable latest direct link)
DOWNLOAD_PAGE="https://www.charlesproxy.com/download/"
echo "Visit ${DOWNLOAD_PAGE} to confirm the latest version, then pass it via VERSION."
VERSION="${VERSION:-}"
if [ -z "$VERSION" ]; then
  echo "Usage: VERSION=4.6.7 $0" >&2
  exit 1
fi

DEB_URL="https://www.charlesproxy.com/assets/release/${VERSION}/charles_${VERSION}_amd64.deb"
TMP_DEB="$(mktemp --suffix=.deb)"
echo "Downloading ${DEB_URL}"
curl -fL "$DEB_URL" -o "$TMP_DEB"

echo "Installing ${TMP_DEB}"
sudo apt install -y "$TMP_DEB"
rm -f "$TMP_DEB"

# Only install a system JRE if charles reports missing Java (official packages bundle one)
if ! command -v charles >/dev/null 2>&1 && [ -x /opt/charles/bin/charles ]; then
  echo "Note: the charles executable is installed at /opt/charles/bin/charles"
fi

cat <<'REPORT'
Install complete. Finish these steps manually to wire up charles-mcp:
1. Launch Charles (menu or the charles command)
2. Proxy → Web Interface Settings, check Enable web interface,
   username admin, password 123456
3. Install the SSL root certificate (see the "Install the SSL Root Certificate" section)
4. Follow the README to add charles-mcp to your MCP client
REPORT
```

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
