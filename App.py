import streamlit as st
import datetime
import pandas as pd

# --- Cấu hình giao diện ---
st.set_page_config(
    page_title="Hệ Thống Quản Lý & Tính Toán Vốn Tín Dụng",
    page_icon="🏦",
    layout="wide"
)

# --- Khởi tạo session_state để lưu trữ dữ liệu thông suốt ---
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "Nguyễn Văn An",
        "phone": "0912345678",
        "purpose": "1. Vay mua bất động sản (Nhà ở, đất ở)",
        "requested_amount": 500000000,
        "monthly_income": 35000000,
        "credit_score": 720,
        "has_collateral": True,
        "collateral_type": "Bất động sản có giấy chứng nhận (Sổ hồng/Sổ đỏ)",
        "collateral_value": 800000000,
        "notes": "Khách hàng có lịch sử tín dụng tốt."
    }

if "history_submissions" not in st.session_state:
    st.session_state.history_submissions = []

# --- Menu điều hướng trong Sidebar ---
st.sidebar.title("🏦 Hệ Thống Tín Dụng Ngân Hàng")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "➕ Tiếp Nhận Hồ Sơ Mới", 
        "🧮 Công Cụ Tính Toán & Xét Duyệt Nâng Cao",
    ]
)
st.sidebar.info("💡 Số liệu từ mục 'Tiếp nhận' sẽ tự động đồng bộ sang 'Công cụ tính toán'.")

# ==========================================
# 1. TIẾP NHẬN HỒ SƠ MỚI
# ==========================================
if menu == "➕ Tiếp Nhận Hồ Sơ Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Mới")
    st.markdown("Nhập thông tin chi tiết hồ sơ khách hàng theo chuẩn ngân hàng thương mại.")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Thông tin định danh & Tài chính")
            name = st.text_input("Họ và tên khách hàng:", value=st.session_state.form_data["name"])
            phone = st.text_input("Số điện thoại liên hệ:", value=st.session_state.form_data["phone"])
            
            purpose = st.selectbox(
                "Mục đích vay vốn ngân hàng:", 
                [
                    "1. Vay mua bất động sản (Nhà ở, đất ở, căn hộ)",
                    "2. Vay xây dựng, sửa chữa nhà ở",
                    "3. Vay mua phương tiện vận tải (Ô tô kinh doanh/tiêu dùng)",
                    "4. Vay bổ sung vốn lưu động sản xuất kinh doanh ngắn hạn",
                    "5. Vay đầu tư trang thiết bị, máy móc nhà xưởng",
                    "6. Vay tiêu dùng có tài sản bảo đảm / Tiêu dùng tín chấp",
                    "7. Vay du học, khám chữa bệnh, đóng học phí"
                ]
            )
            
            requested_amount = st.number_input(
                "Số tiền yêu cầu vay (VNĐ):", 
                min_value=1000000, 
                value=int(st.session_state.form_data["requested_amount"]), 
                step=10000000, 
                format="%d"
            )
            st.caption(f"👉 Đã chọn: **{requested_amount:,.0f} VNĐ**")
            
            monthly_income = st.number_input(
                "Thu nhập thực nhận hàng tháng (VNĐ):", 
                min_value=0, 
                value=int(st.session_state.form_data["monthly_income"]), 
                step=5000000, 
                format="%d"
            )
            st.caption(f"👉 Đã chọn: **{monthly_income:,.0f} VNĐ**")
            
        with col2:
            st.subheader("🛡️ Tín dụng & Tài sản bảo đảm (TSBD)")
            credit_score = st.slider("Điểm tín dụng CIC / Nội bộ:", min_value=300, max_value=850, value=int(st.session_state.form_data["credit_score"]))
            has_collateral = st.checkbox("Có tài sản thế chấp / cầm cố?", value=bool(st.session_state.form_data["has_collateral"]))
            
            collateral_value = 0
            collateral_type = "Không có tài sản bảo đảm"
            if has_collateral:
                collateral_type = st.selectbox(
                    "Loại tài sản bảo đảm chi tiết:",
                    [
                        "Bất động sản có giấy chứng nhận (Sổ hồng/Sổ đỏ)",
                        "Bất động sản hình thành trong tương lai (Hợp đồng mua bán)",
                        "Phương tiện vận tải (Ô tô con / Ô tô tải có đăng ký)",
                        "Giấy tờ có giá (Sổ tiết kiệm, Trái phiếu, Cổ phiếu niêm yết)",
                        "Máy móc thiết bị, dây chuyền sản xuất",
                        "Hàng hóa tồn kho, nguyên vật liệu",
                        "Quyền tài sản / Khoản phải thu hợp pháp khác"
                    ]
                )
                collateral_value = st.number_input(
                    "Giá trị định giá TSBD của Ngân hàng (VNĐ):", 
                    min_value=0, 
                    value=int(st.session_state.form_data["collateral_value"]), 
                    step=50000000, 
                    format="%d"
                )
                st.caption(f"👉 Đã chọn: **{collateral_value:,.0f} VNĐ**")
            
            notes = st.text_area("Ghi chú thẩm định sơ bộ:", value=st.session_state.form_data["notes"])
            
        submitted = st.form_submit_button("Lưu Hồ Sơ & Chuyển Sang Công Cụ Tính Toán ➔")
        
        if submitted:
            if not name.strip() or not phone.strip():
                st.error("Vui lòng điền đầy đủ Họ tên và Số điện thoại khách hàng!")
            else:
                st.session_state.form_data = {
                    "name": name,
                    "phone": phone,
                    "purpose": purpose,
                    "requested_amount": requested_amount,
                    "monthly_income": monthly_income,
                    "credit_score": credit_score,
                    "has_collateral": has_collateral,
                    "collateral_type": collateral_type,
                    "collateral_value": collateral_value,
                    "notes": notes
                }
                
                new_record = {
                    "id": f"HD-{datetime.datetime.now().strftime('%H%M%S')}",
                    **st.session_state.form_data,
                    "date": str(datetime.date.today()),
                    "status": "Chờ thẩm định"
                }
                st.session_state.history_submissions.append(new_record)
                st.success("🎉 Lưu hồ sơ thành công! Dữ liệu đã được đồng bộ sang công cụ tính toán.")

# ==========================================
# 2. CÔNG CỤ TÍNH TOÁN & XÉT DUYỆT NÂNG CAO
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán & Xét Duyệt Nâng Cao":
    st.title("🧮 Công Cụ Tính Toán Nợ Vay & Phân Tích Rủi Ro Nâng Cao")
    st.info(f"💡 Đang nạp dữ liệu khách hàng: **{st.session_state.form_data['name']}** (Nhu cầu vay: **{st.session_state.form_data['requested_amount']:,.0f} VNĐ**)")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.subheader("📋 Tham số tính toán")
        income = st.number_input("Thu nhập hàng tháng (VNĐ):", value=int(st.session_state.form_data["monthly_income"]), step=5000000, format="%d")
        loan_amount = st.number_input("Số tiền muốn vay (VNĐ):", value=int(st.session_state.form_data["requested_amount"]), step=50000000, format="%d")
        term_months = st.slider("Thời hạn vay (Tháng):", min_value=12, max_value=360, value=60, step=12)
        interest_rate_annual = st.slider("Lãi suất năm (%):", min_value=5.0, max_value=20.0, value=10.0, step=0.5)
        
        repayment_method = st.selectbox(
            "Phương thức trả nợ:",
            ["Dư nợ giảm dần (Gốc trả đều, lãi tính trên dư nợ gốc còn lại)", "Trả góp đều hàng tháng (Gốc + Lãi bằng nhau)"]
        )
        
        st.markdown("---")
        has_col = st.checkbox("Có tài sản thế chấp", value=bool(st.session_state.form_data["has_collateral"]))
        col_val = st.number_input("Giá trị định giá TSBD (VNĐ):", value=int(st.session_state.form_data["collateral_value"]), step=50000000, format="%d")
        
    with col_calc2:
        st.subheader("📊 Kết quả phân tích & Xét duyệt tín dụng")
        
        monthly_rate = (interest_rate_annual / 100) / 12
        
        if "giảm dần" in repayment_method:
            principal_per_month = loan_amount / term_months
            first_month_interest = loan_amount * monthly_rate
            max_monthly_payment = principal_per_month + first_month_interest
            total_interest = (loan_amount * monthly_rate * (term_months + 1)) / 2
            total_payment = loan_amount + total_interest
        else:
            if monthly_rate > 0:
                max_monthly_payment = loan_amount * monthly_rate * ((1 + monthly_rate)**term_months) / (((1 + monthly_rate)**term_months) - 1)
            else:
                max_monthly_payment = loan_amount / term_months
            total_payment = max_monthly_payment * term_months
            total_interest = total_payment - loan_amount
            
        dti_ratio = (max_monthly_payment / income) * 100 if income > 0 else 0
        ltv_ratio = (loan_amount / col_val * 100) if (has_col and col_val > 0) else 0.0
        
        st.metric(label="Số tiền trả tháng đầu cao nhất", value=f"{max_monthly_payment:,.0f} VNĐ")
        st.metric(label="Tổng tiền lãi phải trả suốt thời hạn", value=f"{total_interest:,.0f} VNĐ")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="Tỷ lệ trả nợ / Thu nhập (DTI)", value=f"{dti_ratio:.1f}%", 
                      delta="An toàn (<= 50%)" if dti_ratio <= 50 else "Cao (> 50%)",
                      delta_color="normal" if dti_ratio <= 50 else "inverse")
        with col_m2:
            if has_col:
                st.metric(label="Tỷ lệ Vay / Tài sản (LTV)", value=f"{ltv_ratio:.1f}%",
                          delta="An toàn (<= 70%)" if ltv_ratio <= 70 else "Cao (> 70%)",
                          delta_color="normal" if ltv_ratio <= 70 else "inverse")
            else:
                st.metric(label="Loại hình", value="Tín chấp / Không TSBD")
        
        st.markdown("---")
        dti_pass = dti_ratio <= 50
        ltv_pass = (ltv_ratio <= 70) if has_col else True
        
        if dti_pass and ltv_pass:
            st.success("✅ **ĐÁNH GIÁ:** Hồ sơ **ĐẠT TIÊU CHÍ AN TOÀN** để phê duyệt tín dụng.")
        else:
            st.warning("⚠️ **ĐÁNH GIÁ:** Hồ sơ **CẦN KIỂM SOÁT RỦI RO** (Vượt ngưỡng DTI hoặc LTV tiêu chuẩn).")
