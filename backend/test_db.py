
from app.db.session import engine

try:
    with engine.connect() as connection:
        print("MySQL Database Connected Successfully!")
except Exception as e:
    print("Database Connection Failed!")
    print(e)


from app.db.base import Base
import app.models

print("Total Models:", len(Base.metadata.tables))

for table_name in Base.metadata.tables:
    print(table_name)
