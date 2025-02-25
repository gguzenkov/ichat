import click
from .backup import create_backup, restore_backup
import os

@click.group()
def cli():
    """Управление бэкапами базы данных"""
    pass

@cli.command()
def backup():
    """Создать новый бэкап"""
    backup_file = create_backup()
    if backup_file:
        click.echo(f"Бэкап успешно создан: {backup_file}")
    else:
        click.echo("Ошибка при создании бэкапа")

@cli.command()
@click.argument('backup_file', type=click.Path(exists=True))
def restore(backup_file):
    """Восстановить базу данных из бэкапа"""
    if restore_backup(backup_file):
        click.echo("База данных успешно восстановлена")
    else:
        click.echo("Ошибка при восстановлении базы данных")

@cli.command()
def list():
    """Показать список доступных бэкапов"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        click.echo("Папка с бэкапами не найдена")
        return
    
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.sql')])
    if not backups:
        click.echo("Бэкапы не найдены")
        return
    
    click.echo("Доступные бэкапы:")
    for backup in backups:
        size = os.path.getsize(os.path.join(backup_dir, backup)) / 1024 / 1024  # размер в МБ
        click.echo(f"- {backup} ({size:.2f} MB)")

if __name__ == '__main__':
    cli() 