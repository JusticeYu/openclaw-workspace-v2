#!/usr/bin/env python3
"""
小红书真实数据爬取 - 增强反检测版本
使用Stealth插件绕过检测
"""

import asyncio
import json
import os
import random
from datetime import datetime
from playwright.async_api import async_playwright

# 随机User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

async def crawl_xhs_enhanced(keyword: str, cookie: str):
    """增强版爬取"""
    
    results = []
    
    async with async_playwright() as p:
        # 启动浏览器（增强配置）
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-webgl',
                '--disable-software-rasterizer',
            ]
        )
        
        # 创建上下文（模拟真实用户）
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=random.choice(USER_AGENTS),
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            permissions=['geolocation'],
            geolocation={'latitude': 22.5431, 'longitude': 114.0579},  # 深圳坐标
        )
        
        # 设置Cookie（包括所有必要字段）
        cookies = [
            {"name": "web_session", "value": cookie, "domain": ".xiaohongshu.com", "path": "/"},
            {"name": "webId", "value": "xhs_web_" + str(random.randint(10000000000000, 99999999999999)), "domain": ".xiaohongshu.com", "path": "/"},
            {"name": "xhsTrackerId", "value": "xhs_tracker_" + str(random.randint(100000, 999999)), "domain": ".xiaohongshu.com", "path": "/"},
        ]
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        # 注入脚本绕过检测
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.chrome = { runtime: {} };
        """)
        
        try:
            print(f"🔍 正在搜索: {keyword}")
            print("⏳ 等待页面加载...")
            
            # 先访问首页
            await page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(random.uniform(2, 4))
            
            # 再访问搜索页
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
            await page.goto(search_url, wait_until="networkidle", timeout=60000)
            
            # 等待JS执行
            await asyncio.sleep(random.uniform(3, 5))
            
            # 检查页面状态
            title = await page.title()
            print(f"📄 页面标题: {title}")
            
            if "安全限制" in title or "访问异常" in title:
                print("❌ 触发安全限制，尝试备用方案...")
                # 保存调试信息
                await page.screenshot(path="data/error_screenshot.png")
                return []
            
            # 尝试多种方式提取数据
            results = await try_extract_data(page, keyword)
            
        except Exception as e:
            print(f"❌ 爬取错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
    
    return results


async def try_extract_data(page, keyword):
    """尝试多种方式提取数据"""
    results = []
    
    # 方式1: 从window.__INITIAL_STATE__提取
    try:
        notes = await page.evaluate("""
            () => {
                if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.feed) {
                    return window.__INITIAL_STATE__.feed.feeds || [];
                }
                return [];
            }
        """)
        
        if notes and len(notes) > 0:
            print(f"✅ 方式1成功: 获取 {len(notes)} 条数据")
            for note in notes:
                if note.get("noteCard"):
                    card = note["noteCard"]
                    results.append(format_note(card, keyword))
            return results
    except Exception as e:
        print(f"⚠️ 方式1失败: {e}")
    
    # 方式2: 从note数据提取
    try:
        notes = await page.evaluate("""
            () => {
                if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.note) {
                    return Object.values(window.__INITIAL_STATE__.note).filter(n => n && n.title);
                }
                return [];
            }
        """)
        
        if notes and len(notes) > 0:
            print(f"✅ 方式2成功: 获取 {len(notes)} 条数据")
            for note in notes:
                results.append(format_note(note, keyword))
            return results
    except Exception as e:
        print(f"⚠️ 方式2失败: {e}")
    
    # 方式3: 从DOM提取
    try:
        print("🔄 尝试从DOM提取...")
        cards = await page.query_selector_all('section.note-item')
        print(f"找到 {len(cards)} 个卡片元素")
        
        for card in cards[:10]:
            try:
                title_el = await card.query_selector('.title')
                title = await title_el.inner_text() if title_el else "无标题"
                
                author_el = await card.query_selector('.author')
                author = await author_el.inner_text() if author_el else "未知"
                
                results.append({
                    "title": title,
                    "content": "",
                    "author": author,
                    "likes": 0,
                    "comments": 0,
                    "url": "",
                    "publish_time": "",
                    "keyword": keyword
                })
            except:
                pass
        
        if results:
            print(f"✅ 方式3成功: 获取 {len(results)} 条数据")
            return results
    except Exception as e:
        print(f"⚠️ 方式3失败: {e}")
    
    return results


def format_note(card, keyword):
    """格式化笔记数据"""
    user = card.get("user", {}) or {}
    interact = card.get("interactInfo", {}) or {}
    
    return {
        "title": card.get("title", "无标题"),
        "content": (card.get("desc", "") or "")[:200] + "..." if len(card.get("desc", "") or "") > 200 else (card.get("desc", "") or ""),
        "author": user.get("nickname", "未知"),
        "likes": interact.get("likedCount", 0) or card.get("likes", 0),
        "comments": interact.get("commentCount", 0) or card.get("comments", 0),
        "url": f"https://www.xiaohongshu.com/explore/{card.get('noteId', '')}",
        "publish_time": card.get("time", ""),
        "keyword": keyword
    }


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
    
    print("🚀 开始爬取真实数据（增强版）...")
    print("="*60)
    
    keyword = "南山书城 舞房 转卡"
    results = await crawl_xhs_enhanced(keyword, cookie)
    
    print("\n" + "="*60)
    if results:
        print(f"✅ 成功获取 {len(results)} 条真实数据！")
        
        # 显示数据
        print("\n📊 数据预览:")
        print("-"*60)
        for i, item in enumerate(results[:5], 1):
            print(f"\n{i}. {item['title'][:40]}...")
            print(f"   👤 {item['author']} | ❤️ {item['likes']} | 💬 {item['comments']}")
            if item['url']:
                print(f"   🔗 {item['url']}")
        print("-"*60)
        
        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/xhs_real_{timestamp}.json"
        
        os.makedirs("data", exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 真实数据已保存: {filename}")
        return True
    else:
        print("⚠️ 未能获取真实数据")
        print("💡 可能原因:")
        print("   1. Cookie已过期，需要重新获取")
        print("   2. 小红书安全限制严格")
        print("   3. IP地址被限制")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
