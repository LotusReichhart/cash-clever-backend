from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select, func, text

from src.domain.entities import CategoryStatus

from src.infrastructure.cache.redis.redis_client import connect_redis, close_redis
from src.infrastructure.database.postgresql.base import Base
from src.infrastructure.database.postgresql.models import CategoryModel
from src.infrastructure.database.postgresql.session import engine, AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables (startup)...")

    async with engine.begin() as conn:
        # 1. Bật extension unaccent
        print("Đang bật extension 'unaccent' (nếu chưa có)...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))

        # 2. Bật extension pg_trgm (Cần cho GIN index)
        print("Đang bật extension 'pg_trgm' (nếu chưa có)...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        print("Đánh dấu hàm unaccent(text) là IMMUTABLE...")
        await conn.execute(text("ALTER FUNCTION unaccent(text) IMMUTABLE;"))
        # -----------------------------------

        # 4. Tạo bảng (và các index đã định nghĩa trong model)
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created.")

    async with AsyncSessionLocal() as session:
        # Đếm CategoryModel thay vì SystemCategoryModel
        count = await session.scalar(select(func.count(CategoryModel.id)))
        if count == 0:
            print("Seeding default system categories...")

            _path = "https://cash-clever-s3-bucket.s3.ap-southeast-1.amazonaws.com/icons/categories/systems"

            # --- 1. TẠO 20 DANH MỤC CHA ---
            mua_sam = CategoryModel(name="Mua sắm",
                                    icon_url=f"{_path}/shopping.png",
                                    is_system_owned=True, status=CategoryStatus.ACTIVE)
            an_uong = CategoryModel(name="Ăn uống",
                                    icon_url=f"{_path}/eat.png",
                                    is_system_owned=True, status=CategoryStatus.ACTIVE)
            suc_khoe = CategoryModel(name="Sức khỏe",
                                     icon_url=f"{_path}/healthcare.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            hoa_don = CategoryModel(name="Hóa đơn",
                                    icon_url=f"{_path}/transaction.png",
                                    is_system_owned=True, status=CategoryStatus.ACTIVE)
            giai_tri = CategoryModel(name="Giải trí",
                                     icon_url=f"{_path}/entertainment.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            giao_duc = CategoryModel(name="Giáo dục",
                                     icon_url=f"{_path}/education.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            du_lich = CategoryModel(name="Du lịch",
                                    icon_url=f"{_path}/tourism.png",
                                    is_system_owned=True, status=CategoryStatus.ACTIVE)
            dau_tu = CategoryModel(name="Đầu tư",
                                   icon_url=f"{_path}/invest.png",
                                   is_system_owned=True, status=CategoryStatus.ACTIVE)
            van_chuyen = CategoryModel(name="Vận chuyển",
                                       icon_url=f"{_path}/shipped.png",
                                       is_system_owned=True, status=CategoryStatus.ACTIVE)
            thu_cung = CategoryModel(name="Thú cưng",
                                     icon_url=f"{_path}/pets.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            nha_o = CategoryModel(name="Nhà ở",
                                  icon_url=f"{_path}/house.png",
                                  is_system_owned=True, status=CategoryStatus.ACTIVE)
            gia_dinh = CategoryModel(name="Gia đình & Con cái",
                                     icon_url=f"{_path}/family.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            qua_tang = CategoryModel(name="Quà tặng & Từ thiện",
                                     icon_url=f"{_path}/gifts.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            sua_chua = CategoryModel(name="Sửa chữa & Bảo dưỡng",
                                     icon_url=f"{_path}/fixing.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            kinh_doanh = CategoryModel(name="Kinh doanh & Công việc",
                                       icon_url=f"{_path}/business.png",
                                       is_system_owned=True, status=CategoryStatus.ACTIVE)
            thue_phi = CategoryModel(name="Thuế & Phí",
                                     icon_url=f"{_path}/taxes.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            bao_hiem = CategoryModel(name="Bảo hiểm",
                                     icon_url=f"{_path}/insurance.png",
                                     is_system_owned=True, status=CategoryStatus.ACTIVE)
            tiet_kiem = CategoryModel(name="Tiết kiệm",
                                      icon_url=f"{_path}/save.png",
                                      is_system_owned=True, status=CategoryStatus.ACTIVE)
            ca_nhan = CategoryModel(name="Phát triển cá nhân",
                                    icon_url=f"{_path}/motivation.png",
                                    is_system_owned=True, status=CategoryStatus.ACTIVE)
            chi_phi_khac = CategoryModel(name="Chi phí khác",
                                         icon_url=f"{_path}/others.png",
                                         is_system_owned=True, status=CategoryStatus.ACTIVE)

            # --- 2. TẠO DANH MỤC CON ---
            # (Sử dụng 'parent=' để gán quan hệ)
            children_list = [
                # Con của Hóa đơn
                CategoryModel(name="Hóa đơn điện", parent=hoa_don, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Hóa đơn nước", parent=hoa_don, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Hóa đơn Internet", parent=hoa_don, is_system_owned=True,
                              status=CategoryStatus.ACTIVE),
                CategoryModel(name="Hóa đơn điện thoại", parent=hoa_don, is_system_owned=True,
                              status=CategoryStatus.ACTIVE),

                # Con của Mua sắm
                CategoryModel(name="Quần áo", parent=mua_sam, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Mỹ phẩm", parent=mua_sam, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Đồ gia dụng", parent=mua_sam, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Thiết bị điện tử", parent=mua_sam, is_system_owned=True,
                              status=CategoryStatus.ACTIVE),

                # Con của Ăn uống
                CategoryModel(name="Ăn sáng", parent=an_uong, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Ăn trưa", parent=an_uong, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Ăn tối", parent=an_uong, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Đồ uống", parent=an_uong, is_system_owned=True, status=CategoryStatus.ACTIVE),

                # Con của Sức khỏe
                CategoryModel(name="Bệnh viện", parent=suc_khoe, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Thuốc men", parent=suc_khoe, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Thể hình", parent=suc_khoe, is_system_owned=True, status=CategoryStatus.ACTIVE),

                # Con của Giải trí
                CategoryModel(name="Phim ảnh", parent=giai_tri, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Âm nhạc", parent=giai_tri, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Trò chơi", parent=giai_tri, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Sự kiện", parent=giai_tri, is_system_owned=True, status=CategoryStatus.ACTIVE),

                # Con của Giáo dục
                CategoryModel(name="Sách vở", parent=giao_duc, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Khóa học", parent=giao_duc, is_system_owned=True, status=CategoryStatus.ACTIVE),

                # Con của Du lịch
                CategoryModel(name="Vé máy bay", parent=du_lich, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Khách sạn", parent=du_lich, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Tham quan", parent=du_lich, is_system_owned=True, status=CategoryStatus.ACTIVE),

                # Con của Đầu tư
                CategoryModel(name="Cổ phiếu", parent=dau_tu, is_system_owned=True, status=CategoryStatus.ACTIVE),
                CategoryModel(name="Tiền điện tử", parent=dau_tu, is_system_owned=True, status=CategoryStatus.ACTIVE),

                # Con của Vận chuyển
                CategoryModel(name="Xe buýt / Grab", parent=van_chuyen, is_system_owned=True,
                              status=CategoryStatus.ACTIVE),
                CategoryModel(name="Tàu hỏa", parent=van_chuyen, is_system_owned=True, status=CategoryStatus.ACTIVE),

                # Con của Thú cưng
                CategoryModel(name="Thức ăn cho thú cưng", parent=thu_cung, is_system_owned=True,
                              status=CategoryStatus.ACTIVE),
                CategoryModel(name="Chăm sóc thú cưng", parent=thu_cung, is_system_owned=True,
                              status=CategoryStatus.ACTIVE)
            ]

            # --- 3. THÊM TẤT CẢ VÀO SESSION ---
            session.add_all([
                # 20 Cha
                mua_sam, an_uong, suc_khoe, hoa_don, giai_tri, giao_duc, du_lich, dau_tu, van_chuyen, thu_cung,
                nha_o, gia_dinh, qua_tang, sua_chua, kinh_doanh, thue_phi, bao_hiem, tiet_kiem, ca_nhan, chi_phi_khac,

                # Tất cả con
                *children_list
            ])

            await session.commit()
            print("Default system categories inserted.")
        else:
            print("System categories already exist, skip seeding.")

    print("Connect Redis (startup)...")
    await connect_redis()

    yield

    print("Disconnect Redis (shutdown)...")
    await close_redis()

    print("Shutting down...")
