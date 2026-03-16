#!/usr/bin/env python3
"""
季度工作日计算器
计算指定年份和季度的工作日数量，考虑节假日、周末和补班
"""

import argparse
from datetime import datetime, timedelta
from typing import List, Tuple

# 2026年中国法定节假日和调休安排（预测版，实际以国务院通知为准）
HOLIDAYS_2026 = {
    # 元旦
    "2026-01-01": {"name": "元旦", "type": "holiday"},
    "2026-01-02": {"name": "元旦调休", "type": "holiday"},
    "2026-01-03": {"name": "元旦调休", "type": "holiday"},
    
    # 春节（预测：2月17日除夕）
    "2026-02-17": {"name": "春节", "type": "holiday"},
    "2026-02-18": {"name": "春节", "type": "holiday"},
    "2026-02-19": {"name": "春节", "type": "holiday"},
    "2026-02-20": {"name": "春节", "type": "holiday"},
    "2026-02-21": {"name": "春节", "type": "holiday"},
    "2026-02-22": {"name": "春节", "type": "holiday"},
    "2026-02-23": {"name": "春节", "type": "holiday"},
    "2026-02-15": {"name": "春节补班", "type": "workday"},  # 周六补班
    "2026-02-28": {"name": "春节补班", "type": "workday"},  # 周六补班
    
    # 清明节
    "2026-04-04": {"name": "清明节", "type": "holiday"},
    "2026-04-05": {"name": "清明调休", "type": "holiday"},
    "2026-04-06": {"name": "清明调休", "type": "holiday"},
    
    # 劳动节
    "2026-05-01": {"name": "劳动节", "type": "holiday"},
    "2026-05-02": {"name": "劳动节调休", "type": "holiday"},
    "2026-05-03": {"name": "劳动节调休", "type": "holiday"},
    "2026-05-04": {"name": "劳动节调休", "type": "holiday"},
    "2026-05-05": {"name": "劳动节调休", "type": "holiday"},
    "2026-04-26": {"name": "劳动节补班", "type": "workday"},  # 周日补班
    "2026-05-09": {"name": "劳动节补班", "type": "workday"},  # 周六补班
    
    # 端午节（预测：6月19日端午节）
    "2026-06-19": {"name": "端午节", "type": "holiday"},
    "2026-06-20": {"name": "端午调休", "type": "holiday"},
    "2026-06-21": {"name": "端午调休", "type": "holiday"},
    "2026-06-22": {"name": "端午补班", "type": "workday"},  # 周一补班
    
    # 中秋节（预测：9月26日中秋节）
    "2026-09-26": {"name": "中秋节", "type": "holiday"},
    "2026-09-27": {"name": "中秋调休", "type": "holiday"},
    "2026-09-28": {"name": "中秋调休", "type": "holiday"},
    "2026-09-29": {"name": "中秋补班", "type": "workday"},  # 周二补班
    
    # 国庆节
    "2026-10-01": {"name": "国庆节", "type": "holiday"},
    "2026-10-02": {"name": "国庆节", "type": "holiday"},
    "2026-10-03": {"name": "国庆节", "type": "holiday"},
    "2026-10-04": {"name": "国庆调休", "type": "holiday"},
    "2026-10-05": {"name": "国庆调休", "type": "holiday"},
    "2026-10-06": {"name": "国庆调休", "type": "holiday"},
    "2026-10-07": {"name": "国庆调休", "type": "holiday"},
    "2026-10-08": {"name": "国庆调休", "type": "holiday"},
    "2026-09-27": {"name": "国庆补班", "type": "workday"},  # 周日补班
    "2026-10-10": {"name": "国庆补班", "type": "workday"},  # 周六补班
}


def get_quarter_dates(year: int, quarter: int) -> Tuple[datetime, datetime]:
    """获取季度的起始和结束日期"""
    quarter_months = {
        1: (1, 3),
        2: (4, 6),
        3: (7, 9),
        4: (10, 12)
    }
    
    start_month, end_month = quarter_months[quarter]
    start_date = datetime(year, start_month, 1)
    
    # 计算季度最后一天
    if end_month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, end_month + 1, 1) - timedelta(days=1)
    
    return start_date, end_date


def is_weekend(date: datetime) -> bool:
    """判断是否为周末（周六=5，周日=6）"""
    return date.weekday() >= 5


def get_date_key(date: datetime) -> str:
    """获取日期字符串键"""
    return date.strftime("%Y-%m-%d")


def calculate_workdays(year: int, quarter: int, holidays: dict = None) -> dict:
    """
    计算季度工作日
    
    返回：
        dict: 包含详细统计信息
    """
    if holidays is None:
        holidays = HOLIDAYS_2026
    
    start_date, end_date = get_quarter_dates(year, quarter)
    
    total_days = 0
    weekend_days = 0
    holiday_days = 0
    workday_makeup = 0
    actual_workdays = 0
    
    holiday_details = []
    makeup_details = []
    
    current = start_date
    while current <= end_date:
        total_days += 1
        date_key = get_date_key(current)
        
        # 检查是否在节假日字典中
        if date_key in holidays:
            info = holidays[date_key]
            if info["type"] == "holiday":
                holiday_days += 1
                holiday_details.append(f"  {date_key} {info['name']}")
            elif info["type"] == "workday":
                workday_makeup += 1
                makeup_details.append(f"  {date_key} {info['name']}")
                actual_workdays += 1
        elif is_weekend(current):
            weekend_days += 1
        else:
            actual_workdays += 1
        
        current += timedelta(days=1)
    
    return {
        "year": year,
        "quarter": quarter,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_days": total_days,
        "weekend_days": weekend_days,
        "holiday_days": holiday_days,
        "workday_makeup": workday_makeup,
        "actual_workdays": actual_workdays,
        "holiday_details": holiday_details,
        "makeup_details": makeup_details
    }


def print_results(result: dict):
    """打印计算结果"""
    quarter_names = {1: "一", 2: "二", 3: "三", 4: "四"}
    
    print(f"\n{'='*50}")
    print(f"{result['year']}年第{quarter_names[result['quarter']]}季度工作日计算")
    print(f"{'='*50}")
    print(f"📅 日期范围：{result['start_date']} 至 {result['end_date']}")
    print(f"📊 总天数：{result['total_days']}天")
    print(f"🌴 周末：{result['weekend_days']}天")
    print(f"🎉 节假日：{result['holiday_days']}天")
    print(f"💼 补班：{result['workday_makeup']}天")
    print(f"✅ 工作日：{result['actual_workdays']}天")
    
    if result['holiday_details']:
        print(f"\n节假日明细：")
        for detail in result['holiday_details']:
            print(detail)
    
    if result['makeup_details']:
        print(f"\n补班明细：")
        for detail in result['makeup_details']:
            print(detail)
    
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="计算季度工作日")
    parser.add_argument("--year", type=int, required=True, help="年份，如 2026")
    parser.add_argument("--quarter", type=int, required=True, choices=[1, 2, 3, 4], help="季度（1-4）")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出")
    
    args = parser.parse_args()
    
    result = calculate_workdays(args.year, args.quarter)
    
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_results(result)


if __name__ == "__main__":
    main()
