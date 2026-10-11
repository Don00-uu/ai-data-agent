import csv
import random
from datetime import date, timedelta

random.seed(42)   # 固定随机种子，保证每次生成的数据都一样

products = [
    ("无线蓝牙耳机", "数码", 199),
    ("檀木按摩梳", "个护", 129),
    ("牛角梳", "个护", 89),
    ("智能台灯", "家居", 159),
    ("便携榨汁杯", "家居", 99),
    ("颈椎按摩仪", "健康", 299),
    ("香薰蜡烛", "家居", 69),
    ("保温杯", "家居", 79),
]

start = date(2026, 8, 1)
rows = []

for i in range(120):                      # 模拟 120 天的数据
    day = start + timedelta(days=i)
    for name, cat, price in products:
        if random.random() < 0.6:         # 不是每天每个商品都有单
            qty = random.randint(1, 12)   # 这天卖了多少件
            rows.append({
                "日期": day.isoformat(),
                "商品": name,
                "类目": cat,
                "单价": price,
                "销量": qty,
                "销售额": qty * price,
                "退货数": random.randint(0, max(0, qty // 5)),
            })

with open("orders.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["日期", "商品", "类目", "单价", "销量", "销售额", "退货数"])
    writer.writeheader()
    writer.writerows(rows)

print("已生成 orders.csv，共", len(rows), "条记录")