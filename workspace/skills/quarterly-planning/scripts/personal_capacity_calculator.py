#!/usr/bin/env python3
"""
个人资源负荷计算器
计算每个项目组成员的资源负荷情况，识别风险并给出预警
"""

import argparse
import json
from typing import Dict, List, Tuple
from datetime import datetime


def calculate_personal_load(
    members: List[Dict],
    quarter_workdays: int,
    tasks: List[Dict] = None
) -> Dict:
    """
    计算每个项目组成员的个人负荷
    
    参数：
        members: 成员列表
        [
            {"name": "张三", "role": "dev", "capacity": 0.8},
            {"name": "李四", "role": "dev", "capacity": 1.0},
            ...
        ]
        quarter_workdays: 季度工作日
        tasks: 任务分配（可选）
        [
            {"name": "张三", "task_days": 50},
            {"name": "李四", "task_days": 60},
            ...
        ]
    
    返回：
        dict: 包含每个人的负荷详情和风险预警
    """
    
    results = {
        "quarter_workdays": quarter_workdays,
        "total_members": len(members),
        "members": [],
        "risk_warnings": [],
        "summary": {
            "total_overload": 0,
            "total_underload": 0,
            "total_normal": 0,
            "risk_level": "GREEN"  # GREEN/YELLOW/RED
        }
    }
    
    # 如果没有提供任务，显示警告
    if tasks is None:
        # 按系数比例分配总工作量（临时方案，用于演示）
        # 实际使用时应该提供任务分配数据
        total_capacity = sum(m["capacity"] for m in members)
        estimated_total = quarter_workdays * total_capacity * 0.8  # 假设80%利用率
        tasks = []
        for member in members:
            task_days = 0
            if total_capacity > 0:
                task_days = (member["capacity"] / total_capacity) * estimated_total
            tasks.append({
                "name": member["name"],
                "task_days": round(task_days, 1)
            })
        print("⚠️ 注意：未提供任务分配数据，以上为估算值")
        print("   建议提供 --tasks-file 指定实际任务分配")
    
    # 计算每个人的人日
    task_map = {t["name"]: t["task_days"] for t in tasks}
    
    for member in members:
        name = member.get("name", "Unknown")
        role = member.get("role", "unknown")
        capacity = member.get("capacity", 0)
        
        # 计算可用产能
        available_days = capacity * quarter_workdays
        
        # 获取任务人天
        task_days = task_map.get(name, 0)
        
        # 计算负荷率
        load_rate = (task_days / available_days * 100) if available_days > 0 else 0
        
        # 风险评估
        if load_rate > 100:
            risk_level = "🔴 HIGH"
            risk_type = "OVERLOAD"
            suggestion = "减少任务分配或增加资源"
        elif load_rate >= 80:
            risk_level = "🟡 MEDIUM"
            risk_type = "NORMAL"
            suggestion = "负荷正常，注意监控"
        else:
            risk_level = "🟢 LOW"
            risk_type = "UNDERLOAD"
            suggestion = "资源未充分利用，可增加任务"
        
        member_result = {
            "name": name,
            "role": role,
            "capacity": capacity,
            "available_days": round(available_days, 1),
            "task_days": round(task_days, 1),
            "load_rate": round(load_rate, 1),
            "risk_level": risk_level,
            "risk_type": risk_type,
            "suggestion": suggestion,
            "remaining_days": round(available_days - task_days, 1)
        }
        
        results["members"].append(member_result)
        
        # 统计风险
        if load_rate > 100:
            results["summary"]["total_overload"] += 1
            results["risk_warnings"].append({
                "name": name,
                "type": "OVERLOAD",
                "message": f"{name}（{role}）负荷率 {load_rate:.1f}%，超出可用产能！",
                "severity": "HIGH",
                "action": "需要立即调整任务分配或增加资源"
            })
        elif load_rate < 50:
            results["summary"]["total_underload"] += 1
        else:
            results["summary"]["total_normal"] += 1
    
    # 综合风险等级
    if results["summary"]["total_overload"] > 0:
        results["summary"]["risk_level"] = "🔴 RED"
        results["summary"]["risk_message"] = f"有 {results['summary']['total_overload']} 人负荷超过100%，存在资源风险！"
    elif results["summary"]["total_underload"] > len(members) * 0.5:
        results["summary"]["risk_level"] = "🟡 YELLOW"
        results["summary"]["risk_message"] = "资源整体利用率偏低"
    else:
        results["summary"]["risk_level"] = "🟢 GREEN"
        results["summary"]["risk_message"] = "资源负荷整体正常"
    
    return results


def print_results(results: Dict):
    """打印个人负荷计算结果"""
    
    print(f"\n{'='*70}")
    print(f"📊 个人资源负荷分析报告")
    print(f"{'='*70}")
    
    print(f"\n【基本信息】")
    print(f"  季度工作日：{results['quarter_workdays']} 天")
    print(f"  项目组成员：{results['total_members']} 人")
    
    print(f"\n{'='*70}")
    print(f"👥 个人负荷详情")
    print(f"{'='*70}")
    
    # 表头
    print(f"\n{'姓名':<10} {'角色':<8} {'系数':<6} {'可用产能':<10} {'任务人天':<10} {'负荷率':<10} {'状态':<12}")
    print("-" * 70)
    
    for m in results["members"]:
        status = m["risk_level"]
        print(f"{m['name']:<10} {m['role']:<8} {m['capacity']:<6.1f} {m['available_days']:<10.1f} {m['task_days']:<10.1f} {m['load_rate']:<10.1f}% {status:<12}")
    
    print("-" * 70)
    
    # 风险预警
    print(f"\n{'='*70}")
    print(f"⚠️ 风险预警")
    print(f"{'='*70}")
    
    if results["risk_warnings"]:
        for warning in results["risk_warnings"]:
            print(f"\n{warning['message']}")
            print(f"  严重程度：{warning['severity']}")
            print(f"  建议措施：{warning['action']}")
    else:
        print("\n✅ 暂无风险预警")
    
    # 汇总
    print(f"\n{'='*70}")
    print(f"📈 汇总统计")
    print(f"{'='*70}")
    print(f"  负荷超标（>100%）：{results['summary']['total_overload']} 人")
    print(f"  负荷正常（50-100%）：{results['summary']['total_normal']} 人")
    print(f"  负荷偏低（<50%）：{results['summary']['total_underload']} 人")
    print(f"  综合风险等级：{results['summary']['risk_level']}")
    print(f"  风险评估：{results['summary']['risk_message']}")
    
    print(f"\n{'='*70}\n")


def calculate_team_load(
    team_name: str,
    members: List[Dict],
    quarter_workdays: int,
    total_planned_days: float
) -> Dict:
    """
    计算项目组整体负荷（兼容旧接口）
    """
    # 计算总系数
    dev_capacity = sum(m["capacity"] for m in members if m.get("role") == "dev")
    test_capacity = sum(m["capacity"] for m in members if m.get("role") == "test")
    product_capacity = sum(m["capacity"] for m in members if m.get("role") == "product")
    total_capacity = dev_capacity + test_capacity + product_capacity
    
    available_capacity = total_capacity * quarter_workdays
    load_rate = (total_planned_days / available_capacity * 100) if available_capacity > 0 else 0
    
    # 风险预警
    risk_warnings = []
    if load_rate > 100:
        risk_level = "🔴 HIGH"
        risk_warnings.append({
            "team": team_name,
            "type": "OVERLOAD",
            "message": f"项目组【{team_name}】整体负荷率 {load_rate:.1f}%，超出可用产能！",
            "severity": "HIGH",
            "action": "需要减少立项范围或增加资源"
        })
    elif load_rate > 90:
        risk_level = "🟡 MEDIUM"
    else:
        risk_level = "🟢 NORMAL"
    
    # 计算个人负荷
    personal_results = calculate_personal_load(members, quarter_workdays)
    
    return {
        "team_name": team_name,
        "quarter_workdays": quarter_workdays,
        "dev_capacity": dev_capacity,
        "test_capacity": test_capacity,
        "product_capacity": product_capacity,
        "total_capacity": total_capacity,
        "available_capacity": round(available_capacity, 1),
        "planned_days": total_planned_days,
        "load_rate": round(load_rate, 1),
        "risk_level": risk_level,
        "risk_warnings": risk_warnings,
        "personal_loads": personal_results["members"]
    }


def print_team_result(result: Dict):
    """打印项目组负荷结果"""
    
    print(f"\n{'='*60}")
    print(f"📊 项目组负荷评估：{result['team_name']}")
    print(f"{'='*60}")
    
    print(f"\n【基础参数】")
    print(f"  季度工作日：{result['quarter_workdays']} 天")
    print(f"  开发系数：{result['dev_capacity']}")
    print(f"  测试系数：{result['test_capacity']}")
    print(f"  产品系数：{result['product_capacity']}")
    print(f"  系数总和：{result['total_capacity']}")
    
    print(f"\n【产能分析】")
    print(f"  总可用产能：{result['available_capacity']} 人天")
    print(f"  计划人天：{result['planned_days']} 人天")
    
    print(f"\n【负荷评估】")
    print(f"  负荷率：{result['load_rate']}% {result['risk_level']}")
    
    # 风险预警
    if result["risk_warnings"]:
        print(f"\n⚠️ 风险预警：")
        for warning in result["risk_warnings"]:
            print(f"  • {warning['message']}")
            print(f"    建议：{warning['action']}")
    
    print(f"\n【个人负荷】")
    for p in result["personal_loads"]:
        status = "⚠️" if p["load_rate"] > 100 else "✓"
        print(f"  {status} {p['name']}（{p['role']}）: {p['load_rate']}% ({p['task_days']}/{p['available_days']}人天)")
    
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="计算个人资源负荷和风险预警")
    parser.add_argument("--workdays", type=int, required=True, help="季度工作日")
    parser.add_argument("--members-file", type=str, required=True, help="成员列表JSON文件")
    parser.add_argument("--tasks-file", type=str, help="任务分配JSON文件（可选）")
    parser.add_argument("--team-name", type=str, help="项目组名称")
    parser.add_argument("--total-days", type=float, help="计划总人天（用于团队负荷计算）")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出")
    
    args = parser.parse_args()
    
    # 读取成员文件
    with open(args.members_file, 'r', encoding='utf-8') as f:
        members = json.load(f)
    
    # 读取任务文件（可选）
    tasks = None
    if args.tasks_file:
        with open(args.tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    
    # 计算
    if args.team_name and args.total_days:
        # 团队负荷计算
        result = calculate_team_load(args.team_name, members, args.workdays, args.total_days)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_team_result(result)
    else:
        # 个人负荷计算
        result = calculate_personal_load(members, args.workdays, tasks)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_results(result)


if __name__ == "__main__":
    main()
