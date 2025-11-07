import json

from src.infrastructure.cache.redis.redis_client import redis_client


class RedisMethod:
    """
    Lớp dịch vụ cung cấp các phương thức tiện ích để tương tác với Redis,
    bao gồm các thao tác với String, JSON và Hash.
    """
    async def set_json(self, key: str, data: dict, expire_seconds: int | None = None):
        """
        Chuyển đổi một dictionary thành chuỗi JSON và lưu vào Redis với một key.

        :param key: Key để lưu trong Redis.
        :param data: Dữ liệu dictionary cần lưu.
        :param expire_seconds: Thời gian tự hủy (TTL) tính bằng giây (tùy chọn).
        """
        value = json.dumps(data)
        await redis_client.set(key, value, ex=expire_seconds)

    async def get_json(self, key: str) -> dict | None:
        """
        Lấy chuỗi JSON từ Redis theo key và chuyển đổi ngược lại thành dictionary.

        :param key: Key cần lấy dữ liệu.
        :return: Dữ liệu dictionary nếu key tồn tại, ngược lại trả về None.
        """
        value = await redis_client.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: str | int | dict, expire_seconds: int | None = None):
        """
        Lưu một giá trị (string, int, hoặc dict) vào Redis.
        Tự động chuyển đổi dict thành JSON trước khi lưu.

        :param key: Key để lưu trong Redis.
        :param value: Giá trị cần lưu.
        :param expire_seconds: Thời gian tự hủy (TTL) tính bằng giây (tùy chọn).
        """
        if isinstance(value, dict):
            value = json.dumps(value)
        else:
            value = str(value)
        await redis_client.set(key, value, ex=expire_seconds)

    async def get(self, key: str) -> str | None:
        """
        Lấy giá trị dạng chuỗi thô từ Redis theo key.

        :param key: Key cần lấy giá trị.
        :return: Giá trị dạng chuỗi nếu key tồn tại, ngược lại trả về None.
        """
        return await redis_client.get(key)

    async def delete(self, key: str):
        """
        Xóa một key và giá trị tương ứng khỏi Redis.

        :param key: Key cần xóa.
        """
        await redis_client.delete(key)

    async def incr(self, key: str):
        """
        Tăng giá trị (dạng số nguyên) của một key lên 1.
        Nếu key không tồn tại, nó sẽ được tạo với giá trị 0 trước khi tăng.

        :param key: Key cần tăng giá trị.
        :return: Giá trị của key sau khi đã tăng.
        """
        return await redis_client.incr(key)

    async def expire(self, key: str, seconds: int):
        """
        Thiết lập thời gian tự hủy (Time To Live - TTL) cho một key.

        :param key: Key cần thiết lập TTL.
        :param seconds: Thời gian tồn tại tính bằng giây.
        """
        await redis_client.expire(key, seconds)

    async def exists(self, key: str) -> bool:
        """
        Kiểm tra sự tồn tại của một key trong Redis.

        :param key: Key cần kiểm tra.
        :return: True nếu key tồn tại, False nếu không.
        """
        result = await redis_client.exists(key)
        return result == 1

    async def hset(self, key: str, field: str, value: str):
        """
        Thiết lập giá trị cho một trường (field) trong một cấu trúc Hash.
        Nếu key của Hash chưa tồn tại, một Hash mới sẽ được tạo.

        :param key: Key của cấu trúc Hash.
        :param field: Tên của trường trong Hash.
        :param value: Giá trị cần gán cho trường.
        """
        await redis_client.hset(key, field, value)

    async def hget(self, key: str, field: str) -> bytes | None:
        """
        Lấy giá trị của một trường (field) từ một cấu trúc Hash.

        :param key: Key của cấu trúc Hash.
        :param field: Tên của trường cần lấy giá trị.
        :return: Giá trị của trường dưới dạng bytes nếu tồn tại, ngược lại trả về None.
        """
        return await redis_client.hget(key, field)

    async def hdel(self, key: str, field: str):
        """
        Xóa một trường (field) khỏi một cấu trúc Hash.

        :param key: Key của cấu trúc Hash.
        :param field: Tên của trường cần xóa.
        """
        await redis_client.hdel(key, field)