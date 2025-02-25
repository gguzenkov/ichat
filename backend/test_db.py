from sqlalchemy import create_engine

DATABASE_URL = "postgresql://chatdb:chatdb@localhost/chatdb"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Успешное подключение к базе данных!")
except Exception as e:
    print(f"Ошибка подключения: {e}") 