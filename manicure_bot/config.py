import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()


class Settings:
    bot_token: str = os.getenv('BOT_TOKEN')
    master_user_id: int = int(os.getenv('MASTER_USER_ID'))
    master_chat_id: int = int(os.getenv('MASTER_CHAT_ID'))
    database_url: str = os.getenv('DATABASE_URL')


settings = Settings()