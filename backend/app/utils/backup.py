import os
import subprocess
from datetime import datetime
from pathlib import Path
from ..config import settings

def create_backup():
    # Получаем абсолютный путь к корневой директории проекта
    project_root = Path(__file__).parent.parent.parent
    backup_dir = project_root / "backups"
    
    # Создаем директорию для бэкапов если её нет
    backup_dir.mkdir(exist_ok=True)
    
    # Формируем имя файла с текущей датой
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'chatdb_backup_{timestamp}.sql'
    
    # Формируем команду для pg_dump
    command = [
        'pg_dump',
        '-h', settings.DATABASE_HOSTNAME,
        '-p', settings.DATABASE_PORT,
        '-U', settings.DATABASE_USERNAME,
        '-d', settings.DATABASE_NAME,
        '-F', 'p',  # Формат plain text
        '-f', str(backup_file)
    ]
    
    try:
        # Устанавливаем пароль через переменную окружения
        env = os.environ.copy()
        env['PGPASSWORD'] = settings.DATABASE_PASSWORD
        
        # Выполняем команду
        result = subprocess.run(
            command,
            env=env,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stderr:
            print(f"Warning during backup: {result.stderr}")
            
        print(f"Backup created successfully: {backup_file}")
        return str(backup_file)
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def restore_backup(backup_file):
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    # Формируем команду для восстановления
    command = [
        'psql',
        '-h', settings.DATABASE_HOSTNAME,
        '-p', settings.DATABASE_PORT,
        '-U', settings.DATABASE_USERNAME,
        '-d', settings.DATABASE_NAME,
        '-f', backup_file
    ]
    
    try:
        # Устанавливаем пароль через переменную окружения
        env = os.environ.copy()
        env['PGPASSWORD'] = settings.DATABASE_PASSWORD
        
        # Выполняем команду
        result = subprocess.run(
            command,
            env=env,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stderr:
            print(f"Warning during restore: {result.stderr}")
            
        print(f"Backup restored successfully from: {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error restoring backup: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    backup_file = create_backup()
    if backup_file:
        print(f"Backup created: {backup_file}")