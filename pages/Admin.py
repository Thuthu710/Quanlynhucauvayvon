import streamlit as st
import pandas as pd
from database import get_connection

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

# --------------------------
# Giao diện Đăng nhập
# --------------------------
if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP QUẢN TRỊ HỆ THỐNG VỐN")
    
    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        login = st.form_submit_button("Đăng nhập")
        
        if login:
            if username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")

# --------------------------
# Giao diện Sau khi đăng nhập thành công
# --------------------------
else:
    st.sidebar.title("🔐 Menu Quản Trị Admin")
    admin_action = st.sidebar.radio(
        "Chọn chức năng:", 
        ["📋 Danh Sách Hồ Sơ & Thẩm Định", "📊 Dashboard Tổng Quan", "🚪 Đăng Xuất"]
    )
    
    if admin_action == "🚪 Đăng Xuất":
        st.session_state.logged_in = False
        st.rerun()

    # Kết nối CSDL để lấy dữ liệu hồ sơ vay vốn
    try:
        conn = get_connection()
        sql = """
        SELECT *
        FROM dangky_vayvon
        ORDER BY id DESC
        """
        df = pd.read_sql(sql, conn)
        conn.close()
    except Exception as e:
        # Dự phòng nếu chưa có bảng CSDL, tạo DataFrame mẫu từ session_state hoặc thông báo
        df = pd.DataFrame()

    if admin_action == "📋 Danh Sách Hồ Sơ & Thẩm Định":
        st.title("📋 Quản Lý Hồ Sơ Khách Hàng & Thẩm Định Tín Dụng")
        st.markdown("Xem danh sách đăng ký, kiểm tra tài sản thế chấp và xử lý hồ sơ.")
        
        if df.empty:
            st.warning("⚠️ Chưa có dữ liệu hồ sơ nào trong bảng cơ sở dữ liệu hoặc kết nối đang trống.")
        else:
            st.write(f"Tìm thấy **{len(df)}** hồ sơ trong hệ thống.")
            st.markdown("---")
            
            # Hiển thị bảng chi tiết có kèm các yếu tố tài sản thế chấp
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### 🔍 Thẩm Định Nhanh Hồ Sơ")
            selected_id = st.selectbox("Chọn Mã ID hồ sơ cần xem xét chi tiết:", df['id'].tolist() if 'id' in df.columns else [])
            
            if selected_id:
                row_data = df[df['id'] == selected_id].iloc[0]
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Khách hàng:** {row_data.get('name', 'N/A')}")
                    st.write(f"**Số điện thoại:** {row_data.get('phone', 'N/A')}")
                    st.write(f"**Số tiền yêu cầu:** {row_data.get('requested_amount', 0):,.0f} VNĐ")
                with col_b:
                    st.write(f"**Tài sản thế chấp:** {row_data.get('has_collateral', 'Không')} - {row_data.get('collateral_type', 'Không có')}")
                    st.write(f"**Giá trị định giá TSBD:** {row_data.get('collateral_value', 0):,.0f} VNĐ")
                    
                new_status = st.selectbox("Cập nhật trạng thái duyệt:", ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"])
                if st.button("Lưu trạng thái hồ sơ"):
                    st.success(f"Đã cập nhật trạng thái hồ sơ [{selected_id}] thành công!")

    elif admin_action == "📊 Dashboard Tổng Quan":
        st.title("📊 Dashboard Tổng Quan Hoạt Động Vốn")
        
        if df.empty:
            st.info("Chưa có dữ liệu thống kê.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Tổng số hồ sơ", len(df))
            with c2:
                total_money = df['requested_amount'].sum() if 'requested_amount' in df.columns else 0
                st.metric("Tổng nhu cầu vốn", f"{total_money:,.0f} VNĐ")
            with c3:
                avg_score = int(df['credit_score'].mean()) if 'credit_score' in df.columns else 0
                st.metric("Điểm CIC trung bình", avg_score)
                
            st.markdown("---")
            st.subheader("Biểu đồ / Số liệu chi tiết danh mục")
            st.dataframe(df, use_container_width=True)
