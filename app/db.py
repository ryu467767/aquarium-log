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
    ]
    for sql in schema_migrations:
        try:
            con.execute(sql)
            con.commit()
        except _sqlite3.OperationalError:
            pass  # 既にカラムが存在する場合は無視

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
    con.close()

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _migrate()

def session() -> Session:
    return Session(engine)
