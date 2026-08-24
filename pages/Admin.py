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
        login = st.form_submit_button("Đăng nhập Hệ Thống", type="primary")
        
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
    st.sidebar.markdown(f"Xin chào, **{USERNAME}**")
    admin_action = st.sidebar.radio(
        "Chọn chức năng:", 
        ["📋 Danh Sách Hồ Sơ & Thẩm Định", "📊 Dashboard Tổng Quan", "🚪 Đăng Xuất"]
    )
    
    if admin_action == "🚪 Đăng Xuất":
        st.session_state.logged_in = False
        st.rerun()

    # --- LẤY DỮ LIỆU AN TOÀN TỪ MYSQL CLOUD ---
    df = pd.DataFrame()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dangky_vayvon ORDER BY date DESC, id DESC")
        rows = cursor.fetchall()  # Lấy tất cả dữ liệu từ database
        conn.close()
        
        if rows:
            df = pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Lỗi kết nối hoặc truy vấn cơ sở dữ liệu: {e}")

    # --------------------------
    # CHỨC NĂNG 1: DANH SÁCH & THẨM ĐỊNH
    # --------------------------
    if admin_action == "📋 Danh Sách Hồ Sơ & Thẩm Định":
        st.title("📋 Quản Lý Kho Hồ Sơ Khách Hàng & Thẩm Định Tín Dụng")
        st.markdown("Hệ thống tự động tổng hợp toàn bộ các hồ sơ do khách hàng nộp vào kho MySQL.")
        
        if df.empty:
            st.info("📭 Kho dữ liệu MySQL hiện đang trống. Hãy kiểm tra xem lúc khách hàng bấm lưu có báo lỗi màu đỏ nào không nhé!")
        else:
            st.success(f"✨ Kho lưu trữ trên Cloud đang có tổng cộng **{len(df)}** hồ sơ.")
            st.markdown("---")
            
            # Hiển thị bảng dữ liệu
            st.dataframe(df, use_container_width=True)
            
            st.markdown("### 🔍 Thẩm Định Nhanh & Xử Lý Hồ Sơ")
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
                        st.write(f"**💰 Số tiền yêu cầu:** {float(row_data.get('requested_amount', 0)):,.0f} VNĐ")
                        st.write(f"**💵 Thu nhập hàng tháng:** {float(row_data.get('monthly_income', 0)):,.0f} VNĐ")
                    with col_b:
                        has_col = bool(row_data.get('has_collateral', 0))
                        st.write(f"**🛡️ Tài sản thế chấp:** {'Có' if has_col else 'Không'}")
                        st.write(f"**📦 Loại TSBD:** {row_data.get('collateral_type', 'Không có')}")
                        st.write(f"**📈 Giá trị định giá TSBD:** {float(row_data.get('collateral_value', 0)):,.0f} VNĐ")
                        st.write(f"**⭐ Điểm tín dụng CIC:** {row_data.get('credit_score', 'N/A')}")
                        st.write(f"**📝 Ghi chú:** {row_data.get('notes', 'Không có')}")
                        st.write(f"**📅 Ngày nộp:** {row_data.get('date', 'N/A')}")
                    
                    st.markdown("---")
                    current_status = row_data.get('status', 'Chờ thẩm định')
                    status_options = ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"]
                    idx_status = status_options.index(current_status) if current_status in status_options else 0
                    
                    new_status = st.selectbox("Cập nhật trạng thái duyệt:", status_options, index=idx_status)
                    
                    if st.button("💾 Cập Nhật Trạng Thái Vào Kho", type="primary"):
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE dangky_vayvon SET status = %s WHERE id = %s", (new_status, selected_id))
                            conn.commit()
                            conn.close()
                            st.success(f"Đã cập nhật trạng thái hồ sơ [{selected_id}] thành công thành: **{new_status}**!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi cập nhật: {e}")

    # --------------------------
    # CHỨC NĂNG 2: DASHBOARD TỔNG QUAN
    # --------------------------
    elif admin_action == "📊 Dashboard Tổng Quan":
        st.title("📊 Dashboard Tổng Quan Hoạt Động Vốn")
        
        if df.empty:
            st.info("📭 Chưa có dữ liệu thống kê.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Tổng số hồ sơ trong kho", len(df))
            with c2:
                total_money = df['requested_amount'].astype(float).sum() if 'requested_amount' in df.columns else 0
                st.metric("Tổng nhu cầu vốn yêu cầu", f"{total_money:,.0f} VNĐ")
            with c3:
                avg_score = int(df['credit_score'].mean()) if 'credit_score' in df.columns and not df['credit_score'].isnull().all() else 0
                st.metric("Điểm CIC trung bình", avg_score)
                
            st.markdown("---")
            st.subheader("📈 Chi tiết danh mục toàn bộ hồ sơ trong kho")
            st.dataframe(df, use_container_width=True)
