import streamlit as st
import datetime

# --- Cấu hình giao diện ---
st.set_page_config(
    page_title="Hệ Thống Quản Lý & Tính Toán Vốn",
    page_icon="🏦",
    layout="wide"
)

# --- Khởi tạo session_state để lưu trữ dữ liệu thông suốt giữa các mục ---
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "",
        "phone": "",
        "purpose": "Kinh doanh mở rộng xưởng",
        "requested_amount": 400000000,
        "monthly_income": 30000000,
        "credit_score": 700,
        "has_collateral": True,
        "collateral_type": "Bất động sản (Nhà/Đất)",
        "collateral_value": 600000000,
        "notes": ""
    }

if "history_submissions" not in st.session_state:
    st.session_state.history_submissions = []

# --- Menu điều hướng trong Sidebar ---
st.sidebar.title("🏦 Hệ Thống Vốn Tín Dụng")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "➕ Tiếp Nhận Hồ Sơ Mới", 
        "🧮 Công Cụ Tính Toán & Xét Duyệt",
        "🔒 Quản Trị & Danh Sách Hồ Sơ"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 Số liệu từ phần 'Tiếp nhận' sẽ tự động điền sang 'Công cụ tính toán'.")

# ==========================================
# 1. TIẾP NHẬN HỒ SƠ MỚI
# ==========================================
if menu == "➕ Tiếp Nhận Hồ Sơ Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Mới")
    st.markdown("Nhập thông tin khách hàng. Khi bấm **Lưu**, dữ liệu sẽ được tự động đưa sang công cụ tính toán và lưu vào hệ thống.")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Thông tin khách hàng")
            name = st.text_input("Họ và tên khách hàng:", value=st.session_state.form_data["name"])
            phone = st.text_input("Số điện thoại:", value=st.session_state.form_data["phone"])
            purpose = st.selectbox(
                "Mục đích vay vốn:", 
                ["Kinh doanh mở rộng xưởng", "Mua sắm trang thiết bị", "Đầu tư lưu động ngắn hạn", "Tiêu dùng cá nhân / Sửa nhà", "Khác"],
                index=0
            )
            requested_amount = st.number_input("Số tiền yêu cầu vay (VNĐ):", min_value=1000000, value=int(st.session_state.form_data["requested_amount"]), step=50000000, format="%d")
            monthly_income = st.number_input("Thu nhập hàng tháng (VNĐ):", min_value=0, value=int(st.session_state.form_data["monthly_income"]), step=5000000, format="%d")
            
        with col2:
            st.subheader("🛡️ Tài sản thế chấp & Tín dụng")
            credit_score = st.slider("Điểm tín dụng CIC:", min_value=300, max_value=850, value=int(st.session_state.form_data["credit_score"]))
            has_collateral = st.checkbox("Có tài sản thế chấp / cầm cố?", value=bool(st.session_state.form_data["has_collateral"]))
            
            collateral_value = 0
            collateral_type = "Không có"
            if has_collateral:
                collateral_type = st.selectbox(
                    "Loại tài sản bảo đảm:",
                    ["Bất động sản (Nhà/Đất)", "Phương tiện vận tải (Ô tô/Xe máy)", "Giấy tờ có giá (Sổ tiết kiệm, Cổ phiếu)"]
                )
                collateral_value = st.number_input("Giá trị định giá tài sản (VNĐ):", min_value=0, value=int(st.session_state.form_data["collateral_value"]), step=50000000, format="%d")
            
            notes = st.text_area("Ghi chú hồ sơ:", value=st.session_state.form_data["notes"])
            
        submitted = st.form_submit_button("Lưu & Chuyển sang Công Cụ Tính Toán ➔")
        
        if submitted:
            if not name.strip() or not phone.strip():
                st.error("Vui lòng điền đầy đủ Họ tên và Số điện thoại!")
            else:
                # Cập nhật dữ liệu vào session_state để qua trang tính toán nó tự điền vào
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
                
                # Lưu vào danh sách lịch sử chung
                new_record = {
                    "id": f"HD-{datetime.datetime.now().strftime('%H%M%S')}",
                    **st.session_state.form_data,
                    "date": str(datetime.date.today()),
                    "status": "Chờ thẩm định"
                }
                st.session_state.history_submissions.append(new_record)
                
                st.success("🎉 Đã lưu thông tin thành công! Bạn có thể bấm sang mục **'Công Cụ Tính Toán & Xét Duyệt'** ở menu bên trái để thấy số liệu đã tự nhảy qua.")

# ==========================================
# 2. CÔNG CỤ TÍNH TOÁN & XÉT DUYỆT (TỰ ĐỘNG NHẬN DỮ LIỆU TỪ MỤC 1)
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán & Xét Duyệt":
    st.title("🧮 Công Cụ Tính Toán Nợ Vay & Xét Duyệt Hạn Mức")
    st.info(f"💡 Đang nạp dữ liệu của khách hàng: **{st.session_state.form_data['name'] if st.session_state.form_data['name'] else 'Chưa có tên (Đang dùng số liệu mặc định)'}**")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.subheader("📋 Tham số tính toán (Đã lấy từ hồ sơ)")
        # Lấy trực tiếp từ st.session_state.form_data đã nhập ở phần 1
        income = st.number_input("Thu nhập hàng tháng (VNĐ):", value=int(st.session_state.form_data["monthly_income"]), step=5000000, format="%d")
        loan_amount = st.number_input("Số tiền muốn vay (VNĐ):", value=int(st.session_state.form_data["requested_amount"]), step=50000000, format="%d")
        term_months = st.slider("Thời hạn vay (Tháng):", min_value=12, max_value=360, value=60, step=12)
        interest_rate_annual = st.slider("Lãi suất năm (%):", min_value=6.0, max_value=18.0, value=10.5, step=0.5)
        
        st.markdown("---")
        has_col = st.checkbox("Có tài sản thế chấp", value=bool(st.session_state.form_data["has_collateral"]))
        col_val = st.number_input("Giá trị định giá TSBD (VNĐ):", value=int(st.session_state.form_data["collateral_value"]), step=50000000, format="%d")
        
    with col_calc2:
        st.subheader("📊 Kết quả xét duyệt & Phân tích rủi ro")
        
        monthly_rate = (interest_rate_annual / 100) / 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * monthly_rate * ((1 + monthly_rate)**term_months) / (((1 + monthly_rate)**term_months) - 1)
        else:
            monthly_payment = loan_amount / term_months
            
        dti_ratio = (monthly_payment / income) * 100 if income > 0 else 0
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
        if dti_ratio <= 50 and (not has_col or ltv_ratio <= 70):
            st.success("✅ **KẾT LUẬN:** Hồ sơ **ĐẠT TIÊU CHÍ** cho vay an toàn.")
        else:
            st.warning("⚠️ **KẾT LUẬN:** Hồ sơ có rủi ro, **CẦN XEM XÉT THÊM** hoặc bổ sung tài sản.")
