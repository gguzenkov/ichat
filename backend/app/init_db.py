from database import engine, Base
from models.user import User
from models.message import Message

def init_db():
    print("Удаление существующих таблиц...")
    Base.metadata.drop_all(bind=engine)
    print("Создание новых таблиц...")
    Base.metadata.create_all(bind=engine)
    print("База данных успешно инициализирована")

if __name__ == "__main__":
    init_db() 