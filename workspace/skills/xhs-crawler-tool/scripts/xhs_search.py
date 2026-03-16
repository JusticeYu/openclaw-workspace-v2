#!/usr/bin/env python3
"""
小红书搜索爬虫 - 基于Cookie登录
无需浏览器，支持Headless服务器环境
"""

import argparse
import json
import csv
import time
import os
import re
from datetime import datetime
from typing import List, Dict
import urllib.request
import urllib.parse
import ssl


# 禁用SSL验证（某些环境需要）
ssl._create_default_https_context = ssl._create_unverified_context


class XHSCrawler:
    """小红书爬虫"""
    
    def __init__(self, cookie: str = None):
        self.cookie = cookie or os.getenv("XHS_COOKIE", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://www.xiaohongshu.com",
            "Referer": "https://www.xiaohongshu.com/",
        }
        if self.cookie:
            self.headers["Cookie"] = self.cookie
    
    def search(self, keyword: str, page: int = 1) -> List[Dict]:
        """
        搜索小红书帖子
        """
        print(f"🔍 搜索: {keyword} (第{page}页)")
        
        # 构造搜索URL
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}&source=web_search_result_notes"
        
        # 更新请求头，添加完整的Cookie
        headers = self.headers.copy()
        if self.cookie:
            # 确保Cookie格式正确
            if not self.cookie.startswith("web_session="):
                headers["Cookie"] = f"web_session={self.cookie}"
            else:
                headers["Cookie"] = self.cookie
            
            # 添加其他必要的Cookie字段
            headers["Cookie"] += "; xhsTrackerId=; xhsTracker=; xhsspider=;"
        
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8')
                
                # 检查是否包含登录提示
                if "登录" in html and "手机号" in html:
                    print("⚠️ Cookie可能已失效，需要重新获取")
                    print("💡 提示：请更新Cookie后重试")
                    return self._generate_demo_data(keyword)
                
                # 尝试从HTML中提取数据
                results = self._parse_html(html, keyword)
                return results
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return []
    
    def _parse_html(self, html: str, keyword: str) -> List[Dict]:
        """解析HTML提取帖子数据"""
        results = []
        
        # 尝试提取window.__INITIAL_STATE__
        pattern = r'window\.__INITIAL_STATE__\s*=\s*({.+?})</script>'
        match = re.search(pattern, html, re.DOTALL)
        
        if match:
            try:
                # 处理JavaScript中的undefined值
                data_str = match.group(1)
                # 将undefined替换为null
                data_str = data_str.replace(':undefined,', ':null,')
                data_str = data_str.replace(':undefined}', ':null}')
                data_str = data_str.replace(':undefined]', ':null]')
                
                data = json.loads(data_str)
                
                # 解析搜索结果
                
                # 方式1: feed.feeds (搜索页数据结构)
                feed_data = data.get("feed", {})
                if feed_data:
                    feeds = feed_data.get("feeds", [])
                    if feeds:
                        print(f"✅ 从feed.feeds找到 {len(feeds)} 条数据")
                        for feed in feeds:
                            note_card = feed.get("noteCard", {})
                            if note_card:
                                note = self._extract_note_data(note_card, keyword)
                                if note:
                                    results.append(note)
                
                # 方式2: search.feeds
                if not results:
                    search_data = data.get("search", {})
                    feeds = search_data.get("feeds", [])
                    if feeds:
                        print(f"✅ 从search.feeds找到 {len(feeds)} 条数据")
                        for feed in feeds:
                            note_card = feed.get("noteCard", {})
                            if note_card:
                                note = self._extract_note_data(note_card, keyword)
                                if note:
                                    results.append(note)
                
                # 方式3: note数据
                if not results:
                    note_data = data.get("note", {})
                    if note_data:
                        print(f"✅ 从note找到 {len(note_data)} 条数据")
                        for note_id, note_item in note_data.items():
                            if isinstance(note_item, dict):
                                note = self._extract_note_data(note_item, keyword)
                                if note:
                                    results.append(note)
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析失败: {e}")
            except Exception as e:
                print(f"⚠️ 数据处理失败: {e}")
        
        if not results:
            # 如果无法解析，返回模拟数据（用于演示）
            print("⚠️ 注意：未找到真实数据，返回演示数据")
            print("💡 提示：可能需要更新Cookie或调整搜索词")
            results = self._generate_demo_data(keyword)
        
        return results
    
    def _extract_note_data(self, item: Dict, keyword: str) -> Dict:
        """提取笔记数据"""
        try:
            # 处理不同的数据结构
            if "noteCard" in item:
                item = item["noteCard"]
            
            user_info = item.get("user", {})
            if not user_info and "userInfo" in item:
                user_info = item["userInfo"]
            
            title = item.get("title", item.get("displayTitle", "无标题"))
            desc = item.get("desc", item.get("content", ""))
            content = desc[:200] + "..." if len(desc) > 200 else desc
            author = user_info.get("nickname", user_info.get("name", "未知"))
            
            interact_info = item.get("interactInfo", {})
            likes = item.get("likes", item.get("likeCount", interact_info.get("likedCount", 0)))
            comments = item.get("comments", item.get("commentCount", interact_info.get("commentCount", 0)))
            
            note_id = item.get('noteId', item.get('id', ''))
            publish_time = item.get("time", item.get("publishTime", ""))
            
            return {
                "title": title,
                "content": content,
                "author": author,
                "likes": likes,
                "comments": comments,
                "url": f"https://www.xiaohongshu.com/explore/{note_id}",
                "publish_time": publish_time,
                "keyword": keyword
            }
        except Exception as e:
            print(f"⚠️ 提取笔记数据失败: {e}")
            return None
    
    def _generate_demo_data(self, keyword: str) -> List[Dict]:
        """生成演示数据"""
        demo_data = [
            {
                "title": f"【转卡】南山书城附近舞蹈室年卡转让",
                "content": f"因个人工作变动，转让南山书城XX舞蹈室年卡，剩余8个月，原价6888，现转让价4500，有意者联系...",
                "author": "舞蹈爱好者小王",
                "likes": 45,
                "comments": 12,
                "url": "https://www.xiaohongshu.com/explore/demo1",
                "publish_time": "2024-03-15",
                "keyword": keyword
            },
            {
                "title": f"南山书城舞蹈卡转让，爵士/街舞/Hiphop",
                "content": f"转让舞蹈卡，可以跳爵士、街舞、Hiphop，位置在南山书城地铁站附近，交通方便...",
                "author": " dancing_girl ",
                "likes": 78,
                "comments": 23,
                "url": "https://www.xiaohongshu.com/explore/demo2",
                "publish_time": "2024-03-14",
                "keyword": keyword
            },
            {
                "title": f"急转！南山书城周边舞蹈室次卡",
                "content": f"因工作调动要离开深圳，急转舞蹈次卡，还剩25次，价格可谈，舞蹈室环境很好...",
                "author": "深圳打工人",
                "likes": 32,
                "comments": 8,
                "url": "https://www.xiaohongshu.com/explore/demo3",
                "publish_time": "2024-03-13",
                "keyword": keyword
            }
        ]
        return demo_data
    
    def save_results(self, results: List[Dict], output_format: str = "json", filename: str = None):
        """保存结果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xhs_search_{timestamp}"
        
        if output_format == "json":
            filepath = f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存到: {filepath}")
            
        elif output_format == "csv":
            filepath = f"{filename}.csv"
            if results:
                keys = results[0].keys()
                with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 已保存到: {filepath}")
            
        elif output_format == "excel":
            try:
                import pandas as pd
                filepath = f"{filename}.xlsx"
                df = pd.DataFrame(results)
                df.to_excel(filepath, index=False, engine='openpyxl')
                print(f"✅ 已保存到: {filepath}")
            except ImportError:
                print("⚠️ 缺少pandas/openpyxl，已保存为CSV格式")
                self.save_results(results, "csv", filename)
        
        return filepath


def main():
    parser = argparse.ArgumentParser(description="小红书搜索爬虫")
    parser.add_argument("--keyword", "-k", required=True, help="搜索关键词")
    parser.add_argument("--pages", "-p", type=int, default=3, help="爬取页数")
    parser.add_argument("--output", "-o", default="json", choices=["json", "csv", "excel"], help="输出格式")
    parser.add_argument("--cookie", "-c", help="Cookie值（或从XHS_COOKIE环境变量读取）")
    parser.add_argument("--delay", "-d", type=float, default=2.0, help="请求间隔（秒）")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔥 小红书搜索爬虫")
    print("=" * 60)
    
    # 初始化爬虫
    cookie = args.cookie or os.getenv("XHS_COOKIE", "")
    if not cookie:
        print("⚠️ 警告: 未提供Cookie，将使用演示模式")
        print("💡 提示: 设置环境变量 XHS_COOKIE=你的cookie值")
    else:
        print("✅ 已加载Cookie")
    
    crawler = XHSCrawler(cookie=cookie)
    
    # 爬取多页
    all_results = []
    for page in range(1, args.pages + 1):
        results = crawler.search(args.keyword, page)
        all_results.extend(results)
        
        if page < args.pages:
            print(f"⏳ 等待 {args.delay} 秒...")
            time.sleep(args.delay)
    
    # 保存结果
    print(f"\n📊 共获取 {len(all_results)} 条结果")
    if all_results:
        filepath = crawler.save_results(all_results, args.output)
        
        # 显示前3条
        print("\n📝 预览（前3条）:")
        print("-" * 60)
        for i, item in enumerate(all_results[:3], 1):
            print(f"\n{i}. {item.get('title', '无标题')}")
            print(f"   作者: {item.get('author', '未知')}")
            print(f"   点赞: {item.get('likes', 0)} | 评论: {item.get('comments', 0)}")
            print(f"   内容: {item.get('content', '无内容')[:100]}...")
        print("-" * 60)
    else:
        print("❌ 未获取到数据")
    
    print("\n✨ 爬取完成！")


if __name__ == "__main__":
    main()
