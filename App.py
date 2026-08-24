import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Mock Database ---
if "applications" not in st.session_state:
    st.session_state.applications = [
        {
            "id": "HD-2026-0891",
            "name": "Nguyễn Văn An",
            "phone": "0912345678",
            "purpose": "Kinh doanh mở rộng xưởng",
            "requested_amount": 500000000,
            "monthly_income": 35000000,
            "credit_score": 740,
            "status": "Chờ thẩm định",
            "eligibility": "Đạt",
            "suggested_limit": 450000000,
            "date": "2026-08-24",
            "notes": "Hồ sơ đầy đủ, cần xác minh tài sản bảo đảm."
        },
        {
            "id": "HD-2026-0892",
            "name": "Trần Thị Bình",
            "phone": "0988765432",
            "purpose": "Mua sắm trang thiết bị",
            "requested_amount": 200000000,
            "monthly_income": 15000000,
            "credit_score": 620,
            "status": "Đã phê duyệt",
            "eligibility": "Cần xem xét",
            "suggested_limit": 150000000,
            "date": "2026-08-23",
            "notes": "Đã kiểm tra lịch sử tín dụng CIC, chấp nhận mức 150 triệu."
        },
        {
            "id": "HD-2026-0893",
            "name": "Lê Hoàng Long",
            "phone": "0905111222",
            "purpose": "Đầu tư lưu động ngắn hạn",
            "requested_amount": 1000000000,
            "monthly_income": 60000000,
            "credit_score": 810,
            "status": "Đã giải ngân",
            "eligibility": "Đạt xuất sắc",
            "suggested_limit": 1000000000,
            "date": "2026-08-22",
            "notes": "Khách hàng VIP, tài sản thế chấp nhà mặt phố."
        },
        {
            "id": "HD-2026-0894",
            "name": "Phạm Thị Mai",
            "phone": "0933445566",
            "purpose": "Tiêu dùng cá nhân / Sửa nhà",
            "requested_amount": 150000000,
            "monthly_income": 8000000,
            "credit_score": 540,
            "status": "Từ chối",
            "eligibility": "Không đạt",
            "suggested_limit": 0,
            "date": "2026-08-21",
            "notes": "Thu nhập không đủ điều kiện trả nợ theo tỷ lệ DTI."
        }
    ]

# --- Sidebar Navigation ---
st.sidebar.title("🏢 Hệ Thống Quản Lý Vốn")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Chọn phân hệ:",
    ["📊 Dashboard Tổng Quan", "👥 Quản Lý Hồ Sơ & Thẩm Định", "🧮 Công Cụ Tính Toán Nhanh", "➕ Tiếp Nhận Khách Hàng Mới"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Hệ thống hỗ trợ Nhân viên Thẩm định:** Kiểm tra tự động điểm tín dụng, gợi ý hạn mức và ra quyết định nhanh chóng.")

# ==========================================
# 1. DASHBOARD TỔNG QUAN
# ==========================================
if menu == "📊 Dashboard Tổng Quan":
    st.title("📊 Tổng Quan Hoạt Động Vốn")
    st.markdown("Cập nhật tình hình tiếp nhận, thẩm định và giải ngân nguồn vốn theo thời gian thực.")
    
    df = pd.DataFrame(st.session_state.applications)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Tổng số hồ sơ", value=len(df), delta="+2 hôm nay")
    with col2:
        total_req = df['requested_amount'].sum()
        st.metric(label="Tổng nhu cầu vốn", value=f"{total_req:,.0f} VNĐ", delta="+15%")
    with col3:
        approved_count = len(df[df['status'].isin(['Đã phê duyệt', 'Đã giải ngân'])])
        st.metric(label="Hồ sơ đã duyệt/giải ngân", value=approved_count, delta="Ổn định")
    with col4:
        avg_score = int(df['credit_score'].mean())
        st.metric(label="Điểm tín dụng TB", value=avg_score, delta="+5 điểm")
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Trạng Thái Xử Lý Hồ Sơ")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Trạng thái', 'Số lượng']
        fig_status = px.pie(status_counts, values='Số lượng', names='Trạng thái', hole=0.4, 
                            color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_status, use_container_width=True)
        
    with col_chart2:
        st.subheader("Nhu Cầu Vốn Theo Mục Đích")
        fig_bar = px.bar(df, x='purpose', y='requested_amount', color='name',
                         labels={'purpose': 'Mục đích vay', 'requested_amount': 'Số tiền yêu cầu (VNĐ)'},
                         color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# 2. QUẢN LÝ HỒ SƠ & THẨM ĐỊNH (CORE FEATURE)
# ==========================================
elif menu == "👥 Quản Lý Hồ Sơ & Thẩm Định":
    st.title("👥 Quản Lý Hồ Sơ Khách Hàng & Thẩm Định Tín Dụng")
    st.markdown("Nhân viên có thể kiểm tra nhanh tiêu chí, xem xét mức độ phù hợp và duyệt hạn mức cho vay.")
    
    df = pd.DataFrame(st.session_state.applications)
    
    status_filter = st.selectbox("Lọc theo trạng thái hồ sơ:", ["Tất cả", "Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"])
    if status_filter != "Tất cả":
        filtered_df = df[df['status'] == status_filter]
    else:
        filtered_df = df
        
    for idx, row in filtered_df.iterrows():
        with st.expander(f"📁 **{row['id']}** - {row['name']} | Nhu cầu: {row['requested_amount']:,.0f} VNĐ | Trạng thái: **{row['status']}**"):
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.markdown("#### 👤 Thông tin khách hàng")
                st.write(f"**Họ tên:** {row['name']}")
                st.write(f"**Điện thoại:** {row['phone']}")
                st.write(f"**Mục đích:** {row['purpose']}")
                st.write(f"**Ngày nộp:** {row['date']}")
                
            with c2:
                st.markdown("#### 💳 Chỉ số tài chính & Tiêu chí")
                st.write(f"**Thu nhập tháng:** {row['monthly_income']:,.0f} VNĐ")
                st.write(f"**Điểm tín dụng (CIC):** {row['credit_score']}")
                
                eligibility = row['eligibility']
                if "Đạt" in eligibility:
                    st.success(f"Đánh giá tiêu chí: **{eligibility}**")
                elif "Cần" in eligibility:
                    st.warning(f"Đánh giá tiêu chí: **{eligibility}**")
                else:
                    st.error(f"Đánh giá tiêu chí: **{eligibility}**")
                    
            with c3:
                st.markdown("#### 🎯 Gợi ý & Phê duyệt từ hệ thống")
                st.info(f"💡 Hạn mức đề xuất: **{row['suggested_limit']:,.0f} VNĐ**")
                
                new_status = st.selectbox(
                    "Cập nhật trạng thái",
                    ["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"],
                    index=["Chờ thẩm định", "Đã phê duyệt", "Đã giải ngân", "Từ chối"].index(row['status']),
                    key=f"status_{row['id']}"
                )
                
                notes = st.text_input("Ghi chú thẩm định", value=row['notes'], key=f"notes_{row['id']}")
                
                if st.button(f"Lưu thay đổi {row['id']}", key=f"btn_{row['id']}"):
                    st.session_state.applications[idx]['status'] = new_status
                    st.session_state.applications[idx]['notes'] = notes
                    st.success("Đã cập nhật thành công hồ sơ!")
                    st.rerun()

# ==========================================
# 3. CÔNG CỤ TÍNH TOÁN NHANH (LOAN CALCULATOR)
# ==========================================
elif menu == "🧮 Công Cụ Tính Toán Nhanh":
    st.title("🧮 Công Cụ Tính Toán Hạn Mức & Lãi Suất Cho Vay")
    st.markdown("Hỗ trợ nhân viên tư vấn nhanh cho khách hàng các chỉ số tài chính, khả năng trả nợ và gói vay phù hợp.")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.subheader("Thông tin đầu vào")
        income = st.number_input("Thu nhập hàng tháng của KH (VNĐ):", value=30000000, step=5000000, format="%d")
        loan_amount = st.number_input("Số tiền muốn vay (VNĐ):", value=300000000, step=50000000, format="%d")
        term_months = st.slider("Thời hạn vay (Tháng):", min_value=12, max_value=360, value=60, step=12)
        interest_rate_annual = st.slider("Lãi suất năm (%):", min_value=6.0, max_value=18.0, value=10.5, step=0.5)
        
    with col_calc2:
        st.subheader("Kết quả thẩm định nhanh")
        
        monthly_rate = (interest_rate_annual / 100) / 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * monthly_rate * ((1 + monthly_rate)**term_months) / (((1 + monthly_rate)**term_months) - 1)
        else:
            monthly_payment = loan_amount / term_months
            
        total_payment = monthly_payment * term_months
        total_interest = total_payment - loan_amount
        dti_ratio = (monthly_payment / income) * 100
        
        st.metric(label="Gốc & Lãi trả hàng tháng", value=f"{monthly_payment:,.0f} VNĐ")
        st.metric(label="Tổng tiền lãi phải trả", value=f"{total_interest:,.0f} VNĐ")
        st.metric(label="Tỷ lệ trả nợ / Thu nhập (DTI)", value=f"{dti_ratio:.1f}%", 
                  delta="An toàn (< 50%)" if dti_ratio <= 50 else "Cân nhắc rủi ro (> 50%)",
                  delta_color="normal" if dti_ratio <= 50 else "inverse")
        
        if dti_ratio <= 50:
            st.success("✅ Khách hàng **ĐỦ ĐIỀU KIỆN** về khả năng tài chính đối với khoản vay này.")
        else:
            st.warning("⚠️ Khoản vay vượt ngưỡng an toàn tài chính tiêu chuẩn. Cần xem xét thêm tài sản bảo đảm hoặc giảm hạn mức.")

# ==========================================
# 4. TIẾP NHẬN KHÁCH HÀNG MỚI
# ==========================================
elif menu == "➕ Tiếp Nhận Khách Hàng Mới":
    st.title("➕ Tiếp Nhận Hồ Sơ Nhu Cầu Vốn Mới")
    st.markdown("Nhập liệu thông tin khách hàng trực tiếp tại quầy hoặc từ kênh tiếp nhận trực tuyến.")
    
    with st.form("new_loan_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Họ và tên khách hàng:")
            phone = st.text_input("Số điện thoại liên hệ:")
            purpose = st.selectbox("Mục đích vay vốn:", ["Kinh doanh mở rộng xưởng", "Mua sắm trang thiết bị", "Đầu tư lưu động ngắn hạn", "Tiêu dùng cá nhân / Sửa nhà", "Mua bất động sản"])
        with col2:
            req_amount = st.number_input("Số tiền yêu cầu (VNĐ):", value=300000000, step=50000000)
            monthly_inc = st.number_input("Thu nhập hàng tháng (VNĐ):", value=25000000, step=5000000)
            credit_score = st.slider("Điểm tín dụng dự kiến / CIC:", min_value=300, max_value=850, value=700)
            
        submitted = st.form_submit_button("Tiếp nhận & Chạy chấm điểm tự động")
        
        if submitted:
            if not full_name or not phone:
                st.error("Vui lòng điền đầy đủ họ tên và số điện thoại!")
            else:
                if credit_score >= 700 and monthly_inc >= (req_amount * 0.05):
                    eligibility = "Đạt"
                    suggested_limit = req_amount
                elif credit_score >= 600:
                    eligibility = "Cần xem xét"
                    suggested_limit = int(req_amount * 0.8)
                else:
                    eligibility = "Không đạt"
                    suggested_limit = 0
                    
                new_id = f"HD-2026-08{len(st.session_state.applications)+1:02d}"
                new_record = {
                    "id": new_id,
                    "name": full_name,
                    "phone": phone,
                    "purpose": purpose,
                    "requested_amount": req_amount,
                    "monthly_income": monthly_inc,
                    "credit_score": credit_score,
                    "status": "Chờ thẩm định",
                    "eligibility": eligibility,
                    "suggested_limit": suggested_limit,
                    "date": str(datetime.date.today()),
                    "notes": "Hồ sơ mới tiếp nhận từ hệ thống."
                }
                st.session_state.applications.append(new_record)
                st.success(f"Thêm thành công hồ sơ {new_id} cho khách hàng {full_name}!")
                st.balloons()
