import streamlit as st
import pandas as pd
import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Hệ Thống Quản Lý Nguồn Vốn & Thẩm Định",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
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

# --- Database Khởi Tạo Ban Đầu (Trống để người dùng tự nhập) ---
if "applications" not in st.session_state:
    st.session_state.applications = []

# --- Sidebar Navigation ---
st.sidebar.title("🏢 Hệ Thống Quản Lý Vốn")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "➕ Tiếp Nhận Hồ Sơ Mới", 
        "🧮 Công Cụ Tính Toán & Xét Duyệt", 
        "🔒 Trang Admin: Quản Lý Hồ Sơ & Thẩm Định", 
        "📊 Trang Admin: Dashboard Tổng Quan"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Hệ thống hỗ trợ nghiệp vụ:** Tiếp nhận, định giá tài sản thế chấp, chạy công cụ tính toán và quản trị tập trung tại phân hệ Admin.")

# ==========================================
# 1. TIẾP NHẬN HỒ SƠ MỚI (KHÁCH HÀNG / NHÂN VIÊN NHẬP)
# ==========================================
if menu == "➕ Tiếp Nhận Hồ Sơ Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Mới")
    st.markdown("Vui lòng điền đầy đủ thông tin khách hàng, nhu cầu vốn và **tài sản thế chấp / cầm cố** (nếu có).")
    
    with st.form("new_loan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Thông tin khách hàng")
            full_name = st.text_input("Họ và tên khách hàng (Bắt buộc):", placeholder="Ví dụ: Nguyễn Văn A")
            phone = st.text_input("Số điện thoại liên hệ (Bắt buộc):", placeholder="Ví dụ: 0912xxxxxx")
            purpose = st.selectbox(
                "Mục đích vay vốn:", 
                ["Kinh doanh mở rộng xưởng", "Mua sắm trang thiết bị", "Đầu tư lưu động ngắn hạn", "Tiêu dùng cá nhân / Sửa nhà", "Mua bất động sản", "Khác"]
            )
            req_amount = st.number_input("Số tiền yêu cầu vay (VNĐ):", min_value=1000000, value=300000000, step=50000000, format="%d")
            monthly_inc = st.number_input("Thu nhập hàng tháng của KH (VNĐ):", min_value=0, value=25000000, step=5000000, format="%d")
            
        with col2:
            st.subheader("🛡️ Tài sản thế chấp & Tín dụng")
            credit_score = st.slider("Điểm tín dụng dự kiến / CIC:", min_value=300, max_value=850, value=700)
            
            has_collateral = st.checkbox("Khách hàng có Tài sản thế chấp / Cầm cố?", value=True)
            
            collateral_type = "Không có"
            collateral_value = 0
            
            if has_collateral:
                collateral_type = st.selectbox(
                    "Loại tài sản bảo đảm:",
                    ["Bất động sản (Nhà/Đất)", "Phương tiện vận tải (Ô tô/Xe máy)", "Giấy tờ có giá (Sổ tiết kiệm, Cổ phiếu)", "Hàng hóa tồn kho / Máy móc thiết bị"]
                )
                collateral_value = st.number_input("Giá trị định giá tài sản (VNĐ):", min_value=0, value=500000000, step=50000000, format="%d")
            
            staff_note = st.text_area("Ghi chú ban đầu của nhân viên tiếp nhận:", placeholder="Tình trạng hồ sơ, giấy tờ sơ bộ...")
            
        submitted = st.form_submit_button("Lưu & Chuyển hồ sơ vào hệ thống")
        
        if submitted:
            if not full_name.strip() or not phone.strip():
                st.error("Vui lòng điền đầy đủ Họ tên và Số điện thoại của khách hàng!")
            else:
                # Thuật toán gợi ý tự động dựa trên Điểm tín dụng, Thu nhập và Giá trị Tài sản thế chấp
                # Nếu có tài sản thế chấp lớn, tỷ lệ chấp thuận cao hơn
                max_allowable_by_collateral = collateral_value * 0.7 if has_collateral else monthly_inc * 60
                
                if credit_score >= 700 or (has_collateral and collateral_value >= req_amount * 0.8):
                    eligibility = "Đạt (Đủ điều kiện)"
                    suggested_limit = min(req_amount, max_allowable_by_collateral if has_collateral else req_amount)
                elif credit_score >= 600:
                    eligibility = "Cần xem xét thêm (Rủi ro trung bình)"
                    suggested_limit = int(req_amount * 0.7)
                else:
                    eligibility = "Không đạt (Rủi ro cao)"
                    suggested_limit = 0
                    
                new_id = f"HD-2026-{len(st.session_state.applications)+1001}"
                new_record = {
                    "id": new_id,
                    "name": full_name,
                    "phone": phone,
                    "purpose": purpose,
                    "requested_amount": req_amount,
                    "monthly_income": monthly_inc,
                    "credit_score": credit_score,
                    "has_collateral": "Có" if has_collateral else "Không",
                    "collateral_type": collateral_type,
                    "collateral_value": collateral_value,
                    "status": "Chờ thẩm định",
                    "eligibility": eligibility,
                    "suggested_limit": suggested_limit,
                    "date": str(datetime.date.today()),
                    "notes": staff_note if staff_note else "Tiếp nhận mới."
                }
                st.session_state.applications.append(new_record)
                st.success(f"🎉 Đã tiếp nhận thành công hồ sơ mã [{new_id}] cho khách hàng **{full_name}**!")
                st.info("💡 Bạn có thể vào phân hệ **Trang Admin: Quản Lý Hồ Sơ & Thẩm Định** để xem lại và duyệt chi tiết.")

# ==========================================
# 2. CÔNG CỤ TÍNH TOÁN & XÉT DUYỆT (CHO NV VÀ KH)
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán & Xét Duyệt":
    st.title("🧮 Công Cụ Tính Toán Nợ Vay & Xét Duyệt Hạn Mức")
    st.markdown("Giúp nhân viên thẩm định hoặc khách hàng tính toán nhanh khả năng trả nợ (DTI) và mức độ an toàn của tài sản thế chấp.")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.subheader("📋 Tham số tính toán")
        income = st.number_input("Thu nhập hàng tháng (VNĐ):", value=30000000, step=5000000, format="%d")
        loan_amount = st.number_input("Số tiền muốn vay (VNĐ):", value=400000000, step=50000000, format="%d")
        term_months = st.slider("Thời hạn vay (Tháng):", min_value=12, max_value=360, value=60, step=12)
        interest_rate_annual = st.slider("Lãi suất năm (%):", min_value=6.0, max_value=18.0, value=10.5, step=0.5)
        
        st.markdown("---")
        st.subheader("🛡️ Yếu tố Tài sản bảo đảm (TSBD)")
        col_ts1, col_ts2 = st.columns(2)
        with col_ts1:
            has_col = st.checkbox("Có tài sản thế chấp", value=True)
        with col_ts2:
            col_val = st.number_input("Giá trị định giá TSBD (VNĐ):", value=600000000, step=50000000, format="%d")
        
    with col_calc2:
        st.subheader("📊 Kết quả xét duyệt & Phân tích rủi ro")
        
        # Tính gốc lãi hàng tháng theo dư nợ giảm dần / trả đều
        monthly_rate = (interest_rate_annual / 100) / 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * monthly_rate * ((1 + monthly_rate)**term_months) / (((1 + monthly_rate)**term_months) - 1)
        else:
            monthly_payment = loan_amount / term_months
            
        total_payment = monthly_payment * term_months
        total_interest = total_payment - loan_amount
        dti_ratio = (monthly_payment / income) * 100
        
        # Tỷ lệ cho vay / Giá trị tài sản (LTV - Loan-to-Value)
        ltv_ratio = (loan_amount / col_val * 100) if (has_col and col_val > 0) else 100.0
        
        st.metric(label="Gốc & Lãi phải trả hàng tháng", value=f"{monthly_payment:,.0f} VNĐ")
        st.metric(label="Tỷ lệ trả nợ / Thu nhập (DTI)", value=f"{dti_ratio:.1f}%", 
                  delta="An toàn (< 50%)" if dti_ratio <= 50 else "Cần cân nhắc (> 50%)",
                  delta_color="normal" if dti_ratio <= 50 else "inverse")
        
        if has_col:
            st.metric(label="Tỷ lệ Vay / Tài sản thế chấp (LTV)", value=f"{ltv_ratio:.1f}%",
                      delta="An toàn (<= 70%)" if ltv_ratio <= 70 else "Cao (> 70%)",
                      delta_color="normal" if ltv_ratio <= 70 else "inverse")
        
        st.markdown("---")
        # Kết luận xét duyệt
        dti_pass = dti_ratio <= 50
        ltv_pass = (ltv_ratio <= 70) if has_col else True
        
        if dti_pass and ltv_pass:
            st.success("✅ **KẾT LUẬN:** Hồ sơ **ĐẠT TIÊU CHÍ** cho vay an toàn. Khả năng trả nợ và tài sản đảm bảo nằm trong vùng rủi ro cho phép.")
        elif not dti_pass and not ltv_pass:
            st.error("❌ **KẾT LUẬN:** Hồ sơ **KHÔNG ĐẠT**. Cả tỷ lệ thu nhập (DTI) và tỷ lệ tài sản (LTV) đều vượt ngưỡng an toàn.")
        else:
            st.warning("⚠️ **KẾT LUẬN:** Hồ sơ **CẦN XEM XÉT THÊM**. Cần bổ sung thêm tài sản thế chấp hoặc người đồng trả nợ.")

# ==========================================
# 3. TRANG ADMIN: QUẢN LÝ HỒ SƠ & THẨM ĐỊNH
# ==========================================
elif menu == "🔒 Trang Admin: Quản Lý Hồ Sơ & Thẩm Định":
    st.title("🔒 Quản Lý Hồ Sơ Khách Hàng & Thẩm Định Tín Dụng (Admin)")
    st.markdown("Khu vực dành cho nhân viên quản lý/thẩm định duyệt, cập nhật trạng thái và ghi chú hồ sơ.")
    
    if len(st.session_state.applications) == 0:
        st.info("📭 Hiện chưa có hồ sơ nào trong hệ thống. Vui lòng vào mục **'➕ Tiếp Nhận Hồ Sơ Mới'** để thêm hồ sơ đầu tiên.")
    else:
        df = pd.DataFrame(st.session_state.applications)
        
        status_filter = st.selectbox("Lọc theo trạng thái hồ sơ:", ["Tất cả", "Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"])
        if status_filter != "Tất cả":
            filtered_df = df[df['status'] == status_filter]
        else:
            filtered_df = df
            
        st.write(Tìm thấy f"**{len(filtered_df)}** hồ sơ phù hợp.")
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
                    
                    if "Đạt" in row['eligibility']:
                        st.success(f"Hệ thống gợi ý: **{row['eligibility']}**")
                    elif "Cần" in row['eligibility']:
                        st.warning(f"Hệ thống gợi ý: **{row['eligibility']}**")
                    else:
                        st.error(f"Hệ thống gợi ý: **{row['eligibility']}**")
                        
                with c3:
                    st.markdown("#### 🎯 Phê duyệt & Cập nhật")
                    st.info(f"💡 Hạn mức đề xuất: **{row['suggested_limit']:,.0f} VNĐ**")
                    
                    # Tìm index thực tế trong session_state
                    real_idx = next(i for i, item in enumerate(st.session_state.applications) if item["id"] == row['id'])
                    
                    new_status = st.selectbox(
                        "Cập nhật trạng thái",
                        ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"],
                        index=["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"].index(row['status']),
                        key=f"status_{row['id']}"
                    )
                    
                    notes = st.text_input("Ghi chú thẩm định nội bộ", value=row['notes'], key=f"notes_{row['id']}")
                    
                    if st.button(f"Lưu thay đổi {row['id']}", key=f"btn_{row['id']}"):
                        st.session_state.applications[real_idx]['status'] = new_status
                        st.session_state.applications[real_idx]['notes'] = notes
                        st.success("Đã cập nhật hồ sơ thành công!")
                        st.rerun()

# ==========================================
# 4. TRANG ADMIN: DASHBOARD TỔNG QUAN
# ==========================================
elif menu == "📊 Trang Admin: Dashboard Tổng Quan":
    st.title("📊 Dashboard Tổng Quan Hoạt Động Vốn (Admin)")
    st.markdown("Thống kê số liệu thời gian thực toàn bộ danh mục hồ sơ vay vốn.")
    
    if len(st.session_state.applications) == 0:
        st.info("📭 Chưa có dữ liệu thống kê. Vui lòng thêm hồ sơ mới để xem báo cáo.")
    else:
        df = pd.DataFrame(st.session_state.applications)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Tổng số hồ sơ", value=len(df))
        with col2:
            total_req = df['requested_amount'].sum()
            st.metric(label="Tổng nhu cầu vốn", value=f"{total_req:,.0f} VNĐ")
        with col3:
            approved_count = len(df[df['status'].isin(['Đã phê duyệt', 'Đã giải ngân'])])
            st.metric(label="Hồ sơ đã duyệt / giải ngân", value=approved_count)
        with col4:
            avg_score = int(df['credit_score'].mean()) if len(df) > 0 else 0
            st.metric(label="Điểm tín dụng CIC TB", value=avg_score)
            
        st.markdown("---")
        st.subheader("📋 Bảng Dữ Liệu Tổng Hợp")
        st.dataframe(
            df[['id', 'name', 'phone', 'purpose', 'requested_amount', 'has_collateral', 'status', 'eligibility']], 
            use_container_width=True
        )
                st.success(f"Thêm thành công hồ sơ {new_id} cho khách hàng {full_name}!")
                st.balloons()
