#!/usr/bin/env python3
"""
小红书真实数据爬取 - 使用Cookie登录（无图形界面）
使用Playwright的headless模式 + 已保存的Cookie
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

async def crawl_xhs_with_cookie(keyword: str, cookie: str):
    """使用Cookie爬取小红书"""
    
    results = []
    
    async with async_playwright() as p:
        # 启动浏览器（headless模式）
        browser = await p.chromium.launch(headless=True)
        
        # 创建新页面
        context = await browser.new_context()
        page = await context.new_page()
        
        # 设置Cookie
        await context.add_cookies([
            {
                "name": "web_session",
                "value": cookie,
                "domain": ".xiaohongshu.com",
                "path": "/"
            }
        ])
        
        try:
            print(f"🔍 正在搜索: {keyword}")
            
            # 访问搜索页面
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
            await page.goto(search_url, wait_until="networkidle", timeout=60000)
            
            # 等待页面加载
            await page.wait_for_timeout(5000)  # 等待5秒让JS执行
            
            # 获取页面HTML
            html = await page.content()
            
            # 提取数据
            results = await extract_data_from_page(page, keyword)
            
        except Exception as e:
            print(f"❌ 爬取错误: {e}")
        finally:
            await browser.close()
    
    return results


async def extract_data_from_page(page, keyword: str):
    """从页面提取数据"""
    results = []
    
    try:
        # 使用JavaScript提取数据
        notes = await page.evaluate("""
            () => {
                const notes = [];
                // 尝试从window.__INITIAL_STATE__获取数据
                if (window.__INITIAL_STATE__) {
                    const feed = window.__INITIAL_STATE__.feed;
                    if (feed && feed.feeds) {
                        feed.feeds.forEach(feed => {
                            if (feed.noteCard) {
                                notes.push(feed.noteCard);
                            }
                        });
                    }
                }
                return notes;
            }
        """)
        
        print(f"✅ 从页面提取到 {len(notes)} 条数据")
        
        for note in notes:
            result = {
                "title": note.get("title", "无标题"),
                "content": (note.get("desc", "") or "")[:200] + "...",
                "author": note.get("user", {}).get("nickname", "未知"),
                "likes": note.get("interactInfo", {}).get("likedCount", 0),
                "comments": note.get("interactInfo", {}).get("commentCount", 0),
                "url": f"https://www.xiaohongshu.com/explore/{note.get('noteId', '')}",
                "publish_time": note.get("time", ""),
                "keyword": keyword
            }
            results.append(result)
            
    except Exception as e:
        print(f"⚠️ 提取数据失败: {e}")
    
    return results


async def main():
    # 获取Cookie
    cookie_file = "config/cookie.txt"
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r') as f:
            cookie = f.read().strip()
    else:
        cookie = os.getenv("XHS_COOKIE", "")
    
    if not cookie:
        print("❌ 错误: 未找到Cookie")
        return
    
    print("🚀 开始爬取真实数据...")
    print("="*60)
    
    keyword = "南山书城 舞房 转卡"
    results = await crawl_xhs_with_cookie(keyword, cookie)
    
    if results:
        print(f"\n✅ 成功获取 {len(results)} 条真实数据")
        
        # 显示前3条
        print("\n预览:")
        print("-"*60)
        for i, item in enumerate(results[:3], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   作者: {item['author']}")
            print(f"   点赞: {item['likes']} | 评论: {item['comments']}")
            print(f"   链接: {item['url']}")
        print("-"*60)
        
        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/xhs_real_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 数据已保存: {filename}")
    else:
        print("\n⚠️ 未获取到数据，可能Cookie已过期")
        print("💡 请更新Cookie后重试")


if __name__ == "__main__":
    asyncio.run(main())
