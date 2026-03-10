#!/bin/bash

#===============================================================================
# OpenClaw 一键安装配置脚本 (macOS/Linux)
# 
# 使用方法:
#   1. 设置环境变量 (至少需要一个 API key)
#   2. 运行脚本
#
# 环境变量:
#   ANTHROPIC_API_KEY     - Anthropic Claude API Key
#   OPENAI_API_KEY        - OpenAI API Key
#   OPENROUTER_API_KEY    - OpenRouter API Key
#   MOONSHOT_API_KEY      - Moonshot (Kimi) API Key
#   GATEWAY_TOKEN         - Gateway 访问令牌
#   GATEWAY_PASSWORD      - Gateway 密码认证
#
# 示例:
#   export ANTHROPIC_API_KEY="sk-ant-..."
#   ./install_openclaw.sh
#===============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置默认值
DAEMON_RUNTIME="${DAEMON_RUNTIME:-node}"
AUTH_CHOICE="${AUTH_CHOICE:-anthropic-api-key}"
GATEWAY_TOKEN="${GATEWAY_TOKEN:-openclaw-$(openssl rand -hex 8 2>/dev/null || date +%s)}"
GATEWAY_BIND="${GATEWAY_BIND:-auto}"
SECRET_MODE="${SECRET_MODE:-plaintext}"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          🦐 OpenClaw 一键安装配置脚本 🦐                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

#-------------------------------------------------------------------------------
# 检测操作系统
#-------------------------------------------------------------------------------
echo -e "${YELLOW}📍 检测操作系统...${NC}"
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
    OS_TYPE="macos"
    echo "   ✅ macOS"
elif [ "$OS" = "Linux" ]; then
    OS_TYPE="linux"
    echo "   ✅ Linux"
else
    echo -e "   ❌ 不支持的操作系统: $OS"
    exit 1
fi

#-------------------------------------------------------------------------------
# 检查并安装依赖
#-------------------------------------------------------------------------------
echo -e "\n${YELLOW}📦 检查依赖...${NC}"

# 检查 curl
if ! command -v curl &> /dev/null; then
    echo -e "   ⚠️  curl 未安装"
    if [ "$OS_TYPE" = "macos" ]; then
        echo "   →  macOS 通常自带 curl，如有问题请安装 Xcode Command Line Tools"
    fi
    exit 1
fi
echo "   ✅ curl"

# 检查 Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 22 ]; then
        echo "   ✅ Node.js $(node -v)"
    else
        echo -e "   ⚠️  Node.js 版本 $NODE_VERSION < 22，需要升级"
        echo "   →  脚本将自动安装 Node.js 22"
        NEED_NODE_INSTALL=1
    fi
else
    echo "   ⚠️  Node.js 未安装"
    NEED_NODE_INSTALL=1
fi

# 检查 npm
if command -v npm &> /dev/null; then
    echo "   ✅ npm $(npm -v)"
else
    echo -e "   ❌ npm 未安装，请先安装 Node.js"
    exit 1
fi

#-------------------------------------------------------------------------------
# 安装 Node.js 22 (如果需要)
#-------------------------------------------------------------------------------
if [ "$NEED_NODE_INSTALL" = "1" ]; then
    echo -e "\n${YELLOW}📦 安装 Node.js 22...${NC}"
    if [ "$OS_TYPE" = "macos" ]; then
        if command -v brew &> /dev/null; then
            brew install node@22
            brew link node@22 --force
        else
            echo "   ❌ 需要 Homebrew，请先安装: https://brew.sh"
            exit 1
        fi
    else
        # Linux - 使用 NodeSource
        curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs
    fi
    echo "   ✅ Node.js $(node -v)"
fi

#-------------------------------------------------------------------------------
# 安装 OpenClaw
#-------------------------------------------------------------------------------
echo -e "\n${YELLOW}🚀 安装 OpenClaw...${NC}"
npm install -g openclaw@latest
echo "   ✅ OpenClaw $(openclaw --version)"

#-------------------------------------------------------------------------------
# 准备配置参数
#-------------------------------------------------------------------------------
echo -e "\n${YELLOW}⚙️  准备配置...${NC}"

# 构建 onboard 命令参数
ONBOARD_ARGS="--non-interactive"
ONBOARD_ARGS="$ONBOARD_ARGS --accept-risk"
ONBOARD_ARGS="$ONBOARD_ARGS --install-daemon"
ONBOARD_ARGS="$ONBOARD_ARGS --daemon-runtime $DAEMON_RUNTIME"
ONBOARD_ARGS="$ONBOARD_ARGS --flow quickstart"
ONBOARD_ARGS="$ONBOARD_ARGS --auth-choice $AUTH_CHOICE"
ONBOARD_ARGS="$ONBOARD_ARGS --gateway-bind $GATEWAY_BIND"
ONBOARD_ARGS="$ONBOARD_ARGS --gateway-token $GATEWAY_TOKEN"
ONBOARD_ARGS="$ONBOARD_ARGS --secret-input-mode $SECRET_MODE"
ONBOARD_ARGS="$ONBOARD_ARGS --skip-channels"
ONBOARD_ARGS="$ONBOARD_ARGS --skip-skills"
ONBOARD_ARGS="$ONBOARD_ARGS --skip-ui"

# 添加 API Key
if [ -n "$ANTHROPIC_API_KEY" ]; then
    ONBOARD_ARGS="$ONBOARD_ARGS --anthropic-api-key $ANTHROPIC_API_KEY"
    echo "   ✅ Anthropic API Key 已配置"
elif [ -n "$OPENAI_API_KEY" ]; then
    ONBOARD_ARGS="$ONBOARD_ARGS --openai-api-key $OPENAI_API_KEY"
    echo "   ✅ OpenAI API Key 已配置"
elif [ -n "$OPENROUTER_API_KEY" ]; then
    ONBOARD_ARGS="$ONBOARD_ARGS --openrouter-api-key $OPENROUTER_API_KEY"
    echo "   ✅ OpenRouter API Key 已配置"
elif [ -n "$MOONSHOT_API_KEY" ]; then
    ONBOARD_ARGS="$ONBOARD_ARGS --moonshot-api-key $MOONSHOT_API_KEY"
    echo "   ✅ Moonshot API Key 已配置"
else
    echo -e "   ⚠️  未设置任何 API Key 环境变量"
    echo "   →  你可以之后运行: openclaw onboard --skip-channels"
    echo "   →  或设置环境变量后重新运行"
fi

#-------------------------------------------------------------------------------
# 执行配置
#-------------------------------------------------------------------------------
echo -e "\n${YELLOW}🔧 执行配置...${NC}"
echo "   命令: openclaw onboard $ONBOARD_ARGS"
echo ""

openclaw $ONBOARD_ARGS

#-------------------------------------------------------------------------------
# 完成
#-------------------------------------------------------------------------------
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗"
echo "║                    🎉 安装配置完成! 🎉                      ║"
echo "╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📌 重要信息:"
echo "   Gateway Token: $GATEWAY_TOKEN"
echo ""
echo "📝 常用命令:"
echo "   openclaw status          # 查看状态"
echo "   openclaw dashboard       # 打开管理界面"
echo "   openclaw gateway start   # 启动服务"
echo "   openclaw gateway stop    # 停止服务"
echo ""
echo "🔗 下一步:"
echo "   1. 配置聊天渠道: openclaw channel add"
echo "   2. 查看文档: https://docs.openclaw.ai"
echo ""

# 保存配置信息到文件
CONFIG_FILE="$HOME/openclaw-install-info.txt"
cat > "$CONFIG_FILE" << EOF
OpenClaw 安装配置信息
======================
安装时间: $(date)
操作系统: $OS_TYPE
Gateway Token: $GATEWAY_TOKEN

如需重新配置，运行:
  openclaw onboard --non-interactive --accept-risk --skip-channels

文档: https://docs.openclaw.ai
EOF

echo -e "${BLUE}📄 配置信息已保存到: $CONFIG_FILE${NC}"
