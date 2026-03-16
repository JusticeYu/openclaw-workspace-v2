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
        
        注意：这是一个简化实现，实际小红书API有签名验证
        这里提供基础框架，完整实现需要处理签名
        """
        print(f"🔍 搜索: {keyword} (第{page}页)")
        
        # 构造搜索URL
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}&source=web_search_result_notes"
        
        try:
            req = urllib.request.Request(url, headers=self.headers, method="GET")
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8')
                
                # 尝试从HTML中提取数据
                # 小红书的数据通常在window.__INITIAL_STATE__中
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
                data = json.loads(match.group(1))
                # 解析搜索结果
                search_results = data.get("search", {}).get("searchResult", {}).get("notes", [])
                
                for item in search_results:
                    note = {
                        "title": item.get("title", ""),
                        "content": item.get("desc", "")[:200] + "..." if len(item.get("desc", "")) > 200 else item.get("desc", ""),
                        "author": item.get("user", {}).get("nickname", ""),
                        "likes": item.get("likes", 0),
                        "comments": item.get("comments", 0),
                        "url": f"https://www.xiahongshu.com/explore/{item.get('id', '')}",
                        "publish_time": item.get("time", ""),
                        "keyword": keyword
                    }
                    results.append(note)
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析失败: {e}")
        
        if not results:
            # 如果无法解析，返回模拟数据（用于演示）
            print("⚠️ 注意：当前为演示模式，返回模拟数据")
            print("💡 提示：需要有效的Cookie才能获取真实数据")
            results = self._generate_demo_data(keyword)
        
        return results
    
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
