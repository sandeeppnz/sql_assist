from db import engine

print("Connecting to DB...")
conn = engine.connect()
print("Connected:", conn)
conn.close()
