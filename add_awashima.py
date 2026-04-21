import sqlite3
c = sqlite3.connect('/data/app.db')
c.execute("""
INSERT INTO aquariums (name,prefecture,city,url,mola_star,lat,lng,has_dolphin,has_sealion,twitter_id,instagram_id,is_closed)
VALUES ('あわしまマリンパーク','静岡県','沼津市','https://www.marinepark.jp/',0,35.033468,138.890185,1,1,'A_shimatarou','awashima_marinepark',0)
""")
c.commit()
print(c.total_changes, 'rows inserted')
