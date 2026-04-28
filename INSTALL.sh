#!/bin/bash
#
# CI/CD Deploy Plugin - 一键安装脚本
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  CI/CD 自动化部署插件 - 安装脚本    ${NC}"
echo -e "${GREEN}========================================${NC}"

# 检测Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo -e "${GREEN}✅ Python3 版本: $PYTHON_VERSION${NC}"

# 检测Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️ Git 未安装，部分功能可能受限${NC}"
else
    echo -e "${GREEN}✅ Git 已安装${NC}"
fi

# 检测Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker 已安装${NC}"
else
    echo -e "${YELLOW}⚠️ Docker 未安装${NC}"
fi

# 创建目录
INSTALL_DIR="${HOME}/.openclaw/plugins/cicd-deploy"
mkdir -p "$INSTALL_DIR"

# 复制文件
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp -r "$SCRIPT_DIR/"* "$INSTALL_DIR/"

# 安装CLI
CICD_BIN="${HOME}/.local/bin/cicd"
mkdir -p "$(dirname "$CICD_BIN")"

# 创建CLI wrapper
cat > "$CICD_BIN" << 'WRAPPER'
#!/bin/bash
# CI/CD CLI Wrapper
PLUGIN_DIR="${HOME}/.openclaw/plugins/cicd-deploy"
python3 "$PLUGIN_DIR/cicd.py" "$@"
WRAPPER

chmod +x "$CICD_BIN"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  安装完成！                              ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "使用方式:"
echo -e "  ${GREEN}cicd init${NC}        - 初始化配置"
echo -e "  ${GREEN}cicd deploy --path ./my-project${NC} - 部署项目"
echo -e "  ${GREEN}cicd status${NC}      - 查看状态"
echo -e ""
echo -e "详细文档: ${HOME}/.openclaw/plugins/cicd-deploy/README.md"
echo ""
