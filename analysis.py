import pandas as pd

df = pd.read_csv("orders.csv")   # 把 CSV 读成一张表格
print(df.head())                 # 看前 5 行
print(df.shape)                  # 看有多少行、多少列


# 1) 筛选：只要 9 月的数据
sep = df[(df["日期"] >= "2026-09-01") & (df["日期"] <= "2026-09-30")]

# 2) 分组求和：按商品分组，各自把销售额加起来
by_product = sep.groupby("商品")["销售额"].sum()

# 3) 排序：从大到小
ranked = by_product.sort_values(ascending=False)

# 4) 取前 3 名
print(ranked.head(3))


def total_sales(start, end):
    part = df[(df["日期"] >= start) & (df["日期"] <= end)]
    total = part["销售额"].sum()
    return total
print(total_sales("2026-09-01", "2026-09-30"))

def top_products(start, end, n=3):
    part = df[(df["日期"] >= start) & (df["日期"] <= end)]       # 筛选
    by_product = part.groupby("商品")["销售额"].sum()         # 分组求和
    ranked = by_product.sort_values(ascending=False)       # 排序，从大到小
    return  ranked.head(n)                   # 取前 n 个交出去
print(top_products("2026-09-01", "2026-09-30"))


def slow_moving(start, end, n=3):
    part = df[(df["日期"] >= start) & (df["日期"] <= end)]
    by_product = part.groupby("商品")["销售额"].sum()
    ranked = by_product.sort_values(ascending=True)
    return ranked.head(n)

print(slow_moving("2026-09-01", "2026-09-30"))