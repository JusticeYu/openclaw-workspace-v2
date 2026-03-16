#!/bin/bash
# 小红书爬虫快速启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助
show_help() {
    echo -e "${BLUE}🔥 小红书爬虫工具${NC}"
    echo ""
    echo "用法: ./crawl.sh [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  search <关键词> [页数]    搜索帖子"
    echo "  cookie                    显示Cookie获取指南"
    echo "  help                      显示帮助"
    echo ""
    echo "示例:"
    echo "  ./crawl.sh search \"南山书城 舞房 转卡\" 5"
    echo "  ./crawl.sh search \"深圳舞蹈室\" 3"
    echo ""
    echo "环境变量:"
    echo "  XHS_COOKIE    设置Cookie值"
    echo ""
}

# 检查Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ 错误: 未找到 Python3${NC}"
        exit 1
    fi
}

# 搜索命令
cmd_search() {
    local keyword="$1"
    local pages="${2:-3}"
    
    if [ -z "$keyword" ]; then
        echo -e "${RED}❌ 错误: 请提供关键词${NC}"
        echo "用法: ./crawl.sh search <关键词> [页数]"
        exit 1
    fi
    
    echo -e "${GREEN}🔍 开始搜索: $keyword${NC}"
    echo -e "${GREEN}📄 页数: $pages${NC}"
    echo ""
    
    python3 scripts/xhs_search.py \
        --keyword "$keyword" \
        --pages "$pages" \
        --output csv
}

# Cookie指南
cmd_cookie() {
    echo -e "${BLUE}🍪 Cookie获取指南${NC}"
    echo ""
    echo "方法1：浏览器开发者工具"
    echo "  1. 在电脑浏览器登录小红书"
    echo "  2. 按 F12 打开开发者工具"
    echo "  3. 切换到 Application/应用 标签"
    echo "  4. 左侧选择 Storage → Cookies"
    echo "  5. 找到 www.xiaohongshu.com"
    echo "  6. 复制 web_session 或 webId 的值"
    echo ""
    echo "方法2：浏览器扩展"
    echo "  1. 安装 'EditThisCookie' 扩展"
    echo "  2. 登录小红书"
    echo "  3. 点击扩展图标"
    echo "  4. 导出Cookie，找到 web_session"
    echo ""
    echo "设置Cookie:"
    echo "  export XHS_COOKIE='你的Cookie值'"
    echo ""
    echo -e "${YELLOW}⚠️ 注意: Cookie通常7-30天有效${NC}"
}

# 主逻辑
main() {
    check_python
    
    local cmd="${1:-help}"
    
    case "$cmd" in
        search)
            shift
            cmd_search "$@"
            ;;
        cookie)
            cmd_cookie
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $cmd${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
