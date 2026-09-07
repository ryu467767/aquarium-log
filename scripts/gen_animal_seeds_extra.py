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


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))

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
