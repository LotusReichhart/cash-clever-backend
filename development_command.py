import subprocess
import sys

COMPOSE_FILE = "docker-compose.dev.yml"
DB_CONTAINER = "cash-clever-db"
DB_USER = "DevUser"
DB_NAME = "cash_clever_db"

def compose_up():
    """Build & chạy toàn bộ stack (backend + db)"""
    print("Đang build & start container (dev mode)...")
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "up", "--build"], check=True)


def compose_down():
    """Dừng & xóa toàn bộ stack"""
    print("Dừng và xóa container...")
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "down"], check=True)


def compose_restart():
    """Restart nhanh backend container"""
    print("Restart container backend...")
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "restart", "backend"], check=True)


def compose_logs():
    """Xem logs backend"""
    subprocess.run(["docker", "compose", "-f", COMPOSE_FILE, "logs", "-f", "backend"], check=False)


def open_db_shell():
    """Mở psql shell trong container PostgreSQL"""
    print(f"Mở shell PostgreSQL trong container `{DB_CONTAINER}`...")
    try:
        subprocess.run(
            [
                "docker",
                "exec",
                "-it",
                DB_CONTAINER,
                "psql",
                "-U",
                DB_USER,
                "-d",
                DB_NAME,
            ],
            check=True,
        )
    except subprocess.CalledProcessError:
        print("Không thể mở psql shell. Kiểm tra lại container PostgreSQL có đang chạy không.")
        print("Gợi ý: chạy `python development_command.py up` trước.")


def help_menu():
    print("""
  Lệnh hỗ trợ dev:
   .\.venv\Scripts\activate               # Khởi động venv  
  python development_command.py up        # build + chạy toàn bộ stack
  python development_command.py down      # dừng + xóa container
  python development_command.py restart   # restart container backend
  python development_command.py logs      # xem logs backend
  python development_command.py db        # mở shell PostgreSQL trong container
    """)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        help_menu()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "up":
        compose_up()
    elif cmd == "down":
        compose_down()
    elif cmd == "restart":
        compose_restart()
    elif cmd == "logs":
        compose_logs()
    elif cmd == "db":
        open_db_shell()
    else:
        help_menu()
