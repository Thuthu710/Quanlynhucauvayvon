import streamlit as st
import datetime
import pandas as pd

# --- Cấu hình giao diện ---
st.set_page_config(
    page_title="Hệ Thống Quản Lý & Tính Toán Vốn Ngân Hàng",
    page_icon="🏦",
    layout="wide"
)

# --- Khởi tạo session_state ---
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "",
        "phone": "",
        "category": "Khách hàng cá nhân",
        "purpose": "Mua nhà ở, đất ở (có hình thành tài sản)",
        "requested_amount": 500000000,
        "monthly_income": 30000000,
        "credit_score": 720,
        "has_collateral": True,
        "collateral_type": "Bất động sản (Nhà ở, Đất ở, Đất nông nghiệp)",
        "collateral_value": 1000000000,
        "notes": ""
    }

if "history_submissions" not in st.session_state:
    st.session_state.history_submissions = []

# --- Sidebar Điều Hướng ---
st.sidebar.title("🏦 Hệ Thống Tín Dụng Ngân Hàng")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "➕ Tiếp Nhận Hồ Sơ Mới", 
        "🧮 Công Cụ Tính Toán & Xét Duyệt Nâng Cao",
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 Dữ liệu nhập từ phần 'Tiếp Nhận' sẽ tự động truyền sang 'Công Cụ Tính Toán'.")

# ==========================================
# 1. TIẾP NHẬN HỒ SƠ MỚI
# ==========================================
if menu == "➕ Tiếp Nhận Hồ Sơ Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Ngân Hàng")
    st.markdown("Nhập thông tin chi tiết khách hàng và tài sản bảo đảm theo chuẩn thẩm định ngân hàng.")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Thông tin khách hàng & Nhu cầu")
            name = st.text_input("Họ và tên khách hàng:", value=st.session_state.form_data["name"], placeholder="Ví dụ: Nguyễn Văn A")
            phone = st.text_input("Số điện thoại liên hệ:", value=st.session_state.form_data["phone"], placeholder="Ví dụ: 0912xxxxxx")
            
            category = st.selectbox(
                "Phân khúc khách hàng:",
                ["Khách hàng cá nhân", "Khách hàng doanh nghiệp / Hộ kinh doanh"],
                index=0 if st.session_state.form_data["category"] == "Khách hàng cá nhân" else 1
            )
            
            # Phân tách mục đích vay vốn chuẩn ngân hàng
            if category == "Khách hàng cá nhân":
                purpose_options = [
                    "Mua nhà ở, đất ở, căn hộ chung cư",
                    "Xây dựng, sửa chữa nhà cửa",
                    "Mua sắm phương tiện đi lại (Ô tô tiêu dùng)",
                    "Vay tiêu dùng có tài sản bảo đảm",
                    "Vay sản xuất kinh doanh cá thể / Hộ gia đình"
                ]
            else:
                purpose_options = [
                    "Bổ sung vốn lưu động ngắn hạn (Sản xuất/Thương mại)",
                    "Đầu tư tài sản cố định (Mua máy móc, thiết bị, xưởng)",
                    "Tài trợ dự án đầu tư mở rộng quy mô",
                    "Phát hành bảo lãnh / L/C thanh toán quốc tế"
                ]
                
            purpose = st.selectbox("Mục đích vay vốn chi tiết:", purpose_options)
            
            # Số tiền vay có định dạng hiển thị phân cách hàng nghìn giúp dễ đọc
            requested_amount = st.number_input(
                "Số tiền yêu cầu vay (VNĐ):", 
                min_value=1000000, 
                value=int(st.session_state.form_data["requested_amount"]), 
                step=10000000, 
                format="%d"
            )
            st.caption(f"👉 Đọc là: **{requested_amount:,.0f} VNĐ**")
            
            monthly_income = st.number_input(
                "Thu nhập / Lợi nhuận hàng tháng (VNĐ):", 
                min_value=0, 
                value=int(st.session_state.form_data["monthly_income"]), 
                step=5000000, 
                format="%d"
            )
            st.caption(f"👉 Đọc là: **{monthly_income:,.0f} VNĐ**")
            
        with col2:
            st.subheader("🛡️ Tín dụng & Tài sản bảo đảm (TSBD)")
            credit_score = st.slider("Điểm tín dụng CIC / Lịch sử tín dụng:", min_value=300, max_value=850, value=int(st.session_state.form_data["credit_score"]))
            
            has_collateral = st.checkbox("Khách hàng có Tài sản bảo đảm?", value=bool(st.session_state.form_data["has_collateral"]))
            
            collateral_value = 0
            collateral_type = "Không có tài sản bảo đảm"
            
            if has_collateral:
                # Mở rộng các loại tài sản bảo đảm nhiều loại lên
                collateral_type = st.selectbox(
                    "Loại tài sản bảo đảm:",
                    [
                        "Bất động sản (Nhà ở, Đất ở, Đất nông nghiệp/Lâm nghiệp)",
                        "Phương tiện vận tải (Ô tô con, Ô tô tải, Xe chuyên dụng)",
                        "Máy móc thiết bị, dây chuyền sản xuất",
                        "Hàng hóa tồn kho, nguyên vật liệu luân chuyển",
                        "Giấy tờ có giá (Sổ tiết kiệm, Trái phiếu, Cổ phiếu niêm yết)",
                        "Quyền tài sản phát sinh từ hợp đồng/Dự án đầu tư"
                    ]
                )
                collateral_value = st.number_input(
                    "Giá trị định giá tài sản bảo đảm (VNĐ):", 
                    min_value=0, 
                    value=int(st.session_state.form_data["collateral_value"]), 
                    step=50000000, 
                    format="%d"
                )
                st.caption(f"👉 Đọc là: **{collateral_value:,.0f} VNĐ**")
            
            notes = st.text_area("Ghi chú hồ sơ sơ bộ từ giao dịch viên:", value=st.session_state.form_data["notes"])
            
        submitted = st.form_submit_button("Lưu & Chuyển sang Công Cụ Tính Toán Nâng Cao ➔")
        
        if submitted:
            if not name.strip() or not phone.strip():
                st.error("Vui lòng điền đầy đủ Họ tên và Số điện thoại khách hàng!")
            else:
                st.session_state.form_data = {
                    "name": name,
                    "phone": phone,
                    "category": category,
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
                    "id": f"HB-{datetime.datetime.now().strftime('%H%M%S')}",
                    **st.session_state.form_data,
                    "date": str(datetime.date.today()),
                    "status": "Chờ thẩm định"
                }
                st.session_state.history_submissions.append(new_record)
                st.success("🎉 Lưu thông tin thành công! Số liệu đã được đồng bộ sang **'Công Cụ Tính Toán & Xét Duyệt Nâng Cao'**.")

# ==========================================
# 2. CÔNG CỤ TÍNH TOÁN & XÉT DUYỆT NÂNG CAO
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán & Xét Duyệt Nâng Cao":
    st.title("🧮 Công Cụ Tính Toán Nợ Vay & Đánh Giá Rủi Ro Chuyên Sâu")
    
    current_name = st.session_state.form_data['name']
    if current_name:
        st.info(f"💡 Đang nạp dữ liệu tự động của khách hàng: **{current_name}** | Mục đích: **{st.session_state.form_data['purpose']}**")
    else:
        st.warning("⚠️ Chưa có hồ sơ nào được truyền từ mục Tiếp Nhận. Đang hiển thị số liệu mặc định, bạn có thể chỉnh sửa trực tiếp bên dưới.")

    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("⚙️ Điều chỉnh thông số khoản vay")
        
        loan_amount = st.number_input(
            "Số tiền vay đề xuất (VNĐ):", 
            value=int(st.session_state.form_data["requested_amount"]), 
            step=20000000, 
            format="%d"
        )
        st.caption(f"Số tiền: {loan_amount:,.0f} VNĐ")
        
        term_months = st.slider("Thời hạn vay (Tháng):", min_value=12, max_value=360, value=60, step=12)
        
        interest_rate_annual = st.slider("Lãi suất cho vay (%/năm):", min_value=5.0, max_value=18.0, value=10.0, step=0.5)
        
        repayment_method = st.selectbox(
            "Phương thức trả nợ gốc:",
            ["Trả góp đều hàng tháng (Gốc + Lãi chia đều)", "Trả gốc đều hàng tháng + Lãi giảm dần trên dư nợ thực tế"]
        )
        
        income = st.number_input(
            "Thu nhập hàng tháng thực tế của KH (VNĐ):", 
            value=int(st.session_state.form_data["monthly_income"]), 
            step=5000000, 
            format="%d"
        )
        
        has_col = st.checkbox("Có tài sản bảo đảm", value=bool(st.session_state.form_data["has_collateral"]))
        col_val = st.number_input(
            "Giá trị định giá TSBD thực tế (VNĐ):", 
            value=int(st.session_state.form_data["collateral_value"]), 
            step=50000000, 
            format="%d"
        )
        
    with col_c2:
        st.subheader("📊 Kết quả phân tích chỉ số tài chính & Rủi ro")
        
        # Tính toán chi tiết
        monthly_rate = (interest_rate_annual / 100) / 12
        
        if repayment_method.startswith("Trả góp đều"):
            if monthly_rate > 0:
                first_payment = loan_amount * monthly_rate * ((1 + monthly_rate)**term_months) / (((1 + monthly_rate)**term_months) - 1)
            else:
                first_payment = loan_amount / term_months
            max_monthly_payment = first_payment
            total_payment = first_payment * term_months
            total_interest = total_payment - loan_amount
        else:
            # Gốc đều hàng tháng + lãi giảm dần
            principal_per_month = loan_amount / term_months
            first_month_interest = loan_amount * monthly_rate
            max_monthly_payment = principal_per_month + first_month_interest
            
            last_month_interest = principal_per_month * monthly_rate
            min_monthly_payment = principal_per_month + last_month_interest
            total_interest = (loan_amount + principal_per_month) * monthly_rate * term_months / 2 # xấp xỉ tổng lãi
            total_payment = loan_amount + total_interest

        # Các chỉ số quan trọng ngân hàng
        dti_ratio = (max_monthly_payment / income) * 100 if income > 0 else 0
        ltv_ratio = (loan_amount / col_val * 100) if (has_col and col_val > 0) else 100.0
        
        # Hiển thị các metric chuyên nghiệp
        st.metric(
            label="Số tiền trả tháng cao nhất (Gốc + Lãi)", 
            value=f"{max_monthly_payment:,.0f} VNĐ"
        )
        st.metric(
            label="Tổng tiền lãi dự kiến phải trả", 
            value=f"{total_interest:,.0f} VNĐ"
        )
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(
                label="Tỷ lệ trả nợ / Thu nhập (DTI)", 
                value=f"{dti_ratio:.1f}%",
                delta="An toàn (<= 50%)" if dti_ratio <= 50 else "Vượt ngưỡng (> 50%)",
                delta_color="normal" if dti_ratio <= 50 else "inverse"
            )
        with col_m2:
            if has_col:
                st.metric(
                    label="Tỷ lệ Vay / Tài sản (LTV)", 
                    value=f"{ltv_ratio:.1f}%",
                    delta="An toàn (<= 70%)" if ltv_ratio <= 70 else "Cao (> 70%)",
                    delta_color="normal" if ltv_ratio <= 70 else "inverse"
                )
            else:
                st.metric(label="Tỷ lệ Vay / Tài sản (LTV)", value="Không có TSBD")
        
        st.markdown("---")
        st.subheader("🔍 Đánh giá và Khuyến nghị tín dụng")
        
        # Thêm yếu tố kiểm tra biên độ chịu đựng rủi ro lãi suất tăng 2%
        stress_rate = interest_rate_annual + 2.0
        stress_monthly_payment = max_monthly_payment * (stress_rate / interest_rate_annual) if interest_rate_annual > 0 else max_monthly_payment
        stress_dti = (stress_monthly_payment / income) * 100 if income > 0 else 0
        
        st.write(f"📉 **Kiểm tra sức chịu đựng (Stress Test khi lãi suất tăng +2%):** DTI sẽ dịch chuyển lên mức **{stress_dti:.1f}%**.")
        
        if dti_ratio <= 50 and (not has_col or ltv_ratio <= 75):
            st.success("✅ **KẾT LUẬN:** Hồ sơ **ĐẠT TIÊU CHÍ AN TOÀN**, đủ điều kiện trình cấp có thẩm quyền phê duyệt.")
        elif dti_ratio > 70 or (has_col and ltv_ratio > 90):
            st.error("❌ **KẾT LUẬN:** Hồ sơ **RỦI RO CAO**, từ chối hoặc yêu cầu bổ sung tài sản/giảm số tiền vay.")
        else:
            st.warning("⚠️ **KẾT LUẬN:** Hồ sơ **CẦN KIỂM SOÁT THÊM** (Cần bổ sung cam kết thu nhập phụ hoặc bảo lãnh người thứ ba).")
