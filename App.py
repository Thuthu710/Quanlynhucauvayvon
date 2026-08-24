import streamlit as st
import datetime
import pandas as pd

# --- Cấu hình giao diện ---
st.set_page_config(
    page_title="Hệ Thống Quản Lý & Thẩm Định Vốn Ngân Hàng",
    page_icon="🏦",
    layout="wide"
)

# --- Khởi tạo session_state ---
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "",
        "phone": "",
        "purpose": "Vay bổ sung vốn lưu động sản xuất kinh doanh ngắn hạn",
        "requested_amount": 500000000,
        "monthly_income": 35000000,
        "credit_score": 720,
        "has_collateral": True,
        "collateral_type": "Bất động sản (Nhà ở / Đất ở thổ cư)",
        "collateral_value": 1000000000,
        "notes": ""
    }

if "history_submissions" not in st.session_state:
    st.session_state.history_submissions = []

# --- Menu điều hướng ---
st.sidebar.title("🏦 Hệ Thống Tín Dụng Ngân Hàng")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "➕ Tiếp Nhận Hồ Sơ Mới", 
        "🧮 Công Cụ Tính Toán & Xét Duyệt Chuyên Sâu",
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 Số liệu từ phần 'Tiếp nhận' sẽ tự động đồng bộ sang 'Công cụ tính toán và xét duyệt'.")

# ==========================================
# 1. TIẾP NHẬN HỒ SƠ MỚI
# ==========================================
if menu == "➕ Tiếp Nhận Hồ Sơ Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Khách Hàng")
    st.markdown("Nhập liệu thông tin khách hàng và tài sản đảm bảo theo tiêu chuẩn ngân hàng.")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Thông tin định danh & Khách hàng")
            name = st.text_input("Họ và tên khách hàng:", value=st.session_state.form_data["name"], placeholder="Ví dụ: Nguyễn Văn A")
            phone = st.text_input("Số điện thoại liên hệ:", value=st.session_state.form_data["phone"], placeholder="Ví dụ: 0912345678")
            
            # Phân tách mục đích vay vốn chuẩn ngân hàng
            purpose = st.selectbox(
                "Mục đích vay vốn chi tiết:", 
                [
                    "Vay bổ sung vốn lưu động sản xuất kinh doanh ngắn hạn",
                    "Vay đầu tư tài sản cố định / Mở rộng nhà xưởng, máy móc",
                    "Vay mua bất động sản (Nhà ở, đất ở, căn hộ dự án)",
                    "Vay xây dựng, sửa chữa nhà cửa / Bất động sản tiêu dùng",
                    "Vay mua phương tiện vận tải (Ô tô kinh doanh / Ô tô cá nhân)",
                    "Vay tiêu dùng có tài sản đảm bảo / Tiêu dùng không tài sản",
                    "Vay đầu tư nông nghiệp, nông thôn / Chăn nuôi, trồng trọt",
                    "Vay cầm cố giấy tờ có giá / Sổ tiết kiệm thanh khoản nhanh"
                ]
            )
            
            requested_amount = st.number_input(
                "Số tiền yêu cầu vay (VNĐ):", 
                min_value=1000000, 
                value=int(st.session_state.form_data["requested_amount"]), 
                step=10000000, 
                format="%d"
            )
            st.caption(f"✍️ Số tiền hiển thị: **{requested_amount:,.0f} VNĐ**")
            
            monthly_income = st.number_input(
                "Thu nhập thực tế hàng tháng của KH (VNĐ):", 
                min_value=0, 
                value=int(st.session_state.form_data["monthly_income"]), 
                step=5000000, 
                format="%d"
            )
            st.caption(f"✍️ Thu nhập hiển thị: **{monthly_income:,.0f} VNĐ**")
            
        with col2:
            st.subheader("🛡️ Tín dụng & Tài sản bảo đảm (TSBD)")
            credit_score = st.slider("Điểm tín dụng CIC / Lịch sử tín dụng:", min_value=300, max_value=850, value=int(st.session_state.form_data["credit_score"]))
            has_collateral = st.checkbox("Khách hàng có Tài sản bảo đảm (TSBD)?", value=bool(st.session_state.form_data["has_collateral"]))
            
            collateral_value = 0
            collateral_type = "Không có tài sản đảm bảo (Tín chấp)"
            
            if has_collateral:
                # Mở rộng đa dạng loại tài sản đảm bảo
                collateral_type = st.selectbox(
                    "Loại tài sản bảo đảm phong phú:",
                    [
                        "Bất động sản (Nhà ở / Đất ở thổ cư)",
                        "Bất động sản thương mại / Đất dự án / Đất công nghiệp",
                        "Phương tiện vận tải (Ô tô con / Ô tô tải / Xe chuyên dụng)",
                        "Máy móc thiết bị / Dây chuyền sản xuất công nghiệp",
                        "Hàng hóa tồn kho luân chuyển / Nguyên vật liệu",
                        "Giấy tờ có giá (Sổ tiết kiệm ngân hàng, Trái phiếu doanh nghiệp, Cổ phiếu niêm yết)",
                        "Quyền tài sản phát sinh từ hợp đồng mua bán / Hợp đồng nhượng quyền",
                        "Tài sản hình thành trong tương lai từ vốn vay"
                    ]
                )
                collateral_value = st.number_input(
                    "Giá trị định giá chính thức của TSBD (VNĐ):", 
                    min_value=0, 
                    value=int(st.session_state.form_data["collateral_value"]), 
                    step=50000000, 
                    format="%d"
                )
                st.caption(f"✍️ Giá trị TSBD hiển thị: **{collateral_value:,.0f} VNĐ**")
            
            notes = st.text_area("Ghi chú bổ sung hồ sơ:", value=st.session_state.form_data["notes"], placeholder="Đánh giá sơ bộ nguồn thu, lịch sử trả nợ...")
            
        submitted = st.form_submit_button("Lưu & Đồng Bộ Sang Công Cụ Tính Toán ➔")
        
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
                
                st.success("🎉 Lưu hồ sơ thành công! Dữ liệu đã tự động đồng bộ sang mục **'Công Cụ Tính Toán & Xét Duyệt Chuyên Sâu'**.")

# ==========================================
# 2. CÔNG CỤ TÍNH TOÁN & XÉT DUYỆT CHUYÊN SÂU
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán & Xét Duyệt Chuyên Sâu":
    st.title("🧮 Công Cụ Mô Phỏng Dòng Tiền, Trả Nợ & Thẩm Định Tín Dụng")
    
    current_name = st.session_state.form_data['name'] if st.session_state.form_data['name'] else 'Khách hàng mẫu (Chưa nhập tên)'
    st.info(f"💡 Đang nạp dữ liệu tự động từ hồ sơ: **{current_name}** | Mục đích: *{st.session_state.form_data['purpose']}*")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.subheader("📋 Tham số đầu vào phân tích")
        
        income = st.number_input("Thu nhập hàng tháng (VNĐ):", value=int(st.session_state.form_data["monthly_income"]), step=5000000, format="%d")
        st.caption(f"Định dạng: **{income:,.0f} VNĐ**")
        
        loan_amount = st.number_input("Số tiền đề xuất cho vay (VNĐ):", value=int(st.session_state.form_data["requested_amount"]), step=10000000, format="%d")
        st.caption(f"Định dạng: **{loan_amount:,.0f} VNĐ**")
        
        term_months = st.slider("Thời hạn cho vay (Tháng):", min_value=12, max_value=360, value=60, step=12)
        interest_rate_annual = st.slider("Lãi suất cho vay (%/năm):", min_value=6.0, max_value=18.0, value=10.0, step=0.5)
        
        # Bổ sung thêm các yếu tố nâng cao chuyên ngành ngân hàng
        repayment_method = st.selectbox(
            "Phương thức trả nợ:",
            ["Trả góp đều hàng tháng (Gốc + Lãi hàng tháng bằng nhau)", "Trả gốc đều hàng tháng + Lãi giảm dần trên dư nợ gốc thực tế"]
        )
        
        grace_period = st.selectbox("Thời gian ân hạn gốc (Miễn trả gốc ban đầu):", [0, 3, 6, 12])
        
        st.markdown("---")
        st.subheader("🛡️ Thẩm Định Tài Sản Bảo Đảm (TSBD)")
        has_col = st.checkbox("Có tài sản thế chấp", value=bool(st.session_state.form_data["has_collateral"]))
        col_val = st.number_input("Giá trị định giá TSBD (VNĐ):", value=int(st.session_state.form_data["collateral_value"]), step=50000000, format="%d")
        st.caption(f"Định dạng: **{col_val:,.0f} VNĐ**")
        
    with col_calc2:
        st.subheader("📊 Kết quả phân tích tài chính & Rủi ro")
        
        # Tính toán chi tiết dựa trên phương thức
        effective_term = term_months - grace_period if term_months > grace_period else term_months
        monthly_rate = (interest_rate_annual / 100) / 12
        
        if repayment_method.startswith("Trả góp đều"):
            if monthly_rate > 0 and effective_term > 0:
                monthly_payment = loan_amount * monthly_rate * ((1 + monthly_rate)**effective_term) / (((1 + monthly_rate)**effective_term) - 1)
            else:
                monthly_payment = loan_amount / (effective_term if effective_term > 0 else 1)
            max_monthly_payment = monthly_payment
            total_interest = (monthly_payment * effective_term) - loan_amount
        else:
            # Gốc đều + Lãi giảm dần tháng đầu cao nhất
            principal_per_month = loan_amount / (effective_term if effective_term > 0 else 1)
            first_month_interest = loan_amount * monthly_rate
            max_monthly_payment = principal_per_month + first_month_interest
            # Ước tính tổng lãi xấp xỉ
            total_interest = (loan_amount * monthly_rate * (effective_term + 1)) / 2
            
        total_payment = loan_amount + total_interest
        dti_ratio = (max_monthly_payment / income) * 100 if income > 0 else 0
        ltv_ratio = (loan_amount / col_val * 100) if (has_col and col_val > 0) else 100.0
        
        # Hiển thị các chỉ số cốt lõi
        st.metric(label="Đỉnh điểm Nghĩa vụ trả nợ hàng tháng", value=f"{max_monthly_payment:,.0f} VNĐ")
        st.metric(
            label="Tỷ lệ Trả nợ / Thu nhập (DTI - Debt to Income)", 
            value=f"{dti_ratio:.1f}%", 
            delta="An toàn (<= 50% thu nhập)" if dti_ratio <= 50 else "Rủi ro cao (> 50% thu nhập)",
            delta_color="normal" if dti_ratio <= 50 else "inverse"
        )
        
        if has_col:
            st.metric(
                label="Tỷ lệ Cho vay / Giá trị TSBD (LTV - Loan to Value)", 
                value=f"{ltv_ratio:.1f}%",
                delta="An toàn (<= 70% giá trị TS)" if ltv_ratio <= 70 else "Vượt ngưỡng thông thường (> 70%)",
                delta_color="normal" if ltv_ratio <= 70 else "inverse"
            )
            
        st.metric(label="Tổng tiền lãi dự kiến suốt thời hạn", value=f"{total_interest:,.0f} VNĐ")
        st.metric(label="Tổng số tiền phải trả (Gốc + Lãi)", value=f"{total_payment:,.0f} VNĐ")
        
        st.markdown("---")
        # Đánh giá kết luận tự động
        dti_pass = dti_ratio <= 50
        ltv_pass = (ltv_ratio <= 70) if has_col else True
        
        if dti_pass and ltv_pass:
            st.success("✅ **ĐÁNH GIÁ CHUYÊN GIA:** Hồ sơ **ĐẠT CHUẨN AN TOÀN**, đủ điều kiện phê duyệt cấp tín dụng.")
        elif not dti_pass and not ltv_pass:
            st.error("❌ **ĐÁNH GIÁ CHUYÊN GIA:** Hồ sơ **RỦI RO CAO** (Cả DTI và LTV đều vượt ngưỡng an toàn chuẩn mực ngân hàng).")
        else:
            st.warning("⚠️ **ĐÁNH GIÁ CHUYÊN GIA:** Hồ sơ **CẦN XEM XÉT THÊM** (Cần giải trình thêm nguồn thu phụ hoặc bổ sung TSBD).")
