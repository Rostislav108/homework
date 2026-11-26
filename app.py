"""Простое веб-приложение: любой GET-запрос возвращает страницу «Контакты».

Запуск:
    python app.py

Сервер слушает http://localhost:8000. На GET отдаётся contacts.html
(Content-Type: text/html; charset=utf-8), на POST — данные формы печатаются
в консоль, после чего пользователю возвращается та же страница.
"""

import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST = "localhost"
PORT = 8000

# чтобы русский текст в консоли не превращался в «кракозябры»
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONTACTS_PAGE = os.path.join(BASE_DIR, "contacts.html")
NOT_FOUND_PAGE = os.path.join(BASE_DIR, "404.html")
ERROR_PAGE = os.path.join(BASE_DIR, "500.html")


def read_page(path: str) -> bytes:
    """Читает HTML-файл с диска.

    Args:
        path: путь к HTML-файлу.

    Returns:
        Содержимое файла в байтах.
    """
    with open(path, "rb") as file:
        return file.read()


class ShopRequestHandler(BaseHTTPRequestHandler):
    """Обработчик запросов к учебному приложению."""

    def _send_page(self, path: str, status: int = 200) -> None:
        """Отправляет HTML-страницу клиенту.

        Args:
            path: путь к HTML-файлу.
            status: HTTP-код ответа.
        """
        try:
            content = read_page(path)
        except OSError:
            content = read_page(ERROR_PAGE)
            status = 500

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:  # noqa: N802 (имя задано стандартом http.server)
        """На любой GET-запрос возвращает страницу «Контакты»."""
        self._send_page(CONTACTS_PAGE)

    def do_POST(self) -> None:  # noqa: N802
        """Принимает POST, печатает данные формы и отдаёт страницу «Контакты»."""
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
        form_data = parse_qs(raw_body)

        print("=== Получен POST-запрос ===", flush=True)
        print("Путь:", self.path, flush=True)
        print("Данные формы:", form_data, flush=True)
        for field, values in form_data.items():
            print(f"  {field}: {', '.join(values)}", flush=True)
        print("===========================", flush=True)

        self._send_page(CONTACTS_PAGE)

    def _send_not_found(self) -> None:
        """Возвращает страницу 404 для неподдерживаемых методов."""
        self._send_page(NOT_FOUND_PAGE, status=404)

    do_PUT = _send_not_found
    do_DELETE = _send_not_found
    do_PATCH = _send_not_found


def run(host: str = HOST, port: int = PORT) -> None:
    """Запускает HTTP-сервер.

    Args:
        host: адрес, на котором слушать.
        port: порт.
    """
    server = ThreadingHTTPServer((host, port), ShopRequestHandler)
    print(f"Сервер запущен: http://{host}:{port}")
    print("GET — страница «Контакты», POST — данные печатаются в консоль")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера")
    finally:
        server.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(port=port)
