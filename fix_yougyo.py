import sqlite3
c = sqlite3.connect('/data/app.db')
c.execute("UPDATE aquariums SET lat=35.1098,lng=138.9033 WHERE name='幼魚水族館'")
c.commit()
print(c.total_changes, 'rows updated')
