import streamlit as st
import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Cổng Đăng Ký & Tính Toán Vốn",
    page_icon="📥",
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

if "client_submissions" not in st.session_state:
    st.session_state.client_submissions = []

# --- Sidebar Navigation (Chỉ bao gồm phần 1 & 2) ---
st.sidebar.title("📥 Cổng Tiếp Nhận & Tính Toán")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "➕ Tiếp Nhận Hồ Sơ Mới", 
        "🧮 Công Cụ Tính Toán & Xét Duyệt"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Nơi tiếp nhận thông tin nhu cầu vốn, định giá tài sản thế chấp và công cụ mô phỏng trả nợ.")

# ==========================================
# 1. TIẾP NHẬN HỒ SƠ MỚI
# ==========================================
if menu == "➕ Tiếp Nhận Hồ Sơ Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Mới")
    st.markdown("Vui lòng điền đầy đủ thông tin khách hàng, nhu cầu vốn và **tài sản thế chấp / cầm cố**.")
    
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
            
            staff_note = st.text_area("Ghi chú ban đầu:", placeholder="Tình trạng hồ sơ, giấy tờ sơ bộ...")
            
        submitted = st.form_submit_button("Lưu & Gửi Hồ Sơ Vào Hệ Thống")
        
        if submitted:
            if not full_name.strip() or not phone.strip():
                st.error("Vui lòng điền đầy đủ Họ tên và Số điện thoại của khách hàng!")
            else:
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
                    
                new_id = f"HD-2026-{len(st.session_state.client_submissions)+1001}"
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
                st.session_state.client_submissions.append(new_record)
                st.success(f"🎉 Gửi hồ sơ thành công! Mã hồ sơ của bạn là: **{new_id}**")

# ==========================================
# 2. CÔNG CỤ TÍNH TOÁN & XÉT DUYỆT
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán & Xét Duyệt":
    st.title("🧮 Công Cụ Tính Toán Nợ Vay & Xét Duyệt Hạn Mức")
    st.markdown("Giúp tính toán nhanh khả năng trả nợ (DTI) và mức độ an toàn của tài sản thế chấp (LTV).")
    
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
        
        monthly_rate = (interest_rate_annual / 100) / 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * monthly_rate * ((1 + monthly_rate)**term_months) / (((1 + monthly_rate)**term_months) - 1)
        else:
            monthly_payment = loan_amount / term_months
            
        total_payment = monthly_payment * term_months
        total_interest = total_payment - loan_amount
        dti_ratio = (monthly_payment / income) * 100
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
        dti_pass = dti_ratio <= 50
        ltv_pass = (ltv_ratio <= 70) if has_col else True
        
        if dti_pass and ltv_pass:
            st.success("✅ **KẾT LUẬN:** Hồ sơ **ĐẠT TIÊU CHÍ** cho vay an toàn.")
        elif not dti_pass and not ltv_pass:
            st.error("❌ **KẾT LUẬN:** Hồ sơ **KHÔNG ĐẠT**. Cả tỷ lệ thu nhập (DTI) và tỷ lệ tài sản (LTV) đều vượt ngưỡng an toàn.")
        else:
            st.warning("⚠️ **KẾT LUẬN:** Hồ sơ **CẦN XEM XÉT THÊM**.")
