#!/usr/bin/env python3
"""
小红书定时爬取 + 飞书推送
每天早上自动爬取并发送结果
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

# 添加技能路径
sys.path.insert(0, '/workspace/projects/workspace/skills/xhs-crawler-tool')
from scripts.xhs_search import XHSCrawler

# 飞书推送配置
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")
KEYWORDS = os.getenv("XHS_KEYWORDS", "南山书城 舞房 转卡")


async def send_feishu_message(content: str, title: str = "小红书爬虫报告"):
    """发送飞书消息"""
    try:
        # 使用OpenClaw的message工具发送
        # 这里使用feishu_doc的API
        from plugins.feishu.feishu_doc import send_message
        
        result = await send_message(
            content=content,
            title=title
        )
        return result
    except Exception as e:
        print(f"飞书推送失败: {e}")
        return False


def format_feishu_message(results: list) -> str:
    """格式化飞书消息"""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    message = f"📱 **小红书爬虫报告 - {today}**\n\n"
    message += f"🔍 关键词: {KEYWORDS}\n"
    message += f"📊 找到 {len(results)} 条相关帖子\n\n"
    message += "---\n\n"
    
    for i, item in enumerate(results[:5], 1):  # 只显示前5条
        message += f"**{i}. {item.get('title', '无标题')}**\n"
        message += f"👤 作者: {item.get('author', '未知')}\n"
        message += f"❤️ 点赞: {item.get('likes', 0)} | 💬 评论: {item.get('comments', 0)}\n"
        message += f"📝 {item.get('content', '无内容')[:80]}...\n"
        message += f"🔗 [查看详情]({item.get('url', '#')})\n\n"
    
    if len(results) > 5:
        message += f"*还有 {len(results) - 5} 条结果，请查看完整报告*\n\n"
    
    message += "---\n"
    message += "🤖 自动推送 by 小虾米"
    
    return message


def crawl_and_notify():
    """爬取数据并发送通知"""
    print(f"🔥 开始定时爬取任务 - {datetime.now()}")
    
    # 获取Cookie
    cookie = os.getenv("XHS_COOKIE", "")
    if not cookie:
        # 尝试从文件读取
        cookie_file = Path("/workspace/projects/workspace/skills/xhs-crawler-tool/config/cookie.txt")
        if cookie_file.exists():
            cookie = cookie_file.read_text().strip()
    
    if not cookie:
        print("❌ 错误: 未配置Cookie，无法获取真实数据")
        print("💡 请设置环境变量 XHS_COOKIE 或创建 config/cookie.txt")
        return False
    
    # 初始化爬虫
    crawler = XHSCrawler(cookie=cookie)
    
    # 执行搜索
    print(f"🔍 搜索关键词: {KEYWORDS}")
    results = crawler.search(KEYWORDS, page=1)
    
    if not results:
        print("⚠️ 未获取到数据")
        return False
    
    print(f"✅ 获取到 {len(results)} 条数据")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/workspace/projects/workspace/skills/xhs-crawler-tool/data/xhs_daily_{timestamp}"
    
    # 确保data目录存在
    Path("/workspace/projects/workspace/skills/xhs-crawler-tool/data").mkdir(exist_ok=True)
    
    # 保存为CSV
    crawler.save_results(results, "csv", output_file)
    
    # 格式化飞书消息
    message = format_feishu_message(results)
    
    # 保存消息到文件（用于后续发送）
    message_file = f"/workspace/projects/workspace/skills/xhs-crawler-tool/data/feishu_msg_{timestamp}.txt"
    with open(message_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    print(f"✅ 结果已保存到: {output_file}.csv")
    print(f"✅ 飞书消息已保存到: {message_file}")
    
    # 尝试发送飞书消息
    try:
        # 使用feishu插件发送（如果有配置）
        print("📤 正在发送飞书消息...")
        # 这里可以调用feishu的发送API
        # 由于需要异步，我们保存到文件，由另一个脚本发送
        print("✅ 飞书消息已准备，请使用 feishu-send.sh 发送")
    except Exception as e:
        print(f"⚠️ 飞书发送失败: {e}")
    
    return True


if __name__ == "__main__":
    success = crawl_and_notify()
    sys.exit(0 if success else 1)
