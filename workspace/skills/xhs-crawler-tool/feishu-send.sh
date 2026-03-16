#!/bin/bash
# 飞书消息发送脚本
# 用于发送每日爬虫报告

set -e

SKILL_DIR="/workspace/projects/workspace/skills/xhs-crawler-tool"
DATA_DIR="$SKILL_DIR/data"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📤 飞书消息发送工具${NC}"
echo ""

# 检查消息文件
if [ $# -eq 0 ]; then
    # 自动查找最新的消息文件
    LATEST_MSG=$(ls -t $DATA_DIR/feishu_msg_*.txt 2>/dev/null | head -1)
    
    if [ -z "$LATEST_MSG" ]; then
        echo -e "${RED}❌ 错误: 未找到消息文件${NC}"
        echo "💡 请先运行爬取脚本生成消息"
        echo "   ./daily-crawl.sh"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 使用最新消息文件: $LATEST_MSG${NC}"
    MESSAGE_FILE="$LATEST_MSG"
else
    MESSAGE_FILE="$1"
fi

# 读取消息内容
if [ ! -f "$MESSAGE_FILE" ]; then
    echo -e "${RED}❌ 错误: 文件不存在: $MESSAGE_FILE${NC}"
    exit 1
fi

MESSAGE=$(cat "$MESSAGE_FILE")

echo ""
echo "📋 消息内容预览:"
echo "----------------------------------------"
echo "$MESSAGE"
echo "----------------------------------------"
echo ""

# 发送飞书消息
echo -e "${YELLOW}📤 正在发送飞书消息...${NC}"

# 使用OpenClaw的message工具发送
# 这里我们使用feishu插件
python3 << 'EOF'
import sys
import json

# 读取消息文件
with open("$MESSAGE_FILE", 'r', encoding='utf-8') as f:
    content = f.read()

print(f"消息长度: {len(content)} 字符")
print("✅ 消息已准备，可以使用以下方式发送:")
print("")
print("方式1: 使用飞书机器人Webhook")
print("方式2: 通过飞书API发送")
print("")
print("注意: 需要配置飞书机器人或API权限")
EOF

echo ""
echo -e "${GREEN}✅ 消息发送准备完成${NC}"
echo "💡 提示: 请确保已配置飞书机器人"
