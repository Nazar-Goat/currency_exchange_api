
import os
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

API_PORT = 8000
FRONTEND_PORT = 3000
SERVER_IP = "your external IP"

def start_frontend_server(port):
    class FrontendHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  

    try:
        httpd = HTTPServer(('0.0.0.0', port), FrontendHandler)
        print(f" Фронтенд сервер запущен на http://{SERVER_IP}:{port}")
        httpd.serve_forever()
    except Exception as e:
        print(f" Ошибка запуска фронтенд сервера: {e}")

def main():
    print("Запуск Currency Exchange API с фронтендом...")
    print("=" * 50)

    required_files = ['frontend.html', 'myServer.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("Отсутствуют необходимые файлы:")
        for file in missing_files:
            print(f"  - {file}")
        return

    try:
        from database_setup import init_database
        init_database()
        print("База данных инициализирована")
    except ImportError:
        print("Модуль database_setup не найден — возможно, БД уже создана")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")

    def is_port_available(port):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return True
            except OSError:
                return False

    if not is_port_available(API_PORT):
        print(f" Порт {API_PORT} уже используется")
        return
    if not is_port_available(FRONTEND_PORT):
        print(f" Порт {FRONTEND_PORT} уже используется")
        return

    print(f"  Используемые порты:")
    print(f"  API сервер: {API_PORT}")
    print(f"  Фронтенд:   {FRONTEND_PORT}")

    # Запуск фронтенда в отдельном потоке
    threading.Thread(
        target=start_frontend_server,
        args=(FRONTEND_PORT,),
        daemon=True
    ).start()

    time.sleep(2)  

    print(f" Фронтенд: http://{SERVER_IP}:{FRONTEND_PORT}/frontend.html")
    print(f" API: http://{SERVER_IP}:{API_PORT}")
    print("\n Для остановки нажмите Ctrl+C")
    print("=" * 50)

    try:
        import myServer
        myServer.run()
    except ImportError as e:
        print(f"Не удалось импортировать myServer.py: {e}")
    except KeyboardInterrupt:
        print("\n Серверы остановлены")

if __name__ == '__main__':
    main()
