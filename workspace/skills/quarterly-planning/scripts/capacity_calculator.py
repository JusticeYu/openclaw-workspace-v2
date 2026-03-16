#!/usr/bin/env python3
"""
项目组负荷计算器
根据成员系数、季度工作日和计划人天计算项目组负荷情况
"""

import argparse
import json
from typing import Dict, List


def calculate_capacity(
    workdays: int,
    dev_capacity: float,
    test_capacity: float,
    product_capacity: float,
    total_days: float
) -> Dict:
    """
    计算项目组负荷
    
    公式：
    负荷率 = 实际立项故事总计划人天 / (系数总和 × 季度工作日)
    
    参数：
        workdays: 季度工作日
        dev_capacity: 开发系数总和
        test_capacity: 测试系数总和
        product_capacity: 产品系数总和
        total_days: 立项故事总计划人天
    
    返回：
        dict: 包含详细计算结果
    """
    
    # 计算系数总和
    total_capacity = dev_capacity + test_capacity + product_capacity
    
    # 计算总可用产能（人天）
    available_capacity = total_capacity * workdays
    
    # 计算负荷率
    load_rate = (total_days / available_capacity) * 100 if available_capacity > 0 else 0
    
    # 计算剩余产能
    remaining_capacity = available_capacity - total_days
    
    # 评估负荷状态
    if load_rate < 50:
        status = "偏低"
        status_emoji = "⚠️"
        suggestion = "可以考虑增加特性或优化资源分配"
    elif load_rate < 70:
        status = "偏低"
        status_emoji = "⚡"
        suggestion = "负荷较低，有空间增加特性"
    elif load_rate <= 85:
        status = "合理"
        status_emoji = "✅"
        suggestion = "负荷在建议范围内，状态良好"
    elif load_rate <= 100:
        status = "偏高"
        status_emoji = "⚠️"
        suggestion = "负荷较高，建议减少低优先级特性或增加资源"
    else:
        status = "过载"
        status_emoji = "❌"
        suggestion = "负荷严重超标，必须调整立项范围或增加资源"
    
    # 计算各角色负荷分布
    dev_load = (dev_capacity / total_capacity) * 100 if total_capacity > 0 else 0
    test_load = (test_capacity / total_capacity) * 100 if total_capacity > 0 else 0
    product_load = (product_capacity / total_capacity) * 100 if total_capacity > 0 else 0
    
    return {
        "workdays": workdays,
        "dev_capacity": dev_capacity,
        "test_capacity": test_capacity,
        "product_capacity": product_capacity,
        "total_capacity": total_capacity,
        "available_capacity": round(available_capacity, 1),
        "planned_days": total_days,
        "load_rate": round(load_rate, 1),
        "remaining_capacity": round(remaining_capacity, 1),
        "status": status,
        "status_emoji": status_emoji,
        "suggestion": suggestion,
        "role_distribution": {
            "dev": round(dev_load, 1),
            "test": round(test_load, 1),
            "product": round(product_load, 1)
        }
    }


def print_results(result: Dict):
    """打印计算结果"""
    
    print(f"\n{'='*60}")
    print(f"📊 项目组负荷评估报告")
    print(f"{'='*60}")
    
    print(f"\n【基础参数】")
    print(f"  季度工作日：{result['workdays']}天")
    print(f"  开发系数：{result['dev_capacity']}")
    print(f"  测试系数：{result['test_capacity']}")
    print(f"  产品系数：{result['product_capacity']}")
    print(f"  系数总和：{result['total_capacity']}")
    
    print(f"\n【产能分析】")
    print(f"  总可用产能：{result['available_capacity']} 人天")
    print(f"  计划人天：{result['planned_days']} 人天")
    print(f"  剩余产能：{result['remaining_capacity']} 人天")
    
    print(f"\n【负荷评估】")
    print(f"  负荷率：{result['load_rate']}% {result['status_emoji']} ({result['status']})")
    print(f"  建议范围：70% - 85%")
    print(f"  评估建议：{result['suggestion']}")
    
    print(f"\n【角色分布】")
    print(f"  开发占比：{result['role_distribution']['dev']}%")
    print(f"  测试占比：{result['role_distribution']['test']}%")
    print(f"  产品占比：{result['role_distribution']['product']}%")
    
    print(f"{'='*60}\n")


def calculate_from_members(workdays: int, members: List[Dict], total_days: float) -> Dict:
    """
    从成员列表计算负荷
    
    members格式：
    [
        {"name": "张三", "role": "dev", "capacity": 0.8},
        {"name": "李四", "role": "test", "capacity": 1.0},
        ...
    ]
    """
    dev_capacity = sum(m["capacity"] for m in members if m["role"] == "dev")
    test_capacity = sum(m["capacity"] for m in members if m["role"] == "test")
    product_capacity = sum(m["capacity"] for m in members if m["role"] == "product")
    
    return calculate_capacity(workdays, dev_capacity, test_capacity, product_capacity, total_days)


def main():
    parser = argparse.ArgumentParser(description="计算项目组负荷")
    parser.add_argument("--workdays", type=int, required=True, help="季度工作日")
    parser.add_argument("--dev-capacity", type=float, required=True, help="开发系数总和")
    parser.add_argument("--test-capacity", type=float, required=True, help="测试系数总和")
    parser.add_argument("--product-capacity", type=float, required=True, help="产品系数总和")
    parser.add_argument("--total-days", type=float, required=True, help="立项故事总计划人天")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出")
    parser.add_argument("--members-file", type=str, help="从JSON文件读取成员列表")
    
    args = parser.parse_args()
    
    if args.members_file:
        # 从文件读取成员列表
        with open(args.members_file, 'r', encoding='utf-8') as f:
            members = json.load(f)
        result = calculate_from_members(args.workdays, members, args.total_days)
    else:
        # 直接使用参数计算
        result = calculate_capacity(
            args.workdays,
            args.dev_capacity,
            args.test_capacity,
            args.product_capacity,
            args.total_days
        )
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_results(result)


if __name__ == "__main__":
    main()
