import time
import json
import pandas as pd
import requests

IN_CSV  = "aquariums_from_manboumuseum.csv"
OUT_CSV = "aquariums_with_latlng.csv"
CACHE_JSON = "geocode_cache.json"

# Nominatim(OSM) — 利用規約上、User-Agent必須 & 連続叩きすぎNG
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "aquarium-stamp-app/1.0 (local script)"
}

def load_cache():
    try:
        with open(CACHE_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    with open(CACHE_JSON, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def geocode(query: str):
    params = {"q": query, "format": "jsonv2", "limit": 1}
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])

def main():
    df = pd.read_csv(IN_CSV)

    # lat/lng列が無ければ追加
    if "lat" not in df.columns:
        df["lat"] = None
    if "lng" not in df.columns:
        df["lng"] = None

    cache = load_cache()

    updated = 0
    failed = 0

    for i, row in df.iterrows():
        if pd.notna(row["lat"]) and pd.notna(row["lng"]):
            continue

        # クエリは「都道府県 市区町村 施設名」を基本に
        q = f'{row["prefecture"]} {row["city"]} {row["name"]}'.strip()

        if q in cache:
            lat, lng = cache[q]
            df.at[i, "lat"] = lat
            df.at[i, "lng"] = lng
            continue

        try:
            res = geocode(q)
            if res is None:
                failed += 1
            else:
                lat, lng = res
                df.at[i, "lat"] = lat
                df.at[i, "lng"] = lng
                cache[q] = [lat, lng]
                updated += 1
        except Exception as e:
            print("ERROR:", q, e)
            failed += 1

        # レート制限対策（重要）：最低1秒は空ける
        time.sleep(1.1)

        # 途中経過をこまめに保存（中断しても再開できる）
        if (i + 1) % 10 == 0:
            save_cache(cache)
            df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
            print(f"progress: {i+1}/{len(df)} updated={updated} failed={failed}")

    save_cache(cache)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print("DONE", "updated=", updated, "failed=", failed)

if __name__ == "__main__":
    main()
