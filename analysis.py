#!/usr/bin/env python3
"""
Canada28 / PC28 开奖数据分析工具
从 api.3658kj.com 获取实时数据并做趋势统计
"""

import json
import sys
import time
import csv
from datetime import datetime
from urllib.request import urlopen, Request

API_BASE = "https://api.3658kj.com"

LOTTERIES = {
    10029: "加拿大PC28",
    10039: "加拿大西PC28",
    10027: "台湾宾果PC28",
    10049: "比特币3分PC28",
}


def fetch_json(url):
    """请求 API 并返回 JSON"""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_history(lot_code, count=50):
    """获取历史开奖数据"""
    url = f"{API_BASE}/api/v1/trend/getHistoryList?lotCode={lot_code}&pageSize={count}&pageNum=0&t={int(time.time()*1000)}"
    data = fetch_json(url)
    items = data.get("data", {}).get("list", [])
    results = []
    for item in items:
        code = item.get("drawCode", "0,0,0")
        parts = code.split(",")
        n1, n2, n3 = int(parts[0]), int(parts[1]), int(parts[2])
        total = n1 + n2 + n3
        results.append({
            "period": item.get("drawIssue", ""),
            "time": item.get("drawTime", ""),
            "n1": n1, "n2": n2, "n3": n3,
            "sum": total,
            "big_small": "大" if total >= 14 else "小",
            "odd_even": "单" if total % 2 != 0 else "双",
        })
    return results


def trend_analysis(results):
    """趋势统计分析"""
    if not results:
        return

    big = sum(1 for r in results if r["sum"] >= 14)
    small = len(results) - big
    odd = sum(1 for r in results if r["sum"] % 2 != 0)
    even = len(results) - odd

    # 和值频率
    sum_freq = {}
    for r in results:
        s = r["sum"]
        sum_freq[s] = sum_freq.get(s, 0) + 1

    # 波色统计
    red_wave = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24]
    green_wave = [0, 5, 6, 11, 16, 17, 21, 22, 27]
    red = sum(1 for r in results if r["sum"] in red_wave)
    green = sum(1 for r in results if r["sum"] in green_wave)
    blue = len(results) - red - green

    print(f"\n📊 近 {len(results)} 期趋势分析")
    print(f"{'='*40}")
    print(f"  大: {big} 次 ({big/len(results)*100:.1f}%)")
    print(f"  小: {small} 次 ({small/len(results)*100:.1f}%)")
    print(f"  单: {odd} 次 ({odd/len(results)*100:.1f}%)")
    print(f"  双: {even} 次 ({even/len(results)*100:.1f}%)")
    print(f"  红波: {red} 次 ({red/len(results)*100:.1f}%)")
    print(f"  绿波: {green} 次 ({green/len(results)*100:.1f}%)")
    print(f"  蓝波: {blue} 次 ({blue/len(results)*100:.1f}%)")
    print(f"\n🔥 热门和值 TOP5:")
    for s, cnt in sorted(sum_freq.items(), key=lambda x: -x[1])[:5]:
        bar = "█" * cnt
        print(f"  {s:02d}: {cnt}次 {bar}")


def predict(results):
    \"\"\"基于历史数据生成简单预测\"\"\"
    if not results or len(results) < 10:
        print("数据不足，无法预测")
        return

    # 统计最近趋势
    recent = results[:20]
    big_ratio = sum(1 for r in recent if r["sum"] >= 14) / len(recent)
    odd_ratio = sum(1 for r in recent if r["sum"] % 2 != 0) / len(recent)

    # 热号和冷号和值
    sum_freq = {}
    for r in results:
        sum_freq[r["sum"]] = sum_freq.get(r["sum"], 0) + 1

    hot_sums = sorted(sum_freq.items(), key=lambda x: -x[1])[:3]
    cold_sums = sorted(sum_freq.items(), key=lambda x: x[1])[:3]

    # 连续出现模式
    last_5 = results[:5]
    streak_big = sum(1 for r in last_5 if r["sum"] >= 14)
    streak_small = sum(1 for r in last_5 if r["sum"] < 14)

    print(f"\n🔮 预测分析（基于近 {len(results)} 期数据）")
    print(f"{'='*40}")
    print(f"  大小趋势: 大 {big_ratio*100:.0f}% / 小 {(1-big_ratio)*100:.0f}%")
    print(f"  单双趋势: 单 {odd_ratio*100:.0f}% / 双 {(1-odd_ratio)*100:.0f}%")
    if streak_big >= 4:
        print(f"  ⚠️ 连开 {streak_big} 期大，注意回调风险")
    elif streak_small >= 4:
        print(f"  ⚠️ 连开 {streak_small} 期小，注意回调风险")
    print(f"\n  🔥 热门和值: {', '.join(f'{s:02d}({c}次)' for s, c in hot_sums)}")
    print(f"  ❄️ 冷门和值: {', '.join(f'{s:02d}({c}次)' for s, c in cold_sums)}")
    print(f"\n  💡 建议关注: ", end="")
    suggestions = []
    if big_ratio > 0.6:
        suggestions.append("小")
    elif big_ratio < 0.4:
        suggestions.append("大")
    if odd_ratio > 0.6:
        suggestions.append("双")
    elif odd_ratio < 0.4:
        suggestions.append("单")
    if suggestions:
        print(f"偏向 {'、'.join(suggestions)}")
    else:
        print("走势均衡，观望为主")


def export_csv(results, filename):
    """导出为 CSV"""
    if not results:
        print("没有数据可导出")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "time", "n1", "n2", "n3", "sum", "big_small", "odd_even"])
        writer.writeheader()
        writer.writerows(results)
    print(f"✅ 已导出 {len(results)} 条数据到 {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Canada28 数据分析工具")
    parser.add_argument("--lottery", type=int, default=10029, help="彩票代码 (默认 10029 加拿大28)")
    parser.add_argument("--count", type=int, default=50, help="获取期数 (默认 50)")
    parser.add_argument("--trend", action="store_true", help="显示趋势分析")
    parser.add_argument("--predict", action="store_true", help="生成预测建议")
    parser.add_argument("--export", type=str, help="导出 CSV 文件名")

    args = parser.parse_args()

    name = LOTTERIES.get(args.lottery, f"未知彩种({args.lottery})")
    print(f"🎰 {name} - 正在获取最近 {args.count} 期数据...")

    results = get_history(args.lottery, args.count)

    if not results:
        print("❌ 获取数据失败")
        sys.exit(1)

    print(f"✅ 成功获取 {len(results)} 条记录")
    print(f"\n{'─'*60}")
    print(f"{'期号':<14} {'时间':<20} {'号码':<10} {'和值':<6} {'结果':<8}")
    print(f"{'─'*60}")

    for r in results[:10]:
        nums = f"{r['n1']} {r['n2']} {r['n3']}"
        print(f"{r['period'][-8:]:<14} {r['time'][:19]:<20} {nums:<10} {r['sum']:02d}    {r['big_small']}{r['odd_even']}")

    if len(results) > 10:
        print(f"  ... 还有 {len(results)-10} 期")

    if args.trend:
        trend_analysis(results)

    if args.predict:
        predict(results)

    if args.export:
        export_csv(results, args.export)
