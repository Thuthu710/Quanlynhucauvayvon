import streamlit as st
import pandas as pd
import datetime

# Thử import kết nối CSDL, nếu lỗi dùng phương án dự phòng session_state
try:
    from database import get_connection
except ImportError:
    def get_connection():
        return None

st.set_page_config(
    page_title="Trang Quản Trị - Hệ Thống Vốn",
    page_icon="🔐",
    layout="wide"
)

# --------------------------
# Tài khoản quản trị
# --------------------------
USERNAME = "admin"
PASSWORD = "123456"

# Quản lý trạng thái đăng nhập trong session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Khởi tạo dữ liệu mẫu trong session_state nếu chưa có lịch sử (để Admin luôn thấy giao diện trực quan)
if "history_submissions" not in st.session_state:
    st.session_state.history_submissions = [
        {
            "id": "HD-999999",
            "name": "Nguyễn Văn Mẫu (Khách hàng mẫu)",
            "phone": "0901234567",
            "purpose": "1. Vay mua bất động sản (Nhà ở, đất ở)",
            "requested_amount": 500000000,
            "monthly_income": 30000000,
            "credit_score": 750,
            "has_collateral": True,
            "collateral_type": "Bất động sản có giấy chứng nhận (Sổ hồng/Sổ đỏ)",
            "collateral_value": 800000000,
            "notes": "Hồ sơ hiển thị mẫu khi chưa có khách hàng thực tế.",
            "date": str(datetime.date.today()),
            "status": "Chờ thẩm định"
        }
    ]

# --------------------------
# Giao diện Đăng nhập
# --------------------------
if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP QUẢN TRỊ HỆ THỐNG VỐN")
    
    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập", value="admin")
        password = st.text_input("Mật khẩu", type="password", value="123456")
        login = st.form_submit_button("Đăng nhập Hệ Thống", type="primary")
        
        if login:
            if username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu. (Mặc định: admin / 123456)")

# --------------------------
# Giao diện Sau khi đăng nhập thành công
# --------------------------
else:
    st.sidebar.title("🔐 Menu Quản Trị Admin")
    st.sidebar.markdown(f"Xin chào, **{USERNAME}**")
    admin_action = st.sidebar.radio(
        "Chọn chức năng:", 
        ["📋 Danh Sách Hồ Sơ & Thẩm Định", "📊 Dashboard Tổng Quan", "🚪 Đăng Xuất"]
    )
    
    if admin_action == "🚪 Đăng Xuất":
        st.session_state.logged_in = False
        st.rerun()

    # Lấy dữ liệu từ CSDL hoặc đồng bộ từ session_state
    df = pd.DataFrame()
    try:
        conn = get_connection()
        if conn is not None:
            sql = "SELECT * FROM dangky_vayvon ORDER BY id DESC"
            df = pd.read_sql(sql, conn)
            conn.close()
    except Exception:
        pass

    # Nếu CSDL trống hoặc không kết nối được, lấy dữ liệu từ st.session_state.history_submissions
    if df.empty and len(st.session_state.history_submissions) > 0:
        df = pd.DataFrame(st.session_state.history_submissions)

    # --------------------------
    # CHỨC NĂNG 1: DANH SÁCH & THẨM ĐỊNH
    # --------------------------
    if admin_action == "📋 Danh Sách Hồ Sơ & Thẩm Định":
        st.title("📋 Quản Lý Hồ Sơ Khách Hàng & Thẩm Định Tín Dụng")
        st.markdown("Xem danh sách đăng ký, kiểm tra tài sản thế chấp và xử lý hồ sơ vay vốn.")
        
        if df.empty:
            st.warning("⚠️ Hiện chưa có hồ sơ nào trong hệ thống. Dưới đây là giao diện mẫu để bạn xem trước bố cục:")
        else:
            st.info(f"✨ Hệ thống đang quản lý tổng cộng **{len(df)}** hồ sơ.")
            st.markdown("---")
            
            # Hiển thị bảng dữ liệu trực quan
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### 🔍 Thẩm Định Nhanh Hồ Sơ")
            id_list = df['id'].tolist() if 'id' in df.columns else []
            
            if id_list:
                selected_id = st.selectbox("Chọn Mã ID hồ sơ cần xem xét chi tiết:", id_list)
                
                if selected_id:
                    row_data = df[df['id'] == selected_id].iloc[0]
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**👤 Khách hàng:** {row_data.get('name', 'N/A')}")
                        st.write(f"**📞 Số điện thoại:** {row_data.get('phone', 'N/A')}")
                        st.write(f"**🎯 Mục đích vay:** {row_data.get('purpose', 'N/A')}")
                        st.write(f"**💰 Số tiền yêu cầu:** {row_data.get('requested_amount', 0):,.0f} VNĐ")
                        st.write(f"**💵 Thu nhập hàng tháng:** {row_data.get('monthly_income', 0):,.0f} VNĐ")
                    with col_b:
                        has_col = row_data.get('has_collateral', False)
                        st.write(f"**🛡️ Tài sản thế chấp:** {'Có' if has_col else 'Không'}")
                        st.write(f"**📦 Loại TSBD:** {row_data.get('collateral_type', 'Không có')}")
                        st.write(f"**📈 Giá trị định giá TSBD:** {row_data.get('collateral_value', 0):,.0f} VNĐ")
                        st.write(f"**⭐ Điểm tín dụng CIC:** {row_data.get('credit_score', 'N/A')}")
                        st.write(f"**📝 Ghi chú:** {row_data.get('notes', 'Không có')}")
                    
                    st.markdown("---")
                    current_status = row_data.get('status', 'Chờ thẩm định')
                    status_options = ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"]
                    idx_status = status_options.index(current_status) if current_status in status_options else 0
                    
                    new_status = st.selectbox("Cập nhật trạng thái duyệt:", status_options, index=idx_status)
                    
                    if st.button("💾 Lưu Trạng Thái Hồ Sơ", type="primary"):
                        # Cập nhật trong session_state
                        for item in st.session_state.history_submissions:
                            if item["id"] == selected_id:
                                item["status"] = new_status
                        st.success(f"Đã cập nhật trạng thái hồ sơ [{selected_id}] thành công thành: **{new_status}**!")
                        st.rerun()

    # --------------------------
    # CHỨC NĂNG 2: DASHBOARD TỔNG QUAN
    # --------------------------
    elif admin_action == "📊 Dashboard Tổng Quan":
        st.title("📊 Dashboard Tổng Quan Hoạt Động Vốn")
        
        if df.empty:
            st.info("Chưa có dữ liệu thống kê tổng quan.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Tổng số hồ sơ", len(df))
            with c2:
                total_money = df['requested_amount'].sum() if 'requested_amount' in df.columns else 0
                st.metric("Tổng nhu cầu vốn", f"{total_money:,.0f} VNĐ")
            with c3:
                avg_score = int(df['credit_score'].mean()) if 'credit_score' in df.columns and not df['credit_score'].isnull().all() else 0
                st.metric("Điểm CIC trung bình", avg_score)
                
            st.markdown("---")
            st.subheader("📈 Thống kê nhanh danh mục hồ sơ")
            st.dataframe(df, use_container_width=True)
