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
        ["📊 Dashboard Tổng Quan", "📋 Danh Sách & Thẩm Định Hồ Sơ", "🚪 Đăng Xuất"]
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
        rows = cursor.fetchall()  
        conn.close()
        
        if rows:
            df = pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Lỗi kết nối hoặc truy vấn cơ sở dữ liệu: {e}")

    # ----------------------------------------------------
    # CHỨC NĂNG 1: DASHBOARD TỔNG QUAN (ĐÃ LÀM MỚI CHI TIẾT)
    # ----------------------------------------------------
    if admin_action == "📊 Dashboard Tổng Quan":
        st.title("📊 Dashboard Tổng Quan Hoạt Động Tín Dụng")
        st.markdown("Bảng điều khiển trung tâm giúp nhà quản trị nắm bắt nhanh các chỉ số cốt lõi về dòng vốn và tình trạng phê duyệt hồ sơ.")
        
        if df.empty:
            st.info("📭 Chưa có dữ liệu thống kê trên hệ thống.")
        else:
            # Ép kiểu dữ liệu an toàn
            df['requested_amount'] = pd.to_numeric(df['requested_amount'], errors='coerce').fillna(0)
            df['monthly_income'] = pd.to_numeric(df['monthly_income'], errors='coerce').fillna(0)
            df['credit_score'] = pd.to_numeric(df['credit_score'], errors='coerce').fillna(0)
            df['has_collateral'] = pd.to_numeric(df['has_collateral'], errors='coerce').fillna(0)
            
            if 'status' not in df.columns:
                df['status'] = 'Chờ thẩm định'

            # Tính toán các chỉ số KPI chính
            total_applications = len(df)
            total_capital_demand = df['requested_amount'].sum()
            avg_credit_score = int(df['credit_score'].mean())
            
            approved_df = df[df['status'].isin(["Đã phê duyệt", "Đã giải ngân"])]
            total_approved_amount = approved_df['requested_amount'].sum()
            approval_rate = (len(approved_df) / total_applications * 100) if total_applications > 0 else 0

            # Hiển thị các ô Metric hàng trên
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Tổng hồ sơ", total_applications)
            with col2:
                st.metric("Tổng nhu cầu vốn", f"{total_capital_demand:,.0f} VNĐ")
            with col3:
                st.metric("Vốn đã duyệt/giải ngân", f"{total_approved_amount:,.0f} VNĐ")
            with col4:
                st.metric("Tỷ lệ phê duyệt", f"{approval_rate:.1f}%")
            with col5:
                st.metric("Điểm CIC TB", avg_credit_score)

            st.markdown("---")

            # Phân tích chi tiết bằng biểu đồ
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("📌 Tình Trạng Trạng Thái Hồ Sơ")
                status_counts = df['status'].value_counts()
                st.bar_chart(status_counts)
                
            with col_chart2:
                st.subheader("🎯 Phân Bổ Nhu Cầu Theo Mục Đích Vay")
                if 'purpose' in df.columns:
                    purpose_grouped = df.groupby('purpose')['requested_amount'].sum()
                    st.bar_chart(purpose_grouped)
                else:
                    st.info("Chưa có dữ liệu mục đích vay.")

            st.markdown("---")
            st.subheader("📋 Bảng Dữ Liệu Tóm Tắt Nhanh")
            summary_cols = ['id', 'name', 'phone', 'requested_amount', 'credit_score', 'status', 'date']
            available_summary_cols = [c for c in summary_cols if c in df.columns]
            st.dataframe(df[available_summary_cols], use_container_width=True)

    # ----------------------------------------------------
    # CHỨC NĂNG 2: DANH SÁCH & THẨM ĐỊNH HỒ SƠ (NÂNG CẤP MẠNH)
    # ----------------------------------------------------
    elif admin_action == "📋 Danh Sách & Thẩm Định Hồ Sơ":
        st.title("📋 Quản Lý Danh Sách & Thẩm Định Hồ Sơ Tín Dụng")
        st.markdown("Tra cứu chi tiết, lọc hồ sơ thông minh và tiến hành xét duyệt, từ chối hoặc giải ngân vốn an toàn.")
        
        if df.empty:
            st.info("📭 Kho dữ liệu MySQL hiện đang trống.")
        else:
            # Ép kiểu dữ liệu an toàn
            df['requested_amount'] = pd.to_numeric(df['requested_amount'], errors='coerce').fillna(0)
            df['monthly_income'] = pd.to_numeric(df['monthly_income'], errors='coerce').fillna(0)
            df['credit_score'] = pd.to_numeric(df['credit_score'], errors='coerce').fillna(0)
            if 'status' not in df.columns:
                df['status'] = 'Chờ thẩm định'

            # --- Bộ lọc tìm kiếm nhanh ---
            st.markdown("### 🔍 Bộ Lọc & Tìm Kiếm Hồ Sơ")
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                search_query = st.text_input("Tìm kiếm theo Tên hoặc Số điện thoại:", placeholder="Nhập tên/SĐT khách hàng...")
            with f_col2:
                all_statuses = ["Tất cả"] + list(df['status'].unique())
                status_filter = st.selectbox("Lọc theo trạng thái hồ sơ:", all_statuses)
            with f_col3:
                sort_option = st.selectbox("Sắp xếp danh sách theo:", ["Mới nhất", "Số tiền vay cao nhất", "Điểm tín dụng cao nhất"])

            # Áp dụng bộ lọc
            filtered_df = df.copy()
            if search_query:
                filtered_df = filtered_df[
                    filtered_df['name'].str.contains(search_query, case=False, na=False) | 
                    filtered_df['phone'].str.contains(search_query, case=False, na=False)
                ]
            if status_filter != "Tất cả":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]

            if sort_option == "Mới nhất":
                filtered_df = filtered_df.sort_values(by=['date', 'id'], ascending=False)
            elif sort_option == "Số tiền vay cao nhất":
                filtered_df = filtered_df.sort_values(by='requested_amount', ascending=False)
            elif sort_option == "Điểm tín dụng cao nhất":
                filtered_df = filtered_df.sort_values(by='credit_score', ascending=False)

            st.success(f"🔍 Hiển thị **{len(filtered_df)}** / {len(df)} hồ sơ phù hợp với bộ lọc.")
            
            # Hiển thị bảng danh sách rút gọn dễ nhìn
            display_cols = ['id', 'name', 'phone', 'purpose', 'requested_amount', 'credit_score', 'status', 'date']
            st.dataframe(filtered_df[[c for c in display_cols if c in filtered_df.columns]], use_container_width=True)

            st.markdown("---")
            st.markdown("### ⚙️ Khu Vực Thẩm Định & Xét Duyệt Chi Tiết")
            
            id_list = filtered_df['id'].tolist() if not filtered_df.empty else []
            
            if not id_list:
                st.warning("⚠️ Không có hồ sơ nào khớp với bộ lọc để tiến hành thẩm định.")
            else:
                selected_id = st.selectbox("Chọn Mã ID hồ sơ cần thẩm định chi tiết:", id_list)
                
                if selected_id:
                    row_data = filtered_df[filtered_df['id'] == selected_id].iloc[0]
                    
                    # Chia giao diện thẻ thẩm định rõ ràng thành 2 cột thông tin & 1 cột đánh giá rủi ro nhanh
                    col_info1, col_info2, col_risk = st.columns([1.2, 1.2, 1])
                    
                    with col_info1:
                        st.markdown("#### 👤 Thông Tin Khách Hàng")
                        st.write(f"**Mã hồ sơ:** `{row_data.get('id', 'N/A')}`")
                        st.write(f"**Họ tên:** {row_data.get('name', 'N/A')}")
                        st.write(f"**Điện thoại:** {row_data.get('phone', 'N/A')}")
                        st.write(f"**Mục đích vay:** {row_data.get('purpose', 'N/A')}")
                        st.write(f"**Ngày nộp:** {row_data.get('date', 'N/A')}")
                        st.write(f"**Ghi chú sơ bộ:** {row_data.get('notes', 'Không có')}")
                        
                    with col_info2:
                        st.markdown("#### 💰 Tài Chính & Tài Sản")
                        req_amt = float(row_data.get('requested_amount', 0))
                        inc = float(row_data.get('monthly_income', 0))
                        col_val = float(row_data.get('collateral_value', 0))
                        has_col = bool(row_data.get('has_collateral', 0))
                        
                        st.write(f"**Số tiền yêu cầu:** {req_amt:,.0f} VNĐ")
                        st.write(f"**Thu nhập tháng:** {inc:,.0f} VNĐ")
                        st.write(f"**Điểm CIC:** {row_data.get('credit_score', 'N/A')}")
                        st.write(f"**Tài sản thế chấp:** {'Có' if has_col else 'Không'}")
                        st.write(f"**Loại TSBD:** {row_data.get('collateral_type', 'Không có')}")
                        st.write(f"**Giá trị định giá:** {col_val:,.0f} VNĐ")

                    with col_risk:
                        st.markdown("#### 🛡️ Thẩm Định Sơ Bộ")
                        # Thẩm định ước tính DTI giả định kỳ hạn chuẩn 60 tháng, lãi suất 10%/năm
                        est_monthly_payment = req_amt * (0.10/12) / (1 - (1 + 0.10/12)**(-60)) if inc > 0 and req_amt > 0 else 0
                        est_dti = (est_monthly_payment / inc * 100) if inc > 0 else 100
                        est_ltv = (req_amt / col_val * 100) if (has_col and col_val > 0) else 0.0
                        
                        st.metric("DTI ước tính (60 tháng)", f"{est_dti:.1f}%", 
                                  delta="An toàn (<=50%)" if est_dti <= 50 else "Cao (>50%)",
                                  delta_color="normal" if est_dti <= 50 else "inverse")
                        if has_col:
                            st.metric("LTV ước tính", f"{est_ltv:.1f}%",
                                      delta="An toàn (<=70%)" if est_ltv <= 70 else "Cao (>70%)",
                                      delta_color="normal" if est_ltv <= 70 else "inverse")
                        else:
                            st.metric("Hình thức", "Cho vay tín chấp")

                    st.markdown("---")
                    
                    # Form cập nhật trạng thái phê duyệt
                    current_status = row_data.get('status', 'Chờ thẩm định')
                    status_options = ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"]
                    idx_status = status_options.index(current_status) if current_status in status_options else 0
                    
                    st.markdown("#### 📝 Ra Quyết Định Phê Duyệt")
                    with st.form(f"approve_form_{selected_id}"):
                        new_status = st.selectbox("Chọn trạng thái duyệt hồ sơ:", status_options, index=idx_status)
                        admin_notes = st.text_area("Ghi chú của Hội đồng tín dụng / Thẩm định viên:", placeholder="Nhập lý do phê duyệt, yêu cầu bổ sung giấy tờ hoặc lý do từ chối...")
                        
                        submit_approval = st.form_submit_button("💾 Xác Nhận Cập Nhật Trạng Thái", type="primary")
                        
                        if submit_approval:
                            try:
                                conn = get_connection()
                                cursor = conn.cursor()
                                sql_update = "UPDATE dangky_vayvon SET status = %s WHERE id = %s"
                                cursor.execute(sql_update, (new_status, selected_id))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success(f"🎉 Đã cập nhật thành công hồ sơ [{selected_id}] sang trạng thái: **{new_status}**!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Lỗi khi cập nhật vào cơ sở dữ liệu: {e}")
