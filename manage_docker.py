import docker

# Khởi tạo client kết nối tới Docker Engine (thông qua socket /var/run/docker.sock)
client = docker.from_env()


def build_image():
    """Build Docker image từ Dockerfile trong thư mục hiện tại"""
    print("Đang build image...")
    image, logs = client.images.build(path=".", tag="cash-clever-backend:test")
    for log in logs:
        if "stream" in log:
            print(log["stream"].strip())
    print("Build xong:", image.tags)


def run_container():
    """Chạy container từ image vừa build"""
    print("Đang chạy container...")

    # Nếu container đã tồn tại thì xóa trước
    try:
        old = client.containers.get("cash-clever-backend")
        old.stop()
        old.remove()
        print("Container cũ đã được xóa")
    except docker.errors.NotFound:
        pass

    container = client.containers.run(
        "cash-clever-backend:test",
        name="cash-clever-backend",
        detach=True,
        ports={"8000/tcp": 8000},
    )
    print("Container chạy:", container.name)



def list_containers():
    """Liệt kê tất cả container"""
    print("Danh sách container:")
    for c in client.containers.list(all=True):
        print(f"- {c.name} ({c.status})")


def stop_and_remove():
    """Dừng và xóa container cash-clever-backend"""
    try:
        container = client.containers.get("cash-clever-backend")
        print("Dừng container...")
        container.stop()
        print("Xóa container...")
        container.remove()
    except docker.errors.NotFound:
        print("Container không tồn tại")


if __name__ == "__main__":
    build_image()
    run_container()
    list_containers()
    input("Nhấn Enter để stop/remove container...")
    stop_and_remove()
