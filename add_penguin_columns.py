import pandas as pd

file_path = "aquariums_list.csv"

df = pd.read_csv(file_path, encoding="utf-8-sig")

new_cols = [
    "has_penguin",
    "penguin_source_url",
    "penguin_checked_at",
    "penguin_status",
]

for col in new_cols:
    if col not in df.columns:
        df[col] = ""

# ★ここが重要
df.to_csv(file_path, index=False, encoding="utf-8-sig")

print("列を追加して上書き保存しました！")