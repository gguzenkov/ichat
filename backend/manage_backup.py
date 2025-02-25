import sys
from pathlib import Path

# Добавляем путь к backend в PYTHONPATH
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from app.utils.manage_backup import cli

if __name__ == '__main__':
    cli() 