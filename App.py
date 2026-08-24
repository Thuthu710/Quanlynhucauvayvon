import streamlit as st
import datetime
import pandas as pd
import pymysql

# --- Cấu hình giao diện ---
st.set_page_config(
    page_title="Hệ Thống Quản Lý & Tính Toán Vốn Tín Dụng",
    page_icon="🏦",
    layout="wide"
)

# --- Khởi tạo kết nối MySQL & Tạo bảng nếu chưa có ---
def get_connection():
    conn = pymysql.connect(
        host="mysql-11a8761d-dlu-47b.a.aivencloud.com",
        port=27162,
        user="avnadmin",
        password="AVNS_6ykmeDg6U2dI2gt_hX5",
        database="managecapital",
        ssl={"ca": "ca.pem"},
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dangky_vayvon (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255),
                phone VARCHAR(50),
                purpose TEXT,
                requested_amount DECIMAL(18,2),
                monthly_income DECIMAL(18,2),
                credit_score INT,
                has_collateral TINYINT(1),
                collateral_type VARCHAR(255),
                collateral_value DECIMAL(18,2),
                notes TEXT,
                date VARCHAR(50),
                status VARCHAR(50)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Lỗi khởi tạo bảng MySQL: {e}")

init_db()

# --- Khởi tạo session_state ---
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "",
        "phone": "",
        "purpose": "1. Vay mua bất động sản (Nhà ở, đất ở)",
        "requested_amount": 10000000,   # Giá trị khởi điểm tối thiểu để không bị lỗi số 0
        "monthly_income": 0,
        "credit_score": 0,
        "has_collateral": True,
        "collateral_type": "Bất động sản có giấy chứng nhận (Sổ hồng/Sổ đỏ)",
        "collateral_value": 0,
        "notes": ""
    }

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
st.sidebar.info("💡 Điền thông tin bên Tiếp nhận, sau đó sang Công cụ tính toán để đánh giá rủi ro và lưu hồ sơ lên hệ thống khi đạt chuẩn.")

# ==========================================
# 1. TIẾP NHẬN HỒ SƠ MỚI
# ==========================================
if menu == "➕ Tiếp Nhận Hồ Sơ Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Mới")
    st.markdown("Nhập thông tin chi tiết hồ sơ khách hàng theo chuẩn ngân hàng thương mại. Dữ liệu sẽ tự động đồng bộ sang công cụ tính toán.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Thông tin định danh & Tài chính")
        
        st.session_state.form_data["name"] = st.text_input(
            "Họ và tên khách hàng:", 
            value=st.session_state.form_data["name"]
        )
        
        st.session_state.form_data["phone"] = st.text_input(
            "Số điện thoại liên hệ:", 
            value=st.session_state.form_data["phone"]
        )
        
        purposes_list = [
            "1. Vay mua bất động sản (Nhà ở, đất ở, căn hộ)",
            "2. Vay xây dựng, sửa chữa nhà ở",
            "3. Vay mua phương tiện vận tải (Ô tô kinh doanh/tiêu dùng)",
            "4. Vay bổ sung vốn lưu động sản xuất kinh doanh ngắn hạn",
            "5. Vay đầu tư trang thiết bị, máy móc nhà xưởng",
            "6. Vay tiêu dùng có tài sản bảo đảm / Tiêu dùng tín chấp",
            "7. Vay du học, khám chữa bệnh, đóng học phí"
        ]
        curr_purpose = st.session_state.form_data["purpose"]
        idx_p = purposes_list.index(curr_purpose) if curr_purpose in purposes_list else 0
        
        st.session_state.form_data["purpose"] = st.selectbox(
            "Mục đích vay vốn ngân hàng:", 
            purposes_list,
            index=idx_p
        )
        
        st.session_state.form_data["requested_amount"] = st.number_input(
            "Số tiền yêu cầu vay (VNĐ):", 
            min_value=1000000, 
            value=int(st.session_state.form_data["requested_amount"]), 
            step=10000000, 
            format="%d"
        )
        st.caption(f"👉 Giá trị hiện tại: **{st.session_state.form_data['requested_amount']:,.0f} VNĐ**")
        
        st.session_state.form_data["monthly_income"] = st.number_input(
            "Thu nhập thực nhận hàng tháng (VNĐ):", 
            min_value=0, 
            value=int(st.session_state.form_data["monthly_income"]), 
            step=5000000, 
            format="%d"
        )
        st.caption(f"👉 Giá trị hiện tại: **{st.session_state.form_data['monthly_income']:,.0f} VNĐ**")
        
    with col2:
        st.subheader("🛡️ Tín dụng & Tài sản bảo đảm (TSBD)")
        
        st.session_state.form_data["credit_score"] = st.slider(
            "Điểm tín dụng CIC / Nội bộ:", 
            min_value=300, 
            max_value=850, 
            value=int(st.session_state.form_data["credit_score"])
        )
        
        st.session_state.form_data["has_collateral"] = st.checkbox(
            "Có tài sản thế chấp / cầm cố?", 
            value=bool(st.session_state.form_data["has_collateral"])
        )
        
        if st.session_state.form_data["has_collateral"]:
            collateral_options = [
                "Bất động sản có giấy chứng nhận (Sổ hồng/Sổ đỏ)",
                "Bất động sản hình thành trong tương lai (Hợp đồng mua bán)",
                "Phương tiện vận tải (Ô tô con / Ô tô tải có đăng ký)",
                "Giấy tờ có giá (Sổ tiết kiệm, Trái phiếu, Cổ phiếu niêm yết)",
                "Máy móc thiết bị, dây chuyền sản xuất",
                "Hàng hóa tồn kho, nguyên vật liệu",
                "Quyền tài sản / Khoản phải thu hợp pháp khác"
            ]
            curr_col_type = st.session_state.form_data["collateral_type"]
            idx_c = collateral_options.index(curr_col_type) if curr_col_type in collateral_options else 0
            
            st.session_state.form_data["collateral_type"] = st.selectbox(
                "Loại tài sản bảo đảm chi tiết:",
                collateral_options,
                index=idx_c
            )
            
            st.session_state.form_data["collateral_value"] = st.number_input(
                "Giá trị định giá TSBD của Ngân hàng (VNĐ):", 
                min_value=0, 
                value=int(st.session_state.form_data["collateral_value"]), 
                step=50000000, 
                format="%d"
            )
            st.caption(f"👉 Giá trị hiện tại: **{st.session_state.form_data['collateral_value']:,.0f} VNĐ**")
        else:
            st.session_state.form_data["collateral_type"] = "Không có tài sản bảo đảm"
            st.session_state.form_data["collateral_value"] = 0
        
        st.session_state.form_data["notes"] = st.text_area(
            "Ghi chú thẩm định sơ bộ:", 
            value=st.session_state.form_data["notes"]
        )
    
    st.info("💡 Bạn hãy chuyển sang mục **'Công Cụ Tính Toán & Xét Duyệt Nâng Cao'** ở thanh menu bên trái để thực hiện phân tích rủi ro và lưu hồ sơ lên hệ thống quản trị.")

# ==========================================
# 2. CÔNG CỤ TÍNH TOÁN & XÉT DUYỆT NÂNG CAO
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán & Xét Duyệt Nâng Cao":
    st.title("🧮 Công Cụ Tính Toán Nợ Vay & Phân Tích Rủi Ro Nâng Cao")
    st.info(f"💡 Đang nạp dữ liệu khách hàng: **{st.session_state.form_data['name']}**")
    
    col_c1, col_c2 = st.columns([1, 1])
    
    with col_c1:
        st.subheader("⚙️ Điều chỉnh tham số vay")
        income = st.number_input("Thu nhập hàng tháng (VNĐ):", value=int(st.session_state.form_data["monthly_income"]), step=5000000, format="%d")
        loan_amount = st.number_input("Số tiền muốn vay (VNĐ):", value=int(st.session_state.form_data["requested_amount"]), step=50000000, format="%d")
        term_months = st.slider("Thời hạn vay (Tháng):", min_value=12, max_value=360, value=60, step=12)
        interest_rate_annual = st.slider("Lãi suất năm (%):", min_value=5.0, max_value=20.0, value=10.0, step=0.5)
        
        repayment_method = st.selectbox(
            "Phương thức trả nợ:",
            ["Dư nợ giảm dần (Gốc trả đều, lãi tính trên dư nợ còn lại)", "Trả góp đều hàng tháng (Gốc + Lãi cố định hằng tháng)"]
        )
        
        st.markdown("---")
        has_col = st.checkbox("Có tài sản thế chấp", value=bool(st.session_state.form_data["has_collateral"]))
        col_val = st.number_input("Giá trị định giá TSBD (VNĐ):", value=int(st.session_state.form_data["collateral_value"]), step=50000000, format="%d")

    # --- TÍNH TOÁN CHI TIẾT ---
    monthly_rate = (interest_rate_annual / 100) / 12
    schedule_data = []
    
    if "giảm dần" in repayment_method:
        principal_per_month = loan_amount / term_months
        remaining_balance = loan_amount
        total_interest = 0
        
        for m in range(1, term_months + 1):
            interest_month = remaining_balance * monthly_rate
            total_month = principal_per_month + interest_month
            total_interest += interest_month
            remaining_balance -= principal_per_month
            if remaining_balance < 0: remaining_balance = 0
            
            schedule_data.append({
                "Tháng": m,
                "Gốc phải trả": principal_per_month,
                "Lãi phải trả": interest_month,
                "Tổng gốc + lãi": total_month,
                "Dư nợ còn lại": remaining_balance
            })
        max_monthly_payment = schedule_data[0]["Tổng gốc + lãi"]
        min_monthly_payment = schedule_data[-1]["Tổng gốc + lãi"]
        total_payment = loan_amount + total_interest
    else:
        if monthly_rate > 0:
            fixed_monthly = loan_amount * monthly_rate * ((1 + monthly_rate)**term_months) / (((1 + monthly_rate)**term_months) - 1)
        else:
            fixed_monthly = loan_amount / term_months
            
        remaining_balance = loan_amount
        total_interest = 0
        
        for m in range(1, term_months + 1):
            interest_month = remaining_balance * monthly_rate
            principal_month = fixed_monthly - interest_month
            total_interest += interest_month
            remaining_balance -= principal_month
            if remaining_balance < 0: remaining_balance = 0
            
            schedule_data.append({
                "Tháng": m,
                "Gốc phải trả": principal_month,
                "Lãi phải trả": interest_month,
                "Tổng gốc + lãi": fixed_monthly,
                "Dư nợ còn lại": remaining_balance
            })
        max_monthly_payment = fixed_monthly
        min_monthly_payment = fixed_monthly
        total_payment = fixed_monthly * term_months

    df_schedule = pd.DataFrame(schedule_data)
    dti_ratio = (max_monthly_payment / income) * 100 if income > 0 else 0
    ltv_ratio = (loan_amount / col_val * 100) if (has_col and col_val > 0) else 0.0
    surplus_income = income - max_monthly_payment

    with col_c2:
        st.subheader("📊 Bảng Chỉ Số Đánh Giá Rủi Ro")
        
        st.metric(label="Tháng trả cao nhất (Tháng đầu)", value=f"{max_monthly_payment:,.0f} VNĐ")
        if "giảm dần" in repayment_method:
            st.metric(label="Tháng trả thấp nhất (Tháng cuối)", value=f"{min_monthly_payment:,.0f} VNĐ")
        st.metric(label="Tổng tiền lãi phải trả", value=f"{total_interest:,.0f} VNĐ")
        st.metric(label="Tổng gốc và lãi suốt thời hạn", value=f"{total_payment:,.0f} VNĐ")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="Tỷ lệ DTI (Nợ/Thu nhập)", value=f"{dti_ratio:.1f}%", 
                      delta="An toàn (<= 50%)" if dti_ratio <= 50 else "Cao (> 50%)",
                      delta_color="normal" if dti_ratio <= 50 else "inverse")
        with col_m2:
            if has_col:
                st.metric(label="Tỷ lệ LTV (Vay/Tài sản)", value=f"{ltv_ratio:.1f}%",
                          delta="An toàn (<= 70%)" if ltv_ratio <= 70 else "Cao (> 70%)",
                          delta_color="normal" if ltv_ratio <= 70 else "inverse")
            else:
                st.metric(label="Loại hình", value="Tín chấp")
                
        st.metric(label="Thặng dư thu nhập sau trả nợ (Tháng đầu)", value=f"{surplus_income:,.0f} VNĐ",
                  delta="Đủ trang trải" if surplus_income > 5000000 else "Cần cân nhắc",
                  delta_color="normal" if surplus_income > 5000000 else "inverse")

    st.markdown("---")
    
    # --- ĐÁNH GIÁ TỔNG QUAN & ĐIỀU KIỆN LƯU ---
    st.subheader("🎯 Kết Luận & Khuyến Nghị Thẩm Định")
    dti_pass = dti_ratio <= 50
    ltv_pass = (ltv_ratio <= 70) if has_col else True
    
    is_safe = dti_pass and ltv_pass

    if is_safe:
        st.success("✅ **HỒ SƠ ĐẠT TIÊU CHÍ AN TOÀN:** Các chỉ số DTI và LTV đều nằm trong ngưỡng kiểm soát của ngân hàng. Đủ điều kiện đề xuất phê duyệt.")
    else:
        st.error("❌ **HỒ SƠ CÓ RỦI RO CAO:** Vượt quá giới hạn an toàn cho phép (DTI > 50% hoặc LTV > 70%). **Nút lưu hệ thống đã bị khóa** do không đạt chuẩn rủi ro.")

    st.markdown("---")

    # --- KHU VỰC NÚT LƯU CHỈ MỞ KHI AN TOÀN ---
    if is_safe:
        if st.button("💾 Lưu Hồ Sơ An Toàn Lên Hệ Thống Quản Trị", type="primary"):
            if not st.session_state.form_data["name"].strip() or not st.session_state.form_data["phone"].strip():
                st.error("Vui lòng điền đầy đủ Họ tên và Số điện thoại khách hàng!")
            else:
                record_id = f"HD-{datetime.datetime.now().strftime('%H%M%S-%d%m')}"
                
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    sql = """
                        REPLACE INTO dangky_vayvon 
                        (id, name, phone, purpose, requested_amount, monthly_income, credit_score, has_collateral, collateral_type, collateral_value, notes, date, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (
                        record_id,
                        st.session_state.form_data["name"],
                        st.session_state.form_data["phone"],
                        st.session_state.form_data["purpose"],
                        float(loan_amount),
                        float(income),
                        int(st.session_state.form_data["credit_score"]),
                        1 if has_col else 0,
                        st.session_state.form_data["collateral_type"],
                        float(col_val),
                        st.session_state.form_data["notes"],
                        str(datetime.date.today()),
                        "Chờ thẩm định"
                    )
                    
                    cursor.execute(sql, values)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.success("🎉 Lưu hồ sơ thành công vào kho cơ sở dữ liệu trên Cloud cho trang Quản Trị!")
                except Exception as e:
                    st.error(f"Lỗi khi lưu vào MySQL: {e}")
    else:
        st.warning("⚠️ Vui lòng điều chỉnh lại thông số khoản vay (tăng thu nhập, giảm số tiền vay hoặc tăng tài sản thế chấp) để hạ tỷ lệ DTI/LTV xuống mức an toàn trước khi lưu.")

    st.markdown("---")
    
    # --- LỊCH TRẢ NỢ CHI TIẾT ---
    st.subheader("📅 Lịch Trả Nợ Chi Tiết Theo Tháng")
    st.markdown("Khách hàng có thể theo dõi cụ thể số tiền gốc, tiền lãi và dư nợ còn lại qua từng kỳ thanh toán:")
    
    st.dataframe(
        df_schedule.style.format({
            "Gốc phải trả": "{:,.0f} VNĐ",
            "Lãi phải trả": "{:,.0f} VNĐ",
            "Tổng gốc + lãi": "{:,.0f} VNĐ",
            "Dư nợ còn lại": "{:,.0f} VNĐ"
        }),
        use_container_width=True
    )
    
    st.markdown("### 📈 Biểu Đồ Diễn Biến Khoản Trả Hàng Tháng")
    st.line_chart(df_schedule.set_index("Tháng")[["Gốc phải trả", "Lãi phải trả", "Tổng gốc + lãi"]])
