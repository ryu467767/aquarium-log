import os
import sqlite3 as _sqlite3
from sqlmodel import SQLModel, create_engine, Session

def get_db_path() -> str:
    # Renderでは永続ディスクを /data にマウントする（render.yaml参照）
    base = os.getenv("DB_DIR", "/data")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "app.db")

DATABASE_URL = f"sqlite:///{get_db_path()}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

def _migrate():
    """既存テーブルに新しいカラムを追加 + 生き物データを seed するマイグレーション。"""
    con = _sqlite3.connect(get_db_path())

    # --- カラム追加（既存カラムは無視） ---
    schema_migrations = [
        "ALTER TABLE visits ADD COLUMN visit_count INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE visits ADD COLUMN want_to_go INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_penguin INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_dolphin INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_sealion INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_orca INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_jellyfish INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN is_closed INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN closed_at TEXT",
        "ALTER TABLE aquariums ADD COLUMN has_steller INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_seal INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_shark INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_beluga INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE visits ADD COLUMN visit_years TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE visits ADD COLUMN visit_dates TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE user_profiles ADD COLUMN login_count INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE user_profiles ADD COLUMN last_seen_at DATETIME",
        "ALTER TABLE aquariums ADD COLUMN twitter_id TEXT",
        "ALTER TABLE aquariums ADD COLUMN instagram_id TEXT",
        # 詳細ページの「会える生き物」用の追加フラグ
        "ALTER TABLE aquariums ADD COLUMN has_otter INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_seaotter INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_walrus INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_turtle INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_whaleshark INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_ray INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_sunfish INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_gardeneel INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_seahorse INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_clownfish INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_coral INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_capybara INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_salamander INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_deepsea INTEGER NOT NULL DEFAULT 0",
        # 休館中のお知らせ（空なら通常営業）
        "ALTER TABLE aquariums ADD COLUMN suspended_note TEXT",
    ]
    for sql in schema_migrations:
        try:
            con.execute(sql)
            con.commit()
        except _sqlite3.OperationalError:
            pass  # 既にカラムが存在する場合は無視

    # --- 新しく収録する水族館（同じ名前が無いときだけ追加。何度起動しても重複しない）---
    # 生き物フラグは全部0で入れる（必要なら下の seed で上書きされる）。
    # 列を省略すると、作り方によっては NOT NULL で失敗するので全部明示する。
    _flag_cols = [
        "has_penguin", "has_dolphin", "has_sealion", "has_orca", "has_jellyfish",
        "has_steller", "has_seal", "has_shark", "has_beluga",
        "has_otter", "has_seaotter", "has_walrus", "has_turtle", "has_whaleshark",
        "has_ray", "has_sunfish", "has_gardeneel", "has_seahorse", "has_clownfish",
        "has_coral", "has_capybara", "has_salamander", "has_deepsea",
    ]
    new_aquariums = [
        # 2026/11 利用者の要望で追加。廃校（旧深江小学校）を活用した江田島市の施設。
        # 正式名称は大柿自然環境体験学習交流館。位置は正門前（深江バス停の正面）。
        {
            "name": "さとうみ科学館", "prefecture": "広島県", "city": "江田島市",
            "location_raw": "", "url": "https://www.urban.ne.jp/home/fukaesho/SSM/entrance.html",
            "mola_star": 0, "lat": 34.1696253, "lng": 132.4518189,
            "twitter_id": None, "instagram_id": "satoumikagakukan", "is_closed": 0,
        },
        # ---- 2026/11 新しく開館した館（緯度経度はすべて Yahoo!マップの施設ページ）----
        # 旧マリホ水族館の後継。2025/12/2 アルパーク内に開館。クラゲは公式フロアマップで確認
        {
            "name": "シン・マリホ水族館", "prefecture": "広島県", "city": "広島市西区",
            "location_raw": "", "url": "https://shin.mariho-aquarium.com/",
            "mola_star": 0, "lat": 34.3735754, "lng": 132.3945900,
            "twitter_id": "Shin_MAQ", "instagram_id": "shin_mariho_aquarium", "is_closed": 0,
            "has_jellyfish": 1,
        },
        # 2026/5/1 開館。県立大学の学生が運営する町家の水族館
        {
            "name": "おばま水族館", "prefecture": "福井県", "city": "小浜市",
            "location_raw": "", "url": "https://obama-aquarium.com/",
            "mola_star": 0, "lat": 35.4918232, "lng": 135.7340787,
            "twitter_id": None, "instagram_id": None, "is_closed": 0,
        },
        # 2025/9/12 開館。平良西里の西里通り商店街。公式ページは運営会社（兵庫ベンダ工業）のサイト
        {
            "name": "KAIKENのチイサナ水族館", "prefecture": "沖縄県", "city": "宮古島市",
            "location_raw": "", "url": "https://kaiken.bender.jp/",
            "mola_star": 0, "lat": 24.8042854, "lng": 125.2810017,
            "twitter_id": None, "instagram_id": "kaiken_hyogobender", "is_closed": 0,
        },
        # ---- 2026/11 閉館した館（思い出の記録用。今ある閉館館と同じく公式URL・生き物フラグは無し）----
        # 2024/12/1 閉館（借地権終了）。マリーナホップ内
        {
            "name": "マリホ水族館", "prefecture": "広島県", "city": "広島市西区",
            "location_raw": "", "url": "", "mola_star": 0, "lat": 34.3596465, "lng": 132.4164197,
            "twitter_id": None, "instagram_id": None, "is_closed": 1, "closed_at": "2024-12",
        },
        # 2023/3 末で閉館（茨城新聞）。位置はWikipedia（山方535）
        {
            "name": "山方淡水魚館", "prefecture": "茨城県", "city": "常陸大宮市",
            "location_raw": "", "url": "", "mola_star": 0, "lat": 36.625666, "lng": 140.404046,
            "twitter_id": None, "instagram_id": None, "is_closed": 1, "closed_at": "2023-03",
        },
        # 2010/12/15 閉館（読売新聞）。位置は同じ敷地のホテル建物
        {
            "name": "天草いるかワールド", "prefecture": "熊本県", "city": "天草市",
            "location_raw": "", "url": "", "mola_star": 0, "lat": 32.472886, "lng": 130.2069889,
            "twitter_id": None, "instagram_id": None, "is_closed": 1, "closed_at": "2010-12",
        },
        # 2010/3 末で閉館。つつじが岡公園内（建物は今はカフェ）
        {
            "name": "群馬県立水産学習館", "prefecture": "群馬県", "city": "館林市",
            "location_raw": "", "url": "", "mola_star": 0, "lat": 36.241843, "lng": 139.551448,
            "twitter_id": None, "instagram_id": None, "is_closed": 1, "closed_at": "2010-03",
        },
        # 2005/11/3 閉館。シーサイドパーク広尾内（位置は公園。建物の正確な場所は未確認）
        {
            "name": "ひろお水族館", "prefecture": "北海道", "city": "広尾郡広尾町",
            "location_raw": "", "url": "", "mola_star": 0, "lat": 42.315929, "lng": 143.3272947,
            "twitter_id": None, "instagram_id": None, "is_closed": 1, "closed_at": "2005-11",
        },
        # 2005/10/31 閉館。旧海部町奥浦（位置は隣の番地のピアカイフ。おおよそ）
        {
            "name": "大うなぎ水族館イーランド", "prefecture": "徳島県", "city": "海部郡海陽町",
            "location_raw": "", "url": "", "mola_star": 0, "lat": 33.595107, "lng": 134.353276,
            "twitter_id": None, "instagram_id": None, "is_closed": 1, "closed_at": "2005-10",
        },
        # 2016/8/31 閉館（産経新聞）。阪急三番街北館1階の「通路水族館」
        {
            "name": "かわいい水族館", "prefecture": "大阪府", "city": "大阪市北区",
            "location_raw": "", "url": "", "mola_star": 0, "lat": 34.70596755, "lng": 135.49818433,
            "twitter_id": None, "instagram_id": None, "is_closed": 1, "closed_at": "2016-08",
        },
    ]
    for aq in new_aquariums:
        row = {**{c: 0 for c in _flag_cols}, **aq}
        try:
            if con.execute("SELECT 1 FROM aquariums WHERE name=?", (row["name"],)).fetchone():
                continue
            cols = ", ".join(row.keys())
            marks = ", ".join("?" for _ in row)
            con.execute(f"INSERT INTO aquariums ({cols}) VALUES ({marks})", list(row.values()))
            con.commit()
            print(f"[migrate] 水族館を追加しました: {row['name']}")
        except _sqlite3.Error as e:
            print(f"[migrate] 水族館の追加に失敗しました: {row['name']} ({e})")

    # --- 既存の館のデータ修正（休館・閉館・所在地）。何度起動しても同じ結果になる UPDATE だけ ---
    # 休館をやめて通常営業に戻ったら suspended_note を NULL に戻す行をここに足す。
    data_fixes = [
        # 2025/4/7から建て替えで休館（KSB・公式サイト）。屋島山上の同じ場所に建て直し
        ("UPDATE aquariums SET suspended_note=? WHERE name=?",
         ("2025年4月から建て替えのため休館中（2027年春に再開予定）", "新屋島水族館")),
        # 2026/4/21 公式発表：8月から2027年3月末まで改修工事で長期休館
        ("UPDATE aquariums SET suspended_note=? WHERE name=?",
         ("2026年8月から改修工事のため休館中（2027年4月に再開予定）", "小笠原海洋センター")),
        # 東京都の公式ページ：改修工事のため現在閉館、令和9年4月に開館予定
        ("UPDATE aquariums SET suspended_note=? WHERE name=?",
         ("改修工事のため休館中（2027年4月に再開予定）", "小笠原水産センター 小さな水族館")),
        # 2022/10/1から休館 → 干拓の里の通常営業終了（2026/3/29）に合わせて閉館。運営会社も解散しサイト消滅
        ("UPDATE aquariums SET is_closed=1, closed_at=?, url='', suspended_note=NULL WHERE name=?",
         ("2026-03", "諫早ゆうゆうランド 干拓の里 むつごろう水族館")),
        # 所在地は豊川市市田町（豊川市の公式ページ）。豊橋市は誤り
        ("UPDATE aquariums SET city=? WHERE name=?",
         ("豊川市", "赤塚山公園 淡水魚水族館 ぎょぎょランド")),
        # 小笠原は「村」（小笠原町は存在しない）
        ("UPDATE aquariums SET city=? WHERE prefecture='東京都' AND city=? AND name=?",
         ("小笠原村", "小笠原町", "小笠原海洋センター")),
        ("UPDATE aquariums SET city=? WHERE prefecture='東京都' AND city=? AND name=?",
         ("小笠原村", "小笠原町", "小笠原水産センター 小さな水族館")),
    ]
    for sql, params in data_fixes:
        try:
            con.execute(sql, params)
            con.commit()
        except _sqlite3.Error as e:
            print(f"[migrate] データ修正に失敗しました: {params[-1]} ({e})")

    # --- 生き物フラグ seed（公式サイトクロール結果）---
    animal_seeds = [
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='サンピアザ水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='AOAO SAPPORO'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=1, has_seal=1, has_shark=0, has_beluga=0 WHERE name='おたる水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=1, has_beluga=0 WHERE name='登別マリンパークニクス'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='くしろ水族館　ぷくぷく'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='氷海展望塔オホーツクタワー'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='わっかりうむ ノシャップ寒流水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='旭川市 旭山動物園'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='青森県営浅虫水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='男鹿水族館GAO'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='仙台うみの杜水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='鶴岡市立加茂水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='アクアマリンふくしま'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='アクアワールド 茨城県大洗水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=1, has_orca=1, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=1 WHERE name='鴨川シーワールド'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='しながわ水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='マクセル アクアパーク品川'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='すみだ水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='葛西臨海水族園'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='サンシャイン水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='横浜・八景島シーパラダイス'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='新江ノ島水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='北里大学アクアリウムラボ'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='箱根園水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='よみうりランド'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='新潟市水族館 マリンピア日本海'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='上越市立水族博物館 うみがたり'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='魚津水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='のとじま水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='くにみクラゲ公民館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=1, has_beluga=0 WHERE name='越前松島水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='福井県海浜自然センター'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=1, has_seal=1, has_shark=0, has_beluga=0 WHERE name='伊豆・三津シーパラダイス'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='下田海中水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='ドルフィンファンタジー伊東'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='幼魚水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=1 WHERE name='名古屋港水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='南知多ビーチランド'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=1, has_seal=1, has_shark=0, has_beluga=0 WHERE name='伊勢夫婦岩ふれあい水族館 シーパラダイス'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=1, has_beluga=0 WHERE name='京都水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=1, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='神戸須磨シーワールド'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='átoa（アトア）'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=1, has_seal=1, has_shark=0, has_beluga=0 WHERE name='城崎マリンワールド'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=1, has_seal=0, has_shark=0, has_beluga=0 WHERE name='淡路じゃのひれアウトドアリゾート'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='アドベンチャーワールド'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='串本海中公園'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='すさみ町立エビとカニの水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='太地町立くじらの博物館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='ドルフィンベェイス'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='とっとり賀露かにっこ館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=1, has_beluga=1 WHERE name='島根県立しまね海洋館 アクアス'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=1, has_shark=1, has_beluga=0 WHERE name='渋川マリン水族館（玉野海洋水族館）'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='市立しものせき水族館「海響館」'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='虹の森公園 おさかな館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='ドルフィンファームしまなみ'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='高知県立足摺海洋館SATOUMI'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='マリンワールド海の中道'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='佐賀県立宇宙科学館 ゆめぎんが'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=1, has_seal=1, has_shark=0, has_beluga=0 WHERE name='大分マリーンパレス水族館「うみたまご」'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=1, has_seal=0, has_shark=0, has_beluga=0 WHERE name='つくみイルカ島'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=1, has_seal=0, has_shark=0, has_beluga=0 WHERE name='出の山淡水魚水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='志布志湾大黒イルカランド'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='海中水族館シードーナツ'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='長崎ペンギン水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='九十九島水族館「海きらら」'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='壱岐イルカパーク'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='奄美海洋展示館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='沖縄美ら海水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='DMMかりゆし水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='延岡マリンサービス'",
        # --- 追加修正（Web検索で確認） ---
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=0, has_beluga=0 WHERE name='鳥羽水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=1, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=1, has_shark=1, has_beluga=0 WHERE name='海遊館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='四国水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='ニフレル'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=1, has_orca=0, has_jellyfish=0, has_steller=1, has_seal=1, has_shark=0, has_beluga=0 WHERE name='みやじマリン 宮島水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=0, has_sealion=1, has_orca=0, has_jellyfish=1, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='竹島水族館'",
        "UPDATE aquariums SET has_penguin=1, has_dolphin=0, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=0, has_beluga=0 WHERE name='姫路市立水族館'",
        "UPDATE aquariums SET has_penguin=0, has_dolphin=1, has_sealion=0, has_orca=0, has_jellyfish=0, has_steller=0, has_seal=0, has_shark=1, has_beluga=0 WHERE name='いおワールドかごしま水族館'",
    ]
    for sql in animal_seeds:
        try:
            con.execute(sql)
        except _sqlite3.OperationalError:
            pass
    con.commit()

    # --- 公式サイトURLの修正（誤リンクの上書き）---
    url_fixes = [
        # 波左間海中公園のURLが誤ってコピーされていた
        "UPDATE aquariums SET url='https://ioworld.jp/' WHERE name='いおワールドかごしま水族館'",
    ]
    for sql in url_fixes:
        try:
            con.execute(sql)
        except _sqlite3.OperationalError:
            pass
    con.commit()

    # --- 追加の生き物フラグ seed（公式サイトのクロール結果）---
    # データは app/animal_seeds_extra.py（scripts/crawl_animals_extra.py で生成）
    try:
        from .animal_seeds_extra import EXTRA_ANIMAL_SEEDS, EXTRA_ANIMAL_COLS
    except Exception:
        EXTRA_ANIMAL_SEEDS, EXTRA_ANIMAL_COLS = {}, []

    if EXTRA_ANIMAL_SEEDS and EXTRA_ANIMAL_COLS:
        set_clause = ", ".join(f"{c}=?" for c in EXTRA_ANIMAL_COLS)
        sql = f"UPDATE aquariums SET {set_clause} WHERE name=?"
        for name, flags in EXTRA_ANIMAL_SEEDS.items():
            try:
                con.execute(sql, [flags.get(c, 0) for c in EXTRA_ANIMAL_COLS] + [name])
            except _sqlite3.OperationalError:
                pass
        con.commit()

    con.close()

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _migrate()

def session() -> Session:
    return Session(engine)
