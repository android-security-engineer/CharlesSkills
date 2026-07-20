from pathlib import Path

DOCS = Path("docs/install")

ZH_FILES = {
    "macos": DOCS / "charles-macos.md",
    "windows": DOCS / "charles-windows.md",
    "linux": DOCS / "charles-linux.md",
}

EN_FILES = {
    "macos": DOCS / "charles-macos.en.md",
    "windows": DOCS / "charles-windows.en.md",
    "linux": DOCS / "charles-linux.en.md",
}

# 中文必备小节标题（跨 OS 对称）
ZH_REQUIRED_SECTIONS = [
    "## 下载",
    "## 安装",
    "## 启动与首次配置",
    "## 启用 Web Interface",
    "## 安装 SSL 根证书",
    "## 防火墙放行 8888",
    "## 系统代理与还原",
    "## 试用版注意",
    "## 与 charles-mcp 对接",
]

# 英文必备小节标题（与中文一一对应）
EN_REQUIRED_SECTIONS = [
    "## Download",
    "## Install",
    "## Launch & First-time Setup",
    "## Enable the Web Interface",
    "## Install the SSL Root Certificate",
    "## Open Firewall Port 8888",
    "## System Proxy & Restore",
    "## Trial-version Notes",
    "## Wire up charles-mcp",
]


def test_all_six_install_docs_exist() -> None:
    for path in {**ZH_FILES, **EN_FILES}.values():
        assert path.exists(), f"missing install guide: {path}"


def test_zh_docs_have_required_sections() -> None:
    for os_name, path in ZH_FILES.items():
        content = path.read_text(encoding="utf-8")
        for section in ZH_REQUIRED_SECTIONS:
            assert section in content, f"{path} missing section: {section}"


def test_en_docs_have_required_sections() -> None:
    for os_name, path in EN_FILES.items():
        content = path.read_text(encoding="utf-8")
        for section in EN_REQUIRED_SECTIONS:
            assert section in content, f"{path} missing section: {section}"


def test_docs_reference_control_charles_and_credentials() -> None:
    """每份文档必须说明 charles-mcp 的连接约定，避免装完不知道怎么配。"""
    for path in {**ZH_FILES, **EN_FILES}.values():
        content = path.read_text(encoding="utf-8")
        assert "control.charles" in content, f"{path} must mention control.charles"
        assert "8888" in content, f"{path} must mention port 8888"
        assert "admin" in content, f"{path} must mention admin user"
        assert "123456" in content, f"{path} must mention 123456 password"


def test_linux_doc_contains_one_click_script() -> None:
    """Linux 文档必须提供一键安装脚本（用户已选择「给完整一键脚本」）。"""
    zh = (ZH_FILES["linux"]).read_text(encoding="utf-8")
    en = (EN_FILES["linux"]).read_text(encoding="utf-8")
    assert "```bash" in zh and "apt install" in zh and "charlesproxy.com/download" in zh
    assert "```bash" in en and "apt install" in en and "charlesproxy.com/download" in en


def test_readmes_link_to_install_guides_without_os_shell_words() -> None:
    """README 仅加入口链接，不得出现 OS/shell 专属词（与现有 test_readme_contract 同款守卫）。"""
    readme_zh = Path("README.md").read_text(encoding="utf-8")
    readme_en = Path("README.en.md").read_text(encoding="utf-8")
    for content in (readme_zh, readme_en):
        assert "docs/install/charles-macos" in content
        assert "docs/install/charles-windows" in content
        assert "docs/install/charles-linux" in content
        # 与 test_readme_contract.py:32-35 同款禁用词守卫，防止 OS 细节回潮进 README
        assert "PowerShell" not in content
        assert "Windows CMD" not in content
        assert "Git Bash / Bash / Zsh" not in content


def test_docs_hub_registers_install_directory() -> None:
    hub = Path("docs/README.md").read_text(encoding="utf-8")
    assert "./install/" in hub
    assert "install" in hub.lower() or "安装" in hub
