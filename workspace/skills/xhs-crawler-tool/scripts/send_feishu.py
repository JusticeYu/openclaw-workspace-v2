#!/usr/bin/env python3
"""
飞书Webhook消息推送脚本
用于自动发送小红书爬虫报告
"""

import os
import sys
import json
import requests
from datetime import datetime

# 读取消息文件
MESSAGE_FILE = "/workspace/projects/workspace/skills/xhs-crawler-tool/data/feishu_message.txt"
WEBHOOK_ENV = "FEISHU_WEBHOOK"


def send_feishu_webhook(webhook_url: str, message: str) -> bool:
    """发送飞书消息到Webhook"""
    
    # 构建飞书消息卡片格式
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("✅ 飞书消息发送成功！")
                return True
            else:
                print(f"❌ 飞书API错误: {result.get('msg', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False


def load_message(filepath: str) -> str:
    """读取消息文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 消息文件不存在: {filepath}")
        return None
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None


def main():
    print("="*60)
    print("📤 飞书Webhook消息推送")
    print("="*60)
    
    # 1. 获取Webhook URL
    webhook_url = os.getenv(WEBHOOK_ENV)
    
    if not webhook_url:
        print(f"\n❌ 错误: 未设置环境变量 {WEBHOOK_ENV}")
        print("\n💡 请先配置Webhook:")
        print(f"   方式1: export {WEBHOOK_ENV}='你的Webhook地址'")
        print(f"   方式2: 在系统环境变量中配置")
        print("\n📝 获取Webhook方法:")
        print("   1. 打开飞书群聊")
        print("   2. 点击右上角设置 → 群机器人")
        print("   3. 添加机器人 → 选择Webhook")
        print("   4. 复制Webhook地址")
        return 1
    
    print(f"✅ Webhook已配置: {webhook_url[:30]}...")
    
    # 2. 读取消息
    message = load_message(MESSAGE_FILE)
    if not message:
        return 1
    
    print(f"\n📝 消息长度: {len(message)} 字符")
    print(f"📋 消息预览:\n{message[:200]}...")
    
    # 3. 发送消息
    print("\n🚀 正在发送...")
    success = send_feishu_webhook(webhook_url, message)
    
    if success:
        print("\n" + "="*60)
        print("✅ 飞书消息推送完成！")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("❌ 飞书消息推送失败")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
