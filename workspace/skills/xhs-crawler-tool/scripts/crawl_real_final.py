#!/usr/bin/env python3
"""
小红书真实数据爬取 - 最终可用版本
使用Cookie + Playwright获取真实数据
"""

import asyncio
import json
import os
import re
import csv
from datetime import datetime
from playwright.async_api import async_playwright


async def crawl_xhs_real(keyword: str, cookie: str, output_dir: str = "data"):
    """
    爬取小红书真实数据
    
    Args:
        keyword: 搜索关键词
        cookie: web_session cookie值
        output_dir: 输出目录
    
    Returns:
        list: 爬取的数据列表
    """
    
    results = []
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        # 设置Cookie
        await context.add_cookies([
            {"name": "web_session", "value": cookie, "domain": ".xiaohongshu.com", "path": "/"},
        ])
        
        page = await context.new_page()
        
        try:
            print(f"🔍 正在搜索: {keyword}")
            
            # 访问搜索页
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
            await page.goto(search_url, wait_until="domcontentloaded")
            
            # 等待页面渲染
            print("⏳ 等待页面渲染...")
            await asyncio.sleep(10)
            
            # 等待元素加载
            try:
                await page.wait_for_selector('section.note-item, .feeds-page', timeout=10000)
            except:
                pass
            
            # 获取HTML内容
            html = await page.content()
            
            # 提取数据
            results = parse_xhs_data(html, keyword)
            
            if results:
                print(f"✅ 成功获取 {len(results)} 条真实数据！")
                
                # 保存数据
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # JSON格式
                json_file = f"{output_dir}/xhs_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"💾 JSON: {json_file}")
                
                # CSV格式
                csv_file = f"{output_dir}/xhs_{timestamp}.csv"
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    if results:
                        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'likes', 'comments', 'url', 'publish_time'])
                        writer.writeheader()
                        for item in results:
                            writer.writerow({k: item.get(k, '') for k in ['title', 'author', 'likes', 'comments', 'url', 'publish_time']})
                print(f"💾 CSV: {csv_file}")
                
            else:
                print("⚠️ 未获取到数据")
                
        except Exception as e:
            print(f"❌ 爬取错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
    
    return results


def parse_xhs_data(html: str, keyword: str) -> list:
    """解析小红书HTML数据"""
    results = []
    
    # 提取INITIAL_STATE
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})</script>', html, re.DOTALL)
    if not match:
        print("⚠️ 未找到INITIAL_STATE")
        return results
    
    try:
        data_str = match.group(1)
        # 处理JavaScript undefined
        data_str = data_str.replace(':undefined,', ':null,').replace(':undefined}', ':null}').replace(':undefined]', ':null]')
        data = json.loads(data_str)
        
        # 从feed.feeds提取数据
        if data.get("feed") and data["feed"].get("feeds"):
            for feed in data["feed"]["feeds"]:
                if feed.get("noteCard"):
                    card = feed["noteCard"]
                    user = card.get("user", {})
                    interact = card.get("interactInfo", {})
                    
                    # 解析点赞数
                    likes_str = str(interact.get("likedCount", "0"))
                    if "万" in likes_str:
                        likes = int(float(likes_str.replace("万", "")) * 10000)
                    else:
                        likes = int(likes_str) if likes_str.isdigit() else 0
                    
                    note = {
                        "title": card.get("displayTitle", "无标题"),
                        "content": "",  # 列表页无详细内容
                        "author": user.get("nickname", user.get("nickName", "未知")),
                        "likes": likes,
                        "comments": 0,  # 列表页无评论数
                        "url": f"https://www.xiaohongshu.com/explore/{feed.get('id', '')}",
                        "publish_time": "",
                        "keyword": keyword,
                    }
                    results.append(note)
    
    except Exception as e:
        print(f"⚠️ 解析失败: {e}")
    
    return results


async def main():
    """主函数"""
    # 获取Cookie
    cookie_file = "config/cookie.txt"
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    else:
        cookie = os.getenv("XHS_COOKIE", "")
    
    if not cookie:
        print("❌ 错误: 未找到Cookie")
        print("💡 请设置环境变量 XHS_COOKIE 或创建 config/cookie.txt")
        return 1
    
    # 获取关键词
    keyword = os.getenv("XHS_KEYWORD", "南山书城 舞房 转卡")
    
    print("="*60)
    print("🔥 小红书真实数据爬取")
    print("="*60)
    print(f"关键词: {keyword}")
    print(f"Cookie: {cookie[:20]}...")
    print("")
    
    # 执行爬取
    results = await crawl_xhs_real(keyword, cookie)
    
    if results:
        print("\n" + "="*60)
        print("📊 数据预览（前5条）:")
        print("-"*60)
        for i, item in enumerate(results[:5], 1):
            print(f"\n{i}. {item['title'][:50]}...")
            print(f"   👤 {item['author']} | ❤️ {item['likes']}")
            print(f"   🔗 {item['url']}")
        print("-"*60)
        print(f"\n✅ 总计: {len(results)} 条数据")
        return 0
    else:
        print("\n❌ 未获取到数据")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
