#!/usr/bin/env python
import os
import json
import secrets
from pathlib import Path


def setup_project():
    """безопасная настройка проекта"""
    BASE_DIR = Path(__file__).resolve().parent

    # Создаем конфигурационный файл
    config = {
        'SECRET_KEY': secrets.token_urlsafe(50),
        'DEBUG': False,
        'ALLOWED_HOSTS': ['localhost', '127.0.0.1'],
        'DATABASE_NAME': str(BASE_DIR / 'protected_database.db')
    }

    # Запрашиваем данные у пользователя
    print("Настройка безопасной конфигурации проекта")

    domain = input("Введите ваш домен (например: myapp.pythonanywhere.com): ").strip()
    if domain:
        config['ALLOWED_HOSTS'].append(domain)

    debug_input = input("Включить режим отладки? (y/N): ").strip().lower()
    config['DEBUG'] = debug_input == 'y'

    # Сохраняем конфигурацию
    config_path = BASE_DIR / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    # Устанавливаем правильные права доступа (для Unix-систем)
    if os.name != 'nt':  # Не Windows
        os.chmod(config_path, 0o600)  # Только владелец может читать/писать

    print("Конфигурационный файл создан!")
    print("Файл config.json добавлен в .gitignore")
    print("НЕ ДЕЛАЙТЕ КОММИТ config.json В GIT!")


if __name__ == '__main__':
    setup_project()