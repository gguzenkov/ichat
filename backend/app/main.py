from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .models import User, Message, PrivateMessage  # Импортируем модели через __init__.py
from .routers import auth, users, messages, private_messages
import os

# Создаем таблицы при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat API")

# Настраиваем CORS более детально
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
    expose_headers=["*"],  # Разрешаем доступ ко всем заголовкам в ответе
    max_age=3600,  # Время кэширования CORS-ответов
)

# Монтируем директорию uploads для доступа к файлам
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Монтируем директорию с аватарами
avatars_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "avatars")
os.makedirs(avatars_dir, exist_ok=True)
app.mount("/avatars", StaticFiles(directory=avatars_dir), name="avatars")

@app.middleware("http")
async def add_current_user_id(request: Request, call_next):
    # Получаем ID пользователя из заголовка
    current_user_id = request.headers.get('X-Current-User-Id')
    if current_user_id:
        request.state.current_user_id = int(current_user_id)
    
    response = await call_next(request)
    return response

# Подключаем роутеры
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(messages.router, prefix="/api", tags=["messages"])
app.include_router(private_messages.router, prefix="/api", tags=["private_messages"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Chat API"} 