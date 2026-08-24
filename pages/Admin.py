import streamlit as st
import pandas as pd

# Cố gắng import get_connection từ file database.py của bạn
try:
    from database import get_connection
    has_db_module = True
except ImportError:
    has_db_module = False

# --- Page Config ---
st.set_page_config(
    page_title="Trang quản trị - Thẩm Định Vốn",
    page_icon="🔐",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo trạng thái đăng nhập trong session_state nếu chưa có
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

# --------------------------
# KIỂM TRA TRẠNG THÁI ĐĂNG NHẬP
# --------------------------
if not st.session_state.is_authenticated:
    st.title("🔐 ĐĂNG NHẬP QUẢN TRỊ")
    st.markdown("Vui lòng đăng nhập để truy cập hệ thống quản lý và thẩm định nguồn vốn.")
    
    # Tài khoản quản trị
    USERNAME = "admin"
    PASSWORD = "123456"

    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        login_btn = st.form_submit_button("Đăng nhập")

        if login_btn:
            if username == USERNAME and password == PASSWORD:
                st.session_state.is_authenticated = True
                st.success("Đăng nhập thành công! Đang chuyển hướng...")
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")

else:
    # --------------------------
    # KHU VỰC SAU KHI ĐĂNG NHẬP THÀNH CÔNG
    # --------------------------
    st.sidebar.title("🔐 Menu Quản Trị")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.is_authenticated = False
        st.rerun()
        
    admin_menu = st.sidebar.radio(
        "Chọn chức năng:",
        ["📊 Dashboard & Danh Sách Đăng Ký", "👥 Quản Lý & Thẩm Định Hồ Sơ Vay"]
    )

    if admin_menu == "📊 Dashboard & Danh Sách Đăng Ký":
        st.title("📊 Quản Trị: Dữ Liệu Kết Nối Cơ Sở Dữ Liệu")
        st.markdown("Hiển thị dữ liệu trực tiếp từ Database hệ thống.")

        if has_db_module:
            try:
                conn = get_connection()
                sql = """
                SELECT *
                FROM dangky_dulich
                ORDER BY id DESC
                """
                df = pd.read_sql(sql, conn)
                conn.close()

                st.subheader("📋 Danh sách dữ liệu từ bảng dangky_dulich")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.warning(f"Chưa kết nối được tới bảng cơ sở dữ liệu `dangky_dulich`: {e}")
                st.info("💡 Bạn có thể sử dụng bảng quản lý thẩm định bên dưới nếu chưa cấu hình bảng SQL này.")
        else:
            st.info("⚠️ Không tìm thấy file `database.py`. Đang sử dụng dữ liệu mô phỏng trong bộ nhớ tạm.")

    elif admin_menu == "👥 Quản Lý & Thẩm Định Hồ Sơ Vay":
        st.title("👥 Quản Lý Hồ Sơ & Thẩm Định Tín Dụng")
        st.markdown("Xem xét nhu cầu vốn, tài sản thế chấp và cập nhật trạng thái duyệt hồ sơ.")

        # Khởi tạo mock database cho phần thẩm định nếu chưa có
        if "admin_applications" not in st.session_state:
            st.session_state.admin_applications = [
                {
                    "id": "HD-2026-1001",
                    "name": "Nguyễn Văn An",
                    "phone": "0912345678",
                    "purpose": "Kinh doanh mở rộng xưởng",
                    "requested_amount": 500000000,
                    "monthly_income": 35000000,
                    "credit_score": 740,
                    "has_collateral": "Có",
                    "collateral_type": "Bất động sản (Nhà/Đất)",
                    "collateral_value": 800000000,
                    "status": "Chờ thẩm định",
                    "eligibility": "Đạt (Đủ điều kiện)",
                    "suggested_limit": 450000000,
                    "date": "2026-08-24",
                    "notes": "Hồ sơ mẫu, cần xác minh tài sản bảo đảm."
                }
            ]

        df_app = pd.DataFrame(st.session_state.admin_applications)
        
        status_filter = st.selectbox("Lọc theo trạng thái hồ sơ:", ["Tất cả", "Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"])
        filtered_df = df_app if status_filter == "Tất cả" else df_app[df_app['status'] == status_filter]
        
        st.write(f"Tìm thấy **{len(filtered_df)}** hồ sơ phù hợp.")
        st.markdown("---")
        
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📁 [{row['id']}] - KH: {row['name']} | Nhu cầu: {row['requested_amount']:,.0f} VNĐ | Trạng thái: **{row['status']}**"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("#### 👤 Thông tin khách hàng")
                    st.write(f"**Họ tên:** {row['name']}")
                    st.write(f"**Điện thoại:** {row['phone']}")
                    st.write(f"**Mục đích vay:** {row['purpose']}")
                    st.write(f"**Ngày tiếp nhận:** {row['date']}")
                    
                with c2:
                    st.markdown("#### 💳 Tài chính & Tài sản đảm bảo")
                    st.write(f"**Thu nhập tháng:** {row['monthly_income']:,.0f} VNĐ")
                    st.write(f"**Điểm CIC:** {row['credit_score']}")
                    st.write(f"**Tài sản thế chấp:** {row['has_collateral']} ({row['collateral_type']})")
                    if row['has_collateral'] == "Có":
                        st.write(f"**Định giá TS:** {row['collateral_value']:,.0f} VNĐ")
                    st.info(f"Đánh giá gợi ý: {row['eligibility']}")
                    
                with c3:
                    st.markdown("#### 🎯 Phê duyệt & Cập nhật")
                    st.info(f"💡 Hạn mức đề xuất: **{row['suggested_limit']:,.0f} VNĐ**")
                    
                    real_idx = next(i for i, item in enumerate(st.session_state.admin_applications) if item["id"] == row['id'])
                    
                    new_status = st.selectbox(
                        "Cập nhật trạng thái",
                        ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"],
                        index=["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"].index(row['status']),
                        key=f"adm_status_{row['id']}"
                    )
                    
                    notes = st.text_input("Ghi chú thẩm định nội bộ", value=row['notes'], key=f"adm_notes_{row['id']}")
                    
                    if st.button(f"Lưu thay đổi {row['id']}", key=f"adm_btn_{row['id']}"):
                        st.session_state.admin_applications[real_idx]['status'] = new_status
                        st.session_state.admin_applications[real_idx]['notes'] = notes
                        st.success("Đã cập nhật hồ sơ thành công!")
                        st.rerun()
