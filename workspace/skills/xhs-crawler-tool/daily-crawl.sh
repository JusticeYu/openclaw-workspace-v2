#!/bin/bash
# 每日自动爬取脚本
# 每天早上7点自动执行

set -e

SKILL_DIR="/workspace/projects/workspace/skills/xhs-crawler-tool"
LOG_FILE="$SKILL_DIR/logs/daily_crawl.log"

# 确保目录存在
mkdir -p "$SKILL_DIR/data"
mkdir -p "$SKILL_DIR/logs"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "🕐 任务开始: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

# 进入技能目录
cd "$SKILL_DIR"

# 检查Cookie
if [ -z "$XHS_COOKIE" ] && [ ! -f "config/cookie.txt" ]; then
    echo "❌ 错误: 未配置Cookie" >> "$LOG_FILE"
    echo "💡 请设置环境变量 XHS_COOKIE 或创建 config/cookie.txt" >> "$LOG_FILE"
    exit 1
fi

# 执行爬取
echo "🔥 开始爬取..." >> "$LOG_FILE"
python3 scripts/daily_crawl.py >> "$LOG_FILE" 2>&1

# 检查结果
if [ $? -eq 0 ]; then
    echo "✅ 爬取成功" >> "$LOG_FILE"
    
    # 发送飞书通知（可选）
    # ./feishu-send.sh >> "$LOG_FILE" 2>&1
else
    echo "❌ 爬取失败" >> "$LOG_FILE"
fi

echo "🕐 任务结束: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
