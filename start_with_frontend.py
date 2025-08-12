#!/usr/bin/env python3
# start_with_frontend.py

import os
import sys
import threading
import time
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

def is_port_available(port):
    """Проверяет, доступен ли порт"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except OSError:
            return False

def find_free_port(start_port=3000):
    """Находит свободный порт начиная с start_port"""
    port = start_port
    while port < 65535:
        if is_port_available(port):
            return port
        port += 1
    raise Exception("Не удалось найти свободный порт")

def start_frontend_server(port):
    """Запускает простой HTTP сервер для фронтенда"""
    class FrontendHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Подавляем логи фронтенд сервера для чистоты вывода
            pass
    
    try:
        httpd = HTTPServer(('', port), FrontendHandler)
        print(f"🌐 Фронтенд сервер запущен на http://localhost:{port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"❌ Ошибка запуска фронтенд сервера: {e}")

def main():
    """Главная функция"""
    print("🚀 Запуск Currency Exchange API с фронтендом...")
    print("=" * 50)
    
    # Проверяем существование файлов
    required_files = ['frontend.html', 'myServer.py']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Отсутствуют необходимые файлы:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nПожалуйста, убедитесь что файлы находятся в текущей директории.")
        return
    
    # Инициализация базы данных
    try:
        from database_setup import init_database
        init_database()
        print("✅ База данных инициализирована")
    except ImportError:
        print("⚠️  Модуль database_setup не найден - возможно БД уже инициализирована")
    except Exception as e:
        print(f"⚠️  Ошибка инициализации БД: {e}")
    
    # Проверяем доступность портов
    api_port = 8000
    frontend_port = find_free_port(3000)
    
    if not is_port_available(api_port):
        print(f"❌ Порт {api_port} уже используется. Остановите другие сервисы или измените порт.")
        return
    
    print(f"🔧 Используемые порты:")
    print(f"  API сервер: {api_port}")
    print(f"  Фронтенд:   {frontend_port}")
    
    # Запускаем фронтенд сервер в отдельном потоке
    frontend_thread = threading.Thread(
        target=start_frontend_server, 
        args=(frontend_port,), 
        daemon=True
    )
    frontend_thread.start()
    
    # Небольшая задержка для запуска фронтенда
    time.sleep(2)
    
    # Автоматически открываем браузер
    try:
        webbrowser.open(f'http://localhost:{frontend_port}/frontend.html')
        print(f"🌐 Браузер открыт на http://localhost:{frontend_port}/frontend.html")
    except Exception as e:
        print(f"⚠️  Не удалось автоматически открыть браузер: {e}")
        print(f"Откройте браузер и перейдите на http://localhost:{frontend_port}/frontend.html")
    
    print("\n" + "=" * 50)
    print("📋 Полезные ссылки:")
    print(f"🌐 Фронтенд: http://localhost:{frontend_port}/frontend.html")
    print(f"🔧 API:      http://localhost:{api_port}")
    print(f"📊 Валюты:   http://localhost:{api_port}/currencies")
    print(f"💱 Курсы:    http://localhost:{api_port}/exchangeRates")
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем API сервер в основном потоке
    try:
        # Импортируем и запускаем ваш основной сервер
        import myServer
        
        # Если нужно изменить порт, делаем это здесь
        if api_port != 8000:
            print(f"⚠️  Изменение порта API с 8000 на {api_port}")
            # Можно модифицировать код сервера для использования другого порта
        
        # Запускаем сервер
        myServer.run()
    except ImportError as e:
        print(f"❌ Не удалось импортировать myServer.py: {e}")
        print("Убедитесь что файл существует и все зависимости установлены")
    except KeyboardInterrupt:
        print("\n👋 Серверы остановлены")

if __name__ == '__main__':
    main()