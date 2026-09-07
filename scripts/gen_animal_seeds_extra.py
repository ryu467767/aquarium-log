"""crawl_animals_extra.py の結果から app/animal_seeds_extra.py を生成する。

生成したファイルは db.py の _migrate() が読み込み、
起動時に本番DBの追加生き物フラグを更新する。

Usage:
  python scripts/gen_animal_seeds_extra.py
"""
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent
SRC = Path(__file__).parent / "animal_extra_result.json"
DST = ROOT / "app" / "animal_seeds_extra.py"

COLS = [
    "has_otter", "has_seaotter", "has_walrus", "has_turtle", "has_whaleshark",
    "has_ray", "has_sunfish", "has_gardeneel", "has_seahorse", "has_clownfish",
    "has_coral", "has_capybara", "has_salamander", "has_deepsea",
]

# --- 飼育館が少ない生き物は、キーワード検出だと誤りが多いので手で確定させる ---
#
# 公式サイトの過去記事やWikipediaの「かつて飼育していた」という記述を拾ってしまい、
# 実際にはもう会えない館が候補に挙がってしまうため。
# 下の生き物は、ここに書いた館だけを「いる」として扱い、他館の検出結果は捨てる。
#
# 2026-09-07 に調査した内容:
#   ラッコ       … 国内は鳥羽水族館の2頭のみ（2025/01にマリンワールド海の中道の個体が死亡）
#   ジンベエザメ … 海遊館・いおワールドかごしま水族館・沖縄美ら海水族館の3館のみ
#                  （のとじま水族館は2024年の能登半島地震で死亡し展示休止）
VERIFIED_ONLY = {
    "has_seaotter": {
        "鳥羽水族館",
    },
    "has_whaleshark": {
        "海遊館",
        "いおワールドかごしま水族館",
        "沖縄美ら海水族館",
    },
}

# 検出漏れが確認できたぶんの追加（上と同じ調査による）
VERIFIED_ADD = {
    "has_walrus": {"鳥羽水族館", "鴨川シーワールド"},
}


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))

    # --- 手で確定させた生き物の反映 ---
    for col, allowed in VERIFIED_ONLY.items():
        removed = []
        for name, flags in data.items():
            if flags.get(col) and name not in allowed:
                flags[col] = 0
                removed.append(name)
        for name in allowed:
            data.setdefault(name, {c: 0 for c in COLS})[col] = 1
        print(f"{col}: {len(allowed)}館に確定（誤検出 {len(removed)}件を除去）")
        for n in removed:
            print(f"    除去: {n}")

    for col, extra in VERIFIED_ADD.items():
        for name in extra:
            data.setdefault(name, {c: 0 for c in COLS})[col] = 1
        print(f"{col}: 検出漏れ {len(extra)}館を追加")

    # 1つもヒットしなかった館は書き出さない（全部0でUPDATEしても意味がないため）
    kept = {name: flags for name, flags in data.items() if any(flags.get(c) for c in COLS)}

    lines = [
        '"""公式サイトのクロールで判定した「追加の生き物フラグ」。',
        "",
        "scripts/crawl_animals_extra.py → scripts/gen_animal_seeds_extra.py で自動生成。",
        "手で編集せず、再生成するか db.py 側で上書きすること。",
        '"""',
        "",
        "EXTRA_ANIMAL_COLS = [",
    ]
    lines += [f'    "{c}",' for c in COLS]
    lines += ["]", "", "EXTRA_ANIMAL_SEEDS = {"]

    for name in sorted(kept):
        flags = kept[name]
        body = ", ".join(f'"{c}": {1 if flags.get(c) else 0}' for c in COLS)
        lines.append(f"    {json.dumps(name, ensure_ascii=False)}: {{{body}}},")

    lines += ["}", ""]

    DST.write_text("\n".join(lines), encoding="utf-8")
    print(f"生成: {DST}")
    print(f"  対象 {len(data)} 館中、フラグが付いたのは {len(kept)} 館")
    for c in COLS:
        n = sum(1 for f in kept.values() if f.get(c))
        print(f"  {c:18s}: {n} 館")


if __name__ == "__main__":
    main()
